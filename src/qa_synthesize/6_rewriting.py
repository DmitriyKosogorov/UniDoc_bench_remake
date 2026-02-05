import os
import ast
import json
import argparse
import base64
from openai import OpenAI
from chunks_extraction import chunk_match_back, extract_relevant_chunks
from prompts.rewriting import REWRITE_Q_PROMPT
from datetime import datetime

MODEL = "gpt-4o"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def prepare_images(image_paths):
    imgs = []
    for img_path in image_paths:
        with open(img_path, "rb") as image_file:
            img = base64.b64encode(image_file.read()).decode("utf-8")
            imgs.append(img)
    return imgs

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
            "image_url": {"url": f"data:image/jpeg;;base64,{img}"},
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
    response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.85,
            )

    response = response.choices[0].message.content.replace("```json", "```").split("```")[1].strip()
    return ast.literal_eval(response)

def transform_question_to_rag(data):
    """
    Transform the question to be more RAG-like by making it self-contained and adding anchoring signals.
    :param data: A dictionary containing 'question', 'contexts', 'answers', and 'images'.
    :return: A transformed question string.
    """
    prompt = REWRITE_Q_PROMPT.replace("{{current_date}}", datetime.now().strftime("%B %d, %Y"))
    prompt += (
        "\n\nInput Data:\n"
        f"- Question: \"{data.get('question', '')}\"\n"
        f"- Contexts: \"{data.get('contexts', [])}\"\n"
        f"- Correct Answer: \"{data.get('answer', '')}\"\n"
        f"- Images: The image is as follows:"
    )


    user_prompt = [
        {
            "type": "text",
            "text": prompt
        }
    ]
    imgs = prepare_images(image_paths)
    for img in imgs:
        user_prompt.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;;base64,{img}"},
        })
    user_prompt.append(
        {
            "type": "text",
            "text": """Return the output in a JSON object. Avoid any phrasing that refers to the source (e.g., "as shown in the document", "in the context", "in the image", "in figure", "in table", "in diagram", etc.)."""
        }
    )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that responds Python dictionary. ",
        },
        {"role": "user", "content": user_prompt},
    ]

    response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.85,
            )

    response = response.choices[0].message.content.replace("```json", "```").split("```")[1].strip()
    return ast.literal_eval(response)

def make_answer_complete(data):
    """
    Transform the question to be more RAG-like by making it self-contained and adding anchoring signals.
    :param data: A dictionary containing 'question', 'contexts', 'answers', and 'images'.
    :return: A transformed question string.
    """
    prompt = (
        "You are tasked with rewriting the following answer so that it contains all the facts for answering the question, given the contexts and the image.\n"
        "Instruction:\n"
        "- Do not hallucinate any additional information. You can only use information in the provided contexts and images.\n"
        "- The rewritten answer will contain the **old correct answer**. if the old answer is correct.\n"
        "- If the answer is already complete, you may leave it unchanged.\n"
        "- You will make the answer as concise as possible.\n"
        "- The **old correct answer** may not fully answer the question, you need to make the 'complete_answer' fully answer the question."
        "\n\nOutput the transformed question as a JSON dictionary with the key 'complete_answer'."
        "\n\nInput Data:\n"
        f"- Question: \"{data.get('rewritten_question_obscured', '')}\"\n"
        f"- Contexts: \"{data.get('contexts', [])}\"\n"
        f"- Old Correct Answer: \"{data.get('answer', '')}\"\n"
        f"- Images: The image is as follows:"
    )

    user_prompt = [
        {
            "type": "text",
            "text": prompt
        }
    ]
    imgs = prepare_images(image_paths)
    for img in imgs:
        user_prompt.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;;base64,{img}"},
        })
    user_prompt.append(
        {
            "type": "text",
            "text": "Output the transformed question as a JSON dictionary with the key 'complete_answer'"
        }
    )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that responds Python dictionary.",
        },
        {"role": "user", "content": user_prompt},
    ]

    response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.85,
            )

    response = response.choices[0].message.content.replace("```json", "```").split("```")[1].strip()
    return ast.literal_eval(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_path", type=str, required=True
    )
    parser.add_argument(
        "--folder_elements", type=str, required=True
    )
    parser.add_argument(
        "--mode", type=str, required=True
    )
    parser.add_argument(
        "--file_path_save", type=str, required=True
    )
    args = parser.parse_args()


    count = 0
    with open(args.file_path, 'r') as file:
        file = list(file)

    output_file = open(args.file_path_save, "w")

    count = 0
    for line in file:
        data = json.loads(line)

        chunks = data["contexts"]
        chunks_metadata = data["chunks_metadata"]
        image_paths = []
        for chunk, chunk_metadata in zip(chunks, chunks_metadata):
            tabs, img = chunk_match_back(chunk, chunk_metadata, args.folder_elements)
            image_paths += list(img.values())
            image_paths += list(tabs.values())

        if args.mode == "full":
            example_data = {
                'question': data["question"],
                'contexts': data["contexts"],
                'answer': data["answer"],
                'images': image_paths
            }
            transformed_question = transform_question_to_rag(example_data)
            example_data["rewritten_question_obscured"] = transformed_question["obscured_question"]
            new_answer = make_answer_complete(example_data)["complete_answer"]
            if "answer_wrong" in transformed_question and transformed_question["answer_wrong"] == "False":
                data["rewritten_question_specific"] = transformed_question["specific_question"]
                data["rewritten_question_obscured"] = transformed_question["obscured_question"]
                data["complete_answer"] = new_answer
                output_file.write(json.dumps(data) + "\n")
                output_file.flush()
            count += 1
        else:
            example_data = {
                'question': data["rewritten_question_obscured"],
                'contexts': data["contexts"],
                'answer': data["answer"],
                'images': image_paths,
                'rewritten_question_obscured': data["rewritten_question_obscured"]
            }

            new_answer = make_answer_complete(example_data)["complete_answer"]
            if new_answer:
                data["complete_answer"] = new_answer
                output_file.write(json.dumps(data) + "\n")
                output_file.flush()
            count += 1

    output_file.close()

