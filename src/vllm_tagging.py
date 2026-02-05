import os
import ast
import requests
import json
import pdb
import base64
import time
import gc
import torch
import ray
from PIL import Image
from io import BytesIO
import layoutparser as lp
from transformers import AutoProcessor
from vllm import LLM, SamplingParams
from qwen_vl_utils import process_vision_info
from tagging_prompts.main_domain_prompts import MAIN_DOMAIN_PROMPTS
from tagging_prompts.language_prompt import LANGUAGE_PROMPT
from tagging_prompts.date_prompt import DATE_PROMPT
from tagging_prompts.modality_prompts import PDF_MODALITY_PROMPT
from tagging_prompts.format_prompts import PDF_FORMAT_PROMPT
from utils import parse_llm_response
from pdf_layout_parser import find_low_text_images
#//=========================================================
from pdf_convert.pdf_to_image_mthreds import load_pdf_as_base64_images                       #pdf_convert doesn't exist in open space
#//=========================================================
from icl_tagging import prepare_prompt_icl_pt2
from vllm.distributed.parallel_state import destroy_model_parallel

def load_images_from_folder(folder, model, k=20, text_threshold=0.9):
    """Load images from the given folder and return them as base64 strings."""

    if os.path.isdir(folder):
        image_files, layout_results, page_length = find_low_text_images(
            folder_path=folder, model=model, text_threshold=text_threshold
        )
    else:
        pages, base64_images = load_pdf_as_base64_images(folder)
        image_files, layout_results, page_length = find_low_text_images(
            folder_path="/".join(folder.split("/")[:-1]),
            model=model,
            text_threshold=0.9,
            image_files=pages,
        )
        images_base64_idx = [
            int(name.split("/")[-1].replace(".png", "").strip()) for name in image_files
        ]
        image_files = [base64_images[idx] for idx in images_base64_idx]

    images_base64 = []
    count = 0
    for image_file in image_files:
        if not count % k:
            images_base64.append([])
        if os.path.isdir(folder):
            with open(os.path.join(folder, image_file), "rb") as img_file:
                images_base64[-1].append(
                    base64.b64encode(img_file.read()).decode("utf-8")
                )
        else:
            images_base64[-1].append(image_file)
        count += 1

    return images_base64, layout_results, page_length

