# -*- coding: utf-8 -*-
"""
Row-Based Nutrition Parser
===========================
Works from spatially-grouped OCR rows rather than flat text.
This is fundamentally more accurate because it knows which values
are on the same line as which nutrient name.

Pipeline:
  OCRResult list
    → group_into_rows()         (in ocr_engine.py)
    → detect_table_structure()  (find column positions)
    → parse_row()               (extract nutrient + values per row)
    → normalize_output()        (standard field names)
    → fallback to flat parser   (if structured parse fails)
"""

import re
from typing import Dict, List, Optional, Tuple

# Reuse field name constants and flat-text fallback from main parser
from parser import (
    NutritionParser as FlatParser,
    FIELD_ENERGY_KCAL_100, FIELD_ENERGY_KJ_100,
    FIELD_ENERGY_KCAL_SRV, FIELD_ENERGY_KJ_SRV,
    FIELD_PROTEIN_100, FIELD_PROTEIN_SRV,
    FIELD_CARBS_100, FIELD_CARBS_SRV,
    FIELD_SUGAR_100, FIELD_SUGAR_SRV,
    FIELD_FIBER_100, FIELD_FIBER_SRV,
    FIELD_FAT_100, FIELD_FAT_SRV,
    FIELD_SAT_FAT_100, FIELD_SAT_FAT_SRV,
    FIELD_MUFA_100, FIELD_MUFA_SRV,
    FIELD_PUFA_100, FIELD_PUFA_SRV,
    FIELD_TRANS_100, FIELD_TRANS_SRV,
    FIELD_CHOLESTEROL_100, FIELD_CHOLESTEROL_SRV,
    FIELD_SODIUM_100, FIELD_SODIUM_SRV,
    FIELD_CALCIUM_100, FIELD_IRON_100,
    FIELD_SERVING_SIZE, FIELD_SERVING_UNIT,
)

# ---------------------------------------------------------------------------
# Noise patterns — rows matching these are skipped entirely
# ---------------------------------------------------------------------------
NOISE_PATTERNS = [
    r"ingredient",
    r"manufactur",
    r"distribut",
    r"store in",
    r"keep in",
    r"mfd[\s/]",
    r"exp[\s/\.]",
    r"best before",
    r"batch",
    r"barcode",
    r"www\.",
    r"http",
    r"@",
    r"tel[\s:]+\d",
    r"fax[\s:]+\d",
    r"call\s+\d",
    r"iso\s+\d",
    r"certified",
    r"product of",
    r"made in",
    r"country of",
    r"number of servings",
    r"servings per pack",
    r"serving per pack",
    r"may contain",
    r"allergen",
    r"contains.*wheat",
    r"^\d{4,}$",                  # bare long numbers (barcodes)
    r"consumer care",
    r"customer care",
]

# ---------------------------------------------------------------------------
# OCR character-level corrections applied before matching
# ---------------------------------------------------------------------------
OCR_FIXES = [
    # Common OCR misreads in nutrient names
    (r"\bcarbohydr\b",          "carbohydrate"),
    (r"\bcarbohydrs\b",         "carbohydrates"),
    (r"\bdietary\s+f[il1]bre\b","dietary fibre"),
    (r"\bdietary\s+f[il1]ber\b","dietary fiber"),
    (r"\bsatur[ae]ted\b",       "saturated"),
    (r"\btrans[\s\-]*fat\b",    "trans fat"),
    (r"\bpoly\s*unsat\b",       "polyunsaturated"),
    (r"\bmono\s*unsat\b",       "monounsaturated"),
    (r"\bsodlum\b",             "sodium"),
    (r"\bprot[e3][il1]n\b",     "protein"),
    (r"\ben[e3]rgy\b",          "energy"),
    # Unit normalization
    (r"\bkcai\b",               "kcal"),
    (r"\bkeal\b",               "kcal"),
    (r"\bk[cC][aA][lL1]\b",     "kcal"),
    (r"\bkilojoule",            "kj"),
    (r"\bkilocalorie",          "kcal"),
    # "g" misread as "9" when isolated
    (r"(?<!\d)9(?!\d)",         "g"),
]

