import os
import time
import json
import base64
import argparse
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
sys.path.append("/home/user/RAG/UniDoc_bench/UniDoc-Bench/src/qa_synthesize")  # e.g., "/path/to/your/project/src/qa_synthesize"
from chunks_extraction import chunk_match_back, extract_relevant_chunks
from collections import defaultdict
from openai import OpenAI as OpenAI_openai
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


import nest_asyncio
nest_asyncio.apply()



def read_json(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
        json_data.close()
    return data


class MyRAG:
    def __init__(
        self,
        folder,
        folder_elements,
        load_index_path,
        save_index_path,
        model_name,
        similarity_top_k=20,
        hyde_use=False,
    ):
        self.folder_elements = folder_elements
        self.folder = folder
        self.load_index_path = load_index_path
        self.save_index_path = save_index_path
        self.model_name = model_name
        #self.llm = OpenAI(temperature=0.00001, model=model_name)               #changed to local LLM model trhough Ollama
        self.llm=Ollama(temperature=0.00001, model=model_name)
        Settings.llm = self.llm
        self.llm_openai=OpenAI_openai(base_url = 'http://localhost:11434/v1', api_key='ollama')
        #self.embed_model = OpenAIEmbedding()                                   #changed to local embedding model through Ollama
        self.embed_model=OllamaEmbedding(model_name="mxbai-embed-large")
        Settings.embed_model = self.embed_model
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 24
        self.reranker = None
        self.documents = SimpleDirectoryReader(folder)                          #removed reading all documents on creating MyRAG exemplar
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
            nodes = parser.get_nodes_from_documents(self.documents.load_data())     #reading pdfs and getting nodes

            storage_context = StorageContext.from_defaults(
                docstore=SimpleDocumentStore(),
                vector_store=SimpleVectorStore(),
                index_store=SimpleIndexStore(),
            )

            storage_context.docstore.add_documents(nodes)


            vector_index = VectorStoreIndex(nodes, storage_context=storage_context,embed_model=self.embed_model, show_progress=True)
            vector_index.storage_context.persist(persist_dir=self.save_index_path)

        else:
            print('Uploading database...')
            storage_context = StorageContext.from_defaults(
                persist_dir=self.load_index_path
            )
            vector_index = load_index_from_storage(storage_context)
            print('Database is loaded')

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
        for img in imgs:
            img_prompt.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{imgs[img]}", "name": f"This is the image:<<fig-{img}>>"},
            })

        return img_prompt


    def get_answer(self, question, chunks=None, one_by_one=False, filter_unknown=True, answer_any_way=False, hyde_use=False):
        if not chunks and hyde_use:
            return self.rag_query_engine_rewrite.query(question)

        start = time.time()  # record start time
        
        if not chunks:
            chunks, metadata = self.retrieve_chunks(question)

        #print(f"--> CHUNKS: {chunks}\n--> METADATA: {metadata}")
        #img_prompt = self.match_images(chunks, metadata)

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
            #user_prompt += img_prompt
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

            
            user_prompt=f"Context: {chunks_answer}\n\nbased on previous context answer this question: {question}"
            
            
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
            total_cost = input_cost + output_cost


            answers = [response.choices[0].message.content]
        if filter_unknown:
            answers = [a for a in answers if "I don't know" not in a]
        return answers, chunks, metadata, total_cost, elapsed

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
        default="gpt-4.1",
        type=str,
        help="openai model",
    )
    parser.add_argument(
        "--question_path",
        type=str,
        required=True
    )
    parser.add_argument(
        "--save_path",
        type=str,
        required=True
    )
    parser.add_argument(
        "--folder_elements",
        type=str,
        required=True
    )
    parser.add_argument(
        "--similarity_top_k",
        default=10,
        type=int
    )
    
    name_str='commerce_manufacturing'
    
    args = argparse.Namespace(
                                folder=f"/home/user/RAG/UniDoc_bench/UniDoc-Bench/data/downloaded/UniDoc-Bench/{name_str}_pdfs/{name_str}",             #folder with original pdf-files
                                load_index_path=f"/home/user/RAG/UniDoc_bench/UniDoc-Bench/src/baselines/databases/simple_rag/{name_str}/paper",        #folder path, where lies files with vector database. If not None - program will upload existing database, otherwise, create a new one
                                save_index_path=f"/home/user/RAG/UniDoc_bench/UniDoc-Bench/src/baselines/databases/simple_rag/{name_str}/paper",        #folder path where should be saved files with vector database
                                model_name="llama3.1",                                                                                                  #name of LLM model
                                question_path=f"/home/user/RAG/UniDoc_bench/UniDoc-Bench/data/QA/filtered/{name_str}.json",                             #file path to file with questions
                                save_path=f"/home/user/RAG/UniDoc_bench/UniDoc-Bench/src/baselines/results/simple_rag/{name_str}.json",                 #file path to file with retriever work's results
                                folder_elements=f"/home/user/RAG/UniDoc_bench/UniDoc-Bench/data/downloaded/UniDoc-Bench/{name_str}_pdfs/{name_str}",    #don't know what is it
                                similarity_top_k=10                                                                                                     #maybe, path to file with non-text element's descriptions like images and tables
                                )                                                                                                                       #Maybe i got something wrong because of lack of descriptions
    
    myrag = MyRAG(
        folder=args.folder,
        folder_elements=args.folder_elements,
        load_index_path=args.load_index_path,
        save_index_path=args.save_index_path,
        hyde_use=False,
        similarity_top_k=args.similarity_top_k,
        model_name=args.model_name,
    )
    
    
    with open(args.question_path, "r") as f:        #in basis, it should be a jsonl file and should be read in lines but it is json not jsonl
        data = list(f)
        
    data=read_json(args.question_path)

    dataset = defaultdict(list)         #original way to make dataset with retrieves: dictionary of lists
    dataset2=[]                         #more human-readable dataset: list of dictionaries
    
    for element in data:                
        #try:
            #element = json.loads(elementer)[0]
            question = element["rewritten_question_obscured"]
            response, chunks, metadata, total_cost, elapsed = myrag.get_answer(question, hyde_use=False, answer_any_way=True)
            dataset["baseline"].append(response[0])
            dataset["question_type"].append(element["question_type"])
            dataset["answer_type"].append(element["answer_type"])
            #dataset["contexts"].append(element["contexts"])
            dataset["retrieved_contexts"].append(chunks)
            dataset["retrieved_metadata"].append(metadata)
            dataset["chunk_used"].append(element["chunk_used"])
            dataset["question"].append(question)
            dataset["gt"].append(element["complete_answer"])
            dataset["cost"].append(total_cost)
            dataset["elapsed"].append(elapsed)
            dataset2.append({'baseline': response[0], 'question_type':element["question_type"], "answer_type":element["answer_type"],
                             "retrieved_contexts":chunks, "retrieved_metadata":metadata, "chunk_used": element["chunk_used"], "question":question, "gt":element["complete_answer"],
                             "cost": total_cost, "elapsed":elapsed})
            
            #print(f"--> RESPONSE: {response}")
            #break
        #except Exception as error:
        #    print(f"Error: {error}")
    
    
    
    with open(args.save_path, "w") as f:
        json.dump(dataset, f)
    
    with open(f"/home/user/RAG/UniDoc_bench/UniDoc-Bench/src/baselines/results/simple_rag/{name_str}_humanreadable.json", "w") as file:
        json.dump(dataset2, file)
    




