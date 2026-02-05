import os
import json
import numpy as np
import re
from collections import defaultdict


def obtain_retrieved_chunk_elements(file_name, chunk, element_path):
    file_name = file_name.split("_")[0].split(".")[0]
    with open(os.path.join(element_path, file_name+".json"), "r") as f:
        element_data = json.load(f)["elements"]

    retrieved_chunk_elements, image_elements_set = dict(), set()
    for j in range(len(element_data)):
        element = element_data[j]
        if element["text"] in chunk and len(element["text"]) > 25:
            retrieved_chunk_elements[element["element_id"]] = [element["metadata"]['filename'].split(".")[0], element["metadata"]['page_number']]

        if element["element_id"] in chunk and element["type"] in ["Table", "Image"]:
            image_elements_set.add(element["element_id"])
            retrieved_chunk_elements[element["element_id"]] = [element["metadata"]['filename'].split(".")[0], element["metadata"]['page_number']]

    return retrieved_chunk_elements, image_elements_set

def obtain_gt_chunk_elements(file_name, contexts, element_path, gt_metadata_list):
    file_name = file_name.split("_")[0].split(".")[0]
    with open(os.path.join(element_path, file_name+".json"), "r") as f:
        element_data = json.load(f)["elements"]

    gt_chunk_elements = set()
    for name in gt_metadata_list:
        if "chunk" in name and gt_metadata_list[name]["used"]:
            idx = int(name.split("_")[-1])
            chunk = contexts[idx]
            for j in range(len(element_data)):
                element = element_data[j]
                if element["text"] in chunk and len(element["text"]) > 15:
                    gt_chunk_elements.add(element["element_id"])
        elif gt_metadata_list[name]["used"]:
            for j in range(len(element_data)):
                element = element_data[j]
                if "image_path" in element["metadata"]:
                    path = element["metadata"]["image_path"]
                    if path == gt_metadata_list[name]["metadata"]:
                        gt_chunk_elements.add(element["element_id"])
    return gt_chunk_elements

def match_pages(retrieved_metadata, gt_metadata_list):
    file_name = retrieved_metadata["file_name"].split("_")[-2]
    page = int(retrieved_metadata["file_name"].split("_")[-1].replace(".jpg", "").strip())

def parse_filename(filename):
    doc_id_match = re.match(r"(\d+)_id", filename)
    doc_id = int(doc_id_match.group(1)) if doc_id_match else None

    pg_matches = re.findall(r"pg(\d+)", filename)
    if len(pg_matches) >= 2:
        start, end = int(pg_matches[-2]), int(pg_matches[-1])
        pages = list(range(start, end + 1)) if start <= end else [start]
    elif len(pg_matches) == 1:
        pages = [int(pg_matches[0])]
    else:
        pages = []

    return str(doc_id), pages

def find_pages_gt(gt_metadata_list, element_path):
    
    print(f"gt_metadata_list: {gt_metadata_list}\nelement_path: {element_path}")
    gt_path = defaultdict(list)
    for gt_metadata in gt_metadata_list:
        if gt_metadata_list[gt_metadata]["used"]:
            gt_metadata = gt_metadata_list[gt_metadata]["metadata"]
            print(f"gt metadata: {gt_metadata}")
            if "source" in gt_metadata:
                path = gt_metadata["source"]
                file_name, pages = parse_filename(path.split("/")[-1])
                gt_path[file_name] += pages
            else:
                path = gt_metadata
                print(path)
                file_name = path.split("/")[-2]
                with open(os.path.join(element_path, file_name + ".json"), "r") as f:
                    element_data = json.load(f)["elements"]

                for j in range(len(element_data)):
                    element = element_data[j]
                    if "image_path" in element["metadata"]:
                        if path == element["metadata"]["image_path"]:
                            gt_path[file_name].append(element["metadata"]["page_number"])

    for name in gt_path:
        gt_path[name] = list(set(gt_path[name]))
    return gt_path

