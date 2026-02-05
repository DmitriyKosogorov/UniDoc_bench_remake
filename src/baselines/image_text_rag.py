import os
import json
import base64
import requests
import argparse
import math, re
from io import BytesIO
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    ServiceContext,
)
from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    KeywordTableSimpleRetriever,
)
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import PromptTemplate
from llama_index.core import Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.query_engine import TransformQueryEngine
from prompts.rag_template import DEFAULT_TEMPLATE, STRICT_TEMPLATE
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import sys
sys.path.append("YOUR_PROJECT_PATH/src/qa_synthesize")  # e.g., "/path/to/your/project/src/qa_synthesize"
from chunks_extraction import chunk_match_back, extract_relevant_chunks
from collections import defaultdict
from PIL import Image, ImageDraw
from openai import OpenAI as OpenAI_openai

import nest_asyncio
nest_asyncio.apply()

class MyRAG:
    def __init__(
        self,
        folder,
        folder_elements,
        load_index_path,
        save_index_path,
        model_name,
        similarity_top_k=5,
        hyde_use=False,
        search_url="http://0.0.0.0:8002/search"
    ):
        self.similarity_top_k = similarity_top_k
        self.folder_elements = folder_elements
        self.folder = folder
        self.load_index_path = load_index_path
        self.save_index_path = save_index_path
        self.model_name = model_name
        self.llm = OpenAI(temperature=0.00001, model=model_name)
        Settings.llm = self.llm
        self.llm_openai = OpenAI_openai(api_key=os.environ.get("OPENAI_API_KEY"))

        self.embed_model = OpenAIEmbedding()
        Settings.embed_model = self.embed_model
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 24
        self.reranker = None
        self.documents = SimpleDirectoryReader(folder).load_data()
        self.storage_context, self.vector_index = self.build_index()
        self.rag_query_engine, self.retriever, self.rag_query_engine_rewrite = self.build_engine(similarity_top_k, hyde_use)
        rag_query_engine_tool = QueryEngineTool(
            query_engine=self.rag_query_engine,
            metadata=ToolMetadata(
                name="slack_message_rag",
                description="Slack messages.",
            )
        )
        self.rag_query_engine_sub = SubQuestionQueryEngine.from_defaults(
            query_engine_tools=[rag_query_engine_tool],
            use_async=True,
        )
        self.search_url = search_url
        self.max_pixels = 512 * 28 * 28
        self.min_pixels = 256 * 28 * 28

    def process_image(self, image):
        if isinstance(image, dict):
            image = Image.open(BytesIO(image['bytes']))
        elif isinstance(image, str):
            image = Image.open(image)

        if (image.width * image.height) > self.max_pixels:
            resize_factor = math.sqrt(self.max_pixels / (image.width * image.height))
            width, height = int(image.width * resize_factor), int(image.height * resize_factor)
            image = image.resize((width, height))

        if (image.width * image.height) < self.min_pixels:
            resize_factor = math.sqrt(self.min_pixels / (image.width * image.height))
            width, height = int(image.width * resize_factor), int(image.height * resize_factor)
            image = image.resize((width, height))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        byte_stream = BytesIO()
        image.save(byte_stream, format="JPEG")
        byte_array = byte_stream.getvalue()
        base64_encoded_image = base64.b64encode(byte_array)
        base64_string = base64_encoded_image.decode("utf-8")

        return image, base64_string.strip()

    def search_img(self, query):
        if isinstance(query, str):
            query = [query]
        search_response = requests.get(self.search_url, params={"queries": query})
        search_results = search_response.json()

        search_results = [result['image_file'] for result in search_results[0]]
        image_paths = search_results[:self.similarity_top_k]

        user_content = [
                {
                    "type": "text",
                    "text": "These are contexts in image format:"
                }
            ]
        for image_path in image_paths:
            image_raw = Image.open(image_path)
            image_input, img_base64 = self.process_image(image_raw)
            user_content += [{
                'type': 'image_url',
                'image_url': {
                    'url': f"data:image/jpeg;base64,{img_base64}"
                }
            }]
        return user_content, image_paths

    def update_template(self, query_engine, template_usage):
        new_summary_tmpl = PromptTemplate(template_usage)
        query_engine.update_prompts(
            {"response_synthesizer:summary_template": new_summary_tmpl}
        )
    def build_index(self):
        if (
            not self.load_index_path
        ):  # generate and store the index if it doesn't exist, but load it if it does
            parser = SentenceSplitter()
            nodes = parser.get_nodes_from_documents(self.documents)

            storage_context = StorageContext.from_defaults(
                docstore=SimpleDocumentStore(),
                vector_store=SimpleVectorStore(),
                index_store=SimpleIndexStore(),
            )

            storage_context.docstore.add_documents(nodes)


            vector_index = VectorStoreIndex(nodes, storage_context=storage_context,embed_model=self.embed_model, show_progress=True)
            vector_index.storage_context.persist(persist_dir=self.save_index_path)

        else:
            storage_context = StorageContext.from_defaults(
                persist_dir=self.load_index_path
            )
            vector_index = load_index_from_storage(storage_context)

        return storage_context, vector_index

    def build_retriever(self, similarity_top_k):
        vector_retriever = VectorIndexRetriever(
            index=self.vector_index, similarity_top_k=similarity_top_k
        )
        return vector_retriever

    def build_engine(self, similarity_top_k, hyde_use=False):
        retriever = self.build_retriever(similarity_top_k)
        response_synthesizer = get_response_synthesizer(
            response_mode="compact",
        )
        rag_query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )

        rag_query_engine_rewrite = None
        if hyde_use:
            hyde = HyDEQueryTransform(include_original=True)
            rag_query_engine_rewrite = TransformQueryEngine(rag_query_engine, hyde)

        return rag_query_engine, retriever, rag_query_engine_rewrite

    def verify_answer_exist(self, question):
        chunks, metadata = self.retrieve_chunks(question)
        template = (
            "We have provided context information below. \n"
            "---------------------\n"
            "{context_str}"
            "\n---------------------\n"
            "Given this information, please verify whether you can find the answer of the following question: {query_str}\n"
            "If you can find the answer in the context, you will reply 'Yes'.\n"
            "If you can find the answer in the context, you will reply 'No'.\n"
        )

        verify_dict = {"verified-yes": [], "verified-no": []}
        for chunk in chunks:
            prompt = template.format(context_str=chunk, query_str=question)
            if "yes" in self.llm.complete(prompt).text[:10].lower():
                verify_dict["verified-yes"].append(chunk)
            if "no" in self.llm.complete(prompt).text[:10].lower():
                verify_dict["verified-no"].append(chunk)
        return verify_dict

    def match_images(self, chunks, metadata):
        new_metadata = []
        for m in metadata:
            new_metadata.append({"source": m["file_path"]})

        imgs = dict()
        for chunk, chunk_metadata in zip(chunks, new_metadata):
            _, img = chunk_match_back(chunk, chunk_metadata, self.folder_elements)
            for img_key in img:
                with open(img[img_key], "rb") as image_file:
                    imgs[img_key] = base64.b64encode(image_file.read()).decode("utf-8")

        img_prompt = []
        if imgs:
            img_prompt.append({
                "type": "text",
                "text": "Images in the above contexts:\n"
            })
        for img in imgs:
            img_prompt.append({
                "type": "text",
                "text": f"\nThis is the image:<<fig-{img}>>"
            })
            img_prompt.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{imgs[img]}"},
            })

        return img_prompt


    def get_answer(self, question, chunks=None, one_by_one=False, filter_unknown=True, answer_any_way=False, hyde_use=False):
        import time
        start = time.time()  # record start time

        if not chunks and hyde_use:
            return self.rag_query_engine_rewrite.query(question)

        if not chunks:
            chunks, metadata = self.retrieve_chunks(question)

        img_prompt = self.match_images(chunks, metadata)

        image_pdf_prompt, image_paths_retrieval = self.search_img(question)

        if answer_any_way:
            template = DEFAULT_TEMPLATE
        else:
            template = STRICT_TEMPLATE

        if one_by_one:
            answers = []
            for chunk in chunks:
                prompt = template.format(context_str=chunk, query_str=question)
                answers.append(self.llm.complete(prompt).text)
        else:
            chunks_answer = '\n'.join([f"Context {idx}:\n{c}" for idx, c in enumerate(chunks)])
            prompt = template.format(context_str=chunks_answer, query_str=question)
            user_prompt = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            user_prompt += image_pdf_prompt
            user_prompt += img_prompt

            user_prompt += [
                {
                    "type": "text",
                    "text": f"Given the above contexts and images, provide a very direct and concise answer for this question: \n\nQuestion: {question}"
                }
            ]

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant to answer the question based on the given contexts. You will strictly answer the question based on the contexts and images.",
                },
                {"role": "user", "content": user_prompt},
            ]

            response = self.llm_openai.chat.completions.create(
                messages=messages,
                temperature=0.00001,
                model=self.model_name
            )

            end = time.time()  # record end time
            elapsed = end - start

            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            input_cost = (input_tokens / 1000000) * 3
            output_cost = (output_tokens / 1000000) * 12
            total_cost = (input_cost + output_cost, elapsed)


            answers = [response.choices[0].message.content]
        if filter_unknown:
            answers = [a for a in answers if "I don't know" not in a]
        return answers, chunks, metadata+image_paths_retrieval, total_cost

    def retrieve_chunks(self, question):
        retrieve_nodes = self.retriever.retrieve(question)
        metadata = [node.metadata for node in retrieve_nodes]
        nodes = [node.text for node in retrieve_nodes]
        return nodes, metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--folder",
        type=str,
        help="database",
    )
    parser.add_argument(
        "--load_index_path",
        default=None,
        type=str,
        help="database",
    )
    parser.add_argument(
        "--save_index_path",
        type=str,
        help="database",
    )
    parser.add_argument(
        "--model_name",
        default="gpt-4.1-mini",
        type=str,
        help="openai model",
    )
    parser.add_argument(
        "--save_path",
        required=True,
        type=str
    )
    parser.add_argument(
        "--question_path",
        required=True,
        type=str
    )
    parser.add_argument(
        "--folder_elements",
        required=True,
        type=str
    )
    parser.add_argument(
        "--similarity_top_k",
        required=True,
        type=int,
        default=5
    )

    args = parser.parse_args()

    myrag = MyRAG(
        folder=args.folder,
        folder_elements=args.folder_elements,
        load_index_path=args.load_index_path,
        save_index_path=args.save_index_path,
        hyde_use=False,
        similarity_top_k=args.similarity_top_k,
        model_name=args.model_name,
    )

    with open(args.question_path, "r") as f:
        data = list(f)

    dataset = defaultdict(list)

    for element in data:
        for _ in range(5):
            try:
                element = json.loads(element)
                question = element["rewritten_question_obscured"]
                response, chunks, metadata, total_cost = myrag.get_answer(question, hyde_use=False, answer_any_way=True)
                dataset["question"].append(question)
                dataset["gt"].append(element["complete_answer"])
                dataset["baseline"].append(response[0])
                dataset["question_type"].append(element["question_type"])
                dataset["answer_type"].append(element["answer_type"])
                dataset["contexts"].append(element["contexts"])
                dataset["retrieved_contexts"].append(chunks)
                dataset["retrieved_metadata"].append(metadata)
                dataset["chunk_used"].append(element["chunk_used"])
                dataset["cost"].append(total_cost)
                break
            except Exception as error:
                print(f"Error: {error}")                    #There was no code here so file was invalid
    with open(args.save_path, "w") as f:
        json.dump(dataset, f)





