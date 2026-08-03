import os
import io
import json
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont


class LayoutVisualizer:
    """
    Renders visual bounding box layout overlays (layout_debug.png)
    drawing color-coded bounding boxes and labels for questions, figures, tables, formulas, and captions.
    """

    COLOR_MAP = {
        "question": (0, 102, 255),            # Blue
        "VALID_FIGURE": (0, 204, 102),        # Green
        "figure": (0, 204, 102),              # Green
        "REJECT_TEXT_LINE": (255, 51, 51),    # Red
        "table": (255, 51, 51),               # Red
        "REJECT_PAGE_BORDER": (120, 120, 120),# Gray
        "text_block": (120, 120, 120),        # Gray
        "caption": (255, 204, 0),             # Yellow
        "formula": (153, 51, 255)             # Purple
    }

    @classmethod
    def render_layout_debug_overlay(
        cls,
        page_image_bytes: bytes,
        dom_elements: List[Dict[str, Any]],
        parsed_questions: List[Dict[str, Any]],
        output_path: str,
        all_contours: List[Dict[str, Any]] = None
    ) -> bool:
        """
        Renders bounding box overlays with distinct color codes and text badges onto the 300 DPI page image:
        - Blue: Questions
        - Green: Valid Figures
        - Red: Ignored Text Lines
        - Gray: Rejected Page Contour / Border
        """
        try:
            image = Image.open(io.BytesIO(page_image_bytes)).convert("RGB")
            draw = ImageDraw.Draw(image)
            img_w, img_h = image.size

            try:
                font = ImageFont.truetype("arial.ttf", size=24)
                small_font = ImageFont.truetype("arial.ttf", size=16)
            except Exception:
                font = ImageFont.load_default()
                small_font = font

            # 1. Draw All Contours (Valid Figures = Green, Rejected Text = Red, Page Border = Gray)
            if all_contours:
                for c_idx, c_info in enumerate(all_contours):
                    c_type = c_info.get('type', 'REJECT_TEXT_LINE')
                    color = cls.COLOR_MAP.get(c_type, (120, 120, 120))
                    bbox = c_info.get('bbox')
                    if not bbox or len(bbox) < 4:
                        continue
                    x0, y0, x1, y1 = bbox[0], bbox[1], bbox[2], bbox[3]

                    draw.rectangle([x0, y0, x1, y1], outline=color, width=3)
                    area = c_info.get('area', (x1-x0)*(y1-y0))
                    lbl = f"{c_type} (Area: {area})"
                    draw.rectangle([x0, max(0, y0 - 20), x0 + 220, max(20, y0)], fill=color)
                    draw.text((x0 + 4, max(0, y0 - 18)), lbl, fill=(255, 255, 255), font=small_font)

            # 2. Draw DOM Elements
            for elem_idx, elem in enumerate(dom_elements):
                elem_type = elem.get('type', 'text_block')
                bbox = elem.get('bbox')
                if not bbox or len(bbox) < 4:
                    continue

                color = cls.COLOR_MAP.get(elem_type, (150, 150, 150))
                x0, y0, x1, y1 = bbox[0], bbox[1], bbox[2], bbox[3]
                if x1 <= 1.0 and y1 <= 1.0:
                    x0, y0, x1, y1 = x0 * img_w, y0 * img_h, x1 * img_w, y1 * img_h

                draw.rectangle([x0, y0, x1, y1], outline=color, width=4)
                tag_label = f"F{elem_idx+1}" if elem_type == 'figure' else f"{elem_type.upper()} {elem_idx+1}"
                draw.rectangle([x0, max(0, y0 - 25), x0 + 120, max(25, y0)], fill=color)
                draw.text((x0 + 5, max(0, y0 - 23)), tag_label, fill=(255, 255, 255), font=small_font)

            # 3. Draw Question Bounding Boxes (Blue)
            for q_idx, q in enumerate(parsed_questions):
                q_num = q.get('question_number', f"Q{q_idx+1}")
                assoc_figs = q.get('associated_figures', [])

                q_top = 40 + (q_idx * (img_h // max(len(parsed_questions), 1)))
                q_bottom = q_top + (img_h // max(len(parsed_questions), 1)) - 30

                color = cls.COLOR_MAP["question"]
                draw.rectangle([15, q_top, img_w - 15, q_bottom], outline=color, width=5)

                fig_count_txt = f" ({len(assoc_figs)} figs)" if assoc_figs else ""
                lbl_text = f"QUESTION {q_num}{fig_count_txt}"
                draw.rectangle([20, q_top + 5, 280, q_top + 35], fill=color)
                draw.text((25, q_top + 8), lbl_text, fill=(255, 255, 255), font=font)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path, "PNG")
            print(f"[LAYOUT VISUALIZER] Saved visual debug overlay to '{output_path}' ({img_w}x{img_h}px)")
            return True
        except Exception as e:
            print(f"[LAYOUT VISUALIZER WARNING] Failed to render layout overlay: {e}")
            return False