def mrr_at_k(results, k=10):
    """
    results: list of lists, each inner list = ranked items for one query
             with binary relevance (1=relevant, 0=not relevant).
    k: cutoff rank (default 10)
    """
    mrr_total = 0.0
    for res in results:
        reciprocal_rank = 0.0
        for rank, rel in enumerate(res[:k], start=1):
            if rel > 0:
                reciprocal_rank = 1.0 / rank
                break
        mrr_total += reciprocal_rank
    return mrr_total / len(results)

def match_chunk_or_not(retrieved_chunks, retrieved_metadata, contexts, element_path, gt_metadata_list):
    retrieved_metadata = retrieved_metadata[:]
    match_list = []
    match_list_duplicate = []
    gt_path = find_pages_gt(gt_metadata_list, element_path)
    gt_path_matched = dict()
    for file_name in gt_path:
        for page_num in gt_path[file_name]:
            gt_path_matched[file_name + "_" + str(page_num)] = 0

    if len(retrieved_metadata) == 2:
        retrieved_metadata = retrieved_metadata[0] + retrieved_metadata[1]

    for i in range(len(retrieved_metadata)):
        match_list.append(0.0)
        match_list_duplicate.append(0.0)
        if type(retrieved_metadata[i]) == dict:
            gt_chunk_elements = obtain_gt_chunk_elements(retrieved_metadata[i]["file_name"], contexts, element_path, gt_metadata_list)
            retrieved_chunk_elements, image_elements_set = obtain_retrieved_chunk_elements(retrieved_metadata[i]["file_name"], retrieved_chunks[i], element_path)
            if len(gt_chunk_elements.intersection(list(retrieved_chunk_elements.keys()))) > 0:
                for element_id in gt_chunk_elements.intersection(list(retrieved_chunk_elements.keys())):
                    file_name, page_num = retrieved_chunk_elements[element_id]
                    if file_name + "_" + str(page_num) in gt_path_matched and gt_path_matched[file_name + "_" + str(page_num)] == 0:
                        match_list[-1] += 1.0
                        gt_path_matched[file_name + "_" + str(page_num)] = 1
                    if file_name + "_" + str(page_num) in gt_path_matched:
                        match_list_duplicate[-1] = 1
        else:
            file_name = retrieved_metadata[i].split("/")[-1].split("_")[0]
            try:
                page_nums = [int(retrieved_metadata[i].split("/")[-1].split("_")[1].split(".")[0])]
            except:
                pages = re.findall(r'pg(\d+)', retrieved_metadata[i].split("/")[-1])
                if len(pages) == 1:
                    pages = pages * 2
                s, e = [int(p) for p in pages]
                page_nums = [_i for _i in range(s, e+1)]
            for page_num in page_nums:
                if file_name in gt_path and page_num in gt_path[file_name] and gt_path_matched[file_name + "_" + str(page_num)] == 0:
                    match_list[-1] += 1.0
                    gt_path_matched[file_name + "_" + str(page_num)] = 1
                if file_name in gt_path and page_num in gt_path[file_name]:
                    match_list_duplicate[-1] = 1

    ground_truth_count = len(gt_path_matched)

    del gt_path_matched
    return match_list, ground_truth_count, match_list_duplicate



def dcg_from_labels(rels, k=10):
    rels = [1 if r > 0 else 0 for r in rels]
    rels = np.asarray(rels)[:k]
    return np.sum((2 ** rels - 1) / np.log2(np.arange(2, k + 2)))

def evaluate_match_lists(match_lists, ground_truth_counts, k=10, match_list_duplicates=[]):
    """
    match_lists: List of lists, each with 10 values: "match" or "not_match"
    ground_truth_counts: List of integers (same length), total number of relevant docs per sample
    """
    precisions = []
    recalls = []
    ndcgs = []
    total = 0


    for i in range(len(match_lists)):

        labels = match_lists[i][:]
        total_relevant = ground_truth_counts[i]
        match_list_duplicate = match_list_duplicates[i][:k]
        binary = labels[:] + [0.0] * k
        binary = binary[:k]




        precisions.append(sum(match_list_duplicate) / len(match_list_duplicate))

        if total_relevant:
            recalls.append(sum(binary) / total_relevant)
        else:
            recalls.append(0.0)


        dcg = dcg_from_labels(binary, k)
        ideal = sorted(binary, reverse=True)
        idcg = dcg_from_labels(ideal, k)
        ndcgs.append(dcg / idcg if idcg > 0 else 0.0)
        total += total_relevant

    return {
        f'Precision@{k}': np.mean(precisions),
        f'Recall@{k}': np.mean(recalls),
        f'nDCG@{k}': np.mean(ndcgs),
        "total": total,
        "length": len(match_lists)
    }

