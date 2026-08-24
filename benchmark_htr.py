#!/usr/bin/env python3
"""
HTR Benchmarking CLI for IntelliGrade.
Evaluates local Handwriting Text Recognition (HTR) model adapters (SimpleHTR, CRNN_LSTM, etc.)
against ground-truth dataset manifests to compute Character Error Rate (CER), Word Error Rate (WER),
latency, and memory footprint.

Standalone execution:
    python benchmark_htr.py --manifest dataset_manifest.json --output htr_benchmark_report.json
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple

# Attempt to import HTRResult and BaseHandwritingRecognizer from mainproject package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mainproject'))

try:
    from core.ai_engine.ocr.htr_interfaces import HTRResult, BaseHandwritingRecognizer
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mainproject', 'core', 'ai_engine', 'ocr'))
    from htr_interfaces import HTRResult, BaseHandwritingRecognizer


# ==========================================
# 1. Metric Calculation Utilities (CER & WER)
# ==========================================

def levenshtein_distance(seq1: list, seq2: list) -> int:
    """
    Computes Levenshtein edit distance between two sequence lists (characters or words).
    Uses `editdistance` package if installed; otherwise falls back to dynamic programming.
    """
    try:
        import editdistance
        return editdistance.eval(seq1, seq2)
    except ImportError:
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
        return dp[m][n]


def calculate_cer(reference: str, hypothesis: str) -> float:
    """
    Calculates Character Error Rate (CER):
    CER = LevenshteinDistance(ref_chars, hyp_chars) / len(ref_chars)
    """
    ref_chars = list(reference.strip())
    hyp_chars = list(hypothesis.strip())
    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0
    dist = levenshtein_distance(ref_chars, hyp_chars)
    return round(dist / float(len(ref_chars)), 4)


def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Calculates Word Error Rate (WER):
    WER = LevenshteinDistance(ref_words, hyp_words) / len(ref_words)
    """
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    dist = levenshtein_distance(ref_words, hyp_words)
    return round(dist / float(len(ref_words)), 4)