# ---------------------------------------------------------------------------
# Nutrient row definitions
# Each entry: (match_keywords, field_100, field_srv, unit, is_subrow)
# is_subrow=True means skip if it appears as an indented/sub item
# ---------------------------------------------------------------------------
NUTRIENT_ROWS = [
    # Energy — handled separately (two units)
    # Protein
    (["protein content", "total protein", "protein"],
     FIELD_PROTEIN_100, FIELD_PROTEIN_SRV, "g", False),
    # Carbohydrates
    (["total carbohydrate", "carbohydrates total", "carbohydrates-total",
      "available carbohydrate", "carbohydrate", "carbohydr"],
     FIELD_CARBS_100, FIELD_CARBS_SRV, "g", False),
    # Fiber
    (["total dietary fiber", "total dietary fibre",
      "dietary fibre", "dietary fiber", "crude fibre", "crude fiber",
      "total fiber", "total fibre", "fibre", "fiber"],
     FIELD_FIBER_100, FIELD_FIBER_SRV, "g", False),
    # Sugar — parent only (sub-rows filtered separately)
    (["total sugar", "total sugars", "sugar", "sugars"],
     FIELD_SUGAR_100, FIELD_SUGAR_SRV, "g", False),
    # Fat subtypes (must come BEFORE total fat)
    (["saturated fatty acid", "saturated fat", "sat. fat", "saturated"],
     FIELD_SAT_FAT_100, FIELD_SAT_FAT_SRV, "g", True),
    (["monounsaturated fatty acid", "monounsaturated fat", "monounsaturated", "mufa"],
     FIELD_MUFA_100, FIELD_MUFA_SRV, "g", True),
    (["polyunsaturated fatty acid", "polyunsaturated fat", "polyunsaturated", "pufa"],
     FIELD_PUFA_100, FIELD_PUFA_SRV, "g", True),
    (["trans fatty acid", "trans-fatty acid", "trans fat", "trans fatty", "trans"],
     FIELD_TRANS_100, FIELD_TRANS_SRV, "g", True),
    # Total fat (after subtypes to avoid premature matching)
    (["fat-total", "total milk fat", "total fat", "fat (total)", "fat"],
     FIELD_FAT_100, FIELD_FAT_SRV, "g", False),
    # Other
    (["cholesterol"],
     FIELD_CHOLESTEROL_100, FIELD_CHOLESTEROL_SRV, "mg", False),
    (["sodium"],
     FIELD_SODIUM_100, FIELD_SODIUM_SRV, "mg", False),
    (["calcium"],
     FIELD_CALCIUM_100, None, "mg", False),
    (["iron"],
     FIELD_IRON_100, None, "mg", False),
]

# Sub-row keywords: rows starting with these under a parent are skipped
# for PARENT extraction but still parsed for their own field
SUBROW_PREFIXES = [
    "of which", "- ", "–", "naturally occurring", "naturally occuring",
    "added sugar", "added sugars",
    "soluble", "insoluble",
    "energy from fat",
]


