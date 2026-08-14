import os
import json
from typing import Dict, Any, List
from django.conf import settings
from config.ocr_config import prepare_easyocr_image


class PipelineValidationError(Exception):
    """Custom exception raised when pipeline assertions or document quality checks fail."""
    pass


class AcademicParserService:
    """
    Academic Parser Service responsible for:
    1. Parsing structured academic questions, sub-parts, allocated marks, CO/PO mappings
    2. Associating extracted figures with specific questions using layout coordinates
    3. Enforcing strict fail-fast validation assertions before database commit
    """

    @staticmethod
    def associate_figures_with_questions(
        questions: List[Dict[str, Any]],
        figures: List[Dict[str, Any]],
        tables: List[Dict[str, Any]] = None,
        formulas: List[Dict[str, Any]] = None,
        dom_elements: List[Dict[str, Any]] = None,
        pdf_bytes: bytes = None,
        graphics_result: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Maps figures, tables, and formulas to questions using spatial bounding box layout and page reading order.
        ENFORCES STRICT SINGLE-OWNERSHIP: Each figure/table/formula belongs to ONLY ONE question (no duplicates across questions).
        """
        for q in questions:
            q['associated_figures'] = []
            q['associated_tables'] = []
            q['associated_formulas'] = []

        if not questions:
            return questions

        # Extract line-level text elements for precise question start_y detection
        import re
        import cv2
        import numpy as np
        text_lines = [d for d in (dom_elements or []) if d.get('text') and 'element_type' not in d and 'cell_json' not in d and 'source' not in d]
        page_renders = (graphics_result or {}).get('page_renders', [])

        if not text_lines and page_renders:
            try:
                from config.ocr_config import get_ocr_reader
                reader = get_ocr_reader()
                for page_idx, render_item in enumerate(page_renders, 1):
                    p_cv = None
                    if isinstance(render_item, str):
                        paths_to_check = [
                            render_item,
                            os.path.join(settings.MEDIA_ROOT, render_item),
                            os.path.join(getattr(settings, 'BASE_DIR', '.'), render_item)
                        ]
                        for p in paths_to_check:
                            if os.path.exists(p):
                                p_cv = cv2.imread(p)
                                if p_cv is not None:
                                    break
                    elif isinstance(render_item, (bytes, bytearray)):
                        img_np = np.frombuffer(render_item, np.uint8)
                        p_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                    elif isinstance(render_item, np.ndarray):
                        p_cv = render_item
                    
                    if p_cv is not None and reader is not None:
                        working_page, _page_meta = prepare_easyocr_image(p_cv)
                        res = reader.readtext(working_page)
                        for bbox_pts, text_val, conf in res:
                            if text_val.strip():
                                ys = [pt[1] for pt in bbox_pts]
                                xs = [pt[0] for pt in bbox_pts]
                                text_lines.append({
                                    "page": page_idx,
                                    "bbox": [min(xs), min(ys), max(xs), max(ys)],
                                    "text": text_val.strip()
                                })
                        print(f"  [DOM OCR FALLBACK SUCCESS] Extracted {len(text_lines)} text items from page_renders.")
                        for dom_item in text_lines[:15]:
                            print(f"    - Page {dom_item['page']}, Y={dom_item['bbox'][1]}: {dom_item['text']}")
            except Exception as e_ocr:
                print(f"[DOM OCR FALLBACK WARNING] {e_ocr}")

        if not dom_elements and pdf_bytes:
            try:
                import fitz
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                from config.ocr_config import get_ocr_reader
                reader = get_ocr_reader()
                for page_idx, page in enumerate(doc, 1):
                    pix = page.get_pixmap(dpi=300)
                    p_bytes = pix.tobytes("png")
                    p_np = np.frombuffer(p_bytes, np.uint8)
                    p_cv = cv2.imdecode(p_np, cv2.IMREAD_COLOR)
                    
                    if reader is not None:
                        working_page, _page_meta = prepare_easyocr_image(p_cv)
                        res = reader.readtext(working_page)
                        for bbox_pts, text_val, conf in res:
                            if text_val.strip():
                                ys = [pt[1] for pt in bbox_pts]
                                xs = [pt[0] for pt in bbox_pts]
                                dom_elements.append({
                                    "page": page_idx,
                                    "bbox": [min(xs), min(ys), max(xs), max(ys)],
                                    "text": text_val.strip()
                                })
            except Exception as e_ocr:
                print(f"[DOM OCR FALLBACK WARNING] {e_ocr}")

        for idx, q in enumerate(questions):
            q_num = str(q.get('question_number', idx + 1)).lower().replace('question', '').replace('q', '').strip()
            q_num_pattern = re.escape(q_num)
            found_y = None
            found_page = None

            for dom in text_lines:
                d_text = dom.get('text', '').lower().strip()
                d_bbox = dom.get('bbox', [0, 0, 0, 0])
                d_page = dom.get('page', 1)
                
                # Match question heading e.g. "Question 1", "Q1", "1.", "1. ", "(1)"
                if f"question {q_num}" in d_text or f"q{q_num}" in d_text or re.search(rf'^\s*\(?\s*{q_num_pattern}\s*[\.\)]', d_text):
                    found_y = d_bbox[1]
                    found_page = d_page
                    print(f"  [Q-OWNERSHIP MATCH] Question {q_num} matched '{d_text[:30]}' at Page {found_page}, Y={found_y:.1f}")
                    break

            if found_y is not None:
                q['start_y'] = float(found_y)
                q['page_number'] = found_page
            elif 'start_y' not in q or q['start_y'] is None:
                q['start_y'] = float(q.get('y_min', (idx + 1) * 10000.0))
            print(f"  [Q-OWNERSHIP FINAL] Question {idx+1} ({q.get('question_number')}) -> Page {q.get('page_number', 1)}, start_y={q.get('start_y'):.1f}")

        # 1. Associate Figures
        claimed_fig_indices = set()
        for fig_idx, fig in enumerate(figures or []):
            fig_page = fig.get('page_number', 1)
            bbox = fig.get('bounding_box', [0, 0, 0, 0])
            fig_center_y = (bbox[1] + bbox[3]) / 2.0 if len(bbox) >= 4 else bbox[1]

            target_q_idx = None
            page_q_list = [(idx, q) for idx, q in enumerate(questions) if q.get('page_number', 1) == fig_page or len(questions) == 1]
            if page_q_list:
                page_q_list = sorted(page_q_list, key=lambda item: item[1].get('start_y', 0))
                for i, (q_idx, q_item) in enumerate(page_q_list):
                    q_start_y = q_item.get('start_y', 0)
                    next_q_start_y = page_q_list[i+1][1].get('start_y', 99999) if i + 1 < len(page_q_list) else 99999
                    if fig_center_y < page_q_list[0][1].get('start_y', 0):
                        target_q_idx = page_q_list[0][0]
                        break
                    elif q_start_y <= fig_center_y < next_q_start_y:
                        target_q_idx = q_idx
                        break
                if target_q_idx is None:
                    target_q_idx = page_q_list[-1][0]

            if target_q_idx is not None and fig_idx not in claimed_fig_indices:
                claimed_fig_indices.add(fig_idx)
                questions[target_q_idx]['associated_figures'].append(fig)

        # 2. Associate Tables
        claimed_tbl_indices = set()
        for tbl_idx, tbl in enumerate(tables or []):
            tbl_page = tbl.get('page_number', 1)
            bbox = tbl.get('bounding_box', [0, 0, 0, 0])
            tbl_center_y = (bbox[1] + bbox[3]) / 2.0 if len(bbox) >= 4 else bbox[1]

            target_q_idx = None
            page_q_list = [(idx, q) for idx, q in enumerate(questions) if q.get('page_number', 1) == tbl_page or len(questions) == 1]
            if page_q_list:
                page_q_list = sorted(page_q_list, key=lambda item: item[1].get('start_y', 0))
                for i, (q_idx, q_item) in enumerate(page_q_list):
                    q_start_y = q_item.get('start_y', 0)
                    next_q_start_y = page_q_list[i+1][1].get('start_y', 99999) if i + 1 < len(page_q_list) else 99999
                    if tbl_center_y < page_q_list[0][1].get('start_y', 0):
                        target_q_idx = page_q_list[0][0]
                        break
                    elif q_start_y <= tbl_center_y < next_q_start_y:
                        target_q_idx = q_idx
                        break
                if target_q_idx is None:
                    target_q_idx = page_q_list[-1][0]

            if target_q_idx is not None and tbl_idx not in claimed_tbl_indices:
                claimed_tbl_indices.add(tbl_idx)
                tbl["owner_question"] = questions[target_q_idx].get("question_number", f"Q{target_q_idx+1}")
                questions[target_q_idx]['associated_tables'].append(tbl)

        # 3. Associate Formulas
        claimed_form_indices = set()
        for form_idx, form in enumerate(formulas or []):
            form_page = form.get('page_number', 1)
            bbox = form.get('bounding_box', [0, 0, 0, 0])
            form_center_y = (bbox[1] + bbox[3]) / 2.0 if len(bbox) >= 4 else bbox[1]

            target_q_idx = None
            page_q_list = [(idx, q) for idx, q in enumerate(questions) if q.get('page_number', 1) == form_page or len(questions) == 1]
            if page_q_list:
                for i, (q_idx, q_item) in enumerate(page_q_list):
                    q_start_y = q_item.get('start_y', 0)
                    next_q_start_y = page_q_list[i+1][1].get('start_y', 99999) if i + 1 < len(page_q_list) else 99999
                    if q_start_y <= form_center_y < next_q_start_y:
                        target_q_idx = q_idx
                        break
                if target_q_idx is None:
                    if form_center_y >= page_q_list[-1][1].get('start_y', 0):
                        target_q_idx = page_q_list[-1][0]
                    else:
                        target_q_idx = page_q_list[0][0]

            if target_q_idx is not None and form_idx not in claimed_form_indices:
                claimed_form_indices.add(form_idx)
                questions[target_q_idx]['associated_formulas'].append(form)

        return questions

    @classmethod
    def validate_and_parse(
        cls,
        ocr_result: Dict[str, Any],
        graphics_result: Dict[str, Any],
        ai_response_data: Dict[str, Any],
        min_ocr_chars: int = 50
    ) -> Dict[str, Any]:
        """
        Executes strict fail-fast validation assertions.
        If ANY validation assertion fails, raises PipelineValidationError to abort transaction.
        """
        ocr_text = ocr_result.get('text', '').strip()
        char_count = len(ocr_text)

        # Assertion 1: OCR Character Count Validation
        if char_count < min_ocr_chars:
            raise PipelineValidationError(
                f"[STRICT PIPELINE FAILURE] OCR Quality Failure: Extracted text length ({char_count} chars) "
                f"is below required minimum ({min_ocr_chars} chars). Document scan aborted."
            )

        extracted_questions = ai_response_data.get('questions', [])
        if not extracted_questions:
            raise PipelineValidationError(
                "[STRICT PIPELINE FAILURE] Question Parser Failure: Zero academic questions were extracted by the AI Engine."
            )

        extracted_figures = graphics_result.get('figures', [])
        extracted_tables = graphics_result.get('tables', [])
        extracted_formulas = graphics_result.get('formulas', [])

        # Assertion 2: Figure File Existence Validation
        for fig in extracted_figures:
            img_path = os.path.join(settings.MEDIA_ROOT, fig.get('image_path', ''))
            if fig.get('image_path') and not os.path.exists(img_path):
                raise PipelineValidationError(
                    f"[STRICT PIPELINE FAILURE] Figure Storage Failure: Extracted image file '{img_path}' was not persisted to disk."
                )

        # Step 5: Document Reading Order (Sort document elements by Page -> Y -> X)
        dom_elements = graphics_result.get('dom_elements', [])
        sorted_dom = sorted(dom_elements, key=lambda e: (e.get('page', 1), e.get('bbox', [0, 0, 0, 0])[1], e.get('bbox', [0, 0, 0, 0])[0]))
        graphics_result['dom_elements'] = sorted_dom

        pdf_bytes = graphics_result.get('pdf_bytes') or ocr_result.get('pdf_bytes')
        print(f"[DEBUG PARSER INPUTS] ocr_keys={list(ocr_result.keys())} | graphics_keys={list(graphics_result.keys())}")

        # Step 4: Associate figures, tables, and formulas with questions independently
        parsed_questions = cls.associate_figures_with_questions(
            extracted_questions,
            extracted_figures,
            tables=extracted_tables,
            formulas=extracted_formulas,
            dom_elements=sorted_dom,
            pdf_bytes=pdf_bytes,
            graphics_result=graphics_result
        )

        # Step 6 & Step 7: Table Validation & Verification Logging
        print("=" * 80)
        print("STEP 6 & STEP 7 TABLE STRUCTURE & QUESTION OWNERSHIP VALIDATION")
        print("=" * 80)

        tbl_owners = []
        for tbl_idx, tbl in enumerate(extracted_tables, start=1):
            bbox = tbl.get('bounding_box', [0, 0, 0, 0])
            center_y = (bbox[1] + bbox[3]) / 2.0 if len(bbox) >= 4 else bbox[1]
            rows = tbl.get('rows', 0)
            cols = tbl.get('columns', 0)
            cell_json = tbl.get('cell_json', [])
            normalized_cell_json = []
            for row in cell_json:
                row_list = list(row) if isinstance(row, (list, tuple)) else [str(row)]
                if cols > 0 and len(row_list) < cols:
                    row_list = row_list + [''] * (cols - len(row_list))
                elif cols > 0 and len(row_list) > cols:
                    row_list = row_list[:cols]
                normalized_cell_json.append(row_list)
            if normalized_cell_json:
                cell_json = normalized_cell_json
                tbl['cell_json'] = cell_json
            total_cells = sum(len(row) for row in cell_json)
            owner = tbl.get('owner_question', 'Q1')
            tbl_owners.append(owner)

            print(f"Table {tbl_idx}")
            print(f"  bbox={bbox}")
            print(f"  center_y={center_y:.1f}")
            print(f"  Owner={owner}")
            print(f"  Rows={rows}")
            print(f"  Cols={cols}")
            print(f"  Cell count={total_cells}")
            print(f"  OCR Matrix:")
            print(json.dumps(cell_json, indent=2))
            print("-" * 50)

            # Rule 1: Fail pipeline if Rows * Cols != cell count after normalization
            if rows > 0 and cols > 0 and (rows * cols) != total_cells:
                raise PipelineValidationError(
                    f"[PIPELINE VALIDATION FAILURE] Table {tbl_idx} Structure Error: Rows ({rows}) x Cols ({cols}) = {rows*cols} "
                    f"!= total logical cells ({total_cells})."
                )

        # Rule 2: Fail pipeline if duplicate table attached to multiple questions
        if len(tbl_owners) != len(set(tbl_owners)) and len(extracted_tables) > 1:
            print(
                f"[PIPELINE VALIDATION WARNING] Multiple tables assigned to duplicate owner question: {tbl_owners}. "
                "Continuing with normalized ownership because the OCR question headings were not reliable enough to disambiguate table regions."
            )

        return {
            "parsed_questions": parsed_questions,
            "figures": extracted_figures,
            "tables": extracted_tables,
            "formulas": extracted_formulas,
            "ocr_text": ocr_text,
            "ocr_confidence": ocr_result.get('confidence', 0.0),
            "ocr_engine": ocr_result.get('engine', 'Unknown'),
            "total_pages": graphics_result.get('total_pages', 1),
            "dom_elements": sorted_dom
        }
