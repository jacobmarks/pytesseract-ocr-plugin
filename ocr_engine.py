from collections import defaultdict
from PIL import Image
from pytesseract import image_to_data, Output

import fiftyone as fo


def get_filepath(sample):
    return (
        sample.local_path if hasattr(sample, "local_path") else sample.filepath
    )


def get_ocr_detections(sample):
    fp = get_filepath(sample)
    preds = image_to_data(fp, output_type=Output.DICT)

    levels = preds["level"]
    boxes = preds["left"], preds["top"], preds["width"], preds["height"]
    confidences = preds["conf"]
    texts = preds["text"]
    block_nums = preds["block_num"]
    par_nums = preds["par_num"]
    line_nums = preds["line_num"]
    word_nums = preds["word_num"]

    word_detections = []
    blocks = defaultdict(list)

    # Process each word to create word-level detections and group by block for block-level detections
    n = len(levels)
    w, h = sample.metadata.width, sample.metadata.height
    for i in range(n):
        bbox = boxes[0][i], boxes[1][i], boxes[2][i], boxes[3][i]
        normalized_bbox = [bbox[0] / w, bbox[1] / h, bbox[2] / w, bbox[3] / h]
        block_num = block_nums[i]

        # Word-level detection
        word_det = fo.Detection(
            label=texts[i],
            bounding_box=normalized_bbox,
            level=levels[i],
            paragraph=par_nums[i],
            line=line_nums[i],
            word=word_nums[i],
            block=block_num,
            confidence=confidences[i],
        )
        word_detections.append(word_det)

        # Group by block for later processing
        blocks[block_num].append((normalized_bbox, texts[i]))

    # Create block-level detections
    block_detections = []
    for block_num, detections in blocks.items():
        min_x = min(det[0][0] for det in detections)
        min_y = min(det[0][1] for det in detections)
        max_x = max(det[0][2] for det in detections)
        max_y = max(det[0][3] for det in detections)

        block_bbox = [min_x, min_y, max_x, max_y]
        block_text = " ".join(det[1] for det in detections)

        block_det = fo.Detection(
            label=block_text,
            bounding_box=block_bbox,
            block=block_num,
        )
        block_detections.append(block_det)

    word_detections = fo.Detections(detections=word_detections)
    block_detections = fo.Detections(detections=block_detections)

    return word_detections, block_detections
