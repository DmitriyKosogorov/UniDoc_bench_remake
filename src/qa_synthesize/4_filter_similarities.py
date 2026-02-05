import json
import argparse
from openai import OpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_path", type=str, required=True
    )
    args = parser.parse_args()

    with open(args.file_path, 'r') as file:

        data_list = list(file)
        data = []
        for d in data_list:
            try:
                data.append(json.loads(d))
            except:pass

    order = {
        "image_only": 0,
        "table_required": 1,
        "image_plus_text_as_answer": 2,
        "text_only": 3
    }

    data.sort(key=lambda x: order.get(x["answer_type"], 999))
    data = [
        item for item in data
        if not any(phrase in item.get("question", "").lower() for phrase in
                   ["in the context", "in the image", "in the figure"])
    ]

    questions = [item['question'] for item in data]
    answers = [item['answer'] for item in data]

    client = OpenAI()

    def get_embedding(text):
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )

        return response.data[0].embedding

    question_embeddings, answer_embeddings = [], []
    for q in tqdm(questions, desc="Generating Embeddings for Q"):
        question_embeddings.append(get_embedding(q))
    for a in tqdm(questions, desc="Generating Embeddings for A"):
        answer_embeddings.append(get_embedding(a))

    threshold_q = 0.8
    threshold_a = 0.9

    new_data_pool = [0]

    for i, (q_emb, a_emb) in tqdm(enumerate(zip(question_embeddings[1:], answer_embeddings[1:]))):
        i += 1
        is_similar = False
        q_vector = np.array(q_emb)
        a_vector = np.array(a_emb)

        for jdx in new_data_pool:
            prev_q_vector = np.array(question_embeddings[jdx])
            prev_a_vector = np.array(answer_embeddings[jdx])

            q_similarity = np.dot(q_vector, prev_q_vector) / (np.linalg.norm(q_vector) * np.linalg.norm(prev_q_vector))

            a_similarity = np.dot(a_vector, prev_a_vector) / (np.linalg.norm(a_vector) * np.linalg.norm(prev_a_vector))

            if q_similarity >= threshold_q or a_similarity >= threshold_a:
                is_similar = True
                break

        if not is_similar:
            new_data_pool.append(i)

    save_path = args.file_path.replace(".json", "_filtered.json")
    output_file = open(save_path, 'w')
    for idx in new_data_pool:
        output_file.write(json.dumps(data[idx]) + "\n")
        output_file.flush()
    output_file.close()