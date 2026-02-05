import os
import ast
import json
import time
import base64
import argparse
from tqdm import tqdm
import copy
from openai import OpenAI
from ragas.testset.graph import KnowledgeGraph
from utils import flatten_unique_ignore_case
from chunks_extraction import chunk_match_back, extract_relevant_chunks, extract_chunks
from prompts.query_syn_prompt import obtain_user_prompt
from prompts.templates import CHOOSE_TEMPLATE_PROMPT_USER, MESSAGE_WITH_EXAMPLE, choose_fixed_templates

MESSAGE_WITH_EXAMPLE_ONCE = copy.deepcopy(MESSAGE_WITH_EXAMPLE)
MODEL = "gpt-4o"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def choose_distribution(testset_size):
    answer_types = [
        "image_as_answer",
        "image_plus_text_as_answer",
        "text_as_answer",
        "table_as_answer",
    ]

    base_size = testset_size // 4
    remainder = testset_size % 4

    distribution = {atype: base_size for atype in answer_types}

    for i in range(remainder):
        distribution[answer_types[i]] += 1

    distribution["image_as_answer"] *= 3  # image_only is HARD to obtain

    return distribution


def load_chunks(
    loaded_kg,
    distribution,
    different_files_in_cluster,
    different_files_visited,
    no_tab_in_chunk_text,
    no_tab_in_chunk_img
):
    chunks_all, chunks_metadata_all, chunks_overlapped_items = dict(), dict(), dict()

    chunks, chunks_metadata = extract_chunks(
        loaded_kg,
        image_num_min=1,
        image_num_max=4,  # was 2
        different_file=False, #different_files_visited,
        table_num_min=0,
        table_num_max=2,
    )
    chunks_all["image_as_answer"] = chunks[:distribution["image_as_answer"]]
    chunks_metadata_all["image_as_answer"] = chunks_metadata[
        : distribution["image_as_answer"]
    ]
    chunks_overlapped_items["image_as_answer"] = [
        "" for _ in range(len(chunks[: distribution["image_as_answer"]]))
    ]

    chunks, chunks_metadata = extract_chunks(
        loaded_kg,
        image_num_min=0,
        image_num_max=0,
        different_file=different_files_visited,
        table_num_min=1,
        table_num_max=2,
    )
    chunks_all["table_as_answer"] = chunks[:distribution["table_as_answer"]]
    chunks_metadata_all["table_as_answer"] = chunks_metadata[
        : distribution["table_as_answer"]
    ]
    chunks_overlapped_items["table_as_answer"] = [
        "" for _ in range(len(chunks[: distribution["table_as_answer"]]))
    ]

    chunks, chunks_metadata, chunks_overlapped_item = extract_relevant_chunks(
        None,
        loaded_kg,
        overlapping_items_minimum=2,
        testset_size=distribution["text_as_answer"]*2,
        different_files=different_files_in_cluster,
        image_number_min=0,
        image_number_max=2,
        page_diff=1,
        different_files_visited=different_files_visited,
        no_tab=no_tab_in_chunk_text,
        table_number_min=0,
        table_number_max=0,
    )
    chunks_all["text_as_answer"] = chunks[: distribution["text_as_answer"]]
    chunks_metadata_all["text_as_answer"] = chunks_metadata[
        : distribution["text_as_answer"]
    ]
    chunks_overlapped_items["text_as_answer"] = chunks_overlapped_item[
        : distribution["text_as_answer"]
    ]

    chunks, chunks_metadata, chunks_overlapped_item = extract_relevant_chunks(
        None,
        loaded_kg,
        overlapping_items_minimum=1,
        testset_size=distribution["image_plus_text_as_answer"],
        different_files=different_files_in_cluster,
        image_number_min=1,
        image_number_max=2,
        page_diff=1,
        different_files_visited=different_files_visited,
        no_tab=no_tab_in_chunk_img,
        table_number_min=0,
        table_number_max=0,
    )
    chunks_all["image_plus_text_as_answer"] = chunks[
        : distribution["image_plus_text_as_answer"]
    ]
    chunks_metadata_all["image_plus_text_as_answer"] = chunks_metadata[
        : distribution["image_plus_text_as_answer"]
    ]
    chunks_overlapped_items["image_plus_text_as_answer"] = chunks_overlapped_item[
        : distribution["image_plus_text_as_answer"]
    ]

    return chunks_all, chunks_metadata_all, chunks_overlapped_items


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def choose_templates(chunks, chunks_metadata, domain_name):
    messages = copy.deepcopy(MESSAGE_WITH_EXAMPLE_ONCE)
    user_prompt = [
        {
            "type": "text",
            "text": CHOOSE_TEMPLATE_PROMPT_USER.replace(
                "{text_contexts}", json.dumps(chunks, indent=4)).replace(
                "{{TEMPLATES}}", choose_fixed_templates(domain_name)
            )
            + "\n\nThese are the tables and images in the above chunks:",
        }
    ]
    images = {}
    for chunk, chunk_metadata in zip(chunks, chunks_metadata):
        _, img = chunk_match_back(chunk, chunk_metadata, args.folder_elements)
        for im, p in img.items():
            images[f"<<fig-{im}>>"] = [encode_image(p), p]

    for fig, img in images.items():
        user_prompt += [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img[0]}",
                    "name": f"This is the image for {fig} in the above context.",
                },
            }
        ]
    messages.append({"role": "user", "content": user_prompt})
    templates = None
    for j in range(3):
        try:
            response = (
                client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=0.85,
                )
                .choices[0]
                .message.content
            )
            response = response.replace("```json", "```").split("```")[1]
            templates = ast.literal_eval(response)
            break
        except Exception as e:
            time.sleep(j+1)
    return templates