if __name__ == "__main__":
    sim = 10
    k = 10
    totals = 0
    lengths = 0
    for name_str in ["commerce_manufacturing", "crm", "finance", "legal", "construction", "education", "energy", "healthcare"]:  # "commerce_manufacturing", "construction", "crm", "education", "energy", "finance", "healthcare", "legal",
        results_ndcg = []

        for method in ["image"]:
            baseline_file = f"YOUR_DATA_PATH/QA/baseline/{method}/{name_str}_paper_sim{sim}.json"  # e.g., "/path/to/data/QA/baseline"
            element_path = f"YOUR_DATA_PATH/final_database/{name_str}_elements"  # e.g., "/path/to/data/final_database"
            
            baseline_file=f"/home/user/RAG/UniDoc_bench/UniDoc-Bench/src/baselines/results/simple_rag/{name_str}.json"
            element_path=f""
            
            
            if(not os.path.isfile(baseline_file)):           #check if files with retrieves exists
                continue
            
            print('A')

            try:
                with open(baseline_file, "r") as f:
                    baseline = json.load(f)
            except:

                with open(baseline_file, "r") as f:
                    data = list(f)

                baseline = defaultdict(list)
                for d in data:
                    d = json.loads(d)
                    if "contexts" not in d:
                        continue
                    if "chunk_used" not in d:
                        continue
                    if "retrieved_metadata" not in d:
                        continue
                    for key in d:
                        baseline[key].append(d[key])

            baseline_metadata = []
            baseline_chunks = []
            gt_metadata = []
            contexts = []
            img_in = []
            txt_in = []
            #
            for i in range(len(baseline["retrieved_metadata"])):
                
                #print(baseline['answer_type'][i])
                if(baseline['answer_type'][i] != 'text_only'):        #simple rag works only with texts, so no reason to check, how good it is in images and tables retrieval
                    continue
                
                
                if baseline["answer_type"][i]:
                    baseline_metadata.append(baseline["retrieved_metadata"][i])
                    if "retrieved_contexts" in baseline:
                        baseline_chunks.append(baseline["retrieved_contexts"][i])
                    gt_metadata.append(baseline["chunk_used"][i])
                    #contexts.append(baseline["contexts"][i])                       #still don't get what it is
                    contexts.append('')

            match_lists, ground_truth_counts, match_list_duplicates = [], [], []
            for i in range(len(baseline_metadata)):
                retrieved_metadata = baseline_metadata[i]
                gt_metadata_list = gt_metadata[i]
                try:
                    baseline_chunk = baseline_chunks[i]
                except:
                    baseline_chunk = [""] * len(retrieved_metadata)

                match_list, ground_truth_count, match_list_duplicate = match_chunk_or_not(baseline_chunk, retrieved_metadata, contexts[i], element_path, gt_metadata_list)
                img_in.append(sum([True if ".jpg" in p else False for p in retrieved_metadata])/len(retrieved_metadata))
                txt_in.append(sum([True if ".txt" in p else False for p in retrieved_metadata])/len(retrieved_metadata))

                if match_list:
                    match_lists.append(match_list)
                    ground_truth_counts.append(ground_truth_count)
                    match_list_duplicates.append(match_list_duplicate)

            results = evaluate_match_lists(match_lists, ground_truth_counts, k=k, match_list_duplicates=match_list_duplicates)
            f1 = 2 * (results[f"Precision@{k}"] * results[f"Recall@{k}"]) / (results[f"Precision@{k}"] + results[f"Recall@{k}"])
            totals += results["total"]
            lengths += results["length"]
