# -*- coding: utf-8 -*-
"""
Nutrition Label Parser - v4
============================
Handles all Sri Lankan product label variations:

  Layout modes:
    inline   – values on same line as nutrient name
    stacked  – each value on its own line below the name
    single   – only one column (Per 100g/ml, no serving)

  Column order:
    100_first  – Per 100g  | Per Serving
    srv_first  – Per Serving | Per 100g
    single     – only one column

  Special cases:
    3-column labels  (Per 100g | Per Serving | %RDA) → ignore 3rd column
    Two-table labels (Thai/foreign labels with 2 tables) → use English table
    <0.01g notation  → treated as 0.0
    Sodium in mg OR g → auto-detected, convert if in grams
    Sub-rows (of which sugar, soluble fiber, naturally occurring) → skip correctly
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
# Nutrient map — specific keywords BEFORE generic ones
# ---------------------------------------------------------------------------
NUTRIENT_MAP: List[Tuple] = [
    (["protein"],                       FIELD_PROTEIN_100,  FIELD_PROTEIN_SRV,  "g"),
    (["total carbohydrate",
      "carbohydrates-total",
      "carbohydrates total",
      "carbohydrate"],                  FIELD_CARBS_100,    FIELD_CARBS_SRV,    "g"),
    (["dietary fibre",
      "dietary fiber",
      "total dietary fiber",
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
    (["fat-total", "total fat",
      "total milk fat",
      "fat (total)"],                   FIELD_FAT_100,      FIELD_FAT_SRV,      "g"),
    (["cholesterol"],                   FIELD_CHOLESTEROL_100, FIELD_CHOLESTEROL_SRV, "mg"),
    (["sodium"],                        FIELD_SODIUM_100,   FIELD_SODIUM_SRV,   "mg"),
    (["calcium"],                       FIELD_CALCIUM_100,  None,               "mg"),
    (["iron"],                          FIELD_IRON_100,     None,               "mg"),
]

# Sub-rows to SKIP — these are indented child rows under a parent nutrient.
# If a line contains any of these AND comes after the parent, skip it entirely.
# Sub-rows to SKIP — lines that are child/sub items with no nutritional map entry.
# "of which saturated" is NOT here because saturated fat IS a mapped nutrient.
SUBROW_SKIP_KEYWORDS = [
    "of which total sugar",
    "of which added sugar",
    "naturally occurring", "naturally occuring",
    "added sugar", "added sugars",
    "soluble dietary fiber", "soluble fiber", "soluble fibre",
    "insoluble dietary fiber", "insoluble fiber", "insoluble fibre",
    "% rda", "%rda", "% rai", "% thai rdi",
    "salt",
]

# Lines that start a new nutrient (used to stop context scanning)
NEW_ROW_KEYWORDS = [
    "protein", "carbohydrate", "fiber", "fibre", "sugar",
    "fat", "cholesterol", "sodium", "calcium", "iron", "zinc",
    "vitamin", "energy", "saturated", "trans", "monounsaturated",
    "polyunsaturated",
]


class NutritionParser:

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def parse(self, ocr_text: str) -> Dict:
        lines = self._clean_lines(ocr_text)
        self._debug_print_lines(lines)

        result: Dict = {}

        # Step 1 — if two tables present (Thai/foreign labels), isolate English one
        lines = self._isolate_english_table(lines)

        # Step 2 — serving size
        self._extract_serving_size(lines, result)

        # Step 3 — detect column count, layout mode, column order
        col_count = self._detect_column_count(lines)
        col_order = self._detect_column_order(lines, col_count)
        mode      = self._detect_layout_mode(lines)

        print(f"  Layout mode    : {mode}")
        print(f"  Column count   : {col_count}")
        print(f"  Column order   : {col_order}\n")

        # Step 4 — energy
        if mode == "stacked":
            self._extract_energy_stacked(lines, col_order, result)
        else:
            self._extract_energy_inline(lines, col_order, result, col_count)

        # Step 5 — all other nutrients
        if mode == "stacked":
            self._extract_nutrients_stacked(lines, col_order, result)
        else:
            self._extract_nutrients_inline(lines, col_order, result, col_count)

        # Post-parse sanity check: if serving < 100g but per_100g values look like
        # per_serving values (i.e. 100g value < serving value), swap column assignments.
        result = self._verify_and_fix_column_order(result)

        self._debug_print_result(result)
        return result

    def _verify_and_fix_column_order(self, result: Dict) -> Dict:
        """
        Sanity check: for products with serving_size < 100g,
        the per_100g nutrient value should always be LARGER than per_serving.
        If not (e.g. protein_g=1.52 but protein_per_serving_g=7.6), the column
        order was misdetected — swap all paired values.
        """
        serving = result.get(FIELD_SERVING_SIZE, 100.0)
        serving_unit = result.get(FIELD_SERVING_UNIT, "g")

        # Only check when serving is clearly smaller than 100g/ml
        if serving >= 100.0:
            return result

        # Check 2-3 nutrients for the swap signal
        swap_votes = 0
        check_pairs = [
            (FIELD_PROTEIN_100,  FIELD_PROTEIN_SRV),
            (FIELD_CARBS_100,    FIELD_CARBS_SRV),
            (FIELD_ENERGY_KCAL_100, FIELD_ENERGY_KCAL_SRV),
        ]
        for f100, fsrv in check_pairs:
            v100 = result.get(f100)
            vsrv = result.get(fsrv)
            if v100 is not None and vsrv is not None and vsrv > 0:
                if v100 < vsrv:   # 100g value is smaller than serving value → wrong!
                    swap_votes += 1

        # Energy kcal is the single most reliable swap signal:
        # Per-100g kcal is ALWAYS higher than per-serving kcal when serving < 100g.
        # If energy_kcal_per_100g < energy_kcal_per_serving → definitely swapped.
        e100 = result.get(FIELD_ENERGY_KCAL_100)
        esrv = result.get(FIELD_ENERGY_KCAL_SRV)
        energy_swapped = (e100 is not None and esrv is not None and e100 < esrv)

        # Trigger swap if: energy alone signals it, OR 2+ other nutrients signal it
        if not energy_swapped and swap_votes < 2:
            return result  # looks correct

        if energy_swapped:
            print(f"  ⚠ Energy kcal swapped ({e100} < {esrv}) — swapping all paired values")

        # All _per_serving_ ↔ _per_100g_ swaps
        SWAP_PAIRS = [
            (FIELD_ENERGY_KCAL_100, FIELD_ENERGY_KCAL_SRV),
            (FIELD_ENERGY_KJ_100,   FIELD_ENERGY_KJ_SRV),
            (FIELD_PROTEIN_100,     FIELD_PROTEIN_SRV),
            (FIELD_CARBS_100,       FIELD_CARBS_SRV),
            (FIELD_SUGAR_100,       FIELD_SUGAR_SRV),
            (FIELD_FIBER_100,       FIELD_FIBER_SRV),
            (FIELD_FAT_100,         FIELD_FAT_SRV),
            (FIELD_SAT_FAT_100,     FIELD_SAT_FAT_SRV),
            (FIELD_MUFA_100,        FIELD_MUFA_SRV),
            (FIELD_PUFA_100,        FIELD_PUFA_SRV),
            (FIELD_TRANS_100,       FIELD_TRANS_SRV),
            (FIELD_CHOLESTEROL_100, FIELD_CHOLESTEROL_SRV),
            (FIELD_SODIUM_100,      FIELD_SODIUM_SRV),
        ]
        for f100, fsrv in SWAP_PAIRS:
            v100 = result.get(f100)
            vsrv = result.get(fsrv)
            if v100 is not None and vsrv is not None:
                result[f100] = vsrv
                result[fsrv] = v100

        return result

    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        required = [FIELD_ENERGY_KCAL_100, FIELD_PROTEIN_100]
        missing  = [f for f in required if f not in data]
        return (len(missing) == 0, missing)

    # -----------------------------------------------------------------------
    # Two-table isolation (Thai labels have Thai table + English table)
    # -----------------------------------------------------------------------

    def _isolate_english_table(self, lines: List[str]) -> List[str]:
        """
        If two nutrition tables exist, keep only the LAST / English one.
        Detection: count how many lines contain 'nutrition' or 'energy'.
        If there are 2+ 'energy' lines → two tables present → split at 2nd 'nutrition'.
        """
        nutrition_indices = [i for i, l in enumerate(lines)
                             if re.search(r"\bnutrition\b", l.lower())]
        energy_indices    = [i for i, l in enumerate(lines)
                             if re.search(r"\benergy\b", l.lower())]

        # Two tables if we see 2+ nutrition headers OR 2+ energy rows
        if len(nutrition_indices) >= 2:
            print(f"  ⚠ Two tables detected — using table starting at line {nutrition_indices[-1]}")
            return lines[nutrition_indices[-1]:]
        if len(energy_indices) >= 2:
            # Split at the second energy occurrence
            split = energy_indices[1]
            # Back up to find any preceding header lines
            for i in range(split - 1, max(split - 5, -1), -1):
                if re.search(r"nutrition|serving|composition", lines[i].lower()):
                    split = i
                    break
            print(f"  ⚠ Two energy rows detected — using section from line {split}")
            return lines[split:]

        return lines

    # -----------------------------------------------------------------------
    # Column count detection
    # -----------------------------------------------------------------------

    def _detect_column_count(self, lines: List[str]) -> int:
        """
        Returns 1, 2, or 3.
        3-column: header line has 'per 100' + 'per serv' + ('%' or 'rda' or 'rdi')
        1-column: no 'per serv' found anywhere
        2-column: default
        """
        for line in lines:
            lo = line.lower()
            has_100 = bool(re.search(r"per\s*100|100\s*m[lg]", lo))
            has_srv = bool(re.search(r"per\s*serv|per serve\b", lo))
            has_pct = bool(re.search(r"%\s*r[da]|rda|rdi|%\s*per", lo))
            if has_100 and has_srv and has_pct:
                return 3
            if has_100 and has_srv:
                return 2

        # Check stacked headers too
        has_srv_anywhere = any(
            re.search(r"per.{0,2}serv|per serve\b", l.lower()) for l in lines
        )
        if not has_srv_anywhere:
            return 1
        return 2

    # -----------------------------------------------------------------------
    # Layout mode detection
    # -----------------------------------------------------------------------

    def _detect_layout_mode(self, lines: List[str]) -> str:
        for i, line in enumerate(lines):
            lo = line.lower()
            for kw in ["protein", "carbohydrate", "total fat", "fat-total", "sodium"]:
                if kw in lo:
                    nums = self._extract_numbers(line)
                    if len(nums) >= 1:
                        return "inline"
                    if i + 1 < len(lines):
                        next_nums = self._extract_numbers(lines[i + 1])
                        if next_nums:
                            return "stacked"
        return "inline"

    # -----------------------------------------------------------------------
    # Column order detection
    # -----------------------------------------------------------------------

    def _detect_column_order(self, lines: List[str], col_count: int) -> str:
        if col_count == 1:
            return "single"

        re_100 = re.compile(r"per\s*100|100\s*m[lg]|100g|100ml")
        re_srv = re.compile(r"per.{0,2}serv")

        # Pass 1: inline header (both on same line)
        for line in lines:
            lo = line.lower()
            if re_100.search(lo) and re_srv.search(lo):
                pos_100 = lo.find("100")
                pos_srv = re_srv.search(lo).start()
                return "100_first" if pos_100 < pos_srv else "srv_first"

        # Pass 2: stacked header (consecutive lines, no digits in line)
        for i, line in enumerate(lines):
            lo = line.lower()
            is_header = bool(re_100.search(lo) or re_srv.search(lo))
            if not is_header or re.search(r"\d", lo):
                continue
            if i + 1 < len(lines):
                next_lo = lines[i + 1].lower()
                next_has_100 = bool(re_100.search(next_lo))
                next_has_srv = bool(re_srv.search(next_lo))
                if re_srv.search(lo) and next_has_100:
                    return "srv_first"
                if re_100.search(lo) and next_has_srv:
                    return "100_first"

        return "100_first"

    # -----------------------------------------------------------------------
    # Serving size
    # -----------------------------------------------------------------------

    def _extract_serving_size(self, lines: List[str], result: Dict) -> None:
        for i, line in enumerate(lines):
            if "serving size" in line.lower():
                # Include previous line — some OCR puts value BEFORE keyword
                parts = []
                if i > 0:
                    parts.append(lines[i - 1])
                parts.append(line)
                if i + 1 < len(lines):
                    parts.append(lines[i + 1])
                search = " ".join(parts)
                ml = re.search(r"(\d+(?:\.\d+)?)\s*ml", search, re.I)
                g  = re.search(r"(\d+(?:\.\d+)?)\s*g\b", search, re.I)
                if ml:
                    result[FIELD_SERVING_SIZE] = float(ml.group(1))
                    result[FIELD_SERVING_UNIT] = "ml"
                elif g:
                    result[FIELD_SERVING_SIZE] = float(g.group(1))
                    result[FIELD_SERVING_UNIT] = "g"
                if FIELD_SERVING_SIZE in result:
                    print(f"  ✓ Serving size : {result[FIELD_SERVING_SIZE]} {result[FIELD_SERVING_UNIT]}")
                return

    # -----------------------------------------------------------------------
    # Number extraction — handles <0.01 notation
    # -----------------------------------------------------------------------

    @staticmethod
    def _extract_numbers(text: str) -> List[float]:
        """
        Extract numeric values. Handles:
          <0.01  → 0.0
          0.01   → 0.01
          325kJ  → 325.0
        """
        # Replace <N with 0 first
        text = re.sub(r"<\s*(\d+\.?\d*)", r"0", text)
        return [float(m) for m in re.findall(r"\d+\.?\d*", text)]

    @staticmethod
    def _normalize_ocr_units(text: str) -> str:
        """Fix common OCR misreads: kea/keal/kca/kcai → kcal"""
        text = re.sub(r"\bk[ce][ae][al1iI]\b", "kcal", text, flags=re.I)
        text = re.sub(r"\bkcai\b", "kcal", text, flags=re.I)
        text = re.sub(r"\bkeal\b", "kcal", text, flags=re.I)
        return text

    @staticmethod
    def _is_subrow(line: str) -> bool:
        """Return True if this line is a sub-row that should be skipped."""
        lo = line.lower()
        return any(kw in lo for kw in SUBROW_SKIP_KEYWORDS)

    @staticmethod
    def _is_new_nutrient_row(line: str) -> bool:
        lo = line.lower()
        return any(kw in lo for kw in NEW_ROW_KEYWORDS)

    @staticmethod
    def _sodium_needs_conversion(context_lines: List[str]) -> bool:
        window = " ".join(context_lines).lower()
        return "mg" not in window  # if no 'mg' tag → values are in g

    # -----------------------------------------------------------------------
    # INLINE energy
    # -----------------------------------------------------------------------

    def _extract_energy_inline(self, lines, col_order, result, col_count=2):
        for i, line in enumerate(lines):
            if not re.search(r"\benergy\b", line.lower()):
                continue
            # Collect lines for energy window — stop at next nutrient keyword
            window = [lines[i]]
            for wi in range(i + 1, min(i + 5, len(lines))):
                ln = lines[wi]
                # Stop if this looks like a new nutrient row (not another energy line)
                if self._is_new_nutrient_row(ln) and "energy" not in ln.lower():
                    break
                window.append(ln)
            window_text = "\n".join(window).lower()
            kj_vals   = [float(m) for m in re.findall(r"(\d+\.?\d*)\s*kj",   window_text)]
            kcal_vals = [float(m) for m in re.findall(r"(\d+\.?\d*)\s*kcal", window_text)]

            # Special case: "Energy(kcal)" — kcal is in the label name, not after numbers.
            # Extract all numbers from the trigger line directly as kcal values.
            if not kcal_vals and "kcal" in lines[i].lower():
                kcal_vals = self._extract_numbers(lines[i])[:2]

            if not kcal_vals:
                for sub in window[1:]:
                    nums = self._extract_numbers(sub)
                    if nums and "kj" not in sub.lower():
                        kcal_vals = nums[:2]
                        break
            # For 3-column, take only first 2 values
            if kj_vals:
                self._assign(kj_vals[:2],   col_order, FIELD_ENERGY_KJ_100,   FIELD_ENERGY_KJ_SRV,   result)
            if kcal_vals:
                self._assign(kcal_vals[:2], col_order, FIELD_ENERGY_KCAL_100, FIELD_ENERGY_KCAL_SRV, result)
            self._log_energy(result)
            break

    # -----------------------------------------------------------------------
    # STACKED energy
    # -----------------------------------------------------------------------

    def _extract_energy_stacked(self, lines, col_order, result):
        for i, line in enumerate(lines):
            if not re.search(r"\benergy\b", line.lower()):
                continue
            value_lines = []
            for j in range(i + 1, min(i + 7, len(lines))):
                vl = lines[j]
                if self._is_new_nutrient_row(vl) and "energy" not in vl.lower():
                    break
                if re.search(r"\d", vl):
                    value_lines.append(vl)

            entries = []
            for vl in value_lines:
                lo   = vl.lower()
                nums = self._extract_numbers(vl)
                if not nums:
                    continue
                tag = ("kcal" if "kcal" in lo else ("kj" if "kj" in lo else None))
                entries.append((nums[0], tag))

            kj_vals, kcal_vals = [], []
            for pi in range(0, len(entries), 2):
                a = entries[pi]
                b = entries[pi + 1] if pi + 1 < len(entries) else None
                pair_unit = a[1] or (b[1] if b else None)
                pair_vals = [a[0]] + ([b[0]] if b else [])
                if pair_unit == "kj":
                    kj_vals.extend(pair_vals)
                elif pair_unit == "kcal":
                    kcal_vals.extend(pair_vals)
                else:
                    for v in pair_vals:
                        (kj_vals if v > 200 else kcal_vals).append(v)

            if kj_vals:
                self._assign(kj_vals,   col_order, FIELD_ENERGY_KJ_100,   FIELD_ENERGY_KJ_SRV,   result)
            if kcal_vals:
                self._assign(kcal_vals, col_order, FIELD_ENERGY_KCAL_100, FIELD_ENERGY_KCAL_SRV, result)
            self._log_energy(result)
            break

    @staticmethod
    def _log_energy(result):
        if FIELD_ENERGY_KCAL_100 in result:
            print(f"  ✓ Energy  kcal/100g={result.get(FIELD_ENERGY_KCAL_100)}  "
                  f"kcal/srv={result.get(FIELD_ENERGY_KCAL_SRV)}")
        if FIELD_ENERGY_KJ_100 in result:
            print(f"  ✓ Energy  kJ/100g={result.get(FIELD_ENERGY_KJ_100)}  "
                  f"kJ/srv={result.get(FIELD_ENERGY_KJ_SRV)}")

    # -----------------------------------------------------------------------
    # INLINE nutrients
    # -----------------------------------------------------------------------

    def _extract_nutrients_inline(self, lines, col_order, result, col_count=2):
        used: set = set()
        for (keywords, field_100, field_srv, unit) in NUTRIENT_MAP:
            idx = self._find_keyword_line(lines, keywords, used)
            if idx is None:
                continue
            # Skip sub-rows
            if self._is_subrow(lines[idx]):
                continue
            used.add(idx)
            vals = self._collect_inline_values(lines, idx, unit, col_count)
            if not vals:
                continue
            sodium_conv = (field_100 == FIELD_SODIUM_100 and
                           self._sodium_needs_conversion(lines[idx: idx + 3]))
            self._assign(vals, col_order, field_100, field_srv, result,
                         sodium_conversion=sodium_conv)
            self._log_nutrient(keywords[0], field_100, field_srv, result)

    def _collect_inline_values(self, lines, idx, unit, col_count=2) -> List[float]:
        """
        Extract up to 2 values from the inline nutrient row.
        For 3-column labels: take first 2 values only (ignore %RDA).
        """
        vals = []
        context_end = min(idx + 3, len(lines))
        for j in range(idx, context_end):
            line = lines[j]
            lo   = line.lower()
            if j > idx:
                if self._is_new_nutrient_row(lo) or self._is_subrow(lo):
                    break
            for n in self._extract_numbers(line):
                if unit == "g"  and n > 999:
                    continue
                if unit == "mg" and n > 99999:
                    continue
                vals.append(n)
                if len(vals) == 2:  # always take max 2 (ignore 3rd column)
                    return vals
        return vals

    # -----------------------------------------------------------------------
    # STACKED nutrients
    # -----------------------------------------------------------------------

    def _extract_nutrients_stacked(self, lines, col_order, result):
        used: set = set()
        for (keywords, field_100, field_srv, unit) in NUTRIENT_MAP:
            idx = self._find_keyword_line(lines, keywords, used)
            if idx is None:
                continue
            if self._is_subrow(lines[idx]):
                continue
            used.add(idx)
            vals = self._collect_stacked_values(lines, idx, unit)
            if not vals:
                continue
            # For sodium: check both below AND above for mg tag
            sodium_window = lines[max(0, idx-3): idx+4]
            sodium_conv = (field_100 == FIELD_SODIUM_100 and
                           self._sodium_needs_conversion(sodium_window))
            self._assign(vals, col_order, field_100, field_srv, result,
                         sodium_conversion=sodium_conv)
            self._log_nutrient(keywords[0], field_100, field_srv, result)

    def _collect_stacked_values(self, lines, idx, unit) -> List[float]:
        """
        Collect up to 2 values from lines below the trigger.
        Falls back to looking ABOVE the trigger if nothing found below —
        some OCR layouts place values before the nutrient keyword line.
        """
        # Forward scan (normal)
        vals = []
        for j in range(idx + 1, min(idx + 5, len(lines))):
            line = lines[j]
            if self._is_new_nutrient_row(line) or self._is_subrow(line):
                break
            nums = self._extract_numbers(line)
            if not nums:
                continue
            n = nums[0]
            if unit == "g"  and n > 999:
                continue
            if unit == "mg" and n > 99999:
                continue
            vals.append(n)
            if len(vals) == 2:
                break
        if vals:
            return vals

        # Backward scan — keyword comes AFTER its values in the OCR stream
        above = []
        for j in range(idx - 1, max(idx - 4, -1), -1):
            line = lines[j]
            if self._is_new_nutrient_row(line) or self._is_subrow(line):
                break
            nums = self._extract_numbers(line)
            if not nums:
                continue
            n = nums[0]
            if unit == "g"  and n > 999:
                continue
            if unit == "mg" and n > 99999:
                continue
            above.insert(0, n)  # prepend to preserve original order
            if len(above) == 2:
                break
        return above

    # -----------------------------------------------------------------------
    # Shared utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def _find_keyword_line(lines, keywords, used):
        for i, line in enumerate(lines):
            if i in used:
                continue
            lo = line.lower()
            for kw in keywords:
                if kw in lo:
                    return i
        return None

    @staticmethod
    def _assign(vals, col_order, field_100, field_srv, result, sodium_conversion=False):
        def maybe_mg(v):
            return round(v * 1000, 3) if sodium_conversion and v < 5 else v
        if not vals:
            return
        if len(vals) == 1:
            result[field_100] = maybe_mg(vals[0])
            return
        v0, v1 = vals[0], vals[1]
        if col_order == "srv_first":
            val_srv, val_100 = v0, v1
        else:
            val_100, val_srv = v0, v1
        result[field_100] = maybe_mg(val_100)
        if field_srv:
            result[field_srv] = maybe_mg(val_srv)

    @staticmethod
    def _log_nutrient(label, field_100, field_srv, result):
        srv_val = result.get(field_srv, "—") if field_srv else "—"
        print(f"  ✓ {label:35s}  /100g={result.get(field_100, '—'):>8}  /srv={srv_val}")

    @staticmethod
    def _debug_print_lines(lines):
        print("\n" + "=" * 60)
        print("OCR TEXT (cleaned lines):")
        print("=" * 60)
        for i, l in enumerate(lines):
            print(f"  [{i:02d}] {l}")
        print("=" * 60 + "\n")

    @staticmethod
    def _debug_print_result(result):
        print("\n" + "=" * 60)
        print("PARSED NUTRITION DATA:")
        print("=" * 60)
        for k, v in result.items():
            print(f"  {k}: {v}")
        print("=" * 60 + "\n")

    def _clean_lines(self, text):
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return [self._normalize_ocr_units(l) for l in lines]