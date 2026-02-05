import os
import json
from PIL import Image
import layoutparser as lp
from datetime import datetime
import pdb
from pypdf import PdfReader
#from pdf_convert.pdf_to_image_mthreds import load_pdf_as_base64_images


def get_pdf_creation_date(pdf_path):
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    creation_date = metadata.get("/CreationDate", None)
    if creation_date:
        return creation_date[2:16]  # Extract 'YYYYMMDDHHMMSS'
    else:
        return None


def analyze_folder_images(folder_path, model):
    """
    Analyzes all images in a given folder using a layoutparser model and
    computes total bounding box *ratios* for each category
    (box_area / entire_page_area).
    """
    valid_exts = (".jpg", ".jpeg", ".png")
    image_files = [
        os.path.join(folder_path, fn)
        for fn in os.listdir(folder_path)
        if fn.lower().endswith(valid_exts)
    ]
    pages = len(image_files)
    total_area_by_category = {}

    for image_file in image_files:

        image = Image.open(image_file)
        page_width, page_height = image.size
        page_area = float(page_width * page_height)  # ensure float division

        layout = model.detect(image)

        for layout_obj in layout:
            cat = layout_obj.type
            bbox_width = layout_obj.block.width
            bbox_height = layout_obj.block.height
            box_area = bbox_width * bbox_height

            ratio = box_area / page_area

            if cat not in total_area_by_category:
                total_area_by_category[cat] = 0.0
            total_area_by_category[cat] += ratio

    for cat in total_area_by_category:
        total_area_by_category[cat] = round(total_area_by_category[cat] / pages, 5)

    return total_area_by_category, pages


def analyze_single_image(image_path, model):
    """
    Analyzes a single image using a layoutparser model and
    computes bounding box ratios for each category
    (box_area / entire_page_area).

    Args:
        image_path: Path of the image file or image file
        model: LayoutParser model instance

    Returns:
        Dictionary with category ratios for the single image
    """
    try:
        image = Image.open(image_path)
    except:
        image = image_path

    page_width, page_height = image.size
    page_area = float(page_width * page_height)  # ensure float division

    layout = model.detect(image)
    area_results = {}

    for layout_obj in layout:
        cat = layout_obj.type
        bbox_width = layout_obj.block.width
        bbox_height = layout_obj.block.height
        box_area = bbox_width * bbox_height

        ratio = box_area / page_area

        if cat not in area_results:
            area_results[cat] = 0.0
        area_results[cat] += ratio

    total_ratio = sum(area_results.values())
    if total_ratio > 0:  # Avoid division by zero
        for cat in area_results:
            area_results[cat] = area_results[cat] / total_ratio

    for cat in area_results:
        area_results[cat] = round(area_results[cat], 5)

    return area_results


def analyze_folder_images_per_page(folder_path, model, image_files=None):
    """
    Analyzes all images in a given folder using a layoutparser model and
    returns modality percentages for each individual page.

    Args:
        folder_path: Path to the folder containing images
        model: LayoutParser model instance

    Returns:
        Dictionary with image filenames as keys and their modality ratios as values
    """
    if os.path.isdir(folder_path) and not image_files:
        valid_exts = (".jpg", ".jpeg", ".png")
        image_files = [
            os.path.join(folder_path, fn)
            for fn in os.listdir(folder_path)
            if fn.lower().endswith(valid_exts)
        ]

    try:
        image_files.sort()
    except:
        pass

    results = {}
    for idx, image_file in enumerate(image_files):
        try:
            filename = os.path.basename(image_file)
        except:
            filename = os.path.join(folder_path, f"{idx}.png")

        results[filename] = analyze_single_image(image_file, model)

    return results


def find_low_text_images(folder_path, model, text_threshold=0.9, image_files=None):
    """
    Finds images in a folder where the combined percentage of Title, Text, and List
    is less than the specified threshold (default 90%).
    Always includes the first page (XXX_1.png).

    Args:
        folder_path: Path to the folder containing images
        model: LayoutParser model instance
        text_threshold: Threshold for combined text content (default 0.9 or 90%)

    Returns:
        List of absolute paths of images that meet the criteria
    """
    results = analyze_folder_images_per_page(folder_path, model, image_files)

    sorted_files = sorted(results.keys())

    selected_images = []

    if sorted_files:
        selected_images.append(os.path.join(folder_path, sorted_files[0]))

    layout_results = {
        "Text": 0.0,
        "Title": 0.0,
        "List": 0.0,
        "Table": 0.0,
        "Figure": 0.0,
    }

    for idx, filename in enumerate(sorted_files):
        page_results = results[filename]

        for m in layout_results:
            if m in results[filename]:
                layout_results[m] += results[filename][m]
        if idx == 0:
            continue

        text_content = (
            page_results.get("Title", 0)
            + page_results.get("Text", 0)
            + page_results.get("List", 0)
        )

        if text_content < text_threshold:
            selected_images.append(os.path.join(folder_path, filename))

    layout_results["Text"] = (
        layout_results["Text"] + layout_results["Title"] + layout_results["List"]
    )
    del layout_results["Title"]
    del layout_results["List"]
    total_ratio = sum(layout_results.values())
    for cat in layout_results:
        layout_results[cat] = layout_results[cat] / total_ratio
    return selected_images, layout_results, len(sorted_files)


def main(json_file_path, model, out_json_path):
    """
    Loads each line of a JSON file, extracts the "folder" path, runs layout
    analysis on all images in that folder, and then saves the results
    (including total pages and per-category layout ratios) to a new JSON file.
    """
    results = []  # We'll collect updated records here

    with open(json_file_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line.strip())
            if "folder" not in entry:
                continue

            folder_path = entry["folder"]
            if not os.path.isdir(folder_path):
                continue

            pdf_file = folder_path.replace("YOUR_IMAGES_FOLDER", "YOUR_PDF_FOLDER") + ".pdf"
            if os.path.exists(pdf_file):
                creation_date = get_pdf_creation_date(pdf_file)
                if not creation_date:
                    creation_datetime = ""
                else:
                    try:
                        creation_datetime = datetime.strptime(
                            creation_date, "%Y%m%d%H%M%S"
                        )
                        creation_datetime = creation_datetime.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except:
                        print('AAAAAAA') ###ERROR IN CODE THERE WAS NOTHING
            else:
                print('AAAAAAA') ###ERROR IN CODE THERE WAS NOTHING

            area_results, pages = analyze_folder_images(folder_path, model)
            area_results_merge = {"Text": 0, "Table": 0, "Figure": 0}

            if len(area_results) != 0:
                for key, value in area_results.items():
                    if key in ["Text", "List", "Title"]:
                        area_results_merge["Text"] += value
                    else:
                        area_results_merge[key] += value
                for key, value in area_results_merge.items():
                    area_results_merge[key] = f"{value:.5f}"

            entry["pages_num"] = pages
            entry["creation_time"] = creation_datetime

            entry["layout"] = area_results_merge


            results.append(entry)

    with open(out_json_path, "w", encoding="utf-8") as out_f:
        for record in results:
            json_line = json.dumps(record, ensure_ascii=False)
            out_f.write(json_line + "\n")



if __name__ == "__main__":
    model = lp.models.Detectron2LayoutModel(
        "lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config",
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
        device="cuda"
    )


