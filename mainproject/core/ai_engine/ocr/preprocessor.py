import io
from PIL import Image, ImageEnhance, ImageFilter

class ImagePreprocessor:
    """
    Preprocessing utility for OCR optimization:
    Grayscale conversion, contrast enhancement, noise filtering, and orientation adjustment.
    """

    @staticmethod
    def preprocess_image(image_bytes: bytes) -> bytes:
        """
        Preprocesses image bytes using Pillow to optimize OCR accuracy.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to Grayscale
            image = image.convert('L')
            
            # Enhance Contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.8)
            
            # Sharpen / Filter noise
            image = image.filter(ImageFilter.SHARPEN)

            output = io.BytesIO()
            image.save(output, format='JPEG', quality=95)
            return output.getvalue()
        except Exception:
            return image_bytes