def build_prompt(chunks, chunks_metadata, hint, answer_type, query_type, templates):
    images = {}
    tables = {}

    for chunk, chunk_metadata in zip(chunks, chunks_metadata):
        tab, img = chunk_match_back(chunk, chunk_metadata, args.folder_elements)
        for t, p in tab.items():
            tables[f"<<tab-{t}>>"] = [encode_image(p), p]
        for im, p in img.items():
            images[f"<<fig-{im}>>"] = [encode_image(p), p]

    combined_chunk_message = "\n\n".join(
        [f"**Chunk {i}:**\n\n{chunk}" for i, chunk in enumerate(chunks, start=1)]
    )

    user_prompt = [{"type": "text", "text": combined_chunk_message}]

    for tab, img in tables.items():
        user_prompt += [
            {
                "type": "text",
                "text": f"Below is the image for the TABLE: {tab} in the above context.",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img[0]}",
                    "name": f"This is the image for the TABLE: {tab} in the above context.",
                },
            },
        ]

    for fig, img in images.items():
        user_prompt += [
            {
                "type": "text",
                "text": f"Below is the image for the FIGURE: {fig} in the above context.",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img[0]}",
                    "name": f"This is the image for the FIGURE: {fig} in the above context.",
                },
            },
        ]
    messages = []
    for template in templates:
        template = json.dumps(template, indent=4)
        user_query = obtain_user_prompt(answer_type, template, query_type).replace(
            "{{hints}}", "/ ".join(hint)
        )

        user_prompt_each = user_prompt + [{"type": "text", "text": user_query}]

        messages.append(
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that responds Python dictionary.",
                },
                {"role": "user", "content": user_prompt_each},
            ]
        )

    return messages, tables, images


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name_str", type=str, required=True, help="name of the subdomain"
    )
    parser.add_argument(
        "--folder_elements", type=str, required=True, help="Database folder elements"
    )
    parser.add_argument("--output_file", type=str, required=True, help="output_file")
    parser.add_argument("--testset_size", type=int, required=True, help="# of datasets")
    parser.add_argument(
        "--different_files_in_cluster", action="store_true", help="# of datasets"
    )
    parser.add_argument(
        "--different_files_visited", action="store_true", help="# of datasets"
    )
    parser.add_argument("--no_tab_in_chunk_text", action="store_true", help="# of datasets")
    parser.add_argument("--no_tab_in_chunk_img", action="store_true", help="# of datasets")
    parser.add_argument("--domain_name", type=str, required=True)
    args = parser.parse_args()


    output_file = open(
        args.output_file,
        "a",
    )

    kg_path = f"YOUR_QA_DATA_PATH/kg/{args.name_str}_database.json"  # e.g., "/path/to/qa/kg"
    loaded_kg = KnowledgeGraph.load(kg_path)

    answer_type_distribution = choose_distribution(args.testset_size)
    chunks_all, chunks_metadata_all, chunks_overlapped_items = load_chunks(
        loaded_kg,
        answer_type_distribution,
        args.different_files_in_cluster,
        args.different_files_visited,
        args.no_tab_in_chunk_text,
        args.no_tab_in_chunk_img
    )

    #========================================================== this part of code looks senseless and is invalid
    #for answer_type in [
    #    "image_as_answer",
    #    "image_plus_text_as_answer",
    #    "text_as_answer",
    #    "table_as_answer",
    #]:
    #==========================================================
    lines = 0
    
    
    for answer_type in [
        "image_as_answer",
        "image_plus_text_as_answer",
        "text_as_answer",
        "table_as_answer",
    ]:

        chunks_answer, chunks_metadata_answer, hints_answer = (
            chunks_all[answer_type],
            chunks_metadata_all[answer_type],
            chunks_overlapped_items[answer_type],
        )

        for chunks, chunks_metadata, hints in tqdm(
            zip(chunks_answer, chunks_metadata_answer, hints_answer), desc=f"Generating for {answer_type}"
        ):
            hints = flatten_unique_ignore_case(hints)
            try:
                templates = choose_templates(chunks, chunks_metadata, args.domain_name)
                templates = [templates[-1]]
            except Exception as e:
                templates = []

            if not templates:
                continue

            messages_lst, tables, images = build_prompt(
                chunks,
                chunks_metadata,
                hints,
                answer_type,
                query_type=None,
                templates=templates,
            )

            for idx, messages in enumerate(messages_lst):

                try:
                    response = (
                        client.chat.completions.create(
                            model=MODEL,
                            messages=messages,
                            temperature=0.85,
                        )
                        .choices[0]
                        .message.content
                    )
                    response = (
                        response
                        if "```" not in response
                        else response.replace("```json", "```").split("```")[1]
                    )

                except Exception as error:
                    time.sleep(idx+1)                               #shockingly, ther is a code in exception

                try:
                    questions = ast.literal_eval(response.strip())
                    for element in questions["questions"]:
                        element["answer_type"] = answer_type
                        element["contexts"] = chunks
                        element["template"] = templates[idx]
                        element["chunks_metadata"] = chunks_metadata
                        element["hints"] = hints
                        element["tables"] = {t: p[1] for t, p in tables.items()}
                        element["images"] = {t: p[1] for t, p in images.items()}

                        output_file.write(json.dumps(element) + "\n")
                        output_file.flush()
                        lines += 1

                except Exception as error:
                        print(f"Error: {error}")                    #There was no code here so file was invalid
    output_file.close()