def prepare_prompt(text_prompt, image_lst, processor):   # no icl
    img_bytes_list = [
                base64.b64decode(image.encode("utf-8")) for image in image_lst
            ]
    images = [Image.open(BytesIO(img_bytes)) for img_bytes in img_bytes_list]
    image_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": [{"type": "image", "image": image} for image in images]
            + [{"type": "text", "text": text_prompt}],
        }
    ]

    prompt = processor.apply_chat_template(
        image_messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    image_inputs, video_inputs, video_kwargs = process_vision_info(
        image_messages, return_video_kwargs=True
    )

    mm_data = {}
    if image_inputs is not None:
        mm_data["image"] = image_inputs
    if video_inputs is not None:
        mm_data["video"] = video_inputs

    llm_inputs = {
        "prompt": prompt,
        "multi_modal_data": mm_data,
        "mm_processor_kwargs": video_kwargs,
    }
    return llm_inputs

def prepare_prompts_batch(text_prompts, images_lst, processor, fields, icl=False):
    """
    Convert base64 images and text prompts into prompts for VLLM;
    text_prompts: list of string; images_lst; list of list of base64 images
    """
    llm_inputs_lst_batch = []
    for image_lst in images_lst:
        llm_inputs_lst = []
        for idx, text_prompt in enumerate(text_prompts):
            if not icl:
                llm_inputs = prepare_prompt(text_prompt, image_lst, processor)
            else:
                field = fields[idx]
                llm_inputs = prepare_prompt_icl_pt2(processor, image_lst, field)
            llm_inputs_lst.append(llm_inputs)
        llm_inputs_lst_batch.append(llm_inputs_lst)

    return llm_inputs_lst_batch


if __name__ == "__main__":
    params={'pdf_folder_path':'/home/user/RAG/UniDoc_bench/UniDoc-Bench/data/downloaded/UniDoc-Bench/construction_pdfs/construction', # e.g., "/path/to/pdfs"
            'output_folder':'//tests',} # e.g., "/path/to/output"
    MODEL_PATH = "YOUR_MODEL_PATH_HERE"  # e.g., "/path/to/your/model"
    PAGE_LIMIT = 5
    ICL_use = True
    llm = LLM(
        model=MODEL_PATH,
        limit_mm_per_prompt={"image": PAGE_LIMIT + 5, "video": 10},
        tensor_parallel_size=8,
        gpu_memory_utilization=0.85,
        max_model_len=100000,  # 100000
    )

    sampling_params = SamplingParams(
        temperature=0.1,
        repetition_penalty=1.05,
        max_tokens=4096,
        stop_token_ids=[],
    )
    processor = AutoProcessor.from_pretrained(MODEL_PATH)

    folder_path = params['pdf_folder_path']  # e.g., "/path/to/pdfs"
    pdf_paths = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf")
    ]

    icl_use_str = "icl" if ICL_use else "0shot"
    output_file = open(
        f"{params['output_folder']}/tagging_100_batch_32B-{icl_use_str}-0411.jsonl",  # e.g., "/path/to/output"
        "w",
    )

    domains_tagging = ["language", "modality", "format", "domain"]
    text_prompts = [
        LANGUAGE_PROMPT,
        PDF_MODALITY_PROMPT,
        PDF_FORMAT_PROMPT,
        MAIN_DOMAIN_PROMPTS,
    ]

    layout_model = lp.models.Detectron2LayoutModel(
        "lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config",
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
    )

    count = 0
    for i, folder in enumerate(pdf_paths):
        if count % 30 == 29:  # reload model
            destroy_model_parallel()
            del llm
            gc.collect()
            torch.cuda.empty_cache()
            torch.distributed.destroy_process_group()
            ray.shutdown()
            llm = LLM(
                model=MODEL_PATH,
                limit_mm_per_prompt={"image": PAGE_LIMIT + 5, "video": 10},
                tensor_parallel_size=4,
                gpu_memory_utilization=0.85,
                max_model_len=100000,  # 100000
            )
            count = 0

        if i <= 24:
            continue
        images_lst, layout_results, page_length = load_images_from_folder(
            folder, model=layout_model, k=PAGE_LIMIT
        )
        print(i, "page_length>>>", page_length)

        llm_inputs_lst_batch = prepare_prompts_batch(
            text_prompts, images_lst, processor, domains_tagging, icl=ICL_use
        )

        all_languages, all_modalities, all_formats, all_domains = (
            set(),
            set(),
            (None, 0.0),
            (None, 0.0),
        )

        start_time = time.time()

        records = {}
        for idx, llm_input in enumerate(llm_inputs_lst_batch):
            records[idx] = dict()
            try:
                outputs = llm.generate(llm_input * 3, sampling_params=sampling_params)
                outputs = [outputs[idx].outputs[0].text for idx in range(len(outputs))]
            except Exception as error:
                print(error)
                continue

            for language_output in [
                o for jdx, o in enumerate(outputs) if jdx % len(text_prompts) == 0
            ]:
                try:
                    languages = ast.literal_eval(language_output)
                    all_languages.update(languages)
                    break
                except Exception as error:
                    print(error)


            for modalities_output in [
                o for jdx, o in enumerate(outputs) if jdx % len(text_prompts) == 1
            ]:
                try:
                    modalities = parse_llm_response(modalities_output)
                    all_modalities.update(modalities["modalities"])
                    records[idx]["modalities"] = modalities
                    break
                except Exception as error:
                    print(error)

            for formats_output in [
                o for jdx, o in enumerate(outputs) if jdx % len(text_prompts) == 2
            ]:
                try:
                    formats = parse_llm_response(formats_output)
                    if float(formats["confidence_format"]) > all_formats[-1]:
                        all_formats = (
                            formats["primary_format"],
                            float(formats["confidence_format"]),
                        )
                    records[idx]["formats"] = formats
                    break
                except Exception as error:
                    print(error)

            for domains_output in [
                o for jdx, o in enumerate(outputs) if jdx % len(text_prompts) == 3
            ]:
                try:
                    domains = parse_llm_response(domains_output)
                    if float(domains["confidence_domain"]) > all_domains[-1]:
                        all_domains = (
                            domains["primary_domain"],
                            float(domains["confidence_domain"]),
                        )
                    records[idx]["domains"] = domains
                except Exception as error:
                    print(error)

        entry = {
            "folder": folder,
            "language": list(all_languages),
            "modality": list(all_modalities),
            "format": all_formats[0],
            "domain": all_domains[0],
            "layout": layout_results,
            "page_length": page_length,
            "log": records,
        }
        output_file.write(json.dumps(entry) + "\n")
        output_file.flush()

    end_time = time.time()

    processing_time = end_time - start_time
    print(f"Processing time: {processing_time} seconds")

    output_file.close()
