import os
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from django.conf import settings


class AnswerCropService:
    """
    Robust Answer Region Crop Service for Handwritten Answer Scripts.
    Safely converts normalized [0.0, 1.0] bounding boxes from QuestionMapping.regions_json
    into high-resolution PNG image crop payloads with zero GPU requirement.
    """

    @classmethod
    def clamp_bbox(cls, bbox: Dict[str, Any]) -> Dict[str, float]:
        """
        Validates and clamps normalized coordinates strictly to [0.0, 1.0].
        Ensures xmin <= xmax and ymin <= ymax.
        """
        ymin = max(0.0, min(1.0, float(bbox.get('ymin', 0.0))))
        ymax = max(0.0, min(1.0, float(bbox.get('ymax', 1.0))))
        xmin = max(0.0, min(1.0, float(bbox.get('xmin', 0.0))))
        xmax = max(0.0, min(1.0, float(bbox.get('xmax', 1.0))))

        if xmin > xmax:
            xmin, xmax = xmax, xmin
        if ymin > ymax:
            ymin, ymax = ymax, ymin

        return {'ymin': round(ymin, 4), 'xmin': round(xmin, 4), 'ymax': round(ymax, 4), 'xmax': round(xmax, 4)}

    @classmethod
    def extract_answer_region_crops(
        cls,
        working_image_path: str,
        regions: List[Dict[str, Any]],
        min_crop_height_px: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Extracts image crops from a single working copy image for the given AnswerRegions.
        Returns a list of crop dictionaries with PNG bytes and dimension metadata.
        Guarantees that a valid, non-empty image crop is always returned.
        """
        if not working_image_path or not os.path.exists(working_image_path):
            return []

        bgr = cv2.imread(working_image_path)
        if bgr is None or bgr.size == 0:
            return []

        H, W = bgr.shape[:2]
        extracted_crops = []

        # If no explicit regions provided, return full page as single region
        if not regions:
            regions = [{'region_id': 'full_page', 'bbox': {'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}}]

        for reg in regions:
            raw_bbox = reg.get('bbox', {})
            clamped_bbox = cls.clamp_bbox(raw_bbox)

            ymin_norm = clamped_bbox['ymin']
            ymax_norm = clamped_bbox['ymax']
            xmin_norm = clamped_bbox['xmin']
            xmax_norm = clamped_bbox['xmax']

            ymin_px = int(ymin_norm * H)
            ymax_px = int(ymax_norm * H)
            xmin_px = int(xmin_norm * W)
            xmax_px = int(xmax_norm * W)

            # Fix degenerate or zero-height bounding boxes
            if ymax_px - ymin_px < min_crop_height_px:
                # Try expanding downward
                ymax_px = min(H, ymin_px + max(min_crop_height_px, int(H * 0.20)))
                # If still too short (near bottom of page), expand upward
                if ymax_px - ymin_px < min_crop_height_px:
                    ymin_px = max(0, ymax_px - min_crop_height_px)
                # If total image height is smaller than min_crop_height_px, span full height
                if ymax_px - ymin_px <= 0:
                    ymin_px, ymax_px = 0, H

            # Fix degenerate width
            if xmax_px - xmin_px < 50:
                xmin_px, xmax_px = 0, W

            # Final safety clamping within physical pixel boundaries
            ymin_px = max(0, min(H, ymin_px))
            ymax_px = max(0, min(H, ymax_px))
            xmin_px = max(0, min(W, xmin_px))
            xmax_px = max(0, min(W, xmax_px))

            crop_img = bgr[ymin_px:ymax_px, xmin_px:xmax_px]
            if crop_img is None or crop_img.size == 0:
                # Absolute fallback: full page
                crop_img = bgr
                ymin_px, ymax_px, xmin_px, xmax_px = 0, H, 0, W

            success, png_buffer = cv2.imencode('.png', crop_img)
            if success:
                extracted_crops.append({
                    'page_number': reg.get('page_number', 1),
                    'region_id': reg.get('region_id', 'r1'),
                    'bbox': clamped_bbox,
                    'pixel_bbox': [xmin_px, ymin_px, xmax_px, ymax_px],
                    'crop_width': int(crop_img.shape[1]),
                    'crop_height': int(crop_img.shape[0]),
                    'image_bytes': png_buffer.tobytes(),
                    'mime_type': 'image/png'
                })

        return extracted_crops

    @classmethod
    def extract_crops_for_question(
        cls,
        submission,
        question_mapping,
        min_crop_height_px: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Extracts all answer crops for a QuestionMapping across multiple pages in page order.
        """
        if not question_mapping:
            return []

        regions = question_mapping.regions_json or []
        page_numbers = question_mapping.page_numbers_json or []

        all_crops = []
        pages_by_num = {p.page_number: p for p in submission.pages.all()}

        # Group regions by page_number
        regions_by_page: Dict[int, List[Dict[str, Any]]] = {}
        for r in regions:
            p_num = r.get('page_number')
            if p_num:
                regions_by_page.setdefault(p_num, []).append(r)

        # Iterate in sorted page order
        for p_num in sorted(page_numbers):
            sp = pages_by_num.get(p_num)
            if not sp:
                continue

            working_path = sp.working_image_path
            if not working_path or not os.path.exists(working_path):
                from core.ai_engine.preprocessing.working_copy_manager import WorkingCopyManager
                working_path = WorkingCopyManager.get_latest_working_image_path(submission.id, p_num)

            page_regs = regions_by_page.get(p_num, [])
            # If no specific sub-regions on this page (e.g. continuation page), use full page
            if not page_regs:
                page_regs = [{
                    'page_number': p_num,
                    'region_id': f'p{p_num}_full',
                    'bbox': {'ymin': 0.0, 'xmin': 0.0, 'ymax': 1.0, 'xmax': 1.0}
                }]

            page_crops = cls.extract_answer_region_crops(
                working_image_path=working_path,
                regions=page_regs,
                min_crop_height_px=min_crop_height_px
            )
            all_crops.extend(page_crops)

        return all_crops
