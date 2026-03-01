"""
OCR text extraction from nutrition labels
"""
from paddleocr import PaddleOCR
from typing import Tuple, Optional
import numpy as np

from config.config import OCR_CONFIG


class OCREngine:
    """Extracts text from nutrition label images"""

    def __init__(self):
        """Initialize PaddleOCR"""
        self.ocr = PaddleOCR(**OCR_CONFIG)

    def extract_text(
            self,
            image: np.ndarray
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract text from image

        Args:
            image: Numpy array of image

        Returns:
            Tuple of (extracted_text, error_message)
        """
        try:
            # Run OCR
            result = self.ocr.ocr(image, cls=False)

            # Check if text detected
            if not result or not result[0]:
                return None, "No text detected"

            # Combine all text lines
            text_lines = [line[1][0] for line in result[0]]
            full_text = ' '.join(text_lines)

            return full_text, None

        except Exception as e:
            return None, f"OCR error: {str(e)}"

    def extract_with_confidence(
            self,
            image: np.ndarray
    ) -> Tuple[Optional[list], Optional[str]]:
        """Extract text with confidence scores"""
        try:
            result = self.ocr.ocr(image, cls=False)

            if not result or not result[0]:
                return None, "No text detected"

            # Return list of (text, confidence) tuples
            text_data = [(line[1][0], line[1][1]) for line in result[0]]

            return text_data, None

        except Exception as e:
            return None, f"OCR error: {str(e)}"