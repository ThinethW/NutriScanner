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

    def extract_text(self, image: np.ndarray) -> Tuple[Optional[str], Optional[str]]:
        try:
            result = self.ocr.ocr(image, cls=False)

            if not result or not result[0]:
                return None, "No text detected"

            items = []
            for line in result[0]:
                box = line[0]  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                text = line[1][0]
                # top-left point
                x = box[0][0]
                y = box[0][1]
                items.append((y, x, text))

            # Sort: top-to-bottom, then left-to-right
            items.sort(key=lambda t: (t[0], t[1]))

            # Join with newlines to keep "rows" separate
            ordered_lines = [t[2] for t in items]
            full_text = "\n".join(ordered_lines)

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