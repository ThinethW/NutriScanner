# -*- coding: utf-8 -*-
"""
Nutrition Label Parser - v3  (handles real PaddleOCR output)
=============================================================

Real-world PaddleOCR output from Sri Lankan product labels falls into
two structural modes:

  MODE A – "inline" (values on the SAME line as the nutrient name):
      Total Carbohydrate  12.64 g      22.75 g
      Protein             2.18 g       3.92 g

  MODE B – "stacked" (each value on its OWN line, typical for Kandos etc.):
      [06] Energy
      [07] 250.3           ← col-1 value
      [08] 2275.2kJ        ← col-2 value
      [09] 59.9 kcal       ← col-1 kcal
      [10] 545.2           ← col-2 kcal
      [11] Protein
      [12] 0.8g
      [13] 7.7g

  In Mode B, column-header lines are ALSO stacked:
      [04] per'Serving
      [05] per 100g

  The parser auto-detects both modes.

Column order detection
-----------------------
  - If both "per … serv" and "per 100" appear on the SAME line  → inline header
  - If they appear on CONSECUTIVE lines                          → stacked header
    · whichever appears FIRST is column-1

Output
------
  Every nutrient produces TWO canonical keys:
    <nutrient>_per_serving_*   (e.g.  protein_per_serving_g)
    <nutrient>_per_100g / <nutrient>_mg   (e.g.  protein_g,  sodium_mg)

  The health-scoring pipeline in analyzer.py uses the per-100g values.
  The Streamlit display uses the per-serving values.
"""

import re
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Canonical output field names
# ---------------------------------------------------------------------------
FIELD_ENERGY_KCAL_100 = "energy_kcal_per_100g"
FIELD_ENERGY_KJ_100   = "energy_kj_per_100g"
FIELD_ENERGY_KCAL_SRV = "energy_kcal_per_serving"
FIELD_ENERGY_KJ_SRV   = "energy_kj_per_serving"
FIELD_PROTEIN_100     = "protein_g"
FIELD_PROTEIN_SRV     = "protein_per_serving_g"
FIELD_CARBS_100       = "carbohydrates_g"
FIELD_CARBS_SRV       = "carbs_per_serving_g"
FIELD_SUGAR_100       = "sugar_g"
FIELD_SUGAR_SRV       = "sugar_per_serving_g"
FIELD_FIBER_100       = "fiber_g"
FIELD_FIBER_SRV       = "fiber_per_serving_g"
FIELD_FAT_100         = "total_fat_g"
FIELD_FAT_SRV         = "fat_per_serving_g"
FIELD_SAT_FAT_100     = "saturated_fat_g"
FIELD_SAT_FAT_SRV     = "saturated_fat_per_serving_g"
FIELD_MUFA_100        = "mufa_g"
FIELD_MUFA_SRV        = "mufa_per_serving_g"
FIELD_PUFA_100        = "pufa_g"
FIELD_PUFA_SRV        = "pufa_per_serving_g"
FIELD_TRANS_100       = "trans_fat_g"
FIELD_TRANS_SRV       = "trans_fat_per_serving_g"
FIELD_CHOLESTEROL_100 = "cholesterol_mg"
FIELD_CHOLESTEROL_SRV = "cholesterol_per_serving_mg"
FIELD_SODIUM_100      = "sodium_mg"
FIELD_SODIUM_SRV      = "sodium_per_serving_mg"
FIELD_CALCIUM_100     = "calcium_mg"
FIELD_IRON_100        = "iron_mg"
FIELD_SERVING_SIZE    = "serving_size"
FIELD_SERVING_UNIT    = "serving_unit"


