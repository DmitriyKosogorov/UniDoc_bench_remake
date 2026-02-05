import os
import re
import ast
import base64
import json
import argparse
from openai import OpenAI
from tqdm import tqdm
from collections import defaultdict
from chunks_extraction import chunk_match_back, extract_relevant_chunks
from prompts.reclassify_prompts import CHUNK_GROUND_PROMPT, IMAGE_GROUND_PROMPT, ANSWER_FULL_PROMPT, FACT_EXTRACTION_PROMPT, VQA_FILTER_PROMPT, TABLE_GROUND_PROMPT
from litellm import completion
import time

MODEL = "gpt-4o"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def complete_llm(messages, model_name="gemini"):
    if model_name == "gemini":
        for i in range(5):
            try:
                response = completion(
                    messages=messages,
                    model="vertex_ai/gemini-2.5-pro",  # "vertex_ai/gemini-2.5-pro"
                    temperature=0.85,
                )
                return response
            except Exception as e:
                time.sleep(i+1)
    else:
        for i in range(5):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=0.85,
                )
                return response
            except Exception as e:
                time.sleep(i+1)

def extract_facts(question, answer):
    prompt = FACT_EXTRACTION_PROMPT.replace("{{answer}}", str(answer))
    prompt = prompt.replace("{{question}}", question)
    user_prompt = [
        {
            "type": "text",
            "text": prompt
        }
    ]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that responds Python dictionary.",
        },
        {"role": "user", "content": user_prompt},
    ]
    #         )
    response = complete_llm(messages, model_name="gpt-4o")

    response = response.choices[0].message.content.replace("```json", "```").split("```")[1]
    return ast.literal_eval(response)

def ground_contexts(chunk, question, answer):
    prompt = CHUNK_GROUND_PROMPT.replace("{{answer}}", answer)
    prompt = prompt.replace("{{chunk}}", chunk)
    prompt = prompt.replace("{{question}}", question)
    user_prompt = [
        {
            "type": "text",
            "text": prompt
        }
    ]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that responds Python dictionary.",
        },
        {"role": "user", "content": user_prompt},
    ]

    response = complete_llm(messages)
    response = response.choices[0].message.content.replace("```json", "```").split("```")[1]
    return ast.literal_eval(response)

def ground_image(image_path, question, answer, contexts):
    with open(image_path, "rb") as image_file:
        img = base64.b64encode(image_file.read()).decode("utf-8")
    prompt = IMAGE_GROUND_PROMPT.replace("{{answer}}", answer)
    prompt = prompt.replace("{{question}}", question)
    prompt = prompt.replace("{{contexts}}", str(contexts))
    user_prompt = [
        {
            "type": "text",
            "text": prompt
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img}"},
        },
        {
            "type": "text",
            "text": "Return the output in a JSON object."
        }
    ]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that responds Python dictionary.",
        },
        {"role": "user", "content": user_prompt},
    ]

    response = complete_llm(messages, model_name="gpt-4o")
    response = response.choices[0].message.content.replace("```json", "```").split("```")[1].strip()
    return ast.literal_eval(response)

def ground_table(image_path, question, answer, contexts):

    contexts = re.sub(r"<table.*?>.*?</table>", "", str(contexts), flags=re.DOTALL | re.IGNORECASE)

    with open(image_path, "rb") as image_file:
        img = base64.b64encode(image_file.read()).decode("utf-8")
    prompt = TABLE_GROUND_PROMPT.replace("{{answer}}", answer)
    prompt = prompt.replace("{{question}}", question)
    prompt = prompt.replace("{{contexts}}", contexts)

    user_prompt = [
        {
            "type": "text",
            "text": prompt
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img}"},
        },
        {
            "type": "text",
            "text": """Return a JSON object with the following structure:

```json
{
  "table_required": "True" | "False",
  "reason": "Explanation of table_required label",
  "matched_facts": ["Fact 1", "Fact 2", ...]  // Facts from the table that are essential to derive the answer
}

```"""

        }
    ]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that responds Python dictionary.",
        },
        {"role": "user", "content": user_prompt},
    ]

    response = complete_llm(messages)

    response = response.choices[0].message.content.replace("```json", "```").split("```")[1].strip()
    return ast.literal_eval(response)

def verify_proof(question, answer, proof_list):
    prompt = ANSWER_FULL_PROMPT.replace("{{answer}}", answer)
    prompt = prompt.replace("{{chunk}}", str(proof_list))
    prompt = prompt.replace("{{question}}", question)

    user_prompt = [
        {
            "type": "text",
            "text": prompt
        }
    ]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that responds Python dictionary.",
        },
        {"role": "user", "content": user_prompt},
    ]

    response = complete_llm(messages, model_name="gpt-4o")
    response = response.choices[0].message.content.replace("```json", "```").split("```")[1]

    return ast.literal_eval(response)

