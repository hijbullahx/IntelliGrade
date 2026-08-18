import os
import sys
import time
import json
import cv2
import numpy as np

# Ensure Django environment is configured
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')
import django
django.setup()

from core.ai_engine.providers.groq import GroqProvider
from core.ai_engine.providers.openrouter import OpenRouterProvider
from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

# 1. Load all 4 real handwritten Q4 crops in page order
trace_path = os.path.join(os.path.dirname(__file__), 'media', 'request_trace', 'eval_89', 'question_heading_detection.json')
with open(trace_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

q4_summary = next(s for s in data['summary'] if s.get('question_number') == 'Q4')

crops = []
for reg in q4_summary['regions']:
    p_num = reg['page_number']
    img_path = os.path.join(os.path.dirname(__file__), 'media', 'request_trace', 'eval_89', f'page_{p_num}', '01_original.png')
    extracted = AnswerCropService.extract_answer_region_crops(working_image_path=img_path, regions=[reg])
    crops.extend(extracted)

print(f"Loaded {len(crops)} original Q4 crops.")
print("\n--- ORIGINAL CROP DIMENSIONS ---")
for i, c in enumerate(crops, 1):
    w, h, sz = c['crop_width'], c['crop_height'], len(c['image_bytes'])
    p_num = c['page_number']
    print(f"Crop #{i} (Page {p_num}): {w}x{h} px | {sz} bytes")


# 2. Test-only Compaction Function
def compact_crops_into_composites(
    crops_list,
    max_composites=3,
    sep_height_px=40
) -> list:
    """
    Vertically stacks handwritten answer crops into <= max_composites images while
    preserving exact page order, high handwriting resolution, and clear page separators.
    """
    if not crops_list:
        return []

    # Decode bytes into BGR images
    images = []
    for c in crops_list:
        nparr = np.frombuffer(c['image_bytes'], np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        images.append({
            'page_number': c['page_number'],
            'region_id': c.get('region_id', ''),
            'img': img
        })

    # Group crops into bins (for 4 crops -> 2 bins of 2 crops each)
    num_crops = len(images)
    if num_crops <= max_composites:
        # No compaction needed
        groups = [[img] for img in images]
    else:
        # Determine items per bin to stay within max_composites (e.g. 4 -> [2, 2])
        crops_per_bin = (num_crops + max_composites - 1) // max_composites
        groups = [images[i:i + crops_per_bin] for i in range(0, num_crops, crops_per_bin)]

    composites = []
    for comp_idx, group in enumerate(groups, 1):
        target_width = max(item['img'].shape[1] for item in group)
        canvas_parts = []

        for item in group:
            img = item['img']
            h, w = img.shape[:2]
            p_num = item['page_number']

            # Scale to target_width if necessary while preserving aspect ratio
            if w != target_width:
                new_h = int(h * (target_width / float(w)))
                img_resized = cv2.resize(img, (target_width, new_h), interpolation=cv2.INTER_LANCZOS4)
            else:
                img_resized = img.copy()

            # Create visual separator bar with page label
            sep_bar = np.full((sep_height_px, target_width, 3), (230, 230, 230), dtype=np.uint8)
            label = f"--- Page {p_num} (Part {comp_idx}) ---"
            cv2.putText(sep_bar, label, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 50, 50), 2, cv2.LINE_AA)

            canvas_parts.append(sep_bar)
            canvas_parts.append(img_resized)

        # Stack vertically
        composite_bgr = np.vstack(canvas_parts)
        success, png_buffer = cv2.imencode('.png', composite_bgr)
        if success:
            comp_bytes = png_buffer.tobytes()
            composites.append({
                'composite_id': f'composite_{comp_idx}',
                'crop_width': int(composite_bgr.shape[1]),
                'crop_height': int(composite_bgr.shape[0]),
                'image_bytes': comp_bytes,
                'mime_type': 'image/png',
                'pages': [item['page_number'] for item in group]
            })

    return composites


composites = compact_crops_into_composites(crops, max_composites=3)

print(f"\n--- COMPOSITE IMAGES CREATED ({len(composites)} composites) ---")
for i, comp in enumerate(composites, 1):
    w, h, sz = comp['crop_width'], comp['crop_height'], len(comp['image_bytes'])
    pages_str = ", ".join(str(p) for p in comp['pages'])
    print(f"Composite #{i} (Pages [{pages_str}]): {w}x{h} px | {sz} bytes")

question_text = q4_summary['prompt_text']
max_marks = float(q4_summary['max_marks'])
rubric_criteria = (
    "1. Explain core principles of Image Transformation and Feature Selection (10 marks).\n"
    "2. Analyze commonly used techniques and applications in enhancing image analysis, "
    "pattern recognition, and classification (15 marks)."
)
ideal_answer = (
    "Image Transformation converts images into different representations (e.g. Fourier, Wavelet, HSI/CMY) "
    "to analyze frequency/color features. Feature Selection extracts discriminative properties (edges, contours, texture) "
    "to reduce dimensionality for classification."
)

prompt_groq = f"""
Evaluate the following student answer for an academic examination question:

Question: {question_text}
Maximum Marks: {max_marks}
Rubric Criteria: {rubric_criteria}
Ideal Answer: {ideal_answer}

Examine the attached visual handwritten answer composite images ({len(composites)} composite images containing all answer pages).

Return ONLY a raw JSON object with keys:
"ai_suggested_marks": float,
"confidence_score": float (0.0 to 1.0),
"ai_feedback": str,
"strengths": list of str,
"mistakes": list of str,
"missing_points": list of str,
"rubric_breakdown": [
    {{"criteria": str, "allocated_marks": float, "awarded_marks": float, "comments": str}}
],
"requires_manual_review": bool,
"manual_review_reason": str
"""

prompt_openrouter = f"""
Evaluate the following student answer for an academic examination question:

Question: {question_text}
Maximum Marks: {max_marks}
Rubric Criteria: {rubric_criteria}
Ideal Answer: {ideal_answer}

Examine the attached visual handwritten answer crops ({len(crops)} crops).

Return ONLY a raw JSON object with keys:
"ai_suggested_marks": float,
"confidence_score": float (0.0 to 1.0),
"ai_feedback": str,
"strengths": list of str,
"mistakes": list of str,
"missing_points": list of str,
"rubric_breakdown": [
    {{"criteria": str, "allocated_marks": float, "awarded_marks": float, "comments": str}}
],
"requires_manual_review": bool,
"manual_review_reason": str
"""

# 4. RUN GROQ EVALUATION WITH COMPOSITES
print("\n" + "="*50)
print(f"=== GROQ BENCHMARK WITH COMPACTED IMAGES ({len(composites)} images) ===")
print("="*50)

groq_primary = composites[0]['image_bytes']
groq_extra = [{'bytes': c['image_bytes'], 'mime_type': 'image/png'} for c in composites[1:]]

groq = GroqProvider(api_key=os.environ.get('GROQ_API_KEY', ''))
t0 = time.monotonic()
try:
    groq_res = groq.generate_completion(
        prompt=prompt_groq,
        system_instruction="Return strict JSON academic script evaluations.",
        image_bytes=groq_primary,
        mime_type='image/png',
        extra_files=groq_extra,
        timeout=30.0
    )
    groq_elapsed = time.monotonic() - t0
    print(f"STATUS: SUCCESS | TIME: {groq_elapsed:.2f}s")
    print(f"RAW_RESPONSE:\n{groq_res}")
except Exception as e:
    groq_elapsed = time.monotonic() - t0
    print(f"STATUS: ERROR | TIME: {groq_elapsed:.2f}s")
    print(f"ERROR: {e}")

# 5. RUN OPENROUTER BASELINE WITH 4 ORIGINAL CROPS
print("\n" + "="*50)
print(f"=== OPENROUTER BASELINE WITH ORIGINAL 4 CROPS ===")
print("="*50)

or_primary = crops[0]['image_bytes']
or_extra = [{'bytes': c['image_bytes'], 'mime_type': 'image/png'} for c in crops[1:]]

openrouter = OpenRouterProvider(api_key=os.environ.get('OPENROUTER_API_KEY', ''), model_name='openrouter/free')
t0 = time.monotonic()
try:
    or_res = openrouter.generate_completion(
        prompt=prompt_openrouter,
        system_instruction="Return strict JSON academic script evaluations based on visual handwritten answer crops.",
        image_bytes=or_primary,
        mime_type='image/png',
        extra_files=or_extra,
        timeout=60.0
    )
    or_elapsed = time.monotonic() - t0
    print(f"STATUS: SUCCESS | TIME: {or_elapsed:.2f}s")
    print(f"RAW_RESPONSE:\n{or_res}")
except Exception as e:
    or_elapsed = time.monotonic() - t0
    print(f"STATUS: ERROR | TIME: {or_elapsed:.2f}s")
    print(f"ERROR: {e}")