# ---------------------------------------------------------------------------
# Nutrient keyword → (field_100g, field_per_serving, unit)
# Order matters: specific multi-word keywords MUST come before generic ones
# (e.g. "saturated fat" before "fat", "total carbohydrate" before "carbohydrate")
# ---------------------------------------------------------------------------
NUTRIENT_MAP: List[Tuple] = [
    # keywords                          field_100g          field_serving       unit
    (["protein"],                       FIELD_PROTEIN_100,  FIELD_PROTEIN_SRV,  "g"),
    (["total carbohydrate",
      "carbohydrates-total",
      "carbohydrates total",
      "carbohydrate"],                  FIELD_CARBS_100,    FIELD_CARBS_SRV,    "g"),
    (["dietary fibre",
      "dietary fiber",
      "total fiber",
      "fibre"],                         FIELD_FIBER_100,    FIELD_FIBER_SRV,    "g"),
    (["total sugar", "sugar"],          FIELD_SUGAR_100,    FIELD_SUGAR_SRV,    "g"),
    (["saturated fatty acid",
      "saturated fat",
      "sat. fat", "sfa"],               FIELD_SAT_FAT_100,  FIELD_SAT_FAT_SRV,  "g"),
    (["monounsaturated", "mufa"],       FIELD_MUFA_100,     FIELD_MUFA_SRV,     "g"),
    (["polyunsaturated", "pufa"],       FIELD_PUFA_100,     FIELD_PUFA_SRV,     "g"),
    (["trans fatty acid",
      "trans-fatty", "trans fat"],      FIELD_TRANS_100,    FIELD_TRANS_SRV,    "g"),
    # fat-total / total fat AFTER all fat sub-types
    (["fat-total", "total fat",
      "fat (total)"],                   FIELD_FAT_100,      FIELD_FAT_SRV,      "g"),
    (["cholesterol"],                   FIELD_CHOLESTEROL_100, FIELD_CHOLESTEROL_SRV, "mg"),
    (["sodium"],                        FIELD_SODIUM_100,   FIELD_SODIUM_SRV,   "mg"),  # special
    (["calcium"],                       FIELD_CALCIUM_100,  None,               "mg"),
    (["iron"],                          FIELD_IRON_100,     None,               "mg"),
]

# Keywords that unambiguously start a NEW nutrient row.
# Used by Mode-B value harvesting to know when to stop collecting.
NEW_ROW_KEYWORDS = [
    "protein", "carbohydrate", "fiber", "fibre", "sugar",
    "fat", "cholesterol", "sodium", "calcium", "iron", "zinc",
    "vitamin", "energy", "saturated", "trans", "monounsaturated",
    "polyunsaturated",
]