def get_current_ram_mb() -> float:
    """Helper to return current process resident set size (RAM) in Megabytes."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return round(process.memory_info().rss / (1024.0 * 1024.0), 2)
    except ImportError:
        try:
            import resource
            return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 2)
        except Exception:
            return 0.0


# ==========================================
# 2. Mock Adapter (for testing CLI harness)
# ==========================================

class DummyHTRAdapter(BaseHandwritingRecognizer):
    """Fallback dummy adapter to test benchmarking CLI prior to model integration."""

    def initialize(self) -> bool:
        time.sleep(0.05)
        self.is_initialized = True
        return True

    def predict_crop(self, image_input: Any) -> HTRResult:
        start = time.monotonic()
        gt = "Ans to the Q No 1"
        if isinstance(image_input, dict):
            gt = image_input.get('ground_truth', gt)
        latency = time.monotonic() - start
        return HTRResult(
            text=gt,
            confidence=0.95,
            engine_name="DummyHTRAdapter",
            latency_seconds=latency
        )

    def batch_predict(self, image_inputs: List[Any]) -> List[HTRResult]:
        return [self.predict_crop(img) for img in image_inputs]


# ==========================================
# 3. Benchmark Execution Harness
# ==========================================

def run_benchmark(
    manifest_path: str,
    adapters: Dict[str, BaseHandwritingRecognizer],
    output_report_path: str = "htr_benchmark_report.json"
) -> Dict[str, Any]:
    """
    Runs comprehensive benchmark suite across all registered HTR adapters.
    Evaluates CER, WER, Latency, Throughput, and Memory Usage.
    Saves final evaluation results to `output_report_path`.
    """
    samples = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                samples = json.load(f)
            print(f"[BENCHMARK] Loaded {len(samples)} samples from manifest '{manifest_path}'.")
        except Exception as e:
            print(f"[BENCHMARK WARNING] Error reading manifest '{manifest_path}': {e}. Using dummy sample.")
    
    if not samples:
        print("[BENCHMARK] Using synthetic benchmark manifest dataset...")
        samples = [
            {"image_path": "crop_q1.png", "ground_truth": "Ans to the Q No 1"},
            {"image_path": "crop_q2.png", "ground_truth": "Answer to the question no. 2"},
            {"image_path": "crop_q3.png", "ground_truth": "Software Engineering Principles"},
            {"image_path": "crop_q4.png", "ground_truth": "Ans. to Q. 4(a)"},
            {"image_path": "crop_q5.png", "ground_truth": "Database Management Systems"},
        ]

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_samples": len(samples),
        "adapters_evaluated": {},
    }

    print("=" * 85)
    print(f"{'HTR MODEL BENCHMARK EVALUATION SUITE':^85}")
    print("=" * 85)

    for adapter_name, adapter in adapters.items():
        print(f"\n[EVALUATING ADAPTER]: {adapter_name}")
        ram_before = get_current_ram_mb()

        # Step 1: Benchmark Initialization
        init_start = time.monotonic()
        try:
            init_ok = adapter.initialize()
        except Exception as err:
            print(f"  [FAIL] Initialization Failed: {err}")
            continue

        init_latency = round(time.monotonic() - init_start, 4)
        ram_after = get_current_ram_mb()
        ram_delta = round(ram_after - ram_before, 2)
        print(f"  [OK] Initialization Complete: {init_latency}s | RAM Delta: {ram_delta} MB")

        sample_results = []
        total_cer = 0.0
        total_wer = 0.0
        total_latency = 0.0
        total_conf = 0.0

        # Step 2: Sequential Prediction & Error Rate Metric Calculation
        for idx, sample in enumerate(samples, start=1):
            img_input = sample.get('image_path') or sample
            gt_text = sample.get('ground_truth', '')

            s_start = time.monotonic()
            try:
                res = adapter.predict_crop(sample)
            except Exception as exc:
                res = HTRResult(
                    text="",
                    confidence=0.0,
                    engine_name=adapter_name,
                    latency_seconds=round(time.monotonic() - s_start, 4),
                    raw_metadata={"error": str(exc)}
                )

            cer = calculate_cer(gt_text, res.text)
            wer = calculate_wer(gt_text, res.text)

            total_cer += cer
            total_wer += wer
            total_latency += res.latency_seconds
            total_conf += res.confidence

            sample_results.append({
                "sample_index": idx,
                "image_path": sample.get('image_path', f"crop_{idx}.png"),
                "ground_truth": gt_text,
                "predicted_text": res.text,
                "confidence": res.confidence,
                "cer": cer,
                "wer": wer,
                "latency_seconds": round(res.latency_seconds, 4)
            })

        sample_count = max(1, len(samples))
        avg_cer = round(total_cer / float(sample_count), 4)
        avg_wer = round(total_wer / float(sample_count), 4)
        avg_latency_ms = round((total_latency / float(sample_count)) * 1000.0, 2)
        avg_conf = round(total_conf / float(sample_count), 4)
        throughput_fps = round(float(sample_count) / max(0.001, total_latency), 2)

        adapter_metrics = {
            "engine_name": adapter_name,
            "init_latency_seconds": init_latency,
            "ram_delta_mb": ram_delta,
            "avg_cer": avg_cer,
            "avg_wer": avg_wer,
            "accuracy_cer_pct": round((1.0 - avg_cer) * 100.0, 2),
            "accuracy_wer_pct": round((1.0 - avg_wer) * 100.0, 2),
            "avg_confidence": avg_conf,
            "avg_latency_ms": avg_latency_ms,
            "throughput_samples_per_sec": throughput_fps,
            "sample_details": sample_results
        }

        report["adapters_evaluated"][adapter_name] = adapter_metrics

        print(f"  --> Average CER: {avg_cer:.4f} (Accuracy: {(1.0-avg_cer)*100.0:.2f}%)")
        print(f"  --> Average WER: {avg_wer:.4f} (Accuracy: {(1.0-avg_wer)*100.0:.2f}%)")
        print(f"  --> Avg Latency: {avg_latency_ms} ms/crop | Throughput: {throughput_fps} crops/sec")

    # Save detailed JSON report
    try:
        with open(output_report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print("\n" + "=" * 85)
        print(f"[BENCHMARK REPORT SAVED] Detailed metrics written to '{output_report_path}'.")
        print("=" * 85)
    except Exception as err:
        print(f"[BENCHMARK REPORT ERROR] Failed to save report to '{output_report_path}': {err}")

    return report


# ==========================================
# 4. Command Line Interface Entry Point
# ==========================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="IntelliGrade Local HTR Benchmarking Suite")
    parser.add_argument('--manifest', type=str, default="htr_manifest.json", help="Path to ground truth JSON manifest")
    parser.add_argument('--output', type=str, default="htr_benchmark_report.json", help="Path to output JSON report")
    parser.add_argument('--device', type=str, default="cpu", help="Compute device (cpu or cuda)")
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Dynamic deep model path resolution for CRNN_LSTM model weights via os.walk
    crnn_search_dir = os.path.join(base_dir, "OCR and HTR", "Handwriting_Recognition_CRNN_LSTM-main")
    crnn_model_path = None

    if os.path.exists(crnn_search_dir):
        for root, dirs, files in os.walk(crnn_search_dir):
            for f in files:
                if f.lower().endswith(('.hdf5', '.h5')):
                    crnn_model_path = os.path.abspath(os.path.join(root, f))
                    break
            if crnn_model_path:
                break

    # Fallback: wider os.walk search across the entire "OCR and HTR" folder
    if not crnn_model_path:
        wide_ocr_dir = os.path.join(base_dir, "OCR and HTR")
        if os.path.exists(wide_ocr_dir):
            for root, dirs, files in os.walk(wide_ocr_dir):
                for f in files:
                    if f.lower().endswith(('.hdf5', '.h5')):
                        crnn_model_path = os.path.abspath(os.path.join(root, f))
                        break
                if crnn_model_path:
                    break

    # Default fallback path if weight file is not yet downloaded
    if not crnn_model_path:
        crnn_model_path = os.path.join(base_dir, "models", "crnn_lstm.h5")

    print(f"[DEBUG] Final CRNN Model Path: {crnn_model_path}")



    # Dynamic model path resolution for SimpleHTR repo/model directory
    simple_htr_candidates = [
        os.path.join(base_dir, "OCR and HTR", "SimpleHTR-master", "SimpleHTR-master", "model"),
        os.path.join(base_dir, "OCR and HTR", "SimpleHTR-master", "SimpleHTR-master"),
        os.path.join(base_dir, "OCR and HTR", "SimpleHTR-master", "model"),
        os.path.join(base_dir, "OCR and HTR", "SimpleHTR-master"),
        os.path.join(base_dir, "models", "simple_htr"),
    ]
    simple_htr_model_path = next((p for p in simple_htr_candidates if os.path.exists(p)), simple_htr_candidates[0])

    # Active adapters dictionary
    active_adapters: Dict[str, BaseHandwritingRecognizer] = {}

    # Register default fallback Dummy Adapter for verification
    active_adapters["DummyHTRAdapter"] = DummyHTRAdapter(device=args.device)

    # Register CRNN_LSTM Adapter
    try:
        from core.ai_engine.ocr.adapters import CRNNLSTMAdapter
        active_adapters["CRNN_LSTM"] = CRNNLSTMAdapter(
            model_path=crnn_model_path,
            device=args.device
        )
        print(f"[BENCHMARK] Registered CRNN_LSTM adapter with model path: '{crnn_model_path}'")
    except Exception as e:
        print(f"[INFO] CRNNLSTMAdapter load info: {e}")

    # Register SimpleHTR Adapter
    try:
        from core.ai_engine.ocr.adapters import SimpleHTRAdapter
        active_adapters["SimpleHTR"] = SimpleHTRAdapter(
            model_path=simple_htr_model_path,
            device=args.device
        )
        print(f"[BENCHMARK] Registered SimpleHTR adapter with model path: '{simple_htr_model_path}'")
    except Exception as e:
        print(f"[INFO] SimpleHTRAdapter load info: {e}")

    run_benchmark(
        manifest_path=args.manifest,
        adapters=active_adapters,
        output_report_path=args.output
    )

