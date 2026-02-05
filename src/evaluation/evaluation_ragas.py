import json
from ragas import SingleTurnSample, EvaluationDataset
from ragas.metrics._factual_correctness import FactualCorrectness
from ragas.llms import LangchainLLMWrapper
from ragas import evaluate
import asyncio
from ragas.metrics._context_precision import LLMContextPrecisionWithReference, NonLLMContextPrecisionWithReference
from ragas.metrics._context_recall import NonLLMContextRecall, LLMContextRecall
from llama_index.llms.openai import OpenAI
from langchain_openai import ChatOpenAI
from correctness import get_precision, get_recall
import argparse
from tqdm import tqdm
from collections import defaultdict

def turn_sample_lst2dataset(data_samples, test_size=1):
    samples_lst, reference_contexts, ground_truths = (
        [],
        [None for _ in range(len(data_samples["question"]))],
        [None for _ in range(len(data_samples["question"]))],
    )
    if "contexts" in data_samples and data_samples["contexts"][0][0]:
        reference_contexts = data_samples["contexts"]
    if "gt" in data_samples:
        ground_truths = data_samples["gt"]

    for idx in range(len(data_samples["question"])):
        retrieved_chunks = data_samples["retrieved_contexts"][idx] if "retrieved_contexts" in data_samples else []
        sample = SingleTurnSample(
            user_input=str(data_samples["rewritten_question_obscured"][idx]) if "rewritten_question_obscured" in data_samples else str(data_samples["question"][idx]),
            reference_contexts=reference_contexts[idx],
            response=str(data_samples["baseline"][idx]) if data_samples["baseline"][idx] else "I do not know.",
            reference=str(ground_truths[idx]),
            retrieved_contexts=retrieved_chunks,
        )
        samples_lst.append(sample)
        if idx >= test_size-1:
            break
    return EvaluationDataset(samples=samples_lst), samples_lst

def main(args):
    llm_usage = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0001,
    )
    evaluator_llm = LangchainLLMWrapper(langchain_llm=llm_usage)

    metrics, metrics_str = [], []

    try:
        with open(args.input_file, "r") as f:
            dataset = json.load(f)
    except:
        with open(args.input_file, "r") as f:
            data = list(f)
        dataset = defaultdict(list)
        for element in data:
            element = json.loads(element)
            for key in element:
                dataset[key].append(element[key])

    dataset_eval, _ = turn_sample_lst2dataset(dataset, test_size=args.testsize)
    if metrics:
        result_ragas = evaluate(
            dataset_eval, metrics=metrics
        )
        result_pandas = result_ragas.to_pandas()

        for key in metrics_str:
            eval_lst = result_pandas[key].tolist()
            dataset[key] = eval_lst
            dataset[key + '_avg'] = sum(eval_lst) / len(eval_lst)

    dataset["gpt4-correctness-recall"] = []
    dataset["gpt4-correctness-recall_results"] = []
    for idx in tqdm(range(len(dataset["question"][:args.testsize])), desc="Processing GPT-4 correctness - Recall:"):
        question = dataset["question"][idx]
        answer = dataset["baseline"][idx]
        if "gt" in dataset:
            groundtruth = dataset["gt"][idx]
        if "answer" in dataset:
            groundtruth = dataset["answer"][idx]
        correctness, correctness_recall_results = get_recall(question=question, answer=answer, ground_truth=groundtruth)
        dataset["gpt4-correctness-recall"].append(correctness)
        dataset["gpt4-correctness-recall_results"].append(correctness_recall_results)

    dataset["gpt4-correctness-precision"] = []
    dataset["gpt4-correctness-precision_results"] = []
    for idx in tqdm(range(len(dataset["question"][:args.testsize])), desc="Processing GPT-4 correctness - precision:"):
        try:
            question = dataset["question"][idx]
            answer = dataset["baseline"][idx]
            contexts = " ".join(dataset["contexts"][idx])
            if "gt" in dataset:
                groundtruth = dataset["gt"][idx]
            if "answer" in dataset:
                groundtruth = dataset["answer"][idx]
            correctness, correctness_precision_results = get_precision(question=question, answer=answer, ground_truth=str(groundtruth)+contexts)
            dataset["gpt4-correctness-precision"].append(correctness)
            dataset["gpt4-correctness-precision_results"].append(correctness_precision_results)
        except:
            dataset["gpt4-correctness-precision"].append(-1)
            dataset["gpt4-correctness-precision_results"].append(-1)

    avg_correctness_precision = [c for c in dataset["gpt4-correctness-precision"] if c >= 0]
    dataset["gpt4-correctness-precision-avg"] = sum(avg_correctness_precision) / len(avg_correctness_precision)
    avg_correctness_recall = [c for c in dataset["gpt4-correctness-recall"] if c >= 0]
    dataset["gpt4-correctness-recall-avg"] = sum(avg_correctness_recall) / len(avg_correctness_recall)

    with open(args.output_file, 'w') as f:
        json.dump(dataset, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--input_file', type=str, required=True, help='Path to the input JSON file')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output JSON file')
    parser.add_argument('--testsize', type=int, required=True, help='# of questions you want to use')
    args = parser.parse_args()
    main(args)