# ===========================================================================
class NutritionParser:
    """
    Parse PaddleOCR output from nutrition labels into clean dicts.

    Usage
    -----
        parser = NutritionParser()
        data   = parser.parse(ocr_text)   # returns dict of floats
        ok, missing = parser.validate(data)
    """

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def parse(self, ocr_text: str) -> Dict:
        """Convert raw OCR text → nutrition dict."""
        lines = self._clean_lines(ocr_text)
        self._debug_print_lines(lines)

        result: Dict = {}

        # 1. Serving size
        self._extract_serving_size(lines, result)

        # 2. Detect layout mode + column order
        col_order = self._detect_column_order(lines)
        mode      = self._detect_layout_mode(lines)
        print(f"  Layout mode    : {mode}")
        print(f"  Column order   : {col_order}\n")

        # 3. Energy (special dual kJ/kcal handling)
        if mode == "stacked":
            self._extract_energy_stacked(lines, col_order, result)
        else:
            self._extract_energy_inline(lines, col_order, result)

        # 4. All other nutrients
        if mode == "stacked":
            self._extract_nutrients_stacked(lines, col_order, result)
        else:
            self._extract_nutrients_inline(lines, col_order, result)

        self._debug_print_result(result)
        return result

    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        """Return (is_valid, missing_required_fields)."""
        required = [FIELD_ENERGY_KCAL_100, FIELD_PROTEIN_100]
        missing  = [f for f in required if f not in data]
        return (len(missing) == 0, missing)

    # -----------------------------------------------------------------------
    # Debug helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _debug_print_lines(lines: List[str]) -> None:
        print("\n" + "=" * 60)
        print("OCR TEXT (cleaned lines):")
        print("=" * 60)
        for i, l in enumerate(lines):
            print(f"  [{i:02d}] {l}")
        print("=" * 60 + "\n")

    @staticmethod
    def _debug_print_result(result: Dict) -> None:
        print("\n" + "=" * 60)
        print("PARSED NUTRITION DATA:")
        print("=" * 60)
        for k, v in result.items():
            print(f"  {k}: {v}")
        print("=" * 60 + "\n")

    # -----------------------------------------------------------------------
    # Text utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def _clean_lines(text: str) -> List[str]:
        """Strip whitespace, remove blank lines. Keep original case for numbers."""
        return [l.strip() for l in text.split("\n") if l.strip()]

    @staticmethod
    def _extract_numbers(text: str) -> List[float]:
        """Extract all numeric values from a string."""
        return [float(m) for m in re.findall(r"\d+\.?\d*", text)]

    @staticmethod
    def _is_value_line(line: str) -> bool:
        """Return True if line looks like a pure value line (number + optional unit)."""
        lo = line.lower().strip()
        # Contains a digit and no multi-word nutrient keywords
        if not re.search(r"\d", lo):
            return False
        for kw in NEW_ROW_KEYWORDS:
            if kw in lo:
                return False
        return True

    @staticmethod
    def _line_has_units(line: str) -> bool:
        """Return True if line contains an explicit unit tag (g, mg, kcal, kj)."""
        lo = line.lower()
        return bool(re.search(r"\d\s*(g|mg|kcal|kj)\b", lo))

    # -----------------------------------------------------------------------
    # Serving size
    # -----------------------------------------------------------------------

    def _extract_serving_size(self, lines: List[str], result: Dict) -> None:
        for i, line in enumerate(lines):
            if "serving size" in line.lower():
                # Search current line + next line
                search = line + (" " + lines[i + 1] if i + 1 < len(lines) else "")
                ml = re.search(r"(\d+(?:\.\d+)?)\s*ml", search, re.I)
                g  = re.search(r"(\d+(?:\.\d+)?)\s*g\b", search, re.I)
                if ml:
                    result[FIELD_SERVING_SIZE] = float(ml.group(1))
                    result[FIELD_SERVING_UNIT] = "ml"
                elif g:
                    result[FIELD_SERVING_SIZE] = float(g.group(1))
                    result[FIELD_SERVING_UNIT] = "g"
                if FIELD_SERVING_SIZE in result:
                    print(f"  ✓ Serving size : {result[FIELD_SERVING_SIZE]} "
                          f"{result[FIELD_SERVING_UNIT]}")
                return

    # -----------------------------------------------------------------------
    # Layout detection
    # -----------------------------------------------------------------------

    def _detect_layout_mode(self, lines: List[str]) -> str:
        """
        Detect whether values are on the same line as nutrient names (inline)
        or on separate lines below them (stacked).

        Heuristic: look at lines after the first recognisable nutrient keyword.
        If the NEXT non-empty line is a pure value line → stacked.
        If the nutrient line itself contains numbers   → inline.
        """
        for i, line in enumerate(lines):
            lo = line.lower()
            for kw in ["protein", "carbohydrate", "total fat", "fat-total", "sodium"]:
                if kw in lo:
                    # Check if this line itself has numbers
                    nums_on_line = self._extract_numbers(line)
                    if len(nums_on_line) >= 1:
                        return "inline"
                    # Check next line
                    if i + 1 < len(lines):
                        next_nums = self._extract_numbers(lines[i + 1])
                        if next_nums:
                            return "stacked"
        return "inline"  # safe default

    def _detect_column_order(self, lines: List[str]) -> str:
        """
        Determine which column comes first: Per-Serving or Per-100g.

        Pass 1: scan for a line that contains BOTH '100' and 'serv' keywords
                (inline header like 'Per 100ml    Per serving').
        Pass 2: scan for two CONSECUTIVE pure-header lines
                (stacked header like ['per Serving', 'per 100g']).

        'Serving Size: 180ml' is NOT a column header and is excluded from pass 2.

        Returns: 'srv_first' | '100_first'
        """
        re_100 = re.compile(r"per\s*100|100\s*m[lg]|100g|100ml")
        re_srv = re.compile(r"per.{0,2}serv")   # handles per serv / per'serv / per Serv

        # ── Pass 1: inline header (both keywords on same line) ────────────
        for line in lines:
            lo = line.lower()
            if re_100.search(lo) and re_srv.search(lo):
                pos_100 = lo.find("100")
                pos_srv = lo.find("serv")
                return "100_first" if pos_100 < pos_srv else "srv_first"

        # ── Pass 2: stacked header (consecutive lines, each pure header) ──
        for i, line in enumerate(lines):
            lo = line.lower()
            # Must look like a pure column-header line (starts with "per" or
            # contains ONLY a column reference, not "serving size: 180ml")
            is_header = bool(re_100.search(lo) or re_srv.search(lo))
            if not is_header:
                continue
            # Skip lines that also contain a number (serving size lines)
            if re.search(r"\d", lo):
                continue

            if i + 1 < len(lines):
                next_lo = lines[i + 1].lower()
                next_has_100 = bool(re_100.search(next_lo))
                next_has_srv = bool(re_srv.search(next_lo))

                if re_srv.search(lo) and next_has_100:
                    return "srv_first"
                if re_100.search(lo) and next_has_srv:
                    return "100_first"

        return "100_first"  # safe default

    # -----------------------------------------------------------------------
    # Sodium unit detection helper
    # -----------------------------------------------------------------------

    @staticmethod
    def _sodium_needs_conversion(context_lines: List[str]) -> bool:
        """
        Return True if sodium values are in grams and need ×1000 conversion.
        Decision: look for explicit 'mg' anywhere in the context window.
        If 'mg' is present the values are already milligrams → no conversion.
        If only 'g' or no unit → assume grams → convert.
        """
        window = " ".join(context_lines).lower()
        if "mg" in window:
            return False   # already mg
        return True        # assume g → multiply by 1000

    # -----------------------------------------------------------------------
    # INLINE mode – energy
    # -----------------------------------------------------------------------

    def _extract_energy_inline(self, lines: List[str], col_order: str, result: Dict) -> None:
        """
        Handle energy rows where both values appear on the same line(s).
        E.g.:
            Energy    77.31 kcal    139.15 kcal
        or  (kJ row + kcal row):
            ENERGY    320.10 kJ     576.18 kJ
                      76.50 kcal    137.70 kcal
        """
        for i, line in enumerate(lines):
            if not re.search(r"\benergy\b", line.lower()):
                continue

            window      = lines[i: min(i + 4, len(lines))]
            window_text = "\n".join(window).lower()

            kj_vals   = [float(m) for m in re.findall(r"(\d+\.?\d*)\s*kj",   window_text)]
            kcal_vals = [float(m) for m in re.findall(r"(\d+\.?\d*)\s*kcal", window_text)]

            # Fallback: pure number line after Energy when no unit tag on line
            if not kcal_vals:
                for sub in window[1:]:
                    nums = self._extract_numbers(sub)
                    if nums and "kj" not in sub.lower():
                        kcal_vals = nums
                        break

            if kj_vals:
                self._assign(kj_vals,   col_order, FIELD_ENERGY_KJ_100,   FIELD_ENERGY_KJ_SRV,   result)
            if kcal_vals:
                self._assign(kcal_vals, col_order, FIELD_ENERGY_KCAL_100, FIELD_ENERGY_KCAL_SRV, result)

            self._log_energy(result)
            break

    # -----------------------------------------------------------------------
    # STACKED mode – energy
    # -----------------------------------------------------------------------

    def _extract_energy_stacked(self, lines: List[str], col_order: str, result: Dict) -> None:
        """
        Handle stacked energy layout where values are on separate lines.

        Real OCR example (Kandos, srv_first):
            [06] Energy
            [07] 250.3           ← kJ col-1  (no unit – pure number)
            [08] 2275.2kJ        ← kJ col-2
            [09] 59.9 kcal       ← kcal col-1
            [10] 545.2           ← kcal col-2  (no unit)

        Strategy:
          1. Find the "Energy" trigger line.
          2. Collect the next value lines (up to 6) until a new nutrient name.
          3. Separate kJ values from kcal values using unit tags.
          4. Lines with NO unit tag adjacent to kJ lines belong to kJ;
             lines adjacent to kcal lines belong to kcal.
        """
        for i, line in enumerate(lines):
            if not re.search(r"\benergy\b", line.lower()):
                continue

            # Collect up to 6 pure-value lines following "Energy"
            value_lines: List[str] = []
            for j in range(i + 1, min(i + 7, len(lines))):
                vl = lines[j]
                # Stop if we hit a new nutrient name
                if self._is_new_nutrient_row(vl):
                    break
                if re.search(r"\d", vl):
                    value_lines.append(vl)

            # Classify value lines as kJ or kcal using PAIR-BASED logic.
            #
            # Stacked labels emit values in col-1/col-2 pairs:
            #   250.3      ← kJ col-1 (no unit tag)
            #   2275.2kJ   ← kJ col-2 (has 'kj' tag)
            #   59.9 kcal  ← kcal col-1 (has 'kcal' tag)
            #   545.2      ← kcal col-2 (no unit tag)
            #
            # Group consecutive entries into pairs.  Within each pair at least
            # one line usually has a unit tag; propagate that tag to the other.
            kj_vals:   List[float] = []
            kcal_vals: List[float] = []

            entries: List[Tuple] = []   # (value, unit_tag | None)
            for vl in value_lines:
                lo = vl.lower()
                nums = self._extract_numbers(vl)
                if not nums:
                    continue
                tag = ("kcal" if "kcal" in lo
                       else ("kj" if "kj" in lo else None))
                entries.append((nums[0], tag))

            for pi in range(0, len(entries), 2):
                a = entries[pi]
                b = entries[pi + 1] if pi + 1 < len(entries) else None
                pair_unit  = a[1] or (b[1] if b else None)
                pair_vals  = [a[0]] + ([b[0]] if b else [])

                if pair_unit == "kj":
                    kj_vals.extend(pair_vals)
                elif pair_unit == "kcal":
                    kcal_vals.extend(pair_vals)
                else:
                    # No tag at all → classify by magnitude
                    for v in pair_vals:
                        (kj_vals if v > 200 else kcal_vals).append(v)

            if kj_vals:
                self._assign(kj_vals,   col_order, FIELD_ENERGY_KJ_100,   FIELD_ENERGY_KJ_SRV,   result)
            if kcal_vals:
                self._assign(kcal_vals, col_order, FIELD_ENERGY_KCAL_100, FIELD_ENERGY_KCAL_SRV, result)

            self._log_energy(result)
            break

    def _is_new_nutrient_row(self, line: str) -> bool:
        """Return True if line starts a new nutrient section."""
        lo = line.lower()
        for kw in NEW_ROW_KEYWORDS:
            if kw in lo:
                return True
        return False

    @staticmethod
    def _log_energy(result: Dict) -> None:
        if FIELD_ENERGY_KCAL_100 in result:
            print(f"  ✓ Energy  kcal/100g={result.get(FIELD_ENERGY_KCAL_100)}  "
                  f"kcal/srv={result.get(FIELD_ENERGY_KCAL_SRV)}")
        if FIELD_ENERGY_KJ_100 in result:
            print(f"  ✓ Energy  kJ/100g={result.get(FIELD_ENERGY_KJ_100)}  "
                  f"kJ/srv={result.get(FIELD_ENERGY_KJ_SRV)}")

    # -----------------------------------------------------------------------
    # INLINE mode – all other nutrients
    # -----------------------------------------------------------------------

    def _extract_nutrients_inline(self, lines: List[str], col_order: str, result: Dict) -> None:
        """
        Extract nutrients when values appear on the same line as the name.
        E.g.:  Protein   2.18 g   3.92 g
        """
        used: set = set()

        for (keywords, field_100, field_srv, unit) in NUTRIENT_MAP:
            idx = self._find_keyword_line(lines, keywords, used)
            if idx is None:
                continue

            used.add(idx)

            # Collect values from the trigger line + up to 2 continuation lines
            vals = self._collect_inline_values(lines, idx, unit)

            if not vals:
                continue

            sodium_conv = (field_100 == FIELD_SODIUM_100 and
                           self._sodium_needs_conversion(lines[idx: idx + 3]))

            self._assign(vals, col_order, field_100, field_srv, result,
                         sodium_conversion=sodium_conv)

            self._log_nutrient(keywords[0], field_100, field_srv, result)

    def _collect_inline_values(self, lines: List[str], idx: int, unit: str) -> List[float]:
        """
        Extract up to 2 numeric values starting from lines[idx].
        Continuation lines are included only if they look like value lines.
        """
        vals: List[float] = []
        context_end = min(idx + 3, len(lines))

        for j in range(idx, context_end):
            line = lines[j]
            lo   = line.lower()

            # Stop at continuation lines that are new nutrient rows
            if j > idx and self._is_new_nutrient_row(lo):
                break

            for n in self._extract_numbers(line):
                if unit == "g"  and n > 999:
                    continue
                if unit == "mg" and n > 99999:
                    continue
                vals.append(n)
                if len(vals) == 2:
                    return vals

        return vals

    # -----------------------------------------------------------------------
    # STACKED mode – all other nutrients
    # -----------------------------------------------------------------------

    def _extract_nutrients_stacked(self, lines: List[str], col_order: str, result: Dict) -> None:
        """
        Extract nutrients when each value is on its own line below the name.

        Pattern:
            [11] Protein          ← trigger
            [12] 0.8g             ← value col-1
            [13] 7.7g             ← value col-2
        """
        used: set = set()

        for (keywords, field_100, field_srv, unit) in NUTRIENT_MAP:
            idx = self._find_keyword_line(lines, keywords, used)
            if idx is None:
                continue

            used.add(idx)

            # Collect up to 2 value lines immediately below the trigger
            vals = self._collect_stacked_values(lines, idx, unit)

            if not vals:
                continue

            sodium_conv = (field_100 == FIELD_SODIUM_100 and
                           self._sodium_needs_conversion(lines[idx: idx + 4]))

            self._assign(vals, col_order, field_100, field_srv, result,
                         sodium_conversion=sodium_conv)

            self._log_nutrient(keywords[0], field_100, field_srv, result)

    def _collect_stacked_values(self, lines: List[str], idx: int, unit: str) -> List[float]:
        """
        Collect up to 2 values from lines immediately following lines[idx].
        Each stacked line contributes exactly ONE value.
        Stop at the first line that looks like a new nutrient name.
        """
        vals: List[float] = []

        for j in range(idx + 1, min(idx + 5, len(lines))):
            line = lines[j]

            # Stop at new nutrient name lines
            if self._is_new_nutrient_row(line):
                break

            nums = self._extract_numbers(line)
            if not nums:
                continue

            n = nums[0]  # take the first (usually only) number per line

            if unit == "g"  and n > 999:
                continue
            if unit == "mg" and n > 99999:
                continue

            vals.append(n)
            if len(vals) == 2:
                break

        return vals

    # -----------------------------------------------------------------------
    # Shared utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def _find_keyword_line(
        lines: List[str],
        keywords: List[str],
        used: set,
    ) -> Optional[int]:
        """Return index of first line matching any keyword, skipping used lines."""
        for i, line in enumerate(lines):
            if i in used:
                continue
            lo = line.lower()
            for kw in keywords:
                if kw in lo:
                    return i
        return None

    @staticmethod
    def _assign(
        vals: List[float],
        col_order: str,
        field_100: str,
        field_srv: Optional[str],
        result: Dict,
        sodium_conversion: bool = False,
    ) -> None:
        """
        Write vals[0] and vals[1] into result using the correct column assignment.

        col_order:
          'srv_first'  → vals[0]=serving,  vals[1]=100g
          '100_first'  → vals[0]=100g,     vals[1]=serving
        """
        def maybe_mg(v: float) -> float:
            return round(v * 1000, 3) if sodium_conversion and v < 5 else v

        if len(vals) == 0:
            return

        if len(vals) == 1:
            # Only one value found – store as 100g value (most reliable)
            result[field_100] = maybe_mg(vals[0])
            return

        v0, v1 = vals[0], vals[1]

        if col_order == "srv_first":
            val_srv = v0
            val_100 = v1
        else:  # 100_first (default)
            val_100 = v0
            val_srv = v1

        result[field_100] = maybe_mg(val_100)
        if field_srv:
            result[field_srv] = maybe_mg(val_srv)

    @staticmethod
    def _log_nutrient(label: str, field_100: str, field_srv: Optional[str],
                      result: Dict) -> None:
        srv_val = result.get(field_srv, "—") if field_srv else "—"
        print(f"  ✓ {label:35s}  /100g={result.get(field_100, '—'):>8}  "
              f"/srv={srv_val}")


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = NutritionParser()

    # --- Real OCR output from Kandos label (stacked, srv_first) ---
    real_ocr = """
NUTRITION INFORMATION
Serving size:11g
Serving per pack:10
Average Quantity Average Quantity
per'Serving
per 100g
Energy
250.3
2275.2kJ
59.9 kcal
545.2
Protein
0.8g
7.7g
Fat-Total
3.7g
33.5g
Saturated fatty acids
2.3g
20.6 g
Trans fatty acids
0g
0g
Carbohydrates-Tota
5.9g
53.2g
Dietary fiber
0.2g
1.8g
Sugar
5.7g
52.1g
Sodium(Na)
0.02g
0.2g
"""
    print("=" * 60)
    print("REAL OCR – Kandos Chocolate (stacked, srv_first)")
    print("=" * 60)
    result = parser.parse(real_ocr)

    print("\nExpected  protein_g=7.7  protein_per_serving_g=0.8")
    print(f"Got       protein_g={result.get('protein_g')}  "
          f"protein_per_serving_g={result.get('protein_per_serving_g')}")
    print("\nExpected  sodium_mg=200.0  sodium_per_serving_mg=20.0")
    print(f"Got       sodium_mg={result.get('sodium_mg')}  "
          f"sodium_per_serving_mg={result.get('sodium_per_serving_mg')}")
    print("\nExpected  energy_kcal_per_100g=545.2  energy_kcal_per_serving=59.9")
    print(f"Got       energy_kcal_per_100g={result.get('energy_kcal_per_100g')}  "
          f"energy_kcal_per_serving={result.get('energy_kcal_per_serving')}")