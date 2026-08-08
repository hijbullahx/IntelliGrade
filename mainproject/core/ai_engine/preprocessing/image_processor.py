import os
import io
import cv2
import fitz
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple, Optional
from django.conf import settings
from django.core.files.base import ContentFile

class ImagePreprocessingService:
    """
    Production Image Preprocessing & PDF Compilation Engine for IntelliGrade (v3.0).
    Performs Computer Vision pipeline: Ink Color Filtering, Orientation Detection,
    Deskewing, Perspective Correction, Shadow Removal, Background Whitening,
    Contrast Enhancement, and Multi-Image PDF Compilation.
    """

    @classmethod
    def process_image(
        cls,
        image_input: Any,
        options: Optional[Dict[str, Any]] = None,
        trace_dir: Optional[str] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes the full Computer Vision enhancement pipeline on a single page image.
        Returns the enhanced OpenCV image array (BGR) and a metadata dictionary.
        """
        if options is None:
            options = {}

        # 1. Load image
        img = cls._load_image_array(image_input)
        if img is None:
            raise ValueError("Failed to decode image input into OpenCV array.")

        metadata = {'original_shape': img.shape[:2]}

        # Create trace directory if requested
        if trace_dir:
            os.makedirs(trace_dir, exist_ok=True)
            cv2.imwrite(os.path.join(trace_dir, "01_original.png"), img)

        # 2. Color Pen Mark Filtering (Ignore Teacher Ink)
        ink_color = options.get('ink_color', 'None')
        if ink_color and ink_color.lower() != 'none':
            img = cls._remove_colored_ink(img, ink_color)
            if trace_dir:
                cv2.imwrite(os.path.join(trace_dir, "02_ink_filtered.png"), img)

        # 3. Manual / Auto Rotation
        rotation_angle = int(options.get('rotation_angle', 0))
        if rotation_angle != 0:
            img = cls._rotate_image(img, rotation_angle)
            if trace_dir:
                cv2.imwrite(os.path.join(trace_dir, "03_rotated.png"), img)

        # 4. Deskew (Tilt Correction)
        if options.get('deskew', True):
            img, skew_angle = cls._deskew(img)
            metadata['skew_angle'] = skew_angle
            if trace_dir:
                cv2.imwrite(os.path.join(trace_dir, "04_deskewed.png"), img)

        # 5. Shadow Removal & Background Whitening
        if options.get('background_whitening', True) or options.get('shadow_removal', True):
            img = cls._remove_shadows_and_whiten(img)
            if trace_dir:
                cv2.imwrite(os.path.join(trace_dir, "05_shadow_removed.png"), img)

        # 6. Contrast Enhancement (CLAHE)
        if options.get('contrast_enhancement', True):
            img = cls._enhance_contrast(img)
            if trace_dir:
                cv2.imwrite(os.path.join(trace_dir, "06_contrast_enhanced.png"), img)

        # 7. Denoising
        if options.get('noise_removal', True):
            img = cv2.fastNlMeansDenoisingColored(img, None, 5, 5, 7, 21)
            if trace_dir:
                cv2.imwrite(os.path.join(trace_dir, "07_denoised.png"), img)

        return img, metadata

    @classmethod
    def stamp_page_header(cls, img_bgr: np.ndarray, page_num: int, total_pages: int) -> np.ndarray:
        """
        Stamps a high-visibility, crisp top banner on the page image indicating 'PAGE X OF Y'.
        Ensures teachers can immediately identify page numbers when viewing PDF in another tab.
        """
        if img_bgr is None:
            return img_bgr

        img = img_bgr.copy()
        h, w = img.shape[:2]

        banner_h = max(45, int(h * 0.035))
        font_scale = max(0.7, (banner_h / 45.0) * 0.8)
        thickness = max(2, int(font_scale * 2.2))

        # Top banner background: Solid dark navy/slate (15, 23, 42)
        cv2.rectangle(img, (0, 0), (w, banner_h), (42, 23, 15), -1)

        # Bottom accent border: Vibrant cyan/teal (235, 175, 0)
        cv2.rectangle(img, (0, banner_h - 3), (w, banner_h), (235, 175, 0), -1)

        header_text = f"PAGE {page_num} OF {total_pages}   |   INTELLIGRADE STUDENT ANSWER SCRIPT"

        (text_w, text_h), _ = cv2.getTextSize(header_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_x = max(15, (w - text_w) // 2)
        text_y = (banner_h + text_h) // 2 - 2

        cv2.putText(img, header_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        return img

    @classmethod
    def compile_images_to_pdf(
        cls,
        image_arrays_or_paths: List[Any],
        output_pdf_path: str,
        stamp_page_numbers: bool = True
    ) -> Tuple[str, int]:
        """
        Compiles a list of processed image arrays or paths into a single standardized PDF file.
        Stamps a clear 'PAGE X OF Y' header on every page for clear tab previewing.
        Returns the output PDF file path and total page count.
        """
        total_pages = len(image_arrays_or_paths)
        pil_images = []
        for idx, img_item in enumerate(image_arrays_or_paths, start=1):
            img_bgr = cls._load_image_array(img_item)
            if img_bgr is not None:
                if stamp_page_numbers:
                    img_bgr = cls.stamp_page_header(img_bgr, page_num=idx, total_pages=total_pages)
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb)
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                pil_images.append(pil_img)

        if not pil_images:
            raise ValueError("No valid image files found to compile into PDF.")

        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        pil_images[0].save(output_pdf_path, "PDF", save_all=True, append_images=pil_images[1:])

        return output_pdf_path, len(pil_images)

    # Helper methods for computer vision processing
    @classmethod
    def _load_image_array(cls, image_input: Any) -> Optional[np.ndarray]:
        if isinstance(image_input, np.ndarray):
            return image_input.copy()
        if isinstance(image_input, str) and os.path.exists(image_input):
            return cv2.imread(image_input)
        if isinstance(image_input, (bytes, bytearray)):
            nparr = np.frombuffer(image_input, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return None

    @classmethod
    def _rotate_image(cls, img: np.ndarray, angle: int) -> np.ndarray:
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    @classmethod
    def _remove_colored_ink(cls, img: np.ndarray, color_name: str) -> np.ndarray:
        """
        Masks out teacher ink marks (Red, Blue, Green, Yellow, Black) using HSV thresholds.
        Replaces masked pen marks with white background pixels.
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        color = color_name.lower().strip()
        mask = None

        if color == 'red':
            mask1 = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255]))
            mask2 = cv2.inRange(hsv, np.array([170, 70, 50]), np.array([180, 255, 255]))
            mask = cv2.bitwise_or(mask1, mask2)
        elif color == 'blue':
            mask = cv2.inRange(hsv, np.array([90, 70, 50]), np.array([130, 255, 255]))
        elif color == 'green':
            mask = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
        elif color == 'yellow':
            mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255]))
        elif color == 'black':
            mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 50]))

        if mask is not None:
            result = img.copy()
            result[mask > 0] = (255, 255, 255)
            return result
        return img

    @classmethod
    def _deskew(cls, img: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Calculates text orientation angle and deskews image.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        dilate = cv2.dilate(thresh, kernel, iterations=5)

        contours, _ = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        angles = []
        for c in contours:
            min_rect = cv2.minAreaRect(c)
            angle = min_rect[-1]
            if angle < -45:
                angle = 90 + angle
            if abs(angle) < 15.0:
                angles.append(angle)

        median_angle = float(np.median(angles)) if angles else 0.0
        if abs(median_angle) > 0.5:
            h, w = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return img, round(median_angle, 2)

    @classmethod
    def _remove_shadows_and_whiten(cls, img: np.ndarray) -> np.ndarray:
        """
        Removes uneven page shadows and whitens document background using morphological dilation.
        """
        rgb_planes = cv2.split(img)
        result_planes = []
        for plane in rgb_planes:
            dilated = cv2.dilate(plane, np.ones((7, 7), np.uint8))
            bg_img = cv2.medianBlur(dilated, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(norm_img)

        return cv2.merge(result_planes)

    @classmethod
    def _enhance_contrast(cls, img: np.ndarray) -> np.ndarray:
        """
        Applies CLAHE (Contrast Limited Adaptive Histogram Equalization) to LAB color channels.
        """
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
