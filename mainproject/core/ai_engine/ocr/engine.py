import os
import io
import re
import zlib
from typing import Dict, Any
from .preprocessor import ImagePreprocessor
from core.models import AIConfiguration
from core.ai_engine.providers.gemini import GeminiProvider
from django.conf import settings

class OCREngineManager:
    """
    Production OCR Engine Manager supporting PyMuPDF PDF stream extraction, 300 DPI page rendering,
    PaddleOCR, EasyOCR, PyTesseract, and Google Gemini Multimodal Vision.
    Strips raw PostScript font node garbage (e.g. node00000265, Skia/PDF) automatically.
    """

    def __init__(self, engine_choice: str = "AUTO", preprocess: bool = True):
        self.engine_choice = engine_choice
        self.preprocess = preprocess

    @staticmethod
    def extract_pdf_bytes_text(pdf_bytes: bytes) -> str:
        """Extracts clean text from PDF bytes using PyMuPDF (fitz)."""
        try:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text_pages = []
            for page in doc:
                txt = page.get_text("text") or ""
                clean_lines = []
                for line in txt.split('\n'):
                    s = line.strip()
                    # Filter out font node garbage like 'node00000265', 'Skia/PDF', or PDF object refs '41 0 R'
                    if s and not re.search(r'node\d{6,}', s) and not 'Skia/PDF' in s and not re.match(r'^\d+\s+\d+\s+R$', s):
                        clean_lines.append(s)
                if clean_lines:
                    text_pages.append("\n".join(clean_lines))
            return "\n".join(text_pages).strip()
        except Exception:
            return ""

    @staticmethod
    def extract_document_layout_and_figures(doc_bytes: bytes, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Extracts high-resolution rendered pages (300 DPI), embedded figures/diagrams,
        layout bounding boxes, captions, and constructs a page-by-page Document DOM tree.
        """
        import datetime
        from PIL import Image
        now = datetime.datetime.now()
        subfolder = now.strftime('%Y/%m')
        save_dir = os.path.join(settings.MEDIA_ROOT, 'exam_figures', subfolder)
        thumb_dir = os.path.join(settings.MEDIA_ROOT, 'exam_figures', 'thumbs', subfolder)
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)

        extracted_figures = []
        page_renders = []
        dom_elements = []

        try:
            import fitz
            if doc_bytes.startswith(b'%PDF'):
                doc = fitz.open(stream=doc_bytes, filetype="pdf")
                for page_idx, page in enumerate(doc):
                    page_num = page_idx + 1
                    
                    # 1. High-DPI Render (300 DPI)
                    pix = page.get_pixmap(dpi=300)
                    page_png = pix.tobytes("png")
                    page_renders.append(page_png)

                    # 2. Extract Embedded Vector/Raster Images
                    img_list = page.get_images(full=True)
                    for img_idx, img_info in enumerate(img_list):
                        xref = img_info[0]
                        base_img = doc.extract_image(xref)
                        image_bytes = base_img.get("image")
                        image_ext = base_img.get("ext", "png")

                        if image_bytes and len(image_bytes) > 500: # Filter out 1x1 tiny icons
                            fig_filename = f"fig_p{page_num}_{img_idx+1}_{xref}.{image_ext}"
                            fig_rel_path = f"exam_figures/{subfolder}/{fig_filename}"
                            fig_full_path = os.path.join(save_dir, fig_filename)

                            with open(fig_full_path, "wb") as f:
                                f.write(image_bytes)

                            # Generate Thumbnail
                            thumb_rel_path = f"exam_figures/thumbs/{subfolder}/{fig_filename}"
                            thumb_full_path = os.path.join(thumb_dir, fig_filename)
                            try:
                                im = Image.open(io.BytesIO(image_bytes))
                                im.thumbnail((300, 300))
                                im.save(thumb_full_path)
                            except Exception:
                                thumb_rel_path = fig_rel_path

                            # Get Bounding Box Coordinates if available
                            rects = page.get_image_rects(xref)
                            bbox = [round(c, 2) for c in rects[0]] if rects else [0, 0, 0, 0]

                            extracted_figures.append({
                                "page_number": page_num,
                                "caption": f"Figure {img_idx+1} (Page {page_num})",
                                "image_path": fig_rel_path,
                                "image_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                                "thumbnail_url": f"{settings.MEDIA_URL}{thumb_rel_path}",
                                "bounding_box": bbox,
                                "display_order": img_idx + 1
                            })

                            dom_elements.append({
                                "type": "figure",
                                "page": page_num,
                                "caption": f"Figure {img_idx+1}",
                                "image_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                                "bbox": bbox
                            })

                    # DOM Page text blocks & coordinates
                    text_blocks = page.get_text("blocks")
                    for b in text_blocks:
                        if b[4].strip():
                            dom_elements.append({
                                "type": "text_block",
                                "page": page_num,
                                "text": b[4].strip(),
                                "bbox": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)]
                            })
            else:
                # Direct Image Upload (JPEG/PNG)
                page_renders.append(doc_bytes)
                im = Image.open(io.BytesIO(doc_bytes))
                fig_filename = f"fig_upload_{now.strftime('%H%M%S')}.png"
                fig_rel_path = f"exam_figures/{subfolder}/{fig_filename}"
                fig_full_path = os.path.join(save_dir, fig_filename)
                im.save(fig_full_path)

                extracted_figures.append({
                    "page_number": 1,
                    "caption": "Attached Figure 1",
                    "image_path": fig_rel_path,
                    "image_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                    "thumbnail_url": f"{settings.MEDIA_URL}{fig_rel_path}",
                    "bounding_box": [0, 0, im.width, im.height],
                    "display_order": 1
                })
        except Exception as e:
            print(f"[DOCUMENT AI EXTRACTION WARNING] {e}")

        return {
            "figures": extracted_figures,
            "page_renders": page_renders,
            "dom_elements": dom_elements,
            "total_pages": len(page_renders) or 1
        }

    def extract_text(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """
        Processes image_bytes or PDF bytes and extracts text with confidence score.
        For scanned PDFs or PDFs with font node noise (Skia/PDF), renders 300 DPI image for Vision OCR.
        """
        if not image_bytes:
            return {"text": "", "confidence": 0.0, "engine_used": "None"}

        # 0. PDF Processing with PyMuPDF & 300 DPI Rendering
        if image_bytes.startswith(b'%PDF'):
            pdf_text = self.extract_pdf_bytes_text(image_bytes)
            # If valid text extracted without font glyph node garbage
            if pdf_text and len(pdf_text) > 30 and not 'node00000' in pdf_text:
                return {"text": pdf_text, "confidence": 0.95, "engine_used": "PyMuPDF Stream Extractor"}
            
            # Scanned / Skia PDF: Render 300 DPI page image for Multimodal Vision OCR
            try:
                import fitz
                doc = fitz.open(stream=image_bytes, filetype="pdf")
                if len(doc) > 0:
                    page = doc.load_page(0)
                    pix = page.get_pixmap(dpi=300)
                    image_bytes = pix.tobytes("png")
                    mime_type = "image/png"
            except Exception as e:
                print(f"[ENGINE PDF RENDERING WARNING] {e}")
                mime_type = "application/pdf"

        if self.preprocess and not mime_type == "application/pdf":
            try:
                image_bytes = ImagePreprocessor.detect_and_correct_rotation(image_bytes)
                image_bytes = ImagePreprocessor.preprocess_image(image_bytes)
            except Exception:
                pass

        # 1. Try EasyOCR Engine for Image Documents
        if not mime_type == "application/pdf" and self.engine_choice in [AIConfiguration.OCREngine.AUTO]:
            try:
                import easyocr
                reader = easyocr.Reader(['en'], gpu=False)
                result = reader.readtext(image_bytes)
                lines = [res[1] for res in result]
                scores = [res[2] for res in result]
                extracted = "\n".join(lines)
                conf = sum(scores) / len(scores) if scores else 0.85
                if extracted.strip():
                    return {"text": extracted.strip(), "confidence": round(conf, 4), "engine_used": "EasyOCR"}
            except Exception:
                pass

        # 2. Try PyTesseract Fallback Engine
        if not mime_type == "application/pdf" and self.engine_choice in [AIConfiguration.OCREngine.TESSERACT, AIConfiguration.OCREngine.AUTO]:
            try:
                import pytesseract
                from PIL import Image
                img = Image.open(io.BytesIO(image_bytes))
                extracted = pytesseract.image_to_string(img)
                if extracted.strip():
                    return {"text": extracted.strip(), "confidence": 0.80, "engine_used": "PyTesseract"}
            except Exception:
                pass

        # 3. Multimodal Vision Cloud OCR (Failover AI Engine for Real Document Images & PDF Renderings)
        try:
            from core.ai_engine.providers.factory import AIProviderFactory
            provider = AIProviderFactory.get_provider()
            extracted_vision_text = provider.extract_ocr_text(image_bytes, mime_type=mime_type)
            if extracted_vision_text and extracted_vision_text.strip():
                return {
                    "text": extracted_vision_text.strip(),
                    "confidence": 0.98,
                    "engine_used": f"{provider.__class__.__name__} Multimodal OCR"
                }
        except Exception as e:
            print(f"DEBUG ENGINE OCR EXCEPTION: {e}")
            pass

        return {
            "text": "",
            "confidence": 0.0,
            "engine_used": "None"
        }
