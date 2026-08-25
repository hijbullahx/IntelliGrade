#!/usr/bin/env python3
"""
OpenCV-based Line Auto-Segmentation Script for IntelliGrade.
Extracts line-level handwritten text crops from full-page student answer scripts in Materials/.
"""

import os
import cv2
import numpy as np
from typing import List, Tuple


def segment_handwritten_lines(
    input_image_path: str,
    output_dir: str,
    kernel_size: Tuple[int, int] = (50, 10),
    min_width: int = 40,
    min_height: int = 12,
    min_area: int = 400
) -> List[str]:
    """
    Applies OpenCV image processing, Otsu thresholding, horizontal morphological dilation,
    and contour sorting to extract line-level image crops.
    """
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input image file not found: {input_image_path}")

    os.makedirs(output_dir, exist_ok=True)

    print(f"[SEGMENTATION] Loading full-page script: '{input_image_path}'...")
    image = cv2.imread(input_image_path)
    if image is None:
        raise ValueError(f"Failed to read image at '{input_image_path}'")

    orig_h, orig_w = image.shape[:2]

    # Step 1: Convert to Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 2: Apply Gaussian Blur to smooth noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Step 3: Otsu's Binarization (Inverse: text becomes white 255, background black 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Step 4: Morphological Dilation with horizontal rectangular kernel (50, 10)
    # Merges individual words along the horizontal direction into continuous line blocks
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    # Step 5: Find Contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bounding_boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        # Filter out small noise artifacts and non-line regions
        if w >= min_width and h >= min_height and area >= min_area and w > h:
            bounding_boxes.append((x, y, w, h))

    # Step 6: Sort bounding boxes top-to-bottom (ascending y-coordinate)
    bounding_boxes.sort(key=lambda b: b[1])

    saved_line_paths = []
    print(f"[SEGMENTATION] Detected {len(bounding_boxes)} valid text line region(s).")

    # Step 7: Crop and save line images
    padding = 4
    for idx, (x, y, w, h) in enumerate(bounding_boxes, start=1):
        # Apply slight padding safely within bounds
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(orig_w, x + w + padding)
        y2 = min(orig_h, y + h + padding)

        line_crop = image[y1:y2, x1:x2]
        output_filename = f"line_{idx:03d}.jpg"
        output_filepath = os.path.join(output_dir, output_filename)

        cv2.imwrite(output_filepath, line_crop)
        saved_line_paths.append(output_filepath)

    print(f"[SEGMENTATION SUCCESS] Extracted {len(saved_line_paths)} cropped line images to '{output_dir}'.")
    return saved_line_paths


if __name__ == '__main__':
    materials_dir = r"d:\Projects\IntelliGrade\Materials"
    output_crops_dir = r"d:\Projects\IntelliGrade\Materials\Cropped_Lines"

    # Find the first image file in Materials directory
    target_image = None
    if os.path.exists(materials_dir):
        for root, dirs, files in os.walk(materials_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    target_image = os.path.abspath(os.path.join(root, f))
                    break
            if target_image:
                break

    if not target_image:
        print("[ERROR] No image file (.jpg, .jpeg, .png) found in Materials directory.")
        exit(1)

    print(f"Target script image selected: '{target_image}'")
    cropped_files = segment_handwritten_lines(target_image, output_crops_dir)

    print("\nCropped Line Artifacts Summary:")
    for f_path in cropped_files:
        print(f"  - {os.path.basename(f_path)} ({os.path.getsize(f_path)} bytes)")
