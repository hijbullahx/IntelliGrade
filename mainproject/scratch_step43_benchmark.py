import os
import sys
import time
import json
import re

# Ensure Django environment is configured
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')
import django
django.setup()

from core.ai_engine.providers.groq import GroqProvider
from core.ai_engine.providers.gemini import GeminiProvider
from core.ai_engine.providers.openrouter import OpenRouterProvider
from core.ai_engine.evaluation.answer_crop_service import AnswerCropService

# Load real Q4 mapping & crops from eval_89 trace
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

primary_crop_bytes = crops[0]['image_bytes']
extra_crops = [{'bytes': c['image_bytes'], 'mime_type': 'image/png'} for c in crops[1:]]

# A. GROQ BENCHMARK
print("\n" + "="*50)
print("=== A. GROQ BENCHMARK (qwen/qwen3.6-27b) ===")
print("="*50)
groq = GroqProvider(api_key=os.environ.get('GROQ_API_KEY', ''))
groq_t0 = time.monotonic()
try:
    groq_res = groq.generate_completion(
        prompt=prompt,
        system_instruction="Return strict JSON academic script evaluations.",
        image_bytes=primary_crop_bytes,
        mime_type='image/png',
        extra_files=extra_crops
    )
    groq_elapsed = time.monotonic() - groq_t0
    print(f"STATUS: SUCCESS | TIME: {groq_elapsed:.2f}s")
    print(f"RAW_RESPONSE:\n{groq_res}")
except Exception as e:
    groq_elapsed = time.monotonic() - groq_t0
    print(f"STATUS: BLOCKED / ERROR | TIME: {groq_elapsed:.2f}s")
    print(f"ERROR: {e}")

# B. GEMINI BENCHMARK
print("\n" + "="*50)
print("=== B. GEMINI BENCHMARK (gemini-flash-latest) ===")
print("="*50)
gemini = GeminiProvider(api_key=os.environ.get('GEMINI_API_KEY', ''), model_name='gemini-flash-latest')
gemini_t0 = time.monotonic()
try:
    gemini_res = gemini.generate_completion(
        prompt=prompt,
        system_instruction="Return strict JSON academic script evaluations based on visual handwritten answer crops.",
        image_bytes=primary_crop_bytes,
        mime_type='image/png',
        extra_files=extra_crops,
        timeout=60.0
    )
    gemini_elapsed = time.monotonic() - gemini_t0
    print(f"STATUS: SUCCESS | TIME: {gemini_elapsed:.2f}s")
    print(f"RAW_RESPONSE:\n{gemini_res}")
except Exception as e:
    gemini_elapsed = time.monotonic() - gemini_t0
    print(f"STATUS: ERROR | TIME: {gemini_elapsed:.2f}s")
    print(f"ERROR: {e}")

# C. OPENROUTER BENCHMARK
print("\n" + "="*50)
print("=== C. OPENROUTER BENCHMARK (openrouter/free) ===")
print("="*50)
openrouter = OpenRouterProvider(api_key=os.environ.get('OPENROUTER_API_KEY', ''), model_name='openrouter/free')
openrouter_t0 = time.monotonic()
try:
    openrouter_res = openrouter.generate_completion(
        prompt=prompt,
        system_instruction="Return strict JSON academic script evaluations based on visual handwritten answer crops.",
        image_bytes=primary_crop_bytes,
        mime_type='image/png',
        extra_files=extra_crops,
        timeout=60.0
    )
    openrouter_elapsed = time.monotonic() - openrouter_t0
    print(f"STATUS: SUCCESS | TIME: {openrouter_elapsed:.2f}s")
    print(f"RAW_RESPONSE:\n{openrouter_res}")
except Exception as e:
    openrouter_elapsed = time.monotonic() - openrouter_t0
    print(f"STATUS: ERROR | TIME: {openrouter_elapsed:.2f}s")
    print(f"ERROR: {e}")
