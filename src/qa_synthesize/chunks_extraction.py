import os
import json
import orjson
import json_stream
from tqdm import tqdm
import numpy as np
from utils import find_fig_tables
from ragas.executor import Executor
from ragas.testset.graph import Node, Relationship
from ragas.testset.graph import KnowledgeGraph
from ragas.testset.synthesizers import (
    MultiHopAbstractQuerySynthesizer,
    MultiHopSpecificQuerySynthesizer,
    SingleHopSpecificQuerySynthesizer,
)
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from ragas.callbacks import new_group
from ragas.testset.synthesizers.utils import calculate_split_values
from langchain_core.callbacks import Callbacks
from ragas.testset.persona import Persona, generate_personas_from_kg
from ragas.testset.synthesizers.testset_schema import Testset, TestsetSample
import random

def extract_chunks(loaded_kg, image_num_min=1, image_num_max=2, different_file=True, table_num_min=0, table_num_max=1, shuffle_triplets=True):
    chunks = []
    chunks_metadata = []
    different_file_set = set()
    node_list = loaded_kg.nodes
    if shuffle_triplets:
        random.shuffle(node_list)
    for node in node_list:
        chunk = node.get_property("page_content")
        chunk_metadata = node.get_property("document_metadata")
        file_name = chunk_metadata["source"].split("_id")[0]
        if chunk.count("<<fig-") >= image_num_min and chunk.count("<<fig-") <= image_num_max:
            if chunk.count("<<tab-") >= table_num_min and chunk.count("<<tab-") <= table_num_max:
                if not different_file or (different_file and file_name not in different_file_set):
                    chunks.append([chunk])
                    chunks_metadata.append([chunk_metadata])
                    different_file_set.add(file_name)
    return chunks, chunks_metadata

def extract_relevant_chunks(generator_llm, loaded_kg, overlapping_items_minimum=1, testset_size=3, different_files=True, image_number_min=1, image_number_max=3, page_diff=1, different_files_visited=True, no_tab=True, table_number_max=2, table_number_min=0, shuffle_triplets=True):
    triplets = loaded_kg.find_two_nodes_single_rel(
        relationship_condition=lambda rel: (
            True if len(rel.get_property("overlapped_items")) > 1 else False
        )
    )
    nodes_pairs = []
    different_files_visited_set = set()

    if shuffle_triplets:
        random.shuffle(triplets)

    for triplet in triplets:
        node_a, node_b = triplet[0], triplet[-1]
        overlapped_items = triplet[1].properties["overlapped_items"]
        if len(overlapped_items) >= overlapping_items_minimum:
            nodes_pairs.append([node_a, node_b, overlapped_items])

    chunks = [[nodes[0].get_property("page_content"), nodes[1].get_property("page_content")] for nodes in nodes_pairs]
    chunks_metadata = [[nodes[0].get_property("document_metadata"), nodes[1].get_property("document_metadata")] for nodes in nodes_pairs]
    chunks_overlapped_items = [nodes[-1] for nodes in nodes_pairs]
    chunks_res, chunks_metadata_res, chunks_overlapped_items_res = [], [], []
    for chunk, chunk_metadata, chunks_overlapped_items in zip(chunks, chunks_metadata, chunks_overlapped_items):
        chunks_overlapped_items = [pair for pair in chunks_overlapped_items if "figure" not in pair[0].lower() and "table" not in pair[0].lower()]
        if not chunks_overlapped_items:
            continue

        pdf_id_1 = chunk_metadata[0]["source"].split('/')[-1].split('_id_')[0]
        pdf_id_2 = chunk_metadata[1]["source"].split('/')[-1].split('_id_')[0]
        chunk_id_page_1 = int(chunk_metadata[0]["source"].split('/')[-1].split('_pg')[-1].replace('.txt', '').strip())
        chunk_id_page_2 = int(chunk_metadata[1]["source"].split('/')[-1].split('_pg')[-1].replace('.txt', '').strip())

        if different_files_visited:
            id_cp = tuple(sorted([pdf_id_1, pdf_id_2]))
            if id_cp in different_files_visited_set:
                continue
            else:
                different_files_visited_set.add(id_cp)

        if no_tab and any(["<<tab" in c for c in chunk]):
            continue

        if not image_number_min and different_files and pdf_id_1 != pdf_id_2:
            chunks_res.append(chunk)
            chunks_metadata_res.append(chunk_metadata)
            chunks_overlapped_items_res.append(chunks_overlapped_items)
        elif not image_number_min and not different_files and pdf_id_1 == pdf_id_2 and abs(chunk_id_page_1 - chunk_id_page_2) >= page_diff:
            chunks_res.append(chunk)
            chunks_metadata_res.append(chunk_metadata)
            chunks_overlapped_items_res.append(chunks_overlapped_items)
        elif not different_files and any(["<<fig" in c for c in chunk]) and pdf_id_1 == pdf_id_2 and abs(chunk_id_page_1 - chunk_id_page_2) >= page_diff:
            if sum([c.count("<<fig-") for c in chunk]) >= image_number_min and sum([c.count("<<fig-") for c in chunk]) <= image_number_max:
                chunks_res.append(chunk)
                chunks_metadata_res.append(chunk_metadata)
                chunks_overlapped_items_res.append(chunks_overlapped_items)
        elif different_files and any(["<<fig" in c for c in chunk]) and pdf_id_1 != pdf_id_2:
            if sum([c.count("<<fig-") for c in chunk]) >= image_number_min and sum([c.count("<<fig-") for c in chunk]) <= image_number_max:
                chunks_res.append(chunk)
                chunks_metadata_res.append(chunk_metadata)
                chunks_overlapped_items_res.append(chunks_overlapped_items)

    if len(chunks_res) < testset_size:
        extract_chunks(loaded_kg, image_num_min=image_number_min, image_num_max=image_number_max, different_file=True, table_num_min=table_number_min, table_num_max=table_number_max, shuffle_triplets=shuffle_triplets)

    return chunks_res[:testset_size], chunks_metadata_res[:testset_size], chunks_overlapped_items_res[:testset_size]

def chunk_match_back(chunk, chunks_metadata, folder_elements):
    """
    chunk: str
    chunks_metadata: dict. {"source: xxx"}
    folder_elements: str: path to elements folder

    output dict: element_id: img_path
    """

    tab_fig_dict = find_fig_tables(chunk)
    file_name = os.path.splitext(os.path.basename(chunks_metadata["source"]))[0].split("_id")[0]
    elements_dict = dict()
    with open(os.path.join(folder_elements, file_name + ".json"), 'r') as f:
        elements = json.load(f)
        for element in elements["elements"]:
            try:
                element_id = element["element_id"]
                image_path = element["metadata"]["image_path"]
                elements_dict[element_id] = image_path
            except Exception as error: pass

    table_paths = dict()
    for table in tab_fig_dict["Table"]:
        if table in elements_dict:
            table_paths[table] = elements_dict[table]

    figure_paths = dict()
    for figure in tab_fig_dict["Figure"]:
        if figure in elements_dict:
            figure_paths[figure] = elements_dict[figure]

    return table_paths, figure_paths