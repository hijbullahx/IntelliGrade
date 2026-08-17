import os
import io
import re
import datetime
import time
from typing import Dict, Any, List, Optional
from PIL import Image
from django.conf import settings

def get_rss_mb() -> float:
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except ImportError:
        return 0.0
from core.models import AIConfiguration
from config.paths import get_trace_dir
from config.ocr_config import get_ocr_reader, prepare_easyocr_image, is_easyocr_enabled

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
    3. Multi-Engine OCR Text Extraction (PyMuPDF Native -> PyTesseract -> EasyOCR)
    4. Hierarchical Document Object Model (DOM) Tree Construction
    5. Debug Artifact Persistence
    """

    @staticmethod
    def extract_pdf_native_text(pdf_bytes: bytes) -> Dict[str, Any]:
        """Extracts text stream directly from PDF bytes using PyMuPDF."""
        if not FITZ_AVAILABLE or not pdf_bytes.startswith(b'%PDF'):
            return {"text": "", "confidence": 0.0, "engine": "None"}
        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
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
                confidence = 0.98 if len(extracted_text) >= 50 else 0.50
                return {"text": extracted_text, "confidence": confidence, "engine": "PyMuPDF Native Extractor"}
        except Exception as e:
            print(f"[DOCUMENT SERVICE WARNING] PyMuPDF Native OCR Error: {e}")
            return {"text": "", "confidence": 0.0, "engine": "PyMuPDF Error"}

    @staticmethod
    def extract_easyocr_text(image_bytes: bytes) -> Dict[str, Any]:
        """Extracts text from image bytes using EasyOCR if explicitly enabled."""
        if not is_easyocr_enabled():
            return {"text": "", "confidence": 0.0, "engine": "EasyOCR Disabled"}
        try:
            reader = get_ocr_reader()
            if reader is None:
                return {"text": "", "confidence": 0.0, "engine": "EasyOCR Unavailable"}
            working_image, ocr_meta = prepare_easyocr_image(image_bytes)
            print(
                f"[DOCUMENT SERVICE EASYOCR] original={ocr_meta['original_size'][0]}x{ocr_meta['original_size'][1]} | "
                f"working={ocr_meta['working_size'][0]}x{ocr_meta['working_size'][1]} | resized={ocr_meta['resized']} | "
                f"rss_mb={get_rss_mb():.1f}"
            )
            started = time.monotonic()
            result = reader.readtext(working_image)
            lines = [res[1] for res in result]
            scores = [res[2] for res in result]
            extracted = "\n".join(lines).strip()
            conf = sum(scores) / len(scores) if scores else 0.85
            print(
                f"[DOCUMENT SERVICE EASYOCR SUCCESS] text_len={len(extracted)} | confidence={round(conf, 4)} | "
                f"elapsed_s={time.monotonic() - started:.2f}"
            )
            return {"text": extracted, "confidence": round(conf, 4), "engine": "EasyOCR"}
        except Exception:
            return {"text": "", "confidence": 0.0, "engine": "EasyOCR Unavailable"}

    @staticmethod
    def extract_tesseract_text(image_bytes: bytes) -> Dict[str, Any]:
        """Extracts text from image bytes using PyTesseract CPU OCR."""
        try:
            import pytesseract
            img = Image.open(io.BytesIO(image_bytes))
            extracted = pytesseract.image_to_string(img).strip()
            confidence = 0.85 if len(extracted) >= 50 else 0.40
            return {"text": extracted, "confidence": confidence, "engine": "PyTesseract"}
        except Exception:
            return {"text": "", "confidence": 0.0, "engine": "PyTesseract Unavailable"}

    @classmethod
    def extract_deterministic_ocr(cls, doc_bytes: bytes, page_renders: List[bytes] = None, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Determines highest quality OCR text extraction across ALL 300 DPI rendered page images.
        Hierarchy:
        1. PyMuPDF Native Stream Text (fast, accurate for digital PDFs, 0 CPU overhead)
        2. PyTesseract CPU OCR (safe, deterministic)
        3. EasyOCR (only if explicitly enabled via EASYOCR_ENABLED=True)
        """
        import sys
        if FITZ_AVAILABLE:
            print(f"[DOCUMENT SERVICE SYSTEM] sys.executable: {sys.executable} | PyMuPDF version: {fitz.__version__}")
        else:
            print(f"[DOCUMENT SERVICE CRITICAL] sys.executable: {sys.executable} | PyMuPDF (fitz) NOT AVAILABLE!")

        candidates = []

        # 1. PyMuPDF Native Stream Text (for digital PDFs)
        if FITZ_AVAILABLE and doc_bytes.startswith(b'%PDF'):
            native_res = cls.extract_pdf_native_text(doc_bytes)
            if len(native_res["text"]) >= 50:
                candidates.append(native_res)

        # 2. Perform OCR across rendered page images if native text is not present or insufficient
        has_sufficient_native = any(c.get("confidence", 0) >= 0.50 and len(c.get("text", "")) >= 50 for c in candidates)
        if page_renders and not has_sufficient_native:
            tess_text_pages = []
            for p_idx, page_png in enumerate(page_renders):
                t_res = cls.extract_tesseract_text(page_png)
                if t_res["text"]:
                    tess_text_pages.append(t_res["text"])

            if tess_text_pages:
                full_tess = "\n\n".join(tess_text_pages).strip()
                if len(full_tess) >= 50:
                    candidates.append({"text": full_tess, "confidence": 0.85, "engine": "PyTesseract Engine"})

            # Only attempt EasyOCR if enabled and PyTesseract was not sufficient
            if is_easyocr_enabled() and not any(len(c.get("text", "")) >= 50 for c in candidates):
                easy_text_pages = []
                for p_idx, page_png in enumerate(page_renders):
                    e_res = cls.extract_easyocr_text(page_png)
                    if e_res["text"]:
                        easy_text_pages.append(e_res["text"])

                if easy_text_pages:
                    full_easy = "\n\n".join(easy_text_pages).strip()
                    if len(full_easy) >= 50:
                        candidates.append({"text": full_easy, "confidence": 0.88, "engine": "EasyOCR Engine"})

        if not candidates and not doc_bytes.startswith(b'%PDF'):
            # Direct image file upload (.png, .jpg)
            t_res = cls.extract_tesseract_text(doc_bytes)
            if len(t_res["text"]) >= 50:
                candidates.append(t_res)
            elif is_easyocr_enabled():
                e_res = cls.extract_easyocr_text(doc_bytes)
                if len(e_res["text"]) >= 50:
                    candidates.append(e_res)

        if not candidates:
            from core.ai_engine.parser.academic_parser import PipelineValidationError
            raise PipelineValidationError(
                "[STRICT OCR FAILURE] All available OCR engines returned insufficient readable characters (< 50). "
                "The uploaded document appears to be unreadable or empty. Pipeline halted before LLM execution."
            )

        best = max(candidates, key=lambda c: (len(c["text"]), c["confidence"]))
        best["char_count"] = len(best["text"])
        print(f"[DOCUMENT SERVICE OCR] Selected Engine: {best['engine']} | Text Length: {best['char_count']} chars | Confidence: {best['confidence']}")

        if best["char_count"] < 50:
            from core.ai_engine.parser.academic_parser import PipelineValidationError
            raise PipelineValidationError(
                f"[STRICT OCR FAILURE] Extracted text length ({best['char_count']} chars) is below the minimum threshold (50 chars)."
            )

        # Add a warning for potentially large payloads that might cause timeouts
        if best["char_count"] > 30000:
            print(f"[DOCUMENT SERVICE WARNING] Large OCR payload detected ({best['char_count']} chars). "
                  "This may increase AI provider processing time and risk a timeout.")

        return best

    @classmethod
    def process_graphics_and_figures(cls, doc_bytes: bytes, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Extracts embedded raster/vector images, crops figures using bounding boxes,
        saves images to MEDIA_ROOT/exam_figures/%Y/%m/, generates thumbnails, and records coordinates.
        """
        import cv2
        import numpy as np
        from django.utils import timezone

        now = timezone.now()
        subfolder = now.strftime('%Y/%m')
        save_dir = os.path.join(settings.MEDIA_ROOT, 'exam_figures', subfolder)
        thumb_dir = os.path.join(settings.MEDIA_ROOT, 'exam_figures', 'thumbs', subfolder)
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)

        extracted_figures = []
        extracted_tables = []
        extracted_formulas = []
        page_renders = []
        dom_elements = []
        all_contours = []

        if FITZ_AVAILABLE and doc_bytes.startswith(b'%PDF'):
            # PDF Processing Pipeline
            try:
                with fitz.open(stream=doc_bytes, filetype="pdf") as doc:
                    for page_num, page in enumerate(doc, start=1):
                        pix = page.get_pixmap(dpi=300)
                        p_bytes = pix.tobytes("png")
                        page_renders.append(p_bytes)

                    # 1. Detect Tables & Grids in Page Image
                    page_tables = cls.detect_tables_and_grids(p_bytes, page_num=page_num, save_dir=save_dir, subfolder=subfolder)
                    for tbl in page_tables:
                        extracted_tables.append(tbl)
                        dom_elements.append({
                            "type": "table",
                            "page": page_num,
                            "caption": tbl["caption"],
                            "bbox": tbl["bounding_box"]
                        })

                    # 2. Extract Embedded Image Streams
                    img_list = page.get_images()
                    for img_idx, img_info in enumerate(img_list):
                        xref = img_info[0]
                        base_image = doc.extract_image(xref)
                        if base_image:
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]
                            fig_filename = f"fig_pdf_p{page_num}_{img_idx+1}.{image_ext}"
                            fig_rel_path = f"exam_figures/{subfolder}/{fig_filename}"
                            fig_full_path = os.path.join(save_dir, fig_filename)
                            with open(fig_full_path, "wb") as f:
                                f.write(image_bytes)

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

                    # 3. Vector Drawing Box Cropping for Vector Diagrams / Matrices
                    if not img_list and not page_tables:
                        drawings = page.get_drawings()
                        if drawings:
                            rect_boxes = [d["rect"] for d in drawings if "rect" in d]
                            if rect_boxes:
                                x0 = min(r[0] for r in rect_boxes)
                                y0 = min(r[1] for r in rect_boxes)
                                x1 = max(r[2] for r in rect_boxes)
                                y1 = max(r[3] for r in rect_boxes)
                                pw, ph = page.rect.width, page.rect.height
                                if (x1 - x0) > 40 and (y1 - y0) > 40 and not ((x1 - x0) > 0.85 * pw and (y1 - y0) > 0.85 * ph):
                                    crop_rect = fitz.Rect(x0, y0, x1, y1)
                                    crop_pix = page.get_pixmap(clip=crop_rect, dpi=300)
                                    crop_bytes = crop_pix.tobytes("png")

                                    import cv2
                                    import numpy as np
                                    crop_np = np.frombuffer(crop_bytes, np.uint8)
                                    crop_cv = cv2.imdecode(crop_np, cv2.IMREAD_COLOR)

                                    table_struct = cls.extract_table_structure_and_cells(crop_cv, page_num=page_num, tbl_idx=1)
                                    if table_struct and table_struct.get("element_type") in ["MATRIX", "TABLE", "GRID"]:
                                        tbl_filename = f"table_crop_p{page_num}_1.png"
                                        tbl_rel_path = f"exam_tables/{subfolder}/{tbl_filename}" if subfolder else f"exam_tables/{tbl_filename}"
                                        tbl_full_path = os.path.join(save_dir, tbl_filename)
                                        os.makedirs(os.path.dirname(tbl_full_path), exist_ok=True)
                                        with open(tbl_full_path, "wb") as f:
                                            f.write(crop_bytes)

                                        tbl_obj = {
                                            "type": table_struct["classification"].lower(),
                                            "element_type": table_struct["element_type"],
                                            "page_number": page_num,
                                            "caption": f"Matrix (Page {page_num})" if table_struct["element_type"] == "MATRIX" else f"Table / Grid (Page {page_num})",
                                            "image_path": tbl_rel_path,
                                            "image_url": f"{settings.MEDIA_URL}{tbl_rel_path}",
                                            "bounding_box": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                                            "rows": table_struct["rows"],
                                            "columns": table_struct["cols"],
                                            "cell_json": table_struct["cell_json"],
                                            "bytes": crop_bytes,
                                            "is_matrix": (table_struct["element_type"] == "MATRIX"),
                                            "display_order": 1
                                        }
                                        extracted_tables.append(tbl_obj)
                                        dom_elements.append({
                                            "type": "table",
                                            "page": page_num,
                                            "caption": tbl_obj["caption"],
                                            "image_url": tbl_obj["image_url"],
                                            "bbox": tbl_obj["bounding_box"]
                                        })
                                    else:
                                        fig_filename = f"fig_crop_p{page_num}_1.png"
                                        fig_rel_path = f"exam_figures/{subfolder}/{fig_filename}"
                                        fig_full_path = os.path.join(save_dir, fig_filename)
                                        os.makedirs(os.path.dirname(fig_full_path), exist_ok=True)
                                        with open(fig_full_path, "wb") as f:
                                            f.write(crop_bytes)

                                        fig_obj = {
                                            "page_number": page_num,
                                            "caption": f"Figure (Page {page_num})",
                                            "image_path": fig_rel_path,
                                            "image_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                                            "bounding_box": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
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
            except Exception as pdf_err:
                print(f"[DOCUMENT SERVICE WARNING] PDF graphics extraction error: {pdf_err}")

        elif not doc_bytes.startswith(b'%PDF'):
            # Direct Image Upload (.jpg / .png) - Treat as Full Page Document Canvas
            page_renders.append(doc_bytes)
            try:
                import cv2
                import numpy as np
                img_np = np.frombuffer(doc_bytes, np.uint8)
                img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                h, w, _ = img_cv.shape

                # 1. Detect Tables & Grids in Image
                img_tables = cls.detect_tables_and_grids(doc_bytes, page_num=1, save_dir=save_dir, subfolder=subfolder)
                table_bboxes = []
                for tbl in img_tables:
                    extracted_tables.append(tbl)
                    table_bboxes.append(tbl["bounding_box"])
                    all_contours.append({
                        "type": "REJECT_TABLE",
                        "bbox": tbl["bounding_box"],
                        "area": (tbl["bounding_box"][2]-tbl["bounding_box"][0]) * (tbl["bounding_box"][3]-tbl["bounding_box"][1]),
                        "reason": "Classified as Structured Table / Matrix"
                    })
                    dom_elements.append({
                        "type": "table",
                        "page": 1,
                        "caption": tbl["caption"],
                        "bbox": tbl["bounding_box"]
                    })

                # 2. Contour Analysis for Internal Figures & Page Border Rejection
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                
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
                            "reason": "Document Boundary (>90% page area)"
                        })
                        print(f"[LAYOUT ENGINE] Contour Rejected (DOCUMENT_BOUNDARY): bbox=[{cx},{cy},{cw},{ch}], area={area}")
                        continue

                    # Check 2: Reject small text lines / small noise
                    if cw < 50 or ch < 50:
                        all_contours.append({
                            "type": "REJECT_TEXT_LINE",
                            "bbox": [cx, cy, cx + cw, cy + ch],
                            "area": area,
                            "reason": "Small Text Line / Stroke (<50px)"
                        })
                        continue

                    # Check 3: Ignore region if it overlaps significantly with a detected table
                    is_table_overlap = False
                    for t_box in table_bboxes:
                        tx0, ty0, tx1, ty1 = t_box
                        if not (cx + cw < tx0 or cx > tx1 or cy + ch < ty0 or cy > ty1):
                            is_table_overlap = True
                            break
                    if is_table_overlap:
                        continue

                    # Check 4: Edge density check to distinguish text paragraphs from figures
                    roi_edges = edges[cy:cy+ch, cx:cx+cw]
                    edge_density = np.sum(roi_edges > 0) / float(area)

                    if edge_density < 0.02:
                        all_contours.append({
                            "type": "REJECT_TEXT_LINE",
                            "bbox": [cx, cy, cx + cw, cy + ch],
                            "area": area,
                            "reason": f"Low Graphical Edge Density ({edge_density:.4f})"
                        })
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

        # Task: Execute TextMatrixDetector on rendered page images for borderless matrices
        text_matrix_tables = []
        for p_num, p_bytes in enumerate(page_renders, start=1):
            try:
                p_np = np.frombuffer(p_bytes, np.uint8)
                p_cv = cv2.imdecode(p_np, cv2.IMREAD_COLOR)
                tm_cands = cls.detect_text_matrices(p_cv, page_num=p_num, pdf_bytes=doc_bytes, save_dir=save_dir, subfolder=subfolder)
                text_matrix_tables.extend(tm_cands)
            except Exception as tm_err:
                print(f"[DOCUMENT SERVICE WARNING] TextMatrixDetector error on Page {p_num}: {tm_err}")

        # Candidate Union (FigureDetector + ContourTableDetector + TextMatrixDetector)
        union_candidates = []
        for fig in extracted_figures:
            fig["source"] = "figure"
            union_candidates.append(fig)
        for tbl in extracted_tables:
            tbl["source"] = "contour_table"
            union_candidates.append(tbl)
        for tmat in text_matrix_tables:
            tmat["source"] = "text_matrix"
            union_candidates.append(tmat)

        # Draw candidate_union_debug.png overlay with GREEN (contour), CYAN (text matrix), BLUE (figure)
        try:
            import cv2
            import numpy as np
            if page_renders:
                p1_np = np.frombuffer(page_renders[0], np.uint8)
                p1_cv = cv2.imdecode(p1_np, cv2.IMREAD_COLOR)
                union_img = p1_cv.copy()
                for c in union_candidates:
                    bx = c.get("bounding_box", [0, 0, 0, 0])
                    x0, y0, x1, y1 = int(bx[0]), int(bx[1]), int(bx[2]), int(bx[3])
                    src = c.get("source", "figure")
                    if src == "contour_table":
                        color = (0, 255, 0) # GREEN
                        label = "Contour Table"
                    elif src == "text_matrix":
                        color = (255, 255, 0) # CYAN
                        label = "Text Matrix"
                    else:
                        color = (255, 0, 0) # BLUE
                        label = "Figure"
                    cv2.rectangle(union_img, (x0, y0), (x1, y1), color, 3)
                    cv2.putText(union_img, label, (x0 + 5, max(20, y0 + 25)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                trace_dir = get_trace_dir()
                cv2.imwrite(os.path.join(trace_dir, "candidate_union_debug.png"), union_img)
        except Exception as union_err:
            print(f"[DOCUMENT SERVICE WARNING] Candidate union debug image error: {union_err}")

        # Apply NMS deduplication pass on Candidate Union
        nms_res = cls.apply_nms_deduplication(union_candidates, iou_threshold=0.50)
        final_accepted = nms_res.get("accepted", [])

        final_figures = [c for c in final_accepted if c.get("source") == "figure"]
        final_tables = [c for c in final_accepted if c.get("source") in ["contour_table", "text_matrix"]]

        return {
            "figures": final_figures,
            "tables": final_tables,
            "formulas": extracted_formulas,
            "page_renders": page_renders,
            "dom_elements": dom_elements,
            "all_contours": all_contours,
            "total_pages": len(page_renders)
        }

    @classmethod
    def detect_text_matrices(cls, img_cv, page_num: int = 1, pdf_bytes: bytes = b"", save_dir: str = "", subfolder: str = "") -> List[Dict[str, Any]]:
        """
        TextMatrixDetector Pipeline:
        OCR page text lines -> Store bounding boxes -> Group adjacent lines
        -> Cluster by identical left margin & measure X alignment / row spacing
        -> Detect repeated columns (>= 3 rows, >= 3 columns, low variance)
        -> Create MATRIX candidate ROI.
        """
        import cv2
        import numpy as np
        import json
        import os
        import fitz
        from django.conf import settings

        candidates = []
        try:
            h, w, _ = img_cv.shape
            trace_dir = get_trace_dir()

            words = []
            # 1. Prefer PyMuPDF native words for digital PDFs (fast, zero OCR, zero NNPACK overhead)
            if pdf_bytes and FITZ_AVAILABLE:
                try:
                    with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf_doc:
                        if page_num <= len(pdf_doc):
                            page = pdf_doc[page_num - 1]
                            scale_x = w / float(page.rect.width) if page.rect.width > 0 else 1.0
                            scale_y = h / float(page.rect.height) if page.rect.height > 0 else 1.0
                            
                            for w_tuple in page.get_text("words"):
                                x0, y0, x1, y1, w_text = w_tuple[0], w_tuple[1], w_tuple[2], w_tuple[3], w_tuple[4]
                                if str(w_text).strip():
                                    wx1, wy1 = int(x0 * scale_x), int(y0 * scale_y)
                                    wx2, wy2 = int(x1 * scale_x), int(y1 * scale_y)
                                    words.append({
                                        "bbox": [wx1, wy1, wx2, wy2],
                                        "text": str(w_text).strip(),
                                        "xc": (wx1 + wx2) / 2.0,
                                        "yc": (wy1 + wy2) / 2.0
                                    })
                except Exception as fitz_err:
                    print(f"[TEXT MATRIX DETECTOR WARNING] PyMuPDF word extraction failed: {fitz_err}")

            # 2. Fallback to PyTesseract if not a digital PDF or no words found
            if not words:
                try:
                    import pytesseract
                    from PIL import Image as PILImg
                    pil_img = PILImg.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
                    data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                    n_boxes = len(data.get('text', []))
                    for i in range(n_boxes):
                        t_val = str(data['text'][i]).strip()
                        if t_val:
                            bx, by, bw, bh = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                            words.append({
                                "bbox": [bx, by, bx + bw, by + bh],
                                "text": t_val,
                                "xc": bx + (bw / 2.0),
                                "yc": by + (bh / 2.0)
                            })
                except Exception:
                    pass

            # 3. Only attempt EasyOCR if explicitly enabled and still no words
            if not words and is_easyocr_enabled():
                try:
                    reader = get_ocr_reader()
                    if reader:
                        working_image, _ocr_meta = prepare_easyocr_image(img_cv)
                        results = reader.readtext(working_image)
                        for res in results:
                            bbox_pts, text_val, conf = res
                            x_coords = [p[0] for p in bbox_pts]
                            y_coords = [p[1] for p in bbox_pts]
                            wx1, wy1, wx2, wy2 = int(min(x_coords)), int(min(y_coords)), int(max(x_coords)), int(max(y_coords))
                            if text_val.strip():
                                words.append({
                                    "bbox": [wx1, wy1, wx2, wy2],
                                    "text": text_val.strip(),
                                    "xc": (wx1 + wx2) / 2.0,
                                    "yc": (wy1 + wy2) / 2.0
                                })
                except Exception as e_err:
                    print(f"[TEXT MATRIX DETECTOR WARNING] EasyOCR word extraction failed: {e_err}")

            if not words:
                return []

            align_img = img_cv.copy()
            for w_item in words:
                bx1, by1, bx2, by2 = w_item["bbox"]
                cv2.rectangle(align_img, (bx1, by1), (bx2, by2), (255, 255, 0), 1)
            cv2.imwrite(os.path.join(trace_dir, "text_alignment_overlay.png"), align_img)

            words_sorted_y = sorted(words, key=lambda item: item["yc"])
            lines = []
            cur_line = []

            for w_item in words_sorted_y:
                if not cur_line:
                    cur_line.append(w_item)
                else:
                    line_first_yc = cur_line[0]["yc"]
                    if abs(w_item["yc"] - line_first_yc) <= 25.0:
                        cur_line.append(w_item)
                    else:
                        lines.append(cur_line)
                        cur_line = [w_item]
            if cur_line:
                lines.append(cur_line)

            processed_lines = []
            for line_words in lines:
                line_words_sorted = sorted(line_words, key=lambda item: item["bbox"][0])
                if not line_words_sorted:
                    continue

                merged_cells = []
                curr_cell_words = [line_words_sorted[0]]

                for next_w in line_words_sorted[1:]:
                    prev_w = curr_cell_words[-1]
                    prev_x1 = prev_w["bbox"][2]
                    next_x0 = next_w["bbox"][0]
                    gap = next_x0 - prev_x1

                    total_chars = sum(len(w["text"]) for w in curr_cell_words)
                    cell_w_px = prev_x1 - curr_cell_words[0]["bbox"][0]
                    avg_char_w = (cell_w_px / float(max(1, total_chars))) if total_chars > 0 else 10.0

                    prev_text = " ".join([w["text"] for w in curr_cell_words]).strip()
                    next_text = next_w["text"].strip()
                    unclosed_paren = ('(' in prev_text and ')' not in prev_text)

                    # Rule 1: Do NOT merge separate tuple expressions e.g. "(...)" and "(...)"
                    is_tuple_boundary = (prev_text.endswith(')') and next_text.startswith('('))
                    
                    # Rule 2: Do NOT merge separate numeric tokens if gap >= 12px
                    prev_is_num = prev_w["text"].replace('.', '').replace('-', '').isdigit()
                    next_is_num = next_w["text"].replace('.', '').replace('-', '').isdigit()
                    is_num_boundary = (prev_is_num and next_is_num and gap >= 12.0)

                    if not is_tuple_boundary and not is_num_boundary and (gap < max(12.0, avg_char_w * 1.2) or unclosed_paren):
                        curr_cell_words.append(next_w)
                    else:
                        merged_cells.append(curr_cell_words)
                        curr_cell_words = [next_w]
                if curr_cell_words:
                    merged_cells.append(curr_cell_words)

                line_cell_strings = []
                line_x_centers = []
                for cell_w_group in merged_cells:
                    raw_str = " ".join([w["text"] for w in cell_w_group]).strip()
                    clean_str = re.sub(r'\(\s+', '(', raw_str)
                    clean_str = re.sub(r'\s+\)', ')', clean_str)
                    clean_str = re.sub(r'\s*,\s*', ',', clean_str)
                    clean_str = re.sub(r'\s*\+\s*', ' + ', clean_str)
                    clean_str = re.sub(r'\s*=\s*', ' = ', clean_str)
                    
                    c_x0 = min(w["bbox"][0] for w in cell_w_group)
                    c_x1 = max(w["bbox"][2] for w in cell_w_group)
                    line_cell_strings.append(clean_str)
                    line_x_centers.append((c_x0 + c_x1) / 2.0)

                num_count = sum(1 for t in line_cell_strings if any(c.isdigit() for c in t))
                tuple_count = sum(1 for t in line_cell_strings if '(' in t or ')' in t or ',' in t)

                if len(line_cell_strings) >= 3 and (num_count >= 2 or tuple_count >= 2):
                    processed_lines.append({
                        "tokens": line_cell_strings,
                        "x_centers": line_x_centers,
                        "yc": np.mean([item["yc"] for item in line_words_sorted]),
                        "bbox": [
                            min(item["bbox"][0] for item in line_words_sorted),
                            min(item["bbox"][1] for item in line_words_sorted),
                            max(item["bbox"][2] for item in line_words_sorted),
                            max(item["bbox"][3] for item in line_words_sorted)
                        ]
                    })

            if len(processed_lines) < 3:
                return []

            matrix_clusters = []
            cur_cluster = [processed_lines[0]]

            for i in range(1, len(processed_lines)):
                prev_line = cur_cluster[-1]
                cur_l = processed_lines[i]
                y_diff = cur_l["yc"] - prev_line["yc"]
                col_match = abs(len(cur_l["tokens"]) - len(prev_line["tokens"])) <= 2
                if 12 <= y_diff <= 120 and col_match:
                    cur_cluster.append(cur_l)
                else:
                    if len(cur_cluster) >= 3:
                        matrix_clusters.append(cur_cluster)
                    cur_cluster = [cur_l]
            if len(cur_cluster) >= 3:
                matrix_clusters.append(cur_cluster)

            candidate_img = img_cv.copy()

            for c_idx, cluster in enumerate(matrix_clusters):
                # Step 3: Column Detection - Cluster X-centers across all lines in candidate matrix
                all_line_x_centers = [l["x_centers"] for l in cluster]
                flat_x_centers = sorted([xc for line_xcs in all_line_x_centers for xc in line_xcs])

                col_clusters = []
                for xc in flat_x_centers:
                    if not col_clusters:
                        col_clusters.append([xc])
                    else:
                        if abs(xc - np.mean(col_clusters[-1])) <= 40.0:
                            col_clusters[-1].append(xc)
                        else:
                            col_clusters.append([xc])

                col_centers = [float(np.mean(c)) for c in col_clusters]
                num_cols = len(col_centers)
                num_rows = len(cluster)

                grid_cells_2d = []
                for line_info in cluster:
                    row_tokens = [""] * num_cols
                    for cell_str, x_center in zip(line_info["tokens"], line_info["x_centers"]):
                        closest_col_idx = int(np.argmin([abs(x_center - cc) for cc in col_centers]))
                        if not row_tokens[closest_col_idx]:
                            row_tokens[closest_col_idx] = cell_str
                        else:
                            row_tokens[closest_col_idx] += " " + cell_str
                    grid_cells_2d.append(row_tokens)

                min_x = min(l["bbox"][0] for l in cluster)
                min_y = min(l["bbox"][1] for l in cluster)
                max_x = max(l["bbox"][2] for l in cluster)
                max_y = max(l["bbox"][3] for l in cluster)
                
                pad = 10
                cx = max(0, min_x - pad)
                cy = max(0, min_y - pad)
                cw = min(w - cx, (max_x - min_x) + 2 * pad)
                ch = min(h - cy, (max_y - min_y) + 2 * pad)

                cv2.rectangle(candidate_img, (cx, cy), (cx + cw, cy + ch), (255, 255, 0), 3)
                cv2.putText(candidate_img, f"TextMatrix Candidate {c_idx+1}", (cx + 5, cy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                crop = img_cv[cy:cy+ch, cx:cx+cw]
                is_ok, buf = cv2.imencode(".png", crop)
                crop_bytes = buf.tobytes() if is_ok else b""

                cell_json = grid_cells_2d
                has_tuples = any(('(' in cell and ')' in cell) for row in cell_json for cell in row if cell)

                tbl_obj = {
                    "source": "text_matrix",
                    "type": "matrix" if not has_tuples else "grid",
                    "element_type": "GRID" if has_tuples else "MATRIX",
                    "page_number": page_num,
                    "caption": f"Matrix / Tuple Grid (Page {page_num})",
                    "image_path": f"exam_tables/candidate_textmatrix_{c_idx+1}.png",
                    "image_url": f"{settings.MEDIA_URL}exam_tables/candidate_textmatrix_{c_idx+1}.png",
                    "bounding_box": [cx, cy, cx + cw, cy + ch],
                    "rows": num_rows,
                    "columns": num_cols,
                    "cell_json": cell_json,
                    "bytes": crop_bytes,
                    "is_matrix": True,
                    "display_order": c_idx + 1
                }
                candidates.append(tbl_obj)

            cv2.imwrite(os.path.join(trace_dir, "text_matrix_candidates.png"), candidate_img)

        except Exception as e:
            print(f"[TEXT MATRIX DETECTOR ERROR] {e}")

        return candidates

    @classmethod
    def extract_table_structure_and_cells(cls, crop_cv, page_num: int = 1, tbl_idx: int = 1) -> Optional[Dict[str, Any]]:
        """
        True Table Structure Recognition Pipeline:
        Candidate ROI -> Adaptive Threshold -> Horizontal/Vertical Morphology -> Cell Bounding Box Extraction
        -> Cluster Rows & Sort Cells -> Independent Cell OCR -> Construct 2D Matrix JSON
        """
        try:
            import cv2
            import numpy as np
            import json
            import os

            h, w, _ = crop_cv.shape
            gray = cv2.cvtColor(crop_cv, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

            # Fixed 25px / 15px morphology kernels to extract grid lines inside ROI crop
            h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            horizontal = cv2.erode(thresh, h_kernel, iterations=1)
            horizontal = cv2.dilate(horizontal, h_kernel, iterations=1)

            v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
            vertical = cv2.erode(thresh, v_kernel, iterations=1)
            vertical = cv2.dilate(vertical, v_kernel, iterations=1)

            table_grid = cv2.add(horizontal, vertical)
            trace_dir = get_trace_dir()

            # Save debug table_grid.png
            cv2.imwrite(os.path.join(trace_dir, "table_grid.png"), table_grid)

            # Find internal cell contours
            contours, _ = cv2.findContours(table_grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cell_boxes = []

            for c in contours:
                x, y, cw, ch = cv2.boundingRect(c)
                # Filter internal cell boxes (ignore outer table frame & tiny noise)
                if 10 < cw < 0.95 * w and 8 < ch < 0.95 * h:
                    cell_boxes.append((x, y, cw, ch))

            if len(cell_boxes) < 4:
                print(f"  [TABLE STRUCTURE REJECTED] Found only {len(cell_boxes)} cell boxes (< 4 required for grid)")
                return None

            # Group cells into rows by Y-center clustering (threshold = 15px)
            cell_boxes = sorted(cell_boxes, key=lambda b: b[1] + (b[3] / 2.0))
            rows = []
            current_row = []
            last_y_center = None

            for box in cell_boxes:
                y_center = box[1] + (box[3] / 2.0)
                if last_y_center is None or abs(y_center - last_y_center) <= 15:
                    current_row.append(box)
                    last_y_center = y_center
                else:
                    rows.append(current_row)
                    current_row = [box]
                    last_y_center = y_center
            if current_row:
                rows.append(current_row)

            # Sort cells within each row left-to-right by X-center
            grid_cells_2d = []
            cell_boxes_img = crop_cv.copy()
            cell_counter = 0

            for r_idx, r_boxes in enumerate(rows):
                r_boxes_sorted = sorted(r_boxes, key=lambda b: b[0] + (b[2] / 2.0))
                row_cell_texts = []
                for c_idx, box in enumerate(r_boxes_sorted):
                    cell_counter += 1
                    bx, by, bw, bh = box

                    # Draw debug cell box overlay
                    cv2.rectangle(cell_boxes_img, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
                    cv2.putText(cell_boxes_img, f"C{cell_counter}", (bx + 2, max(12, by + 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

                    # Crop cell ROI image
                    cell_crop = crop_cv[by:by+bh, bx:bx+bw]
                    cell_filename = f"cell_{cell_counter:03d}.png"
                    cell_filepath = os.path.join(trace_dir, cell_filename)
                    cv2.imwrite(cell_filepath, cell_crop)

                    # OCR cell slice independently
                    cell_text = ""
                    # 1. Try PyTesseract first (fast, CPU safe)
                    try:
                        import pytesseract
                        from PIL import Image as PILImg
                        pil_crop = PILImg.fromarray(cv2.cvtColor(cell_crop, cv2.COLOR_BGR2RGB))
                        cell_text = pytesseract.image_to_string(pil_crop, config='--psm 6').strip()
                    except Exception:
                        pass

                    # 2. Only try EasyOCR if explicitly enabled and PyTesseract was empty
                    if not cell_text and is_easyocr_enabled():
                        try:
                            reader = get_ocr_reader()
                            if reader:
                                working_cell, _cell_meta = prepare_easyocr_image(cell_crop)
                                res = reader.readtext(working_cell)
                                if res:
                                    cell_text = " ".join([r[1].strip() for r in res])
                        except Exception:
                            pass

                    # 3. PyMuPDF fallback
                    if not cell_text:
                        is_ok, buf = cv2.imencode(".png", cell_crop)
                        if is_ok:
                            try:
                                import fitz
                                with fitz.open(stream=buf.tobytes(), filetype="png") as cdoc:
                                    cell_text = cdoc[0].get_text().strip()
                            except Exception:
                                pass

                    row_cell_texts.append(cell_text)
                grid_cells_2d.append(row_cell_texts)

            # Save cell_boxes.png
            cv2.imwrite(os.path.join(trace_dir, f"cell_boxes.png"), cell_boxes_img)

            # Save table.json
            num_rows = len(grid_cells_2d)
            num_cols = max(len(r) for r in grid_cells_2d) if grid_cells_2d else 0
            table_json_content = {
                "rows": num_rows,
                "cols": num_cols,
                "cells": grid_cells_2d
            }
            with open(os.path.join(trace_dir, "table.json"), "w", encoding="utf-8") as f:
                json.dump(table_json_content, f, indent=2)

            # Content-driven Classification Rules
            all_cell_tokens = [cell for row in grid_cells_2d for cell in row if cell.strip()]
            if not all_cell_tokens:
                print("  [TABLE CLASSIFIER] All cell OCR returned empty -> UNKNOWN (confidence=0)")
                return None

            joined_text = " ".join(all_cell_tokens).upper()
            header_keywords = ['QUESTION', 'MARKS', 'CO', 'PO', 'BLOOM', 'COURSE', 'STUDENT', 'FACULTY', 'SECTION', 'MODULE', 'WEEK']
            has_headers = any(kw in joined_text for kw in header_keywords)

            has_tuples = any(('(' in cell and ')' in cell and ',' in cell) for cell in all_cell_tokens)
            numeric_count = sum(1 for cell in all_cell_tokens if cell.replace('.', '').replace('-', '').replace('(', '').replace(')', '').replace(',', '').strip().isdigit())
            num_ratio = numeric_count / float(len(all_cell_tokens))

            if has_headers:
                classification = "TABLE"
                element_type = "TABLE"
            elif has_tuples:
                classification = "NUMERIC GRID"
                element_type = "GRID"
            elif num_ratio >= 0.95:
                classification = "MATRIX"
                element_type = "MATRIX"
            else:
                classification = "TABLE"
                element_type = "TABLE"

            return {
                "classification": classification,
                "element_type": element_type,
                "rows": num_rows,
                "cols": num_cols,
                "cell_json": grid_cells_2d,
                "confidence": 0.98 if all_cell_tokens else 0.0
            }
        except Exception as e:
            print(f"[TABLE STRUCTURE ENGINE ERROR] {e}")
            return None

    @staticmethod
    def calculate_iou(boxA: List[float], boxB: List[float]) -> float:
        """
        Calculates Intersection Over Union (IoU) between two bounding boxes [x1, y1, x2, y2].
        """
        if not boxA or not boxB or len(boxA) < 4 or len(boxB) < 4:
            return 0.0

        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        denominator = float(boxAArea + boxBArea - interArea)
        if denominator <= 0:
            return 0.0

        return interArea / denominator

    @classmethod
    def apply_nms_deduplication(cls, candidate_regions: List[Dict[str, Any]], iou_threshold: float = 0.70) -> Dict[str, Any]:
        """
        Applies Non-Maximum Suppression (NMS) to eliminate duplicate overlapping bounding box detections.
        Logs every region's bbox, area, IoU, and ACCEPTED/REJECTED status.
        """
        if not candidate_regions:
            return {"accepted": [], "rejected": []}

        # Sort candidate regions by area descending (largest / most complete grid first)
        sorted_candidates = sorted(
            candidate_regions,
            key=lambda r: (r.get("bounding_box", [0,0,0,0])[2]-r.get("bounding_box", [0,0,0,0])[0]) * 
                         (r.get("bounding_box", [0,0,0,0])[3]-r.get("bounding_box", [0,0,0,0])[1]),
            reverse=True
        )

        accepted = []
        rejected = []

        print("=" * 80)
        print(f"[NMS REGION DEDUPLICATION ENGINE] Evaluating {len(sorted_candidates)} Candidate Regions (IoU Threshold={iou_threshold})...")
        print("=" * 80)

        for idx, candidate in enumerate(sorted_candidates):
            c_box = candidate.get("bounding_box", [0, 0, 0, 0])
            c_w = c_box[2] - c_box[0]
            c_h = c_box[3] - c_box[1]
            c_area = c_w * c_h
            c_type = str(candidate.get("type", candidate.get("source", "table")))
            c_is_fig = (candidate.get("source") == "figure" or candidate.get("type") == "figure" or candidate.get("element_type") == "FIGURE")

            max_iou = 0.0
            overlapping_box = None

            for acc in accepted:
                acc_is_fig = (acc.get("source") == "figure" or acc.get("type") == "figure" or acc.get("element_type") == "FIGURE")
                # NMS deduplicates overlapping regions within the SAME element category (Figure vs Figure, Table vs Table)
                if c_is_fig == acc_is_fig:
                    acc_box = acc.get("bounding_box", [0, 0, 0, 0])
                    iou = cls.calculate_iou(c_box, acc_box)
                    if iou > max_iou:
                        max_iou = iou
                        overlapping_box = acc_box

            if max_iou > iou_threshold:
                rejected_item = {
                    "type": "REJECT_DUPLICATE_NMS",
                    "bbox": c_box,
                    "area": c_area,
                    "iou": round(max_iou, 4),
                    "reason": f"NMS Duplicate (IoU={max_iou:.4f} > {iou_threshold})"
                }
                rejected.append(rejected_item)
                print(f"  [REJECTED] Candidate {idx+1}: bbox={c_box} | area={c_area} | IoU={max_iou:.4f} -> REJECTED (Duplicate NMS)")
            else:
                accepted.append(candidate)
                print(f"  [ACCEPTED] Candidate {idx+1}: bbox={c_box} | area={c_area} | IoU={max_iou:.4f} -> ACCEPTED ({c_type.upper()})")

        print("=" * 80)
        print(f"[NMS DEDUPLICATION COMPLETE] Accepted: {len(accepted)} | Rejected Duplicates: {len(rejected)}")
        print("=" * 80)

        return {"accepted": accepted, "rejected": rejected}

    @classmethod
    def detect_tables_and_grids(cls, image_bytes: bytes, page_num: int = 1, save_dir: str = "", subfolder: str = "") -> List[Dict[str, Any]]:
        """
        OpenCV Table & Matrix Grid Detector using horizontal and vertical morphology kernels.
        Applies NMS deduplication pass to eliminate duplicate grid contours.
        Extracts 2D cell_json matrix and classifies region as MATRIX vs TABLE.
        """
        raw_tables = []
        try:
            import cv2
            import numpy as np

            img_np = np.frombuffer(image_bytes, np.uint8)
            img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            if img_cv is None:
                return []

            h, w, _ = img_cv.shape
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

            # Kernels tuned to isolate continuous structural grid lines (ignoring letter stems)
            h_scale = 10  # Horizontal lines must span >= 1/10th page width (~250px)
            v_scale = 12  # Vertical lines must span >= 1/12th page height (~290px)
            
            h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(1, w // h_scale), 1))
            horizontal = cv2.erode(thresh, h_kernel, iterations=1)
            horizontal = cv2.dilate(horizontal, h_kernel, iterations=1)

            v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(1, h // v_scale)))
            vertical = cv2.erode(thresh, v_kernel, iterations=1)
            vertical = cv2.dilate(vertical, v_kernel, iterations=1)

            table_grid = cv2.add(horizontal, vertical)
            grid_intersections = cv2.bitwise_and(horizontal, vertical)
            contours, _ = cv2.findContours(table_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            tbl_idx = 0
            page_roi_md5_set = set()

            for c in contours:
                cx, cy, cw, ch = cv2.boundingRect(c)
                aspect_ratio = cw / float(ch) if ch > 0 else 0
                # Task 4 & 5 Validation Gate:
                if aspect_ratio > 3.5:
                    print(f"  [TABLE REJECTED] bbox=[{cx},{cy},{cw},{ch}] -> REJECTED (Banner Aspect Ratio {aspect_ratio:.2f} > 3.5)")
                    continue

                if ch >= 0.50 * h:
                    print(f"  [TABLE REJECTED] bbox=[{cx},{cy},{cw},{ch}] -> REJECTED (Page Container Box: height {ch}px >= 50% page height)")
                    continue

                if cw > 150 and ch > 100 and not (cw >= 0.90 * w and ch >= 0.90 * h):
                    roi_intersections = grid_intersections[cy:cy+ch, cx:cx+cw]
                    intersection_count = np.sum(roi_intersections > 0)
                    if intersection_count < 4:
                        print(f"  [TABLE REJECTED] bbox=[{cx},{cy},{cw},{ch}] -> REJECTED (Insufficient Grid Intersections: {intersection_count} < 4)")
                        continue

                    tbl_idx += 1
                    # Extract exact ROI slice from image
                    table_crop = img_cv[cy:cy+ch, cx:cx+cw]
                    roi_shape = table_crop.shape
                    is_success, buffer = cv2.imencode(".png", table_crop)

                    if is_success:
                        crop_bytes = buffer.tobytes()
                        import hashlib
                        md5_hash = hashlib.md5(crop_bytes).hexdigest()

                        tbl_filename = f"candidate_{tbl_idx:03d}.png"
                        tbl_rel_path = f"exam_tables/{subfolder}/{tbl_filename}" if subfolder else f"exam_tables/{tbl_filename}"
                        tbl_full_path = os.path.join(save_dir, tbl_filename)
                        trace_candidate_path = os.path.join(get_trace_dir(), tbl_filename)

                        os.makedirs(os.path.dirname(tbl_full_path), exist_ok=True)

                        with open(tbl_full_path, "wb") as f:
                            f.write(crop_bytes)
                        with open(trace_candidate_path, "wb") as f:
                            f.write(crop_bytes)

                        # Pre-OCR Log & MD5 Collision Verification
                        print("-" * 70)
                        print(f"Candidate ID        : Candidate {tbl_idx}")
                        print(f"bbox                : [{cx}, {cy}, {cx + cw}, {cy + ch}]")
                        print(f"ROI shape           : {roi_shape}")
                        print(f"ROI filename        : {tbl_filename}")
                        print(f"ROI md5 hash        : {md5_hash}")

                        if md5_hash in page_roi_md5_set:
                            raise RuntimeError(f"Duplicate ROI detected on Page {page_num}: MD5 Hash collision '{md5_hash}' for bbox [{cx}, {cy}, {cx+cw}, {cy+ch}]")
                        page_roi_md5_set.add(md5_hash)

                        # Task 1-5: True Table Structure Recognition Pipeline (Cell Extraction & 2D Grid Construction)
                        table_struct = cls.extract_table_structure_and_cells(table_crop, page_num=page_num, tbl_idx=tbl_idx)
                        if not table_struct:
                            print(f"  [CONTOUR REGION CONVERTED] Candidate {tbl_idx} -> Classified as FIGURE (No 2D Grid lines detected)")
                            fig_rel_path = f"exam_figures/{subfolder}/fig_contour_p{page_num}_{tbl_idx}.png" if subfolder else f"exam_figures/fig_contour_p{page_num}_{tbl_idx}.png"
                            fig_full_path = os.path.join(save_dir, f"fig_contour_p{page_num}_{tbl_idx}.png")
                            with open(fig_full_path, "wb") as f:
                                f.write(crop_bytes)

                            tbl_obj = {
                                "source": "figure",
                                "type": "figure",
                                "element_type": "FIGURE",
                                "page_number": page_num,
                                "caption": f"Figure {tbl_idx} (Page {page_num})",
                                "image_path": fig_rel_path,
                                "image_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                                "thumbnail_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                                "bounding_box": [cx, cy, cx + cw, cy + ch],
                                "width": cw,
                                "height": ch,
                                "bytes": crop_bytes,
                                "mime_type": "image/png",
                                "display_order": tbl_idx
                            }
                            raw_tables.append(tbl_obj)
                            continue

                        predicted_class = table_struct["classification"].lower()
                        element_type = table_struct["element_type"]
                        cell_json = table_struct["cell_json"]
                        rows_cnt = table_struct["rows"]
                        cols_cnt = table_struct["cols"]
                        caption_label = f"Matrix (Page {page_num})" if element_type == "MATRIX" else f"Table / Grid (Page {page_num})"

                        # Post-OCR Log
                        print(f"OCR 2D Matrix        : {cell_json}")
                        print(f"rows | columns      : {rows_cnt} x {cols_cnt}")
                        print(f"predicted class     : {element_type}")
                        print(f"confidence          : {table_struct['confidence']:.2f}")
                        print("-" * 70)

                        tbl_obj = {
                            "type": predicted_class,
                            "element_type": element_type,
                            "page_number": page_num,
                            "caption": caption_label,
                            "image_path": tbl_rel_path,
                            "image_url": f"{settings.MEDIA_URL}{tbl_rel_path}",
                            "bounding_box": [cx, cy, cx + cw, cy + ch],
                            "rows": rows_cnt,
                            "columns": cols_cnt,
                            "cell_json": cell_json,
                            "bytes": crop_bytes,
                            "is_matrix": (element_type == "MATRIX"),
                            "display_order": tbl_idx
                        }
                        raw_tables.append(tbl_obj)

        except Exception as tbl_err:
            print(f"[DOCUMENT SERVICE WARNING] Table detection error: {tbl_err}")

        # Task 1 & 2: Apply NMS Deduplication Pass
        nms_result = cls.apply_nms_deduplication(raw_tables, iou_threshold=0.70)
        return nms_result["accepted"]
