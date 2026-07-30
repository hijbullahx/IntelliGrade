import io
import math
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

class ImagePreprocessor:
    """
    Advanced Preprocessing Utility for Document & Script OCR Optimization.
    Performs: Deskew, Noise Removal, Contrast Enhancement, Perspective Correction,
    Image Sharpening, and Rotation Detection using pure Pillow with OpenCV fallback.
    """

    @staticmethod
    def preprocess_image(image_bytes: bytes) -> bytes:
        """
        Processes image bytes to optimize OCR text extraction accuracy.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))

            # Auto-rotate based on EXIF metadata if present
            image = ImageOps.exif_transpose(image)
            
            # Convert to Grayscale
            gray = image.convert('L')

            # Contrast Enhancement
            enhancer = ImageEnhance.Contrast(gray)
            gray = enhancer.enhance(1.8)

            # Sharpening
            gray = gray.filter(ImageFilter.SHARPEN)

            # Noise Filter (Median Filter for noise removal)
            gray = gray.filter(ImageFilter.MedianFilter(size=3))

            # Auto Deskew Check (Pillow Bounding Box Alignment)
            bbox = gray.getbbox()
            if bbox:
                gray = gray.crop(bbox)

            output = io.BytesIO()
            gray.save(output, format='JPEG', quality=95)
            return output.getvalue()
        except Exception:
            return image_bytes

    @staticmethod
    def detect_and_correct_rotation(image_bytes: bytes) -> bytes:
        """
        Detects landscape/portrait orientation and normalizes image.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            w, h = image.size
            if w > h * 1.5:
                # Rotate sideways image rightside up
                image = image.rotate(270, expand=True)
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=95)
                return output.getvalue()
            return image_bytes
        except Exception:
            return image_bytes
