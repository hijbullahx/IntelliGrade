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
from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

# Load real Q4 crops
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

print(f"Loaded {len(crops)} real handwritten Q4 crops.")

# Decoded cv2 images
decoded_imgs = []
for c in crops:
    nparr = np.frombuffer(c['image_bytes'], np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    decoded_imgs.append({'page_number': c['page_number'], 'img': img})


# --- LAYOUT A: Vertical Stacking (900px target width) ---
def layout_a_vertical(images, target_w=900):
    composites = []
    groups = [images[0:2], images[2:4]]
    for idx, group in enumerate(groups, 1):
        parts = []
        for item in group:
            img = item['img']
            h, w = img.shape[:2]
            new_h = int(h * (target_w / float(w)))
            img_r = cv2.resize(img, (target_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            bar = np.full((35, target_w, 3), (230, 230, 230), dtype=np.uint8)
            cv2.putText(bar, f"--- Page {item['page_number']} ---", (20, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (40, 40, 40), 2)
            parts.extend([bar, img_r])
        comp = np.vstack(parts)
        _, buf = cv2.imencode('.png', comp)
        composites.append({'composite_id': f'comp_a_{idx}', 'bytes': buf.tobytes(), 'width': comp.shape[1], 'height': comp.shape[0]})
    return composites

# --- LAYOUT B1: Optimized Bounded Vertical (650px target width) ---
def layout_b1_bounded_vertical(images, target_w=650):
    composites = []
    groups = [images[0:2], images[2:4]]
    for idx, group in enumerate(groups, 1):
        parts = []
        for item in group:
            img = item['img']
            h, w = img.shape[:2]
            new_h = int(h * (target_w / float(w)))
            img_r = cv2.resize(img, (target_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            bar = np.full((30, target_w, 3), (235, 235, 235), dtype=np.uint8)
            cv2.putText(bar, f"--- Page {item['page_number']} ---", (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 2)
            parts.extend([bar, img_r])
        comp = np.vstack(parts)
        _, buf = cv2.imencode('.png', comp)
        composites.append({'composite_id': f'comp_b1_{idx}', 'bytes': buf.tobytes(), 'width': comp.shape[1], 'height': comp.shape[0]})
    return composites

# --- LAYOUT B2: Two-Column Side-by-Side Tiling ---
def layout_b2_twocolumn(images, target_h=1000):
    composites = []
    # Comp 1: Page 4 (left) & Page 6 (right)
    # Comp 2: Page 7 (left) & Page 8 (right)
    groups = [images[0:2], images[2:4]]
    for idx, group in enumerate(groups, 1):
        resized_items = []
        for item in group:
            img = item['img']
            h, w = img.shape[:2]
            new_w = int(w * (target_h / float(h)))
            img_r = cv2.resize(img, (new_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            
            # Header
            header = np.full((30, new_w, 3), (230, 230, 230), dtype=np.uint8)
            cv2.putText(header, f"Page {item['page_number']}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 2)
            col = np.vstack([header, img_r])
            resized_items.append(col)

        # Equalize heights if necessary
        max_h = max(c.shape[0] for c in resized_items)
        padded_cols = []
        for c in resized_items:
            ch, cw = c.shape[:2]
            if ch < max_h:
                pad = np.full((max_h - ch, cw, 3), (255, 255, 255), dtype=np.uint8)
                c = np.vstack([c, pad])
            padded_cols.append(c)

        # Add vertical separator line between columns
        sep = np.full((max_h, 15, 3), (200, 200, 200), dtype=np.uint8)
        comp = np.hstack([padded_cols[0], sep, padded_cols[1]])
        _, buf = cv2.imencode('.png', comp)
        composites.append({'composite_id': f'comp_b2_{idx}', 'bytes': buf.tobytes(), 'width': comp.shape[1], 'height': comp.shape[0]})
    return composites


comps_a = layout_a_vertical(decoded_imgs, target_w=900)
comps_b1 = layout_b1_bounded_vertical(decoded_imgs, target_w=650)
comps_b2 = layout_b2_twocolumn(decoded_imgs, target_h=1000)

print("\n--- LAYOUT SUMMARY ---")
print("Layout A (Vertical 900px):")
for i, c in enumerate(comps_a, 1):
    print(f"  Comp #{i}: {c['width']}x{c['height']} px | {len(c['bytes'])} bytes")

print("Layout B1 (Bounded Vertical 650px):")
for i, c in enumerate(comps_b1, 1):
    print(f"  Comp #{i}: {c['width']}x{c['height']} px | {len(c['bytes'])} bytes")

print("Layout B2 (Two-Column Side-by-Side):")
for i, c in enumerate(comps_b2, 1):
    print(f"  Comp #{i}: {c['width']}x{c['height']} px | {len(c['bytes'])} bytes")

# Prompt
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

prompt = f"""
Evaluate the following student answer for an academic examination question:

Question: {question_text}
Maximum Marks: {max_marks}
Rubric Criteria: {rubric_criteria}
Ideal Answer: {ideal_answer}

Examine the attached visual handwritten answer composite images.

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

groq = GroqProvider(api_key=os.environ.get('GROQ_API_KEY', ''))

def evaluate_layout(layout_name, composites_list):
    print(f"\n" + "="*50)
    print(f"=== TESTING LAYOUT: {layout_name} ===")
    print("="*50)

    # Sleep 35 seconds to ensure Groq TPM counter is completely zeroed
    print("Sleeping 35s to reset Groq TPM quota...")
    time.sleep(35)

    primary = composites_list[0]['bytes']
    extra = [{'bytes': c['bytes'], 'mime_type': 'image/png'} for c in composites_list[1:]]

    t0 = time.monotonic()
    try:
        res = groq.generate_completion(
            prompt=prompt,
            system_instruction="Return strict JSON academic script evaluations based on visual handwritten answer crops.",
            image_bytes=primary,
            mime_type='image/png',
            extra_files=extra,
            timeout=30.0
        )
        elapsed = time.monotonic() - t0
        print(f"STATUS: SUCCESS | LATENCY: {elapsed:.2f}s")
        print(f"RESPONSE:\n{res}")
        return {'status': 'SUCCESS', 'latency': elapsed, 'raw': res}
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"STATUS: ERROR | LATENCY: {elapsed:.2f}s")
        print(f"ERROR: {e}")
        return {'status': 'ERROR', 'latency': elapsed, 'error': str(e)}

# Execute layout tests sequentially
res_b1 = evaluate_layout("Layout B1 (Bounded Vertical 650px)", comps_b1)
res_b2 = evaluate_layout("Layout B2 (Two-Column Side-by-Side)", comps_b2)
res_a = evaluate_layout("Layout A (Vertical Baseline 900px)", comps_a)
