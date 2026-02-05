import json
from tqdm import tqdm 
import argparse
from copy import deepcopy
import os 
import openai
from typing import List, Dict
import time
import re
from typing import Dict, List, Optional, Sequence, Set, Tuple
import ast


from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.extractors import BaseExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.voyageai import VoyageEmbedding
from llama_index.core.llms import ChatMessage

#from llama_index.embeddings.instructor import InstructorEmbedding
#from llama_index.postprocessor import FlagEmbeddingReranker
from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
from llama_index.core.postprocessor import LLMRerank
from llama_index.core import Settings, VectorStoreIndex, load_index_from_storage, StorageContext
from llama_index.core.schema import QueryBundle, MetadataMode
#from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.retrievers.bm25 import BM25Retriever

from FlagEmbedding import FlagReranker
from llama_index.core import Document
import json

from PyPDF2 import PdfReader
import pymeteor.pymeteor as pymeteor
from rouge_score import rouge_scorer



def read_json(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
        json_data.close()
    return data


def read_jsonl(filename):
    with open(filename) as f:
        data = [json.loads(line) for line in f]
        f.close()
    return data

def get_pdf_text(pdf_docs):
    text = []
    metadata = []
    unread=open('unreadable.txt', 'w')
    for pdf in pdf_docs:
        if('/._' in pdf):
            continue
        print(pdf)
        try:
            pdf_reader = PdfReader(pdf)
            print(len(pdf_reader.pages))
            for i, page in enumerate(pdf_reader.pages):
                text.append(page.extract_text())
                metadata.append({'page_number': i, 'source': re.findall(r'\/\d+\.pdf',pdf)[0].replace('/','').replace('.pdf','')})
        except:
            unread.write(f"{pdf}\n")
    unread.close()
    return text, metadata

def save_store(data, metadata, persist_directory):
    documents = [Document(text=data[i], metadata=metadata[i]) for i in range(len(data))]
    index=VectorStoreIndex.from_documents(documents, show_progress=True)
    index.storage_context.persist(persist_dir=persist_directory)
    
def upload_store(persist_directory):
    print('Uploading Storage...')
    start_time=time.time()
    storage_context = StorageContext.from_defaults(persist_dir=persist_directory)
    index = load_index_from_storage(storage_context, show_progress=True)
    print(f"Storage is Uploaded in {time.time()-start_time} sec.")
    return index
    
def count_chunks(filepath):
    index=upload_store(filepath)
    print(len(index.ref_doc_info))
    

def query_bot(messages, temperature=0.1, max_new_tokens=512, **kwargs):
    llm=Ollama(
                model="llama3.1",
                #model="erwan2/DeepSeek-R1-Distill-Qwen-1.5B:latest",
                request_timeout=360.0,
                # Manually set the context window to limit memory usage
                context_window=8000,
            )
    messages = [
                    ChatMessage(role="user", content=messages)
                ]
    #response=llm.complete(messages[0]['content'])
    response=llm.stream_chat(messages)
    answer=''
    for r in response:
        #print(f"\n responses: {r.delta}", end="")
        answer=answer+r.delta
    return answer


def retrieve(faiss_path, stats_filename):
    dataset=read_jsonl('LongDocURL_public.jsonl')
    statistic_answer=[]
    processed_ids=[]
    index=upload_store(faiss_path)
    start_time=time.time()
    #retrieverBM25 = BM25Retriever.from_defaults(index=index, similarity_top_k=20)
    autosave=False
    if(os.path.exists(stats_filename)):
        statistic_answer=read_json(stats_filename)
        for elem in statistic_answer:
            processed_ids.append(elem['id'])
    for j, elem in enumerate(dataset):
        if(j>1000000):
            break
        if (elem['question_id'] not in processed_ids):
            #retrieval_evaluate
            query=elem['question']
            nodes_score = index.as_retriever(similarity_top_k=20, retriever_mode='embeddings').retrieve(query)
            #nodes_score=retrieverBM25.retrieve(query)
            retrieved_docs=[]
            for i, ns in enumerate(nodes_score):
                '''
                print(f"{ns.metadata['source']}/{ns.metadata['page_number']} <-> {elem['doc_no']}/{elem['evidence_pages']}")
                if(ns.metadata['source'].replace('.pdf', '')==elem['doc_no']):
                    print('Same source')
                    if(int(ns.metadata['page_number']) in elem['evidence_pages']):
                        print('page_is_present')
                '''
                retrieved_docs.append({'page': ns.metadata['page_number'], 'doc': ns.metadata['source'], 'text': ns.get_content(metadata_mode=MetadataMode.LLM), 'scores': ns.score})
                
            
            statistic_answer.append({'id': elem['question_id'], 'question':elem['question'], 'correct_answer': elem['answer'],
                                    'evidence_pages': elem['evidence_pages'],'document_name': elem['doc_no'], 'answer_format':elem['answer_format'],
                                    'task_tag': elem['task_tag'], 'retrieved_documents':retrieved_docs})
            #print('//=============================================================================================================')
            if(autosave and j%10==0):
                with open(stats_filename, 'w') as fp:
                    json.dump(statistic_answer, fp)
    print(f"retrieveing_time: {time.time()-start_time} sec.")                
    with open(stats_filename, 'w') as fp:
        json.dump(statistic_answer, fp)
    
    
    

def rerank(faiss_path, stats_filename):
    dataset=read_jsonl('LongDocURL_public.jsonl')
    rerank_postprocessors = FlagEmbeddingReranker(model="BAAI/bge-reranker-large", top_n=10)
    statistic_answer=[]
    processed_ids=[]
    index=upload_store(faiss_path)
    retrieverBM25 = BM25Retriever.from_defaults(index=index, similarity_top_k=20)
    autosave=True
    if(os.path.exists(stats_filename)):
        statistic_answer=read_json(stats_filename)
        for elem in statistic_answer:
            processed_ids.append(elem['id'])
    for j, elem in enumerate(dataset):
        if(j>1000000):
            break
        if (elem['question_id'] not in processed_ids):
            #retrieval_evaluate
            query=elem['question']
            #nodes_score = index.as_retriever(similarity_top_k=20).retrieve(query)
            nodes_score=retrieverBM25.retrieve(query)
            nodes_score = rerank_postprocessors.postprocess_nodes(nodes_score, query_bundle=QueryBundle(query_str=query))
            retrieved_docs=[]
            for i, ns in enumerate(nodes_score):
                print(f"{ns.metadata['source']}/{ns.metadata['page_number']} <-> {elem['doc_no']}/{elem['evidence_pages']}")
                if(ns.metadata['source'].replace('.pdf', '')==elem['doc_no']):
                    print('Same source')
                    if(int(ns.metadata['page_number']) in elem['evidence_pages']):
                        print('page_is_present')
                retrieved_docs.append({'page': ns.metadata['page_number'], 'doc': ns.metadata['source'], 'text': ns.get_content(metadata_mode=MetadataMode.LLM), 'scores': ns.score})
                
            
            statistic_answer.append({'id': elem['question_id'], 'question':elem['question'], 'correct_answer': elem['answer'],
                                    'evidence_pages': elem['evidence_pages'],'document_name': elem['doc_no'], 'answer_format':elem['answer_format'],
                                    'task_tag': elem['task_tag'], 'retrieved_documents':retrieved_docs})
            print('//=============================================================================================================')
            if(autosave and j%10==0):
                with open(stats_filename, 'w') as fp:
                    json.dump(statistic_answer, fp)
                    
        with open(stats_filename, 'w') as fp:
            json.dump(statistic_answer, fp)
    

def generate_answers(filename, stats_filename):
    prefixU="Below is a question followed by some context from different sources. Please answer the question based on the context. If the provided information is insufficient to answer the question, respond 'not answerable'. Each source starts with page and document it was taken from."
    prefixR=''
    prefixL="Below is a question followed by texts from differnet pages of different source. Question is based on locating , respond 'not answerable'"
    prefixInt="The answer have to be a number. Answer directly without explanation."
    prefixStr="Answer directly without explanation."
    prefixList="The answer have to be a list of entities in the format ['element 1', 'element 2', ...]. Nothing else needed to be in the answer unless in is not answerable. Answer directly without explanation.\n\nHere are some examples of answer: \n 1) ['Tribal Engagement Resources', 'Tribal Engagement Training'] \n 2) ['Stock-Based Compensatiom Expense', '201I Compensation and Incewtie Plan'] 3) ['Table 3.3']"
    #prefixList="The answer have to be a list of entities in the format <element 1 \n element 2 \n ...>. Nothing else needed to be in the answer unless in is not answerable. Answer directly without explanation.\n\nHere are an example of answer: \n < Tribal Engagement Resources \n Tribal Engagement Training> \n"
    dataset=read_json(filename)
    wrong_count=0
    result=[]
    for i, elem in enumerate(dataset):
        print(f"{i}/{len(dataset)}=====================================================================================================")
        #if(i>1000000):
        #    break
        query=elem['question']
        retrieval=''
        for retrieve in elem['retrieved_documents']:
            retrieval=retrieval+'\n'+retrieve['text']
        if(elem['task_tag']=='Locating'):
            prompt=f"{prefixL}\n Query: \n{query} \n Texts: \n {retrieval}"
        else:
            prompt=f"{prefixU}\n{query}\n{retrieval}"
        if(elem['answer_format']=='String'):
            prompt=f"{prompt} {prefixStr}"
        if(elem['answer_format'] in ['Integer', 'Float']):
            prompt=f"{prompt} {prefixInt}"
        if(elem['answer_format']=='List'):
            prompt=f"{prompt} {prefixList}"
        answer=query_bot(prompt)
        print(f"correct_answer:\n{elem['correct_answer']}\n\ngenerated_answer:\n{answer}\n\n")
        #print(elem['answer'])
        elem['generated_answer']=answer

        #correct_answer=str(elem['answer'])
        #meteor_score=pymeteor.meteor(answer.lower(), correct_answer.lower())
        
        #meteor_total.append(meteor_score)
    
    
    with open(stats_filename, 'w') as fp:
        json.dump(dataset, fp)

def retrieve_evaluate(filepath, retrname='retrieved_documents', separate_types=True):
    dataset=read_json(filepath)
    #query_count=0
    if(separate_types==False):
        hitAt10=0
        hitAt4=0
        recall_total=[]
        precision_total=[]
        for elem in dataset:
            correct_docs=0
            incorrect_docs=0
            for i, retrieve in enumerate(elem[retrname]):
                if(retrieve['doc']==elem['document_name'] and retrieve['page'] in elem['evidence_pages']):
                    if(i<10):
                        hitAt10+=1
                    if(i<4):
                        hitAt4+=1
                    correct_docs+=1
                else:
                    incorrect_docs+=1
            recall_total.append(correct_docs/len(elem[retrname]))
            precision_total.append(correct_docs/incorrect_docs)
        recall=sum(recall_total)/len(recall_total)
        precision=sum(precision_total)/len(precision_total)
        hitAt10/=len(dataset)
        hitAt4/=len(dataset)
    else:
        results={'hitAt20': {'Understanding':{'value':0, 'count':0}, 'Reasoning':{'value':0, 'count':0}, 'Locating':{'value':0, 'count':0}, 'Total':{'value':0, 'count':0}},
                 'hitAt10': {'Understanding':{'value':0, 'count':0}, 'Reasoning':{'value':0, 'count':0}, 'Locating':{'value':0, 'count':0}, 'Total':{'value':0, 'count':0}},
                 'hitAt4': {'Understanding':{'value':0, 'count':0}, 'Reasoning':{'value':0, 'count':0}, 'Locating':{'value':0, 'count':0}, 'Total':{'value':0, 'count':0}},
                 'recall_total':{'Understanding':[], 'Reasoning':[], 'Locating':[], 'Total':[]},
                 'precision_total': {'Understanding':[], 'Reasoning':[], 'Locating':[], 'Total':[]}}
        partly=0.0
        for elem in dataset:
            correct_docs=0
            incorrect_docs=0
            typer=elem['task_tag']
            addAt10=0
            addAt4=0
            for i, retrieve in enumerate(elem[retrname]):
                if(retrieve['doc']==elem['document_name'] and retrieve['page'] in elem['evidence_pages']):
                    if(i<10):
                        addAt10=1
                    if(i<4):
                        addAt4=1
                    correct_docs+=1
                
                if(retrieve['doc']==elem['document_name'] and retrieve['page'] not in elem['evidence_pages']):
                    if(i<10 and addAt10==0):
                        addAt10=partly
                    if(i<4 and addAt4==0):
                        addAt4=partly
                    correct_docs+=partly
                    incorrect_docs+=(1-partly)
                if(retrieve['doc']!=elem['document_name'] and retrieve['page'] not in elem['evidence_pages']):    
                    incorrect_docs+=1
            for typers in [typer, 'Total']:        
                results['hitAt10'][typers]['value']+=addAt10
                results['hitAt10'][typers]['count']+=1
                results['hitAt4'][typers]['value']+=addAt4
                results['hitAt4'][typers]['count']+=1
                #print(f"{elem['evidence_pages']}: {len(elem['evidence_pages'])}")
                if(len(elem['evidence_pages'])==0):
                    results['recall_total'][typers].append(1)
                else:
                    results['recall_total'][typers].append(correct_docs/len(elem['evidence_pages']))
                results['precision_total'][typers].append(correct_docs/len(elem[retrname]))
        #print(results['hitAt10'], '\n\n')
        for tkey in results.keys():
            for rkey in results[tkey]:
                if(isinstance(results[tkey][rkey], dict)):
                    if(results[tkey][rkey]['count']==0):
                        results[tkey][rkey]='No Objects'
                    else:
                        results[tkey][rkey]=results[tkey][rkey]['value']/results[tkey][rkey]['count']
                else:
                    if(len(results[tkey][rkey])==0):
                        results[tkey][rkey]='No Objects'
                    else:
                        results[tkey][rkey]=sum(results[tkey][rkey])/len(results[tkey][rkey])
        hitAt10=results['hitAt10']
        hitAt4=results['hitAt4']
        recall=results['recall_total']
        precision=results['precision_total']
        
    return {'hit@10': hitAt10, 'hit@4': hitAt4, 'recall': recall, 'precision': precision}


def rerank_evaluate(filepath):
    return retrieve_evaluate(filepath, 'retrieved_documents')

def generator_evaluate(filepath, answer_formats=['String', 'Integer', 'List', 'Float'], task_tags=['Understanding','Reasoning_','Locating_']):
    dataset=read_json(filepath)
    number_correctness=0
    numbers_count=1
    correct_count=0
    rouge_scores={'rougeL':{'precision':[], 'recall':[], 'fmeasure':[]}, 'rouge1':{'precision':[], 'recall':[], 'fmeasure':[]}}
    rouge_scores=[]
    meteor_scores=[]
    list_scores=[]
    unparsable=0
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    for i, elem in enumerate(dataset):
        #if(i in [936, 1174]):
        #    continue
        if(elem['answer_format'] not in answer_formats or elem['task_tag'] not in task_tags):
            continue
        #print(f"{i}/{len(dataset)}")
        if(elem['answer_format'] in ['Integer', 'Float']):
            numbers_count+=1
            generated_answer=re.findall(r'\d[\d\.\,]*', elem['generated_answer'])
            if(isinstance(elem['correct_answer'], str)):
                correct_answer=int(re.findall(r'\d[\d\.\,]*', elem['correct_answer'])[-1].replace(',','').replace('.',''))
            else:
                correct_answer=elem['correct_answer']
            if(len(generated_answer)>0):
                addition=0
                for genans in generated_answer:
                    genans1=int(genans.replace(',','').replace('.',''))
                    if(correct_answer==genans1):
                        addition=1
                    if(genans1==0 and genans1==0):
                        addition=1
                number_correctness+=1
                correct_count+=addition
            else:
                number_correctness+=1
        if(elem['answer_format']=='String'):
            rouge_score = scorer.score(str(elem['correct_answer']), str(elem['generated_answer']))
            rouge_scores.append(rouge_score['rougeL'].fmeasure)
            meteor_score=pymeteor.meteor(str(elem['generated_answer']), str(elem['correct_answer']))
            meteor_scores.append(meteor_score)
        if(elem['answer_format']=='List'):
            generated_list=re.findall(r'\[.+\]', elem['generated_answer'])
            if(len(generated_list)>0):
                try:
                    generated_list=re.sub(r"(?<=[a-zA-Z])'(?=[a-zA-Z])", r"" ,generated_list[-1])
                    generated_list=ast.literal_eval(generated_list)
                except:
                    #print(f"unparsable_list index: {i}\nText: {elem['generated_answer']}")
                    #print("processed_list:", re.sub(r"(?<=[a-zA-Z])'(?=[a-zA-Z])", r"" ,generated_list[-1]))
                    unparsable+=1
                    generated_list=[]
                if(len(generated_list)>0 and isinstance(elem['correct_answer'], list)):
                    correct_list=elem['correct_answer']
                    scores_list=[0 for i in range(max(len(generated_list), len(correct_list)))]
                    for j, stroka1 in enumerate(generated_list):
                        for stroka2 in correct_list:
                            rouge_score=scorer.score(str(stroka1), str(stroka2))['rougeL'].fmeasure
                            if(rouge_score>scores_list[j]):
                                scores_list[j]=rouge_score
                    list_scores.append(sum(scores_list)/len(scores_list))
                else:
                    list_scores.append(0)
            else:
                #print(elem['generated_answer'])
                list_scores.append(0)
               
                        
            
    if('Integer' in answer_formats):
        #print(number_correctness/numbers_count)
        print(f"exact answers for numbers: {correct_count}/{numbers_count} ({correct_count/numbers_count})")
    if('String' in answer_formats):
        print(f"Mean rougeL f1-score: {sum(rouge_scores)/len(rouge_scores)}")
        print(f"mean meteor score: {sum(meteor_scores)/len(meteor_scores)}")
    if('List' in answer_formats):
        print(f"Mean list value: {sum(list_scores)/len(list_scores)}")
        print(f"Amount of unparsable lists: {unparsable}")
        

def show_results(dicter):
    for key1 in dicter.keys():
        print(f"{key1}:")
        for key2 in dicter[key1].keys():
            print(f"\t{key2}: {dicter[key1][key2]}")
    print('\n\n')


if __name__=='__main__':
    start_time=time.time()
    args={'create_faiss_database': True, 'retireve_documents':False}
    theme='commerce_manufactoring'
    
    theme_dataset_filepath='/home/user/RAG/UniDoc_bench/UniDoc-Bench/data/downloaded/UniDoc-Bench/data/commerce_manufacturing-00000-of-00001.json'
    #print(len(os.listdir(pdf_filepath)))
    dataset=read_json(theme_dataset_filepath)
    counter=[]
    cur_key='answer_type'
    #keys:['question', 'answer', 'gt_image_paths', 'question_type', 'answer_type', 'domain', 'longdoc_image_paths']
    #question_types: ['factual_retrieval', 'summarization', 'causal_reasoning', 'comparison', 'temporal_comparison']
    #answer_types: ['image_only', 'table_required', 'image_plus_text_as_answer', 'text_only']
    for i, elem in enumerate(dataset):
        if(elem[cur_key] not in counter):
            counter.append(elem[cur_key])
    print(counter)
    
    
    if(args['create_faiss_database']):
        pdf_filepath='/home/user/RAG/UniDoc_bench/UniDoc-Bench/data/downloaded/UniDoc-Bench/commerce_manufacturing_pdfs/commerce_manufacturing'
        files_paths=os.listdir(pdf_filepath)
        for i in range(len(files_paths)):
            files_paths[i]=f"{pdf_filepath}/{files_paths[i]}"
        text, metadata=get_pdf_text(files_paths)
        index=2
        #print(f"{metadata[index]}\n//==========================================================================\n{text[index]}")
        
        embed_model=OllamaEmbedding(model_name="mxbai-embed-large")
        Settings.chunk_size=256
        Settings.embed_model=embed_model
        save_store(text, metadata, 'Faiss_naive_database')
        
    print(f"Total processing time: {time.time()-start_time}")
    