class RowBasedParser:
    """
    Parses nutrition labels from spatially-grouped OCR rows.
    Falls back to the flat text parser if row-based extraction fails.
    """

    def __init__(self):
        self._flat_parser = FlatParser()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_from_rows(
        self,
        rows: List[List],          # List of OCRResult rows from ocr_engine
        fallback_text: str = "",   # flat OCR text for fallback
    ) -> Dict:
        """
        Primary entry point.

        Args:
            rows:           Spatially grouped OCR rows (list of lists of OCRResult)
            fallback_text:  Raw flat text for fallback parser

        Returns:
            Normalized nutrition dict
        """
        try:
            result = self._parse_rows(rows)
            # Check if we got meaningful data
            if self._is_sufficient(result):
                print("  [RowParser] Structured parse succeeded")
                return result
            else:
                print("  [RowParser] Structured parse insufficient — falling back")
        except Exception as e:
            print(f"  [RowParser] Structured parse error: {e} — falling back")

        # Fallback: use flat text parser
        if fallback_text:
            return self._flat_parser.parse(fallback_text)

        # Last resort: reconstruct text from rows and try flat parser
        flat = self._rows_to_flat_text(rows)
        return self._flat_parser.parse(flat)

    def parse_from_text(self, text: str) -> Dict:
        """Direct flat-text entry point (uses flat parser only)."""
        return self._flat_parser.parse(text)

    # ------------------------------------------------------------------
    # Core row-based parsing
    # ------------------------------------------------------------------

    def _parse_rows(self, rows: List[List]) -> Dict:
        result: Dict = {}

        # Convert rows to normalized text rows for easier processing
        text_rows = self._normalize_rows(rows)

        # Print for debug
        print("\n" + "=" * 60)
        print("ROW-BASED TABLE RECONSTRUCTION:")
        print("=" * 60)
        for i, row in enumerate(text_rows):
            print(f"  [{i:02d}] {' | '.join(row)}")
        print("=" * 60 + "\n")

        # 1. Extract serving size
        self._extract_serving_size(text_rows, result)

        # 2. Detect table structure (which columns are per100 vs serving)
        col_structure = self._detect_column_structure(text_rows)
        print(f"  Column structure: {col_structure}")

        # 3. Find and parse energy rows
        self._parse_energy_rows(text_rows, col_structure, result)

        # 4. Parse all nutrient rows
        self._parse_nutrient_rows(text_rows, col_structure, result)

        # 5. Apply sanity fixes from flat parser
        result = self._flat_parser._verify_and_fix_column_order(result)
        result = self._flat_parser._post_parse_sanity_fix(result)

        return result

    # ------------------------------------------------------------------
    # Row normalization
    # ------------------------------------------------------------------

    def _normalize_rows(self, rows: List[List]) -> List[List[str]]:
        """
        Convert OCRResult rows → List[List[str]] with text normalization.
        Filters out noise rows.
        """
        text_rows = []
        for row in rows:
            # Join text from each cell in the row
            cells = [r.text if hasattr(r, 'text') else str(r) for r in row]
            cells = [self._normalize_text(c) for c in cells if c.strip()]
            if not cells:
                continue
            # Skip noise rows
            joined = " ".join(cells).lower()
            if self._is_noise(joined):
                continue
            text_rows.append(cells)
        return text_rows

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Apply OCR corrections and text normalization."""
        t = text.strip().lower()
        for pattern, replacement in OCR_FIXES:
            t = re.sub(pattern, replacement, t, flags=re.I)
        return t

    @staticmethod
    def _is_noise(text: str) -> bool:
        """Return True if this row is non-nutritional noise."""
        for pattern in NOISE_PATTERNS:
            if re.search(pattern, text, re.I):
                return True
        return False

    # ------------------------------------------------------------------
    # Serving size extraction
    # ------------------------------------------------------------------

    def _extract_serving_size(self, text_rows: List[List[str]], result: Dict):
        for row in text_rows:
            joined = " ".join(row)
            # "serving size: 30g" or "serving size 30 g"
            m = re.search(
                r"serving\s+size\s*[:\-–]?\s*(\d+(?:\.\d+)?)\s*(ml|g)\b",
                joined, re.I)
            if m:
                result[FIELD_SERVING_SIZE] = float(m.group(1))
                result[FIELD_SERVING_UNIT] = m.group(2).lower()
                print(f"  ✓ Serving size: {result[FIELD_SERVING_SIZE]} "
                      f"{result[FIELD_SERVING_UNIT]}")
                return
            # "17.5g" alone in a row near "serving size" text
            if any("serving" in c for c in row):
                for cell in row:
                    m2 = re.search(r"(\d+(?:\.\d+)?)\s*(ml|g)\b", cell)
                    if m2:
                        result[FIELD_SERVING_SIZE] = float(m2.group(1))
                        result[FIELD_SERVING_UNIT] = m2.group(2).lower()
                        return

    # ------------------------------------------------------------------
    # Column structure detection
    # ------------------------------------------------------------------

    def _detect_column_structure(self, text_rows: List[List[str]]) -> Dict:
        """
        Determine:
          - num_value_cols: how many numeric columns (1, 2, or 3)
          - col_100: index of the per-100g column (0 or 1)
          - col_srv: index of the per-serving column (0 or 1)

        Returns dict with keys: num_cols, col_100, col_srv
        """
        # Look for a header row with "per 100" and "per serv"
        for row in text_rows[:10]:  # check only early rows
            joined = " ".join(row).lower()
            has_100 = bool(re.search(r"per\s*100|100\s*m[lg]", joined))
            has_srv = bool(re.search(r"per\s*serv|per serve\b", joined))
            if has_100 and has_srv:
                # Find which comes first
                pos_100 = joined.find("100")
                pos_srv = re.search(r"per\s*serv|per serve", joined).start()
                if pos_100 < pos_srv:
                    return {"num_cols": 2, "col_100": 0, "col_srv": 1}
                else:
                    return {"num_cols": 2, "col_100": 1, "col_srv": 0}
            if has_100 and not has_srv:
                return {"num_cols": 1, "col_100": 0, "col_srv": None}

        # No header found — infer from data rows
        # Count how many numeric cells a typical nutrient row has
        numeric_counts = []
        for row in text_rows:
            n_numeric = sum(1 for c in row if re.search(r"\d", c)
                            and not re.search(r"[a-zA-Z]{3,}", c))
            if 1 <= n_numeric <= 3:
                numeric_counts.append(n_numeric)
        if numeric_counts:
            most_common = max(set(numeric_counts), key=numeric_counts.count)
            if most_common >= 2:
                return {"num_cols": 2, "col_100": 0, "col_srv": 1}

        return {"num_cols": 1, "col_100": 0, "col_srv": None}

    # ------------------------------------------------------------------
    # Energy parsing
    # ------------------------------------------------------------------

    def _parse_energy_rows(self, text_rows, col_structure, result):
        """
        Find energy row(s) and extract kJ and kcal values.
        Handles both inline (same row) and stacked (separate rows) formats.
        """
        energy_idx = None
        for i, row in enumerate(text_rows):
            if re.search(r"\benergy\b|\bcalories\b", " ".join(row), re.I):
                energy_idx = i
                break
        if energy_idx is None:
            return

        # Collect up to 4 rows starting at energy (kJ row + kcal row)
        window_rows = text_rows[energy_idx: energy_idx + 5]

        kj_vals, kcal_vals = [], []
        for row in window_rows:
            joined = " ".join(row).lower()
            # Stop at next major nutrient
            if re.search(r"\b(protein|carbohydrate|fat|fiber|fibre|sodium)\b",
                         joined) and "energy" not in joined:
                break
            # Extract kJ values
            for m in re.finditer(r"(\d+\.?\d*)\s*kj", joined):
                kj_vals.append(float(m.group(1)))
            # Extract kcal values
            for m in re.finditer(r"(\d+\.?\d*)\s*kcal", joined):
                kcal_vals.append(float(m.group(1)))
            # "Calories NNN" (US style)
            if re.search(r"\bcalories\b", joined) and not kcal_vals:
                nums = re.findall(r"\d+\.?\d*", joined)
                if nums:
                    kcal_vals = [float(nums[0])]

        # Repair OCR digit errors using kJ ↔ kcal cross-validation
        kj_vals, kcal_vals = self._flat_parser._repair_energy_ocr(
            kj_vals[:2], kcal_vals[:2])

        col_100 = col_structure.get("col_100", 0)
        col_srv = col_structure.get("col_srv", 1)

        def assign_pair(vals, f100, fsrv):
            if not vals:
                return
            if col_structure["num_cols"] == 1 or len(vals) == 1:
                result[f100] = vals[0]
            elif col_100 == 0:
                result[f100], result[fsrv] = vals[0], vals[1]
            else:
                result[fsrv], result[f100] = vals[0], vals[1]

        assign_pair(kj_vals,   FIELD_ENERGY_KJ_100,   FIELD_ENERGY_KJ_SRV)
        assign_pair(kcal_vals, FIELD_ENERGY_KCAL_100, FIELD_ENERGY_KCAL_SRV)

        if FIELD_ENERGY_KCAL_100 in result:
            print(f"  ✓ Energy kcal/100g={result.get(FIELD_ENERGY_KCAL_100)}  "
                  f"kcal/srv={result.get(FIELD_ENERGY_KCAL_SRV)}")

    # ------------------------------------------------------------------
    # Nutrient row parsing
    # ------------------------------------------------------------------

    def _parse_nutrient_rows(self, text_rows, col_structure, result):
        """
        For each row, determine if it's a nutrient row, extract values,
        and assign to per-100g and per-serving fields.
        """
        col_100 = col_structure.get("col_100", 0)
        col_srv = col_structure.get("col_srv", 1)
        num_cols = col_structure.get("num_cols", 2)

        for row in text_rows:
            joined = " ".join(row).lower()

            # Skip noise and energy rows (already handled)
            if self._is_noise(joined):
                continue
            if re.search(r"\benergy\b|\bcalories\b", joined):
                continue

            # Check if this is a sub-row
            is_sub = self._is_subrow(joined)

            # Try to match a nutrient
            match = self._match_nutrient(joined, is_sub)
            if match is None:
                continue

            keywords, field_100, field_srv, unit, _ = match

            # Extract numeric values from the row
            nums = self._extract_row_numbers(row, unit)
            if not nums:
                continue

            # Assign based on column structure
            if num_cols == 1 or len(nums) == 1:
                result[field_100] = nums[0]
            else:
                # Take first two valid numbers as col1, col2
                v0, v1 = nums[0], nums[1]
                if col_100 == 0:
                    result[field_100] = v0
                    if field_srv:
                        result[field_srv] = v1
                else:
                    result[field_100] = v1
                    if field_srv:
                        result[field_srv] = v0

            print(f"  ✓ {keywords[0]:30s}  "
                  f"/100g={result.get(field_100,'—'):>8}  "
                  f"/srv={result.get(field_srv,'—') if field_srv else '—'}")

    def _match_nutrient(
        self, text: str, is_sub: bool
    ) -> Optional[Tuple]:
        """
        Match text against NUTRIENT_ROWS.
        Returns the matching entry or None.
        Skips sub-rows for parent nutrients when is_sub=True.
        """
        for entry in NUTRIENT_ROWS:
            keywords, field_100, field_srv, unit, row_is_sub = entry
            # Don't match a sub-row entry for a non-sub row position
            # (but DO match it if this row IS a sub-row)
            for kw in keywords:
                if kw in text:
                    # If this is a sub-row, make sure we're matching the right thing
                    # e.g. "of which saturated" should map to SAT_FAT not TOTAL_FAT
                    return entry
        return None

    @staticmethod
    def _is_subrow(text: str) -> bool:
        """Return True if this row appears to be a sub-item."""
        for prefix in SUBROW_PREFIXES:
            if text.strip().startswith(prefix):
                return True
        return False

    @staticmethod
    def _extract_row_numbers(row: List, unit: str) -> List[float]:
        """
        Extract numeric values from a row, filtering by plausible range for unit.
        Handles: <0.01, ND, LOQ, "g" misread as "9".
        """
        nums = []
        for cell in row:
            text = str(cell.text if hasattr(cell, 'text') else cell)
            # Apply ND/LOQ → 0
            text = re.sub(r"<\s*(\d+\.?\d*)", r"0", text)
            text = re.sub(r"\bN\.?D\.?\b", "0", text, flags=re.I)
            text = re.sub(r"\bLOQ[^\s]*", "0", text, flags=re.I)
            text = re.sub(r"\bnot\s+detected\b", "0", text, flags=re.I)

            found = re.findall(r"\d+\.?\d*", text)
            for f in found:
                v = float(f)
                if unit == "g"  and v > 9999:
                    continue
                if unit == "mg" and v > 99999:
                    continue
                # Ignore values that look like years or serving counts
                if 1990 <= v <= 2100:
                    continue
                nums.append(v)

        # Deduplicate while preserving order (take first 2 distinct values)
        seen = []
        for n in nums:
            if n not in seen:
                seen.append(n)
            if len(seen) == 2:
                break
        return seen

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_sufficient(result: Dict) -> bool:
        """Return True if we extracted enough data to be useful."""
        required = [FIELD_ENERGY_KCAL_100, FIELD_PROTEIN_100, FIELD_CARBS_100]
        found = sum(1 for f in required if f in result)
        return found >= 2

    @staticmethod
    def _rows_to_flat_text(rows: List[List]) -> str:
        lines = []
        for row in rows:
            parts = []
            for r in row:
                parts.append(r.text if hasattr(r, 'text') else str(r))
            lines.append("  ".join(parts))
        return "\n".join(lines)