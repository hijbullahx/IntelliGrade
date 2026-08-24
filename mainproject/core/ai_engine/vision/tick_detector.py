import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional


class TickDetector:
    """
    OpenCV Computer Vision Engine for MCQ Option Mark Classification.
    
    Detects and classifies mark types in option Regions of Interest (ROI):
    - Valid Positive Marks: Tick (✓), Filled Circle/Bubble (⬤), Circle around label
    - Invalidation: Cross Mark / Struck Out (✗)
    - None / Unmarked
    
    Option Label Schemes:
    - Alphabetic: A, B, C, D / a, b, c, d
    - Numeric: 1, 2, 3, 4
    - Roman Numerals: i, ii, iii, iv / I, II, III, IV
    """

    SCHEMES = {
        'ALPHA_UPPER': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
        'ALPHA_LOWER': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
        'NUMERIC': ['1', '2', '3', '4', '5', '6', '7', '8'],
        'ROMAN_LOWER': ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii'],
        'ROMAN_UPPER': ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'],
    }

    @classmethod
    def get_label_for_index(cls, index: int, scheme: str = 'ALPHA_UPPER') -> str:
        """Returns the corresponding label string for a generic 0-based option index."""
        labels = cls.SCHEMES.get(scheme.upper(), cls.SCHEMES['ALPHA_UPPER'])
        if 0 <= index < len(labels):
            return labels[index]
        return str(index + 1)

    @classmethod
    def detect_mark_type(cls, option_roi: np.ndarray) -> Tuple[str, float]:
        """
        Classifies the mark type inside an option ROI image.
        
        Returns:
            Tuple[mark_type, confidence_score]
            mark_type in: ["TICK", "FILLED_BUBBLE", "CIRCLED_LABEL", "CROSS_OUT", "UNMARKED"]
        """
        if option_roi is None or option_roi.size == 0:
            return "UNMARKED", 0.0

        # Convert to grayscale if color
        if len(option_roi.shape) == 3:
            gray = cv2.cvtColor(option_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = option_roi.copy()

        # Gaussian blur & otsu thresholding for clean binarization
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        total_pixels = binary.shape[0] * binary.shape[1]
        if total_pixels == 0:
            return "UNMARKED", 0.0

        non_zero_pixels = cv2.countNonZero(binary)
        fill_ratio = non_zero_pixels / float(total_pixels)

        # 1. Clean / Unmarked ROI check (minimal ink/noise)
        if fill_ratio < 0.05:
            return "UNMARKED", 0.95

        # 2. Check for Filled Circle / Bubble (High pixel fill ratio > 42%)
        if fill_ratio >= 0.42:
            return "FILLED_BUBBLE", min(1.0, round(fill_ratio * 1.8, 2))

        # Find contours inside ROI for structural feature analysis
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return "UNMARKED", 0.90

        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)

        if area < 10 or perimeter == 0:
            return "UNMARKED", 0.85

        # Feature Extraction
        x, y, w, h = cv2.boundingRect(largest_contour)
        aspect_ratio = float(w) / float(h)
        hull = cv2.convexHull(largest_contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / float(hull_area) if hull_area > 0 else 0.0

        # Circularity score (4 * pi * Area / Perimeter^2)
        circularity = (4.0 * np.pi * area) / (perimeter * perimeter)

        # Quadrant ink distribution analysis
        h_mid, w_mid = binary.shape[0] // 2, binary.shape[1] // 2
        q_tl = cv2.countNonZero(binary[:h_mid, :w_mid])
        q_tr = cv2.countNonZero(binary[:h_mid, w_mid:])
        q_bl = cv2.countNonZero(binary[h_mid:, :w_mid])
        q_br = cv2.countNonZero(binary[h_mid:, w_mid:])
        min_q_ink = min(q_tl, q_tr, q_bl, q_br)

        # 3. Check for Explicit Invalidation / Negation (Cross Mark ✗)
        # Crosses have intersecting diagonal lines (ink in all 4 quadrants) and near 1.0 aspect ratio
        if 0.65 <= aspect_ratio <= 1.4 and min_q_ink > 0.01 * total_pixels and fill_ratio < 0.40:
            # Check lines using Hough transform on ROI skeleton/edges
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=12, minLineLength=8, maxLineGap=5)
            if lines is not None and len(lines) >= 2:
                angles = []
                for line in lines:
                    pts = line.ravel()
                    if len(pts) == 4:
                        x1, y1, x2, y2 = pts
                        angle = np.degrees(np.arctan2(float(y2 - y1), float(x2 - x1)))
                        angles.append(angle)
                
                # Check for opposing diagonal angles
                has_positive_diag = any(15 <= abs(a) <= 75 for a in angles)
                has_negative_diag = any(105 <= abs(a) <= 165 for a in angles)
                if has_positive_diag and has_negative_diag:
                    return "CROSS_OUT", 0.95

            # Fallback 4-quadrant check for X mark (all 4 quadrants populated with balance)
            q_ratios = [q_tl, q_tr, q_bl, q_br]
            max_q = max(q_ratios)
            if max_q > 0 and all(q / float(max_q) > 0.25 for q in q_ratios):
                return "CROSS_OUT", 0.90

        # 4. Check for Tick / Checkmark (✓)
        # Ticks are asymmetric: usually high ink in bottom-right/top-right, low ink in top-left
        if 0.35 <= aspect_ratio <= 2.5 and 0.20 <= solidity <= 0.75:
            if q_br + q_tr >= q_tl * 1.2:
                return "TICK", round(min(1.0, 0.75 + (area / total_pixels)), 2)

        # 5. Check for Circle around option label
        if 0.75 <= aspect_ratio <= 1.25 and circularity > 0.55 and solidity > 0.60:
            return "CIRCLED_LABEL", round(min(1.0, circularity), 2)

        # Default fallback: if moderate ink present, treat as valid positive tick mark
        if fill_ratio >= 0.12:
            return "TICK", 0.75

        return "UNMARKED", 0.80

    @classmethod
    def evaluate_question_options(
        cls,
        option_rois: List[np.ndarray],
        scheme: str = 'ALPHA_UPPER'
    ) -> Dict[str, Any]:
        """
        Processes all option ROIs for a single question block.
        
        Args:
            option_rois: List of image arrays for each option (index 0, 1, 2, 3...)
            scheme: Label scheme ('ALPHA_UPPER', 'ALPHA_LOWER', 'NUMERIC', 'ROMAN_LOWER', 'ROMAN_UPPER')
            
        Returns:
            Dict containing:
                - status: 'VALID', 'NOT_ATTEMPTED', or 'REJECTED_MULTIPLE_MARKS'
                - detected: List of option label strings (e.g. ['A'] or ['1', '3'])
                - mark_type: Human readable mark classification summary
                - options_detail: Detailed breakdown per option index
        """
        positive_marks = []
        rejected_marks = []
        options_detail = []
        mark_types_found = []

        for idx, roi in enumerate(option_rois):
            label = cls.get_label_for_index(idx, scheme)
            mark_type, conf = cls.detect_mark_type(roi)
            
            options_detail.append({
                'index': idx,
                'label': label,
                'mark_type': mark_type,
                'confidence': conf
            })

            if mark_type in ["TICK", "FILLED_BUBBLE", "CIRCLED_LABEL"]:
                positive_marks.append(label)
                mark_types_found.append(mark_type)
            elif mark_type == "CROSS_OUT":
                rejected_marks.append(label)

        # Apply Resolution Logic
        if len(positive_marks) == 1:
            status = 'VALID'
            detected = positive_marks
            primary_mark = mark_types_found[0]
            if primary_mark == "TICK":
                mark_type_label = "Tick (✓)"
            elif primary_mark == "FILLED_BUBBLE":
                mark_type_label = "Filled Bubble (⬤)"
            elif primary_mark == "CIRCLED_LABEL":
                mark_type_label = "Circled Label"
            else:
                mark_type_label = "Valid Selection"
        elif len(positive_marks) == 0:
            status = 'NOT_ATTEMPTED'
            detected = []
            mark_type_label = "None"
        else:
            status = 'REJECTED_MULTIPLE_MARKS'
            detected = positive_marks
            mark_type_label = "Multi-Fill / Multi-Mark Rejection"

        return {
            'status': status,
            'detected': detected,
            'mark_type': mark_type_label,
            'options_detail': options_detail
        }
