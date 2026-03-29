# -*- coding: utf-8 -*-
"""
Nutrition Label Detector - v2
================================
Improvements over v1:
  - Selects BEST box (highest confidence * area score) not just first
  - Adds configurable padding around the crop
  - Filters out boxes that are too small or too large to be a nutrition table
  - Returns confidence score alongside the crop
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from pathlib import Path
from ultralytics import YOLO

from config.config import YOLO_MODEL_PATH, YOLO_CONFIDENCE


class NutritionLabelDetector:
    """Detects and crops nutrition labels from package images."""

    def __init__(self, model_path: Path = YOLO_MODEL_PATH):
        self.model = YOLO(str(model_path))

    def detect_and_crop(
        self,
        image_path: str,
        confidence: float = YOLO_CONFIDENCE,
        padding_px: int = 8,
    ) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Detect nutrition label and return the best-matching cropped image.

        Args:
            image_path:  Path to the package image
            confidence:  YOLO detection confidence threshold
            padding_px:  Pixels to pad around the detected box (prevents
                         border text from being clipped by OCR)

        Returns:
            (cropped_image, error_message)
        """
        try:
            results = self.model.predict(
                image_path, conf=confidence, verbose=False)

            boxes = results[0].boxes
            if len(boxes) == 0:
                return None, "No nutrition label detected"

            img = cv2.imread(str(image_path))
            if img is None:
                return None, f"Failed to load image: {image_path}"

            img_h, img_w = img.shape[:2]
            img_area = img_h * img_w

            # Score each detected box and pick the best one
            best_box  = None
            best_score = -1

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf  = float(box.conf[0])
                w     = x2 - x1
                h     = y2 - y1
                area  = w * h

                # Filter out boxes that are unreasonably small or large
                area_ratio = area / img_area
                if area_ratio < 0.02:   # < 2% of image → too small
                    continue
                if area_ratio > 0.95:   # > 95% of image → likely whole image
                    continue

                # Prefer taller-than-wide boxes (nutrition tables are portrait)
                # but don't penalize landscape boxes too harshly
                aspect_bonus = min(h / max(w, 1), 2.0) / 2.0   # 0–1

                # Score = confidence * sqrt(area_ratio) * aspect_bonus
                score = conf * (area_ratio ** 0.5) * (0.5 + 0.5 * aspect_bonus)

                if score > best_score:
                    best_score = score
                    best_box   = (x1, y1, x2, y2, conf)

            if best_box is None:
                # All boxes were filtered — fall back to highest-confidence box
                best_raw = max(boxes, key=lambda b: float(b.conf[0]))
                x1, y1, x2, y2 = map(int, best_raw.xyxy[0].tolist())
                conf = float(best_raw.conf[0])
                best_box = (x1, y1, x2, y2, conf)

            x1, y1, x2, y2, conf = best_box

            # Add padding, clamped to image boundaries
            x1p = max(0, x1 - padding_px)
            y1p = max(0, y1 - padding_px)
            x2p = min(img_w, x2 + padding_px)
            y2p = min(img_h, y2 + padding_px)

            cropped = img[y1p:y2p, x1p:x2p]

            print(f"  [Detector] Best box: ({x1},{y1})->({x2},{y2})  "
                  f"conf={conf:.2f}  padded=+{padding_px}px")

            return cropped, None

        except Exception as e:
            return None, f"Detection error: {str(e)}"

    def save_cropped_label(
        self, cropped_image: np.ndarray, output_path: str
    ) -> bool:
        try:
            cv2.imwrite(output_path, cropped_image)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False