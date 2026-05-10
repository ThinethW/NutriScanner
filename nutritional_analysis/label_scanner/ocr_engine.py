# -*- coding: utf-8 -*-
"""
OCR Engine - v2
================
Returns text WITH bounding box coordinates and confidence scores.
This enables proper row-based table reconstruction instead of flat text parsing.
"""

from paddleocr import PaddleOCR
from typing import Tuple, Optional, List, Dict
import numpy as np

from config.config import OCR_CONFIG


class OCRResult:
    """Single OCR detection with position and confidence."""
    def __init__(self, text: str, x_center: float, y_center: float,
                 x_min: float, y_min: float, x_max: float, y_max: float,
                 confidence: float):
        self.text       = text.strip()
        self.x_center   = x_center
        self.y_center   = y_center
        self.x_min      = x_min
        self.y_min      = y_min
        self.x_max      = x_max
        self.y_max      = y_max
        self.confidence = confidence
        self.height     = y_max - y_min

    def __repr__(self):
        return (f"OCRResult(text={self.text!r}, x={self.x_center:.0f}, "
                f"y={self.y_center:.0f}, conf={self.confidence:.2f})")


class OCREngine:
    """Extracts text from nutrition label images with full spatial metadata."""

    def __init__(self):
        self.ocr = PaddleOCR(**OCR_CONFIG)

    # ------------------------------------------------------------------
    # Primary method: returns structured OCR results with coordinates
    # ------------------------------------------------------------------

    def extract_structured(
        self, image: np.ndarray
    ) -> Tuple[Optional[List[OCRResult]], Optional[str]]:
        """
        Run OCR and return a list of OCRResult objects sorted top-to-bottom,
        left-to-right.  Each result carries text, position, and confidence.

        Returns:
            (results, error_message)
        """
        try:
            raw = self.ocr.ocr(image, cls=False)
            if not raw or not raw[0]:
                return None, "No text detected"

            results = []
            for line in raw[0]:
                box  = line[0]   # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                text = line[1][0]
                conf = line[1][1]

                xs = [pt[0] for pt in box]
                ys = [pt[1] for pt in box]
                x_min, x_max = min(xs), max(xs)
                y_min, y_max = min(ys), max(ys)

                results.append(OCRResult(
                    text      = text,
                    x_center  = (x_min + x_max) / 2,
                    y_center  = (y_min + y_max) / 2,
                    x_min     = x_min,
                    y_min     = y_min,
                    x_max     = x_max,
                    y_max     = y_max,
                    confidence= conf,
                ))

            # Sort top → bottom, then left → right
            results.sort(key=lambda r: (r.y_center, r.x_center))
            return results, None

        except Exception as e:
            return None, f"OCR error: {str(e)}"

    # ------------------------------------------------------------------
    # Row grouping: cluster OCRResults into table rows
    # ------------------------------------------------------------------

    @staticmethod
    def group_into_rows(
        results: List[OCRResult],
        row_tolerance_factor: float = 0.4
    ) -> List[List[OCRResult]]:
        """
        Group OCR results into rows based on Y-coordinate proximity.

        Two items are in the same row if their y_center values are within
        (row_tolerance_factor * median_height) of each other.

        Returns list of rows, each row sorted left → right by x_center.
        """
        if not results:
            return []

        # Estimate typical text height from the results
        heights = [r.height for r in results if r.height > 2]
        if not heights:
            heights = [12]
        median_h = sorted(heights)[len(heights) // 2]
        threshold = max(median_h * row_tolerance_factor, 6)

        rows: List[List[OCRResult]] = []
        used = [False] * len(results)

        for i, item in enumerate(results):
            if used[i]:
                continue
            row = [item]
            used[i] = True
            for j, other in enumerate(results):
                if used[j]:
                    continue
                if abs(other.y_center - item.y_center) <= threshold:
                    row.append(other)
                    used[j] = True
            # Sort row left → right
            row.sort(key=lambda r: r.x_center)
            rows.append(row)

        # Sort rows top → bottom
        rows.sort(key=lambda row: min(r.y_center for r in row))
        return rows

    # ------------------------------------------------------------------
    # Convert rows to simple text-per-row format (for debug / fallback)
    # ------------------------------------------------------------------

    @staticmethod
    def rows_to_text(rows: List[List[OCRResult]]) -> str:
        """Convert row groups back to newline-separated text (for fallback parser)."""
        lines = []
        for row in rows:
            lines.append("  ".join(r.text for r in row))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Legacy method: flat text extraction (kept for fallback)
    # ------------------------------------------------------------------

    def extract_text(
        self, image: np.ndarray
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Legacy flat-text extraction.
        Calls extract_structured internally and reconstructs row-aware text.
        """
        results, err = self.extract_structured(image)
        if err:
            return None, err

        rows = self.group_into_rows(results)
        text = self.rows_to_text(rows)
        return text, None

    def extract_with_confidence(
        self, image: np.ndarray
    ) -> Tuple[Optional[list], Optional[str]]:
        """Extract text with confidence scores (legacy interface)."""
        try:
            raw = self.ocr.ocr(image, cls=False)
            if not raw or not raw[0]:
                return None, "No text detected"
            return [(line[1][0], line[1][1]) for line in raw[0]], None
        except Exception as e:
            return None, f"OCR error: {str(e)}"