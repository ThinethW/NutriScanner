# -*- coding: utf-8 -*-
"""
NutriScanner - Label Scan Pipeline v2
"""

import numpy as np
from typing import Dict, Tuple, Optional

from detector   import NutritionLabelDetector
from ocr_engine import OCREngine
from row_parser import RowBasedParser


class PackagedFoodScanner:
    """
    Main class imported by main.py.
    Wraps the full detection → OCR → parsing pipeline.
    Returns dicts compatible with NutriScanner in main.py.
    """

    def __init__(self):
        self.detector   = NutritionLabelDetector()
        self.ocr        = OCREngine()
        self.row_parser = RowBasedParser()

    def scan(self, image_path: str) -> Dict:
        """
        Full pipeline: image path → nutrition dict.

        Returns:
            {'success': True,  'data': {nutrition values}}
            {'success': False, 'error': 'reason'}
        """
        try:
            # Step 1: Detect and crop
            print("\n[Scanner] Step 1: Detecting nutrition label...")
            cropped, err = self.detector.detect_and_crop(
                image_path, padding_px=8)
            if err:
                return {'success': False, 'error': f"Detection failed: {err}"}
            print(f"[Scanner] Crop: {cropped.shape[1]}x{cropped.shape[0]} px")

            # Step 2: OCR with bounding boxes
            print("[Scanner] Step 2: Running OCR...")
            ocr_results, err = self.ocr.extract_structured(cropped)
            if err:
                return {'success': False, 'error': f"OCR failed: {err}"}
            print(f"[Scanner] OCR: {len(ocr_results)} text items detected")

            # Step 3: Group into spatial rows
            print("[Scanner] Step 3: Grouping into rows...")
            rows = self.ocr.group_into_rows(ocr_results)
            print(f"[Scanner] Formed {len(rows)} rows")

            # Build flat fallback text from properly-ordered rows
            fallback_text = self.ocr.rows_to_text(rows)

            # Step 4: Parse nutrition (row-based with flat fallback)
            print("[Scanner] Step 4: Parsing nutrition data...")
            nutrition = self.row_parser.parse_from_rows(rows, fallback_text)

            if not nutrition:
                return {'success': False,
                        'error': 'Parser returned empty result'}

            return {'success': True, 'data': nutrition}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def scan_from_image(self, image: np.ndarray) -> Dict:
        """
        Skip YOLO detection — use when you already have a cropped image array.

        Returns same format as scan():
            {'success': True,  'data': {...}}
            {'success': False, 'error': '...'}
        """
        try:
            print("[Scanner] Using provided image array (no detection)")

            ocr_results, err = self.ocr.extract_structured(image)
            if err:
                return {'success': False, 'error': f"OCR failed: {err}"}

            rows = self.ocr.group_into_rows(ocr_results)
            fallback_text = self.ocr.rows_to_text(rows)
            nutrition = self.row_parser.parse_from_rows(rows, fallback_text)

            if not nutrition:
                return {'success': False,
                        'error': 'Parser returned empty result'}

            return {'success': True, 'data': nutrition}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}


# Alias — keeps any old imports working
LabelScanner = PackagedFoodScanner