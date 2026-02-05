import os
import json
from collections import defaultdict
import argparse
from collections import defaultdict, Counter
import random

def balance_dataset(data, max_diff):
    answer_type_groups = defaultdict(list)
    for item in data:
        answer_type_groups[item["answer_type"]].append(item)

    min_answer_count = min(len(items)+max_diff for items in answer_type_groups.values())

    balanced_data = []
    for answer_type, items in answer_type_groups.items():
        question_type_groups = defaultdict(list)
        for item in items:
            question_type_groups[item["question_type"]].append(item)

        question_types = list(question_type_groups.keys())
        per_qtype = min_answer_count // len(question_types)
        remainder = min_answer_count % len(question_types)

        subset = []
        for qtype in question_types:
            group = question_type_groups[qtype]
            count = per_qtype + (1 if remainder > 0 else 0)
            remainder -= 1 if remainder > 0 else 0
            sampled = random.sample(group, min(len(group), count))
            subset.extend(sampled)

        if len(subset) < min_answer_count:
            remaining = [item for group in question_type_groups.values() for item in group if item not in subset]
            extra_needed = min_answer_count - len(subset)
            subset.extend(random.sample(remaining, min(len(remaining), extra_needed)))

        balanced_data.extend(subset)

    return balanced_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_path", type=str, required=True
    )
    parser.add_argument(
        "--max_diff", type=int, required=True
    )
    args = parser.parse_args()

    output_file = args.file_path.replace(".json", '_balanced.json')

    json_files = [args.file_path]

    merged_data = []

    data = []
    for file_path in json_files:
        with open(file_path, 'r') as file:
            data += list(file)

    answer_type_count = defaultdict(int)
    question_type_count = defaultdict(int)
    for element in data:
        element = json.loads(element)
        answer_type_count[element["answer_type"]] += 1
        question_type_count[element["question_type"]] += 1

    data = [json.loads(d) for d in data]
    data = balance_dataset(data, args.max_diff)

    with open(output_file, 'w') as file:
        for element in data:
            file.write(json.dumps(element) + "\n")
            file.flush()