def rearrange_type(chunk_used):
    category = []

    chunk_metadata = []
    for chunk_idx in chunk_used:
        if "chunk" in chunk_idx and chunk_used[chunk_idx]["used"]:
            chunk_metadata.append(chunk_used[chunk_idx]["metadata"]["source"])
    if len(chunk_metadata) <= 1:
        category.append("single-chunk")
    else:
        if set(chunk_metadata) == 1:
            category.append("multiple-chunk-single-doc")
        else:
            category.append("multiple-chunk-multiple-doc")

    img_metadata, tab_metadata = [], []
    for chunk_idx in chunk_used:
        if "img" in chunk_idx and chunk_used[chunk_idx]["used"]:
            img_metadata.append(chunk_used[chunk_idx]["metadata"])
        if "tab" in chunk_idx and chunk_used[chunk_idx]["used"]:
            tab_metadata.append(chunk_used[chunk_idx]["metadata"])

    if not img_metadata and not tab_metadata:
        category.append("text_only")
    elif not img_metadata and tab_metadata:
        category.append("table_required")
    else:
        if chunk_metadata:
            category.append("image_plus_text_as_answer")
        else:
            category.append("image_only")

    return category

def filter_vqa(question):
    user_prompt = VQA_FILTER_PROMPT.replace("{{question}}", question)
    messages = [
        {"role": "user", "content": user_prompt},
    ]

    response = complete_llm(messages, model_name="gpt-4o")
    response = response.choices[0].message.content

    if "true" in response.lower():
        return True
    else:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--folder_elements", type=str, required=True
    )
    parser.add_argument("--qa_path", type=str, required=True)
    args = parser.parse_args()

    output_file_filtered_path = args.qa_path.replace('.json', "_filtered_out.json")
    output_file_remain_path = args.qa_path.replace('.json', "_remained.json")
    output_file_filtered = open(output_file_filtered_path, "a")
    output_file_remain = open(output_file_remain_path, "a")

    question_type = defaultdict(dict)
    with open(args.qa_path, "r") as f:
        questions = list(f)
    count = 0

    for question_dict in tqdm(questions[:]):
        try:
            question_dict = json.loads(question_dict)
        except: continue

        question = question_dict["question"]
        answer = question_dict["answer"]
        chunks = question_dict["contexts"]
        chunks_metadata = question_dict["chunks_metadata"]
        image_paths, tab_paths = [], []
        chunk_used = dict()
        for chunk, chunk_metadata in zip(chunks, chunks_metadata):
            tabs, img = chunk_match_back(chunk, chunk_metadata, args.folder_elements)
            image_paths += list(img.values())
            tab_paths += list(tabs.values())

        facts = extract_facts(question, answer)["facts"]
        question_dict["facts_in_answer"] = facts

        verify_contexts = []
        new_contexts = []

        for idx, chunk in enumerate(chunks):
            chunk_used[f"chunk_{idx}"] = {"used": False, "metadata": chunks_metadata[idx]}
            result = None
            for jdx in range(3):
                try:
                    result = ground_contexts(chunk, question, str(facts))
                    break
                except:
                    time.sleep(jdx+1)
            if not result or "found_sentences" not in result:
                continue
            if result["found_sentences"] or result["extra_proof"]:
                new_contexts.append(chunk)
                verify_contexts += result["found_sentences"]
                verify_contexts += result["extra_proof"]
                chunk_used[f"chunk_{idx}"]["used"] = True
                chunk_used[f"chunk_{idx}"]["facts"] = result["found_sentences"] + result["extra_proof"]

        img_contexts = []
        for idx, img_path in enumerate(image_paths):
            result = None
            for jdx in range(3):
                try:
                    result = ground_image(img_path, question, str(facts), verify_contexts)
                    if "matched_facts" in result:
                        break
                except:
                    time.sleep(jdx+1)

            if not result:
                continue
            img_contexts += result["matched_facts"]
            verify_contexts += result["matched_facts"]
            chunk_used[f"img_{idx}"] = {"used": True if "true" in result["image_required"].lower() and result["matched_facts"] else False, "metadata": img_path, "facts": result["matched_facts"]}
        tab_contexts = []

        for idx, tab_path in enumerate(tab_paths):
            for jdx in range(10):
                try:
                    result = ground_table(tab_path, question, str(facts), chunks)
                    if "matched_facts" in result:
                        break
                except Exception as error:
                    time.sleep(jdx + 1)

            tab_contexts += result["matched_facts"]
            verify_contexts += result["matched_facts"]
            chunk_used[f"tab_{idx}"] = {"used": True if "true" in result["table_required"].lower() else False, "metadata": tab_path, "facts": result["matched_facts"]}

        question_dict["verify_contexts"] = verify_contexts
        for jdx in range(3):
            try:
                result_1 = verify_proof(question, answer, verify_contexts)
                break
            except:
                time.sleep(jdx+1)

        question_dict["verify_contexts_result"] = result_1
        verify_contexts += new_contexts + img_contexts
        for jdx in range(3):
            try:
                result_2 = verify_proof(question, answer, verify_contexts)
                break
            except:
                time.sleep(jdx+1)

        question_dict["verify_contexts_result_full"] = result_2
        verified = True if "full" in result_1["verification_result"].lower() or "full" in result_2["verification_result"].lower() else False
        question_dict["chunk_used"] = chunk_used

        if not verified:
            output_file_filtered.write(json.dumps(question_dict) + "\n")
            output_file_filtered.flush()
            continue

        category = rearrange_type(chunk_used)
        question_dict["doc_source"] = category[0]
        question_dict["answer_type"] = category[1]
        if filter_vqa(question):
            output_file_filtered.write(json.dumps(question_dict) + "\n")
            output_file_filtered.flush()
            continue

        output_file_remain.write(json.dumps(question_dict) + "\n")
        output_file_remain.flush()
        count += 1

    output_file_filtered.close()
    output_file_remain.close()