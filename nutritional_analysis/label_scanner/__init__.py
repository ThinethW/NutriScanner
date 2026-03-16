"""
Packaged Food Label Scanner
Complete pipeline for scanning nutrition labels
"""
from .detector import NutritionLabelDetector
from .ocr_engine import OCREngine
from .parser import NutritionParser
import cv2
from typing import Dict, Any


class PackagedFoodScanner:
    """Complete pipeline for scanning packaged food nutrition labels"""

    def __init__(self):
        self.detector = NutritionLabelDetector()
        self.ocr = OCREngine()
        self.parser = NutritionParser()

    def scan(self, image_path: str, save_cropped: bool = False) -> Dict[str, Any]:
        """
        Complete scan pipeline

        Args:
            image_path: Path to package image
            save_cropped: Whether to save cropped label

        Returns:
            Dictionary with nutrition data or error
        """
        # Step 1: Detect and crop label
        cropped_image, error = self.detector.detect_and_crop(image_path)
        if error:
            return {"success": False, "error": error}

        if save_cropped:
            self.detector.save_cropped_label(
                cropped_image,
                'temp_cropped_label.jpg'
            )

        # Step 2: Extract text
        ocr_text, error = self.ocr.extract_text(cropped_image)
        if error:
            return {"success": False, "error": error}

        # Step 3: Parse nutrition data
        nutrition_data = self.parser.parse(ocr_text)

        # Step 4: Validate
        is_valid, missing = self.parser.validate(nutrition_data)

        return {
            "success": True,
            "data": nutrition_data,
            "is_complete": is_valid,
            "missing_fields": missing if not is_valid else [],
            "raw_text": ocr_text
        }


__all__ = [
    'PackagedFoodScanner',
    'NutritionLabelDetector',
    'OCREngine',
    'NutritionParser'
]