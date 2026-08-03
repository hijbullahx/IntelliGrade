import os
import io
import re
import datetime
from typing import Dict, Any, List, Optional
from PIL import Image
from django.conf import settings
from core.models import AIConfiguration

try:
    import fitz
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False


class DocumentService:
    """
    Deterministic Document Service responsible for:
    1. 300 DPI High-Resolution PDF Page Rendering
    2. Embedded Image Stream Extraction & Bounding Box Cropping
    3. Multi-Engine OCR Text Extraction (PyMuPDF Native -> EasyOCR -> PyTesseract)
    4. Hierarchical Document Object Model (DOM) Tree Construction
    5. Debug Artifact Persistence
    """

    @staticmethod
    def extract_pdf_native_text(pdf_bytes: bytes) -> Dict[str, Any]:
        """Extracts text stream directly from PDF bytes using PyMuPDF."""
        if not FITZ_AVAILABLE or not pdf_bytes.startswith(b'%PDF'):
            return {"text": "", "confidence": 0.0, "engine": "None"}
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text_pages = []
            for page in doc:
                txt = page.get_text("text") or ""
                clean_lines = []
                for line in txt.split('\n'):
                    s = line.strip()
                    if s and not re.search(r'node\d{6,}', s) and not 'Skia/PDF' in s and not re.match(r'^\d+\s+\d+\s+R$', s):
                        clean_lines.append(s)
                if clean_lines:
                    text_pages.append("\n".join(clean_lines))
            extracted_text = "\n\n".join(text_pages).strip()
            confidence = 0.98 if len(extracted_text) > 100 else 0.50
            return {"text": extracted_text, "confidence": confidence, "engine": "PyMuPDF Native Extractor"}
        except Exception as e:
            print(f"[DOCUMENT SERVICE WARNING] PyMuPDF Native OCR Error: {e}")
            return {"text": "", "confidence": 0.0, "engine": "PyMuPDF Error"}

    @staticmethod
    def extract_easyocr_text(image_bytes: bytes) -> Dict[str, Any]:
        """Extracts text from image bytes using EasyOCR."""
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(image_bytes)
            lines = [res[1] for res in result]
            scores = [res[2] for res in result]
            extracted = "\n".join(lines).strip()
            conf = sum(scores) / len(scores) if scores else 0.85
            return {"text": extracted, "confidence": round(conf, 4), "engine": "EasyOCR"}
        except Exception:
            return {"text": "", "confidence": 0.0, "engine": "EasyOCR Unavailable"}

    @staticmethod
    def extract_tesseract_text(image_bytes: bytes) -> Dict[str, Any]:
        """Extracts text from image bytes using PyTesseract."""
        try:
            import pytesseract
            img = Image.open(io.BytesIO(image_bytes))
            extracted = pytesseract.image_to_string(img).strip()
            return {"text": extracted, "confidence": 0.80, "engine": "PyTesseract"}
        except Exception:
            return {"text": "", "confidence": 0.0, "engine": "PyTesseract Unavailable"}

    @classmethod
    def extract_deterministic_ocr(cls, doc_bytes: bytes, page_renders: List[bytes] = None, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Determines highest quality OCR text extraction across ALL 300 DPI rendered page images.
        Compares PyMuPDF Native Stream, EasyOCR per page, and PyTesseract per page.
        """
        import sys
        if FITZ_AVAILABLE:
            print(f"[DOCUMENT SERVICE SYSTEM] sys.executable: {sys.executable} | PyMuPDF version: {fitz.__version__}")
        else:
            print(f"[DOCUMENT SERVICE CRITICAL] sys.executable: {sys.executable} | PyMuPDF (fitz) NOT AVAILABLE!")

        candidates = []

        # 1. PyMuPDF Native Stream Text
        if FITZ_AVAILABLE and doc_bytes.startswith(b'%PDF'):
            native_res = cls.extract_pdf_native_text(doc_bytes)
            if len(native_res["text"]) > 30:
                candidates.append(native_res)

        # 2. Perform OCR across all 300 DPI rendered page images
        if page_renders:
            easy_text_pages = []
            tess_text_pages = []
            for p_idx, page_png in enumerate(page_renders):
                e_res = cls.extract_easyocr_text(page_png)
                if e_res["text"]:
                    easy_text_pages.append(e_res["text"])

                t_res = cls.extract_tesseract_text(page_png)
                if t_res["text"]:
                    tess_text_pages.append(t_res["text"])

            if easy_text_pages:
                full_easy = "\n\n".join(easy_text_pages).strip()
                if len(full_easy) > 30:
                    candidates.append({"text": full_easy, "confidence": 0.88, "engine": "EasyOCR Engine"})

            if tess_text_pages:
                full_tess = "\n\n".join(tess_text_pages).strip()
                if len(full_tess) > 30:
                    candidates.append({"text": full_tess, "confidence": 0.80, "engine": "PyTesseract Engine"})

        if not candidates:
            # Fallback to direct EasyOCR / PyTesseract attempt on doc_bytes if image
            if not doc_bytes.startswith(b'%PDF'):
                e_res = cls.extract_easyocr_text(doc_bytes)
                if e_res["text"]:
                    candidates.append(e_res)

        if not candidates:
            from core.ai_engine.parser.academic_parser import PipelineValidationError
            raise PipelineValidationError(
                "[STRICT OCR FAILURE] All OCR engines (PyMuPDF, EasyOCR, PyTesseract) returned 0 readable characters. "
                "The uploaded document appears to be unreadable or blurred. Pipeline halted before LLM execution."
            )

        best = max(candidates, key=lambda c: (len(c["text"]), c["confidence"]))
        best["char_count"] = len(best["text"])
        print(f"[DOCUMENT SERVICE OCR] Selected Engine: {best['engine']} | Text Length: {best['char_count']} chars | Confidence: {best['confidence']}")
        return best

    @classmethod
    def process_graphics_and_figures(cls, doc_bytes: bytes, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Extracts embedded raster/vector images, crops figures using bounding boxes,
        saves images to MEDIA_ROOT/exam_figures/%Y/%m/, generates thumbnails, and records coordinates.
        """
        now = datetime.datetime.now()
        subfolder = now.strftime('%Y/%m')
        save_dir = os.path.join(settings.MEDIA_ROOT, 'exam_figures', subfolder)
        thumb_dir = os.path.join(settings.MEDIA_ROOT, 'exam_figures', 'thumbs', subfolder)
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)

        extracted_figures = []
        page_renders = []
        dom_elements = []

        if FITZ_AVAILABLE and doc_bytes.startswith(b'%PDF'):
            doc = fitz.open(stream=doc_bytes, filetype="pdf")
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1

                # Render 300 DPI page image
                pix = page.get_pixmap(dpi=300)
                page_png = pix.tobytes("png")
                page_renders.append(page_png)

                # Extract embedded images
                img_list = page.get_images(full=True)
                for img_idx, img_info in enumerate(img_list):
                    xref = img_info[0]
                    base_img = doc.extract_image(xref)
                    image_bytes = base_img.get("image")
                    image_ext = base_img.get("ext", "png")

                    if image_bytes and len(image_bytes) > 500:
                        fig_filename = f"fig_p{page_num}_{img_idx+1}_{xref}.{image_ext}"
                        fig_rel_path = f"exam_figures/{subfolder}/{fig_filename}"
                        fig_full_path = os.path.join(save_dir, fig_filename)

                        with open(fig_full_path, "wb") as f:
                            f.write(image_bytes)

                        # Generate 300px Thumbnail
                        thumb_rel_path = f"exam_figures/thumbs/{subfolder}/{fig_filename}"
                        thumb_full_path = os.path.join(thumb_dir, fig_filename)
                        w, h = 300, 300
                        try:
                            im = Image.open(io.BytesIO(image_bytes))
                            w, h = im.width, im.height
                            im.thumbnail((300, 300))
                            im.save(thumb_full_path)
                        except Exception:
                            thumb_rel_path = fig_rel_path

                        rects = page.get_image_rects(xref)
                        bbox = [round(c, 2) for c in rects[0]] if rects else [0, 0, w, h]

                        fig_obj = {
                            "page_number": page_num,
                            "caption": f"Figure {img_idx+1} (Page {page_num})",
                            "image_path": fig_rel_path,
                            "image_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                            "thumbnail_url": f"{settings.MEDIA_URL}{thumb_rel_path}",
                            "bounding_box": bbox,
                            "width": w,
                            "height": h,
                            "bytes": image_bytes,
                            "mime_type": f"image/{image_ext}",
                            "display_order": img_idx + 1
                        }
                        extracted_figures.append(fig_obj)

                        dom_elements.append({
                            "type": "figure",
                            "page": page_num,
                            "caption": fig_obj["caption"],
                            "image_url": fig_obj["image_url"],
                            "bbox": bbox
                        })

                # 3. Fallback Bounding Box Drawing Cropping for Vector Diagrams / Matrices
                if not img_list:
                    drawings = page.get_drawings()
                    if drawings:
                        # Compute bounding box covering drawings
                        rect_boxes = [d["rect"] for d in drawings if "rect" in d]
                        if rect_boxes:
                            x0 = min(r[0] for r in rect_boxes)
                            y0 = min(r[1] for r in rect_boxes)
                            x1 = max(r[2] for r in rect_boxes)
                            y1 = max(r[3] for r in rect_boxes)
                            pw, ph = page.rect.width, page.rect.height
                            # Filter out small underline strokes AND full-page border boxes (>80% of page)
                            if (x1 - x0) > 40 and (y1 - y0) > 40 and not ((x1 - x0) > 0.85 * pw and (y1 - y0) > 0.85 * ph):
                                crop_rect = fitz.Rect(x0, y0, x1, y1)
                                crop_pix = page.get_pixmap(clip=crop_rect, dpi=300)
                                crop_bytes = crop_pix.tobytes("png")
                                
                                fig_filename = f"fig_crop_p{page_num}_1.png"
                                fig_rel_path = f"exam_figures/{subfolder}/{fig_filename}"
                                fig_full_path = os.path.join(save_dir, fig_filename)
                                with open(fig_full_path, "wb") as f:
                                    f.write(crop_bytes)

                                thumb_rel_path = f"exam_figures/thumbs/{subfolder}/{fig_filename}"
                                thumb_full_path = os.path.join(thumb_dir, fig_filename)
                                try:
                                    im = Image.open(io.BytesIO(crop_bytes))
                                    im.thumbnail((300, 300))
                                    im.save(thumb_full_path)
                                except Exception:
                                    thumb_rel_path = fig_rel_path

                                fig_obj = {
                                    "page_number": page_num,
                                    "caption": f"Diagram / Matrix (Page {page_num})",
                                    "image_path": fig_rel_path,
                                    "image_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                                    "thumbnail_url": f"{settings.MEDIA_URL}{thumb_rel_path}",
                                    "bounding_box": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                                    "width": crop_pix.width,
                                    "height": crop_pix.height,
                                    "bytes": crop_bytes,
                                    "mime_type": "image/png",
                                    "display_order": 1
                                }
                                extracted_figures.append(fig_obj)
                                dom_elements.append({
                                    "type": "figure",
                                    "page": page_num,
                                    "caption": fig_obj["caption"],
                                    "image_url": fig_obj["image_url"],
                                    "bbox": fig_obj["bounding_box"]
                                })

                # DOM Text Blocks
                text_blocks = page.get_text("blocks")
                for b in text_blocks:
                    if b[4].strip():
                        dom_elements.append({
                            "type": "text_block",
                            "page": page_num,
                            "text": b[4].strip(),
                            "bbox": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)]
                        })
        elif not doc_bytes.startswith(b'%PDF'):
            # Direct Image Upload (.jpg / .png) - Treat as Full Page Document
            page_renders.append(doc_bytes)
            all_contours = []
            try:
                import cv2
                import numpy as np
                img_np = np.frombuffer(doc_bytes, np.uint8)
                img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                h, w, _ = img_cv.shape

                # Convert to grayscale and Canny edge detection for graphical density
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                
                # Morphological close to group internal diagram graphics/lines
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
                closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
                contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                fig_idx = 0
                for c in contours:
                    cx, cy, cw, ch = cv2.boundingRect(c)
                    area = cw * ch

                    # Check 1: Reject Page Boundary (>90% page width AND >90% page height)
                    if cw >= 0.90 * w and ch >= 0.90 * h:
                        all_contours.append({
                            "type": "REJECT_PAGE_BORDER",
                            "bbox": [cx, cy, cx + cw, cy + ch],
                            "area": area,
                            "reason": "Page Boundary Contour (>90% page area)"
                        })
                        print(f"[LAYOUT ENGINE] Contour Rejected (PAGE BORDER): bbox=[{cx},{cy},{cw},{ch}], area={area}")
                        continue

                    # Check 2: Reject Small Text Lines / Small Strokes
                    if cw < 50 or ch < 50:
                        all_contours.append({
                            "type": "REJECT_TEXT_LINE",
                            "bbox": [cx, cy, cx + cw, cy + ch],
                            "area": area,
                            "reason": "Small Text Line / Stroke (<50px)"
                        })
                        continue

                    # Check 3: Graphical Edge Density Check (Distinguish text blocks from figures)
                    roi_edges = edges[cy:cy+ch, cx:cx+cw]
                    edge_density = np.sum(roi_edges > 0) / float(area)

                    if edge_density < 0.02:
                        all_contours.append({
                            "type": "REJECT_TEXT_LINE",
                            "bbox": [cx, cy, cx + cw, cy + ch],
                            "area": area,
                            "reason": f"Low Graphical Edge Density ({edge_density:.4f})"
                        })
                        print(f"[LAYOUT ENGINE] Contour Rejected (TEXT BLOCK): bbox=[{cx},{cy},{cw},{ch}], density={edge_density:.4f}")
                        continue

                    # Valid Internal Graphical Figure Contour
                    fig_idx += 1
                    all_contours.append({
                        "type": "VALID_FIGURE",
                        "bbox": [cx, cy, cx + cw, cy + ch],
                        "area": area,
                        "density": round(edge_density, 4)
                    })

                    cropped_cv = img_cv[cy:cy+ch, cx:cx+cw]
                    is_success, buffer = cv2.imencode(".png", cropped_cv)
                    if is_success:
                        crop_bytes = buffer.tobytes()
                        fig_filename = f"fig_img_p1_{fig_idx}.png"
                        fig_rel_path = f"exam_figures/{subfolder}/{fig_filename}"
                        fig_full_path = os.path.join(save_dir, fig_filename)
                        with open(fig_full_path, "wb") as f:
                            f.write(crop_bytes)

                        thumb_rel_path = f"exam_figures/thumbs/{subfolder}/{fig_filename}"
                        thumb_full_path = os.path.join(thumb_dir, fig_filename)
                        try:
                            im = Image.open(io.BytesIO(crop_bytes))
                            im.thumbnail((300, 300))
                            im.save(thumb_full_path)
                        except Exception:
                            thumb_rel_path = fig_rel_path

                        fig_obj = {
                            "page_number": 1,
                            "caption": f"Internal Figure {fig_idx}",
                            "image_path": fig_rel_path,
                            "image_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                            "thumbnail_url": f"{settings.MEDIA_URL}{thumb_rel_path}",
                            "bounding_box": [cx, cy, cx + cw, cy + ch],
                            "width": cw,
                            "height": ch,
                            "bytes": crop_bytes,
                            "mime_type": "image/png",
                            "display_order": fig_idx
                        }
                        extracted_figures.append(fig_obj)
                        dom_elements.append({
                            "type": "figure",
                            "page": 1,
                            "caption": fig_obj["caption"],
                            "image_url": fig_obj["image_url"],
                            "bbox": fig_obj["bounding_box"]
                        })
            except Exception as img_layout_err:
                print(f"[DOCUMENT SERVICE WARNING] Image layout analysis error: {img_layout_err}")

        return {
            "figures": extracted_figures,
            "page_renders": page_renders,
            "dom_elements": dom_elements,
            "all_contours": locals().get("all_contours", []),
            "total_pages": len(page_renders)
        }
