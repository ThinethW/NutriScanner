"""Package Food Label Scanner"""
from .detector import NutritionLabelDetector
from .ocr_engine import OCREngine
from .parser import NutritionParser
from typing import Dict
import cv2


class PackagedFoodScanner:
    """Scans nutrition labels from packaged food"""

    def __init__(self):
        self.detector = NutritionLabelDetector()
        self.ocr = OCREngine()
        self.parser = NutritionParser()

    def scan(self, image_path: str) -> Dict:
        """
        Complete pipeline: Image → Detection → OCR → Parsed Data

        Returns:
            {
                "success": bool,
                "data": dict,  # Nutrition data
                "error": str   # If failed
            }
        """
        # Step 1: Detect label
        cropped, error = self.detector.detect_and_crop(image_path)
        if error:
            return {"success": False, "error": error}

        # Step 2: OCR
        text, error = self.ocr.extract_text(cropped)
        if error:
            return {"success": False, "error": error}

        # Step 3: Parse
        nutrition = self.parser.parse(text)

        return {
            "success": True,
            "data": nutrition,
            "raw_text": text
        }