import json
import os
import base64
from PIL import Image
from io import BytesIO
from tagging_prompts.main_domain_prompts import MAIN_DOMAIN_PROMPTS, MAIN_DOMAIN_PROMPTS_QUESTION
from tagging_prompts.language_prompt import LANGUAGE_PROMPT
from tagging_prompts.date_prompt import DATE_PROMPT
from tagging_prompts.modality_prompts import PDF_MODALITY_PROMPT, PDF_MODALITY_PROMPT_QUESTION
from tagging_prompts.format_prompts import PDF_FORMAT_PROMPT, PDF_FORMAT_PROMPT_QUESTION
import layoutparser as lp
from transformers import AutoProcessor
from pdf_layout_parser import find_low_text_images
from qwen_vl_utils import process_vision_info
FIELD_MAPPING_SYS = {"domain": MAIN_DOMAIN_PROMPTS, "format": PDF_FORMAT_PROMPT, "modality": PDF_MODALITY_PROMPT, "language": LANGUAGE_PROMPT}
FIELD_MAPPING_Q= {"domain": MAIN_DOMAIN_PROMPTS_QUESTION , "format": PDF_FORMAT_PROMPT_QUESTION, "modality": PDF_MODALITY_PROMPT_QUESTION, "language": LANGUAGE_PROMPT}
MODEL_PATH = "YOUR_MODEL_PATH_HERE"  # e.g., "/path/to/your/model"
PROCESSOR = AutoProcessor.from_pretrained(MODEL_PATH)
ICL_PATH = "YOUR_ICL_DATA_PATH_HERE"  # e.g., "/path/to/your/icl_example.jsonl"
LAYOUT_MODEL = lp.models.Detectron2LayoutModel(
        "lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config",
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
    )

def load_images_from_folder(folder, model, k=20, text_threshold=0.9):
    """Load images from the given folder and return them as base64 strings."""
    image_files, layout_results, page_length = find_low_text_images(
        folder_path=folder, model=model, text_threshold=text_threshold
    )
    images_base64 = []
    count = 0
    for image_file in image_files:
        if not count % k:
            images_base64.append([])

        with open(os.path.join(folder, image_file), "rb") as img_file:
            images_base64[-1].append(
                base64.b64encode(img_file.read()).decode("utf-8")
            )
        count += 1
    return images_base64, layout_results, page_length

def transform_entry(entry, field):
    if field == "domain":
        transformed_entry = {
            "primary_domain": entry["primary_domain"],
            "secondary_domains": entry["secondary_domains"],
            "confidence_domain": entry["confidence_domain"]
        }

    if field == "format":
        transformed_entry = {
            "primary_format": entry["primary_format"].upper(),
            "secondary_formats": [e.upper() for e in entry["secondary_formats"]],  # Using secondary_domains as secondary_formats
            "confidence_format": entry["confidence_format"]  # Using confidence_domain as confidence_format
        }

    if field == "modality":
        transformed_entry = {
            "modalities": [e.upper() for e in entry["modalities"]],
            "confidence_modalities": entry["confidence_modalities"]
        }

    if field == "language":
        transformed_entry = json.dumps(entry["language"])
        return transformed_entry

    transformed_entry = json.dumps(transformed_entry, indent=4)
    return "```json\n" + transformed_entry + '\n```'

def process_answers_jsonl(input_file, field):
    entries = []
    with open(input_file, 'r') as f_in:
        for line in f_in:
            entry = json.loads(line.strip())
            transformed_entry = transform_entry(entry, field)
            entries.append(transformed_entry)
    return entries

def load_icl(icl_path, field, model):
    question_prompt = FIELD_MAPPING_Q[field]

    with open(icl_path, 'r') as f:
        icl_data = list(f)

    image_lsts_icl, text_prompts_icl, answers_icl = [], [], []
    for element in icl_data:
        element = json.loads(element)
        images_lst, layout_results, page_length = load_images_from_folder(folder=element["folder"], model=model)
        image_lsts_icl.append(images_lst[0])
        text_prompts_icl.append(question_prompt)
        answers_icl.append(transform_entry(element, field))

    return text_prompts_icl, image_lsts_icl, answers_icl

def prepare_prompt_icl_pt1(icl_path, processor, field):
    text_prompts_icl, image_lsts_icl, answers_icl = load_icl(icl_path, field, LAYOUT_MODEL)
    question_prompt = FIELD_MAPPING_Q[field]
    system_prompt = FIELD_MAPPING_SYS[field]
    image_messages = [
            {"role": "system", "content": system_prompt}
        ]
    for text_prompt, image_lst, answer in zip(text_prompts_icl, image_lsts_icl, answers_icl):
        img_bytes_list = [
            base64.b64decode(image.encode("utf-8")) for image in image_lst
        ]
        images = [Image.open(BytesIO(img_bytes)) for img_bytes in img_bytes_list]
        image_messages += [
            {
                "role": "user",
                "content": [{"type": "image", "image": image} for image in images]
                + [{"type": "text", "text": text_prompt}],
            }
        ]
        image_messages += [
            {
                "role": "assistant",
                "content": answer,
            },
        ]
    return image_messages

IMAGE_MESSAGES = {
    "domain": prepare_prompt_icl_pt1(ICL_PATH, PROCESSOR, "domain"),
    "modality": prepare_prompt_icl_pt1(ICL_PATH, PROCESSOR, "modality"),
    "language": prepare_prompt_icl_pt1(ICL_PATH, PROCESSOR, "language"),
    "format": prepare_prompt_icl_pt1(ICL_PATH, PROCESSOR, "format")
    }

def prepare_prompt_icl_pt2(processor, image_lst, field):
    question_prompt = FIELD_MAPPING_Q[field]
    img_bytes_list = [
                    base64.b64decode(image.encode("utf-8")) for image in image_lst
                ]
    images = [Image.open(BytesIO(img_bytes)) for img_bytes in img_bytes_list]
    image_messages = IMAGE_MESSAGES[field][:]
    image_messages += [
            {
                "role": "user",
                "content": [{"type": "image", "image": image} for image in images]
                + [{"type": "text", "text": question_prompt}],
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
