import os
import io
from PIL import Image
import uuid
from pathlib import Path
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
from llama_index.core.embeddings import MultiModalEmbedding
import sys
sys.path.append("YOUR_PROJECT_PATH/src/qa_synthesize")  # e.g., "/path/to/your/project/src/qa_synthesize"
from chunks_extraction import chunk_match_back, extract_relevant_chunks
from collections import defaultdict
from PIL import Image, ImageDraw
from openai import OpenAI as OpenAI_openai
from tqdm import tqdm
import nest_asyncio
nest_asyncio.apply()
from llama_index.core.schema import ImageDocument
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from typing import Any, List
from llama_index.core.embeddings import BaseEmbedding
from transformers import AutoModel

import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4")  # or "gpt-3.5-turbo"

class GMEEmbeddings(MultiModalEmbedding):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._model = AutoModel.from_pretrained(
    "YOUR_MODEL_PATH_HERE",  # e.g., "/path/to/your/models/gme-Qwen2-VL-7B-Instruct"
    torch_dtype="float16", device_map='cuda:1', trust_remote_code=True
)
        self._instruction = "Find an image or text that matches the given text.\n"

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = self._model.get_text_embeddings(texts=[self._instruction + query])
        return embeddings[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = self._model.get_text_embeddings(texts=[self._instruction + text])
        return embeddings[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.get_text_embeddings(
            texts=[self._instruction + text for text in texts]
        )
        return embeddings

    def _get_image_embedding(self, image: str) -> List[float]:
        embeddings = self._model.get_image_embeddings(images=[image])
        return embeddings[0]

    def _get_image_embeddings(self, images: List[str]) -> List[List[float]]:
        embeddings = self._model.get_text_embeddings(
            images=images
        )
        return embeddings

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    async def _aget_image_embedding(self, image: str) -> List[float]:
        return self._get_image_embedding(image)

    async def _aget_query_embeddings(self, query: List[str]) -> List[float]:
        return self._get_query_embeddings(query)

    async def _aget_text_embeddings(self, texts: List[str]) -> List[float]:
        return self._get_text_embeddings(text)

    async def _aget_image_embeddings(self, images: List[str]) -> List[float]:
        return self._get_image_embeddings(images)


Settings.embed_model = GMEEmbeddings(model_name="Alibaba-NLP/gme-Qwen2-VL-7B-Instruct")
Settings.image_embed_model = GMEEmbeddings(model_name="Alibaba-NLP/gme-Qwen2-VL-7B-Instruct")

class MyRAG:
    def __init__(
        self,
        folder,
        folder_elements,
        load_index_path,
        save_index_path,
        model_name,
        folder_images="",
        load_index_img_path="",
        save_index_img_path="",
        similarity_top_k=5,
        hyde_use=False,

    ):
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 56

        self.similarity_top_k = similarity_top_k
        self.folder_elements = folder_elements
        self.folder = folder
        self.load_index_path = load_index_path
        self.save_index_path = save_index_path
        self.model_name = model_name
        self.llm = OpenAI(temperature=0.00001, model=model_name)
        Settings.llm = self.llm
        self.llm_openai = OpenAI_openai(api_key=os.environ.get("OPENAI_API_KEY"))

        self.reranker = None
        self.documents = SimpleDirectoryReader(folder).load_data()

        self.folder_images = folder_images
        self.load_index_img_path = load_index_img_path
        self.save_index_img_path = save_index_img_path
        self.storage_context_voyage, self.vector_index_voyage = self.build_index_img()
        self.retriever_img = self.vector_index_voyage.as_retriever(image_similarity_top_k=self.similarity_top_k, similarity_top_k=self.similarity_top_k)

        self.max_pixels = 512 * 28 * 28
        self.min_pixels = 256 * 28 * 28

    def build_index_img(self, extensions=(".png", ".jpg", ".jpeg", ".bmp", ".gif")):
        if not os.path.exists(self.load_index_img_path):
            folder = Path(self.folder_images)
            documents = []

            total_files = len(os.listdir(folder))

            for file_path in tqdm(folder.iterdir(), total=total_files, desc="Processing files"):
                if file_path.suffix.lower() in extensions:
                    with open(file_path, "rb") as f:
                        img_bytes = f.read()
                        encoded_img = base64.b64encode(img_bytes).decode("utf-8")
                        documents.append(
                            ImageDocument(
                                image_path=str(file_path),
                                metadata={"file": str(file_path)}
                            )
                        )

            storage_context = StorageContext.from_defaults(
                vector_store=SimpleVectorStore(),
            )

            from llama_index.core.indices import MultiModalVectorStoreIndex

            vector_index = MultiModalVectorStoreIndex.from_documents(
                documents + self.documents,
                storage_context=storage_context,
                show_progress=True
            )
            vector_index.storage_context.persist(persist_dir=self.save_index_img_path)
        else:
            storage_context = StorageContext.from_defaults(persist_dir=self.save_index_img_path)
            vector_index = load_index_from_storage(storage_context)

        return storage_context, vector_index


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
        nodes = self.retriever_img.retrieve(query)
        nodes = sorted(nodes, key=lambda n: n.score, reverse=True)
        search_results = []
        search_results_path = []
        for node in nodes:
            try:
                #
                #
                #
                with open(node.node.image_path, "rb") as f:
                    img_bytes = f.read()
                    encoded_img = base64.b64encode(img_bytes).decode("utf-8")
                    search_results.append(encoded_img)
                search_results_path.append(node.node.image_path)
            except:
                search_results.append(node.node.text)
                search_results_path.append(node.node.metadata["file_path"])

        search_results = search_results[:self.similarity_top_k]
        search_results_path = search_results_path[:self.similarity_top_k]

        user_content = [
                {
                    "type": "text",
                    "text": "These are contexts (pdfs) in image and text format:"
                }
            ]

        for search_result, search_result_path in zip(search_results, search_results_path):
            if "img" not in search_result_path:
                user_content += [
                    {
                        "type": "text",
                        "text": f"Context: {search_result}"
                    }
                ]
            else:
                user_content += [{
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:image/jpeg;base64,{search_result}"
                    }
                }]

        return user_content, search_results_path

    def update_template(self, query_engine, template_usage):
        new_summary_tmpl = PromptTemplate(template_usage)
        query_engine.update_prompts(
            {"response_synthesizer:summary_template": new_summary_tmpl}
        )

    #
    #         )
    #
    #
    #
    #
    #         )
    #

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

    #
    #
    #         })
    #         })
    #         })
    #


    def get_answer(self, question, chunks=None, one_by_one=False, filter_unknown=True, answer_any_way=False, hyde_use=False):
        import time
        start = time.time()  # record start time

        image_pdf_prompt, image_paths_retrieval = self.search_img(question)

        user_prompt = []

        user_prompt += image_pdf_prompt

        user_prompt += [
            {
                "type": "text",
                "text": f"Given the above pdfs, provide a very direct and concise answer for this question: \n\nQuestion: {question}"
            }
        ]

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant to answer the question based on the given pdfs in image format. You will strictly answer the question based on the contexts in image format.",
            },
            {"role": "user", "content": user_prompt},
        ]

        response = self.llm_openai.chat.completions.create(
            messages=messages,
            temperature=0.00001,
            model=self.model_name,
            max_tokens=2048,
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
        return answers, chunks, image_paths_retrieval, total_cost

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
        "--folder_images",
        required=True,
        type=str
    )
    parser.add_argument(
        "--load_index_img_path",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--save_index_img_path",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--similarity_top_k",
        required=True,
        type=int,
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
        folder_images=args.folder_images,
        load_index_img_path=args.load_index_img_path,
        save_index_img_path=args.save_index_img_path
    )

    with open(args.question_path, "r") as f:
        data = list(f)

    dataset = defaultdict(list)

    for element in data:
        element = json.loads(element)
        question = element["rewritten_question_obscured"]
        response, chunks, metadata, total_cost = myrag.get_answer(question, hyde_use=False, answer_any_way=True)
        if response:
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

    with open(args.save_path, "w") as f:
        json.dump(dataset, f)






