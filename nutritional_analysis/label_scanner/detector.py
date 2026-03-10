"""
Nutrition label detection using YOLO
"""
from ultralytics import YOLO
import cv2
import numpy as np
from typing import Tuple, Optional
from pathlib import Path

from config.config import YOLO_MODEL_PATH, YOLO_CONFIDENCE


class NutritionLabelDetector:
    """Detects and crops nutrition labels from package images"""

    def __init__(self, model_path: Path = YOLO_MODEL_PATH):
        """Initialize YOLO model"""
        self.model = YOLO(str(model_path))

    def detect_and_crop(
            self,
            image_path: str,
            confidence: float = YOLO_CONFIDENCE
    ) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Detect nutrition label and return cropped image

        Args:
            image_path: Path to package image
            confidence: Detection confidence threshold

        Returns:
            Tuple of (cropped_image, error_message)
        """
        try:
            # Run detection
            results = self.model.predict(
                image_path,
                conf=confidence,
                verbose=False
            )

            # Check if label detected
            if len(results[0].boxes) == 0:
                return None, "No nutrition label detected"

            # Get bounding box
            box = results[0].boxes[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # Crop label
            img = cv2.imread(str(image_path))
            if img is None:
                return None, f"Failed to load image: {image_path}"

            cropped = img[y1:y2, x1:x2]

            return cropped, None

        except Exception as e:
            return None, f"Detection error: {str(e)}"

    def save_cropped_label(
            self,
            cropped_image: np.ndarray,
            output_path: str
    ) -> bool:
        """Save cropped label to file"""
        try:
            cv2.imwrite(output_path, cropped_image)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False