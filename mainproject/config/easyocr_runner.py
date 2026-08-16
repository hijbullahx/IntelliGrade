"""
Isolated EasyOCR Subprocess Runner.
Executes EasyOCR in an independent Python process so any PyTorch/NNPACK SIGILL or memory fault
terminates only this worker process, protecting the parent Django/Passenger server.
"""

import sys
import os
import json
import argparse


def main():
    parser = argparse.ArgumentParser(description="Isolated EasyOCR Subprocess Runner")
    parser.add_argument("--image", type=str, help="Path to input image file", required=False)
    parser.add_argument("--gpu", type=str, default="auto", help="Use GPU (True/False/auto)")
    parser.add_argument("--threads", type=int, default=4, help="CPU threads for PyTorch")
    parser.add_argument("--model-dir", type=str, default="", help="EasyOCR model storage directory")
    parser.add_argument("--user-dir", type=str, default="", help="EasyOCR user network directory")
    parser.add_argument("--languages", type=str, default="en", help="Comma-separated language codes")
    args = parser.parse_args()

    # Determine image path or read from stdin
    img_path = args.image
    temp_file_to_clean = None

    if not img_path or not os.path.exists(img_path):
        # Read raw bytes from sys.stdin.buffer and write to a temporary file
        import tempfile
        stdin_bytes = sys.stdin.buffer.read()
        if not stdin_bytes:
            print(json.dumps({"success": False, "error": "No image input provided", "text": "", "confidence": 0.0}))
            sys.exit(1)
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(stdin_bytes)
        tmp.flush()
        tmp.close()
        img_path = tmp.name
        temp_file_to_clean = tmp.name

    try:
        import torch
        import easyocr

        # Configure GPU / CPU threads
        if args.gpu.lower() == "true":
            use_gpu = True
        elif args.gpu.lower() == "false":
            use_gpu = False
        else:
            use_gpu = bool(torch.cuda.is_available())

        if not use_gpu:
            try:
                torch.set_num_threads(max(1, args.threads))
                torch.set_num_interop_threads(1)
            except Exception:
                pass

        lang_list = [l.strip() for l in args.languages.split(",") if l.strip()]
        model_storage = args.model_dir or os.path.expanduser("~/.EasyOCR/model")
        user_network = args.user_dir or os.path.expanduser("~/.EasyOCR/user_network")
        os.makedirs(model_storage, exist_ok=True)
        os.makedirs(user_network, exist_ok=True)

        reader = easyocr.Reader(
            lang_list,
            gpu=use_gpu,
            model_storage_directory=model_storage,
            user_network_directory=user_network,
            verbose=False
        )

        results = reader.readtext(img_path)

        lines = []
        scores = []
        boxes = []

        for item in results:
            # item: (bbox, text, confidence)
            bbox_pts, text_val, conf = item[0], item[1], item[2]
            if text_val and text_val.strip():
                lines.append(text_val.strip())
                scores.append(float(conf))
                # Bounding box as [x1, y1, x2, y2]
                xs = [p[0] for p in bbox_pts]
                ys = [p[1] for p in bbox_pts]
                boxes.append({
                    "bbox": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))],
                    "text": text_val.strip(),
                    "confidence": round(float(conf), 4)
                })

        extracted_text = "\n".join(lines).strip()
        avg_conf = round(sum(scores) / len(scores), 4) if scores else 0.0

        output = {
            "success": True,
            "text": extracted_text,
            "confidence": avg_conf,
            "boxes": boxes,
            "engine": "EasyOCR Subprocess"
        }
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        err_output = {
            "success": False,
            "error": str(e),
            "text": "",
            "confidence": 0.0,
            "engine": "EasyOCR Subprocess Failed"
        }
        print(json.dumps(err_output))
        sys.exit(1)
    finally:
        if temp_file_to_clean and os.path.exists(temp_file_to_clean):
            try:
                os.unlink(temp_file_to_clean)
            except Exception:
                pass


if __name__ == "__main__":
    main()
