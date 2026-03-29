# -*- coding: utf-8 -*-
"""
Nutrition Label Parser - v5
============================
Handles all Sri Lankan product label variations observed across 55+ real labels:

  Layout modes:
    inline   – values on same line as nutrient name
    stacked  – each value on its own line below the name
    single   – only one column (Per 100g/ml, no serving)

  Column orders:
    100_first  – Per 100g  | Per Serving   (most common)
    srv_first  – Per Serving | Per 100g    (KIST juice, CBL chocolate, Kandos)
    single     – only one column

  Special cases handled:
    3-column labels  (Per 100g | Per Serving | %RDA)  → ignore 3rd column
    4-column labels  (Kellogg's with milk column)      → ignore 3rd + 4th
    Two-table labels (Thai/foreign labels)             → use English/last table
    Vitamin/mineral rows embedded WITHOUT a header     → truncate at first vitamin row
    <0.01g / ND / LOQ notation                        → treated as 0.0
    Sodium in mg OR g                                 → auto-detected
    "of which" sub-rows                               → universally skipped
    "Naturally occurring sugar" / "Added sugar"       → skipped
    Salt as NaCl (g) → convert to sodium mg           → ÷ 2.5
    "Calories" header (US-style labels)               → treated as energy kcal
    Single-column labels (Finches Gem, white beans)   → parsed correctly
    Rotated / bottom-to-top labels (Maliban packets)  → handled via value scan
    Labels with Unit column (Ratthi milk powder)      → unit column skipped
    Per-1g serving labels (seasoning/spice products)  → handled
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
    (["protein content", "total protein", "protein"],
                                            FIELD_PROTEIN_100,  FIELD_PROTEIN_SRV,  "g"),
    (["total carbohydrate",
      "carbohydrates-total",
      "carbohydrates total",
      "available carbohydrate",
      "carbohydr"],                         FIELD_CARBS_100,    FIELD_CARBS_SRV,    "g"),
    (["total dietary fiber",
      "dietary fibre",
      "dietary fiber",
      "crude fibre",
      "total fiber",
      "fibre"],                             FIELD_FIBER_100,    FIELD_FIBER_SRV,    "g"),
    (["total sugar", "total sugars", "sugar"],
                                            FIELD_SUGAR_100,    FIELD_SUGAR_SRV,    "g"),
    (["saturated fatty acid",
      "saturated fat",
      "sat. fat", "sfa",
      "saturated"],                         FIELD_SAT_FAT_100,  FIELD_SAT_FAT_SRV,  "g"),
    (["monounsaturated", "mufa"],           FIELD_MUFA_100,     FIELD_MUFA_SRV,     "g"),
    (["polyunsaturated", "pufa"],           FIELD_PUFA_100,     FIELD_PUFA_SRV,     "g"),
    (["trans fatty acid",
      "trans-fatty", "trans fat",
      "trans fatty", "trans"],              FIELD_TRANS_100,    FIELD_TRANS_SRV,    "g"),
    (["fat-total", "total milk fat",
      "total fat", "fat (total)",
      "fat"],                               FIELD_FAT_100,      FIELD_FAT_SRV,      "g"),
    (["cholesterol"],                       FIELD_CHOLESTEROL_100, FIELD_CHOLESTEROL_SRV, "mg"),
    (["sodium"],                            FIELD_SODIUM_100,   FIELD_SODIUM_SRV,   "mg"),
    (["calcium"],                           FIELD_CALCIUM_100,  None,               "mg"),
    (["iron"],                              FIELD_IRON_100,     None,               "mg"),
]

# ---------------------------------------------------------------------------
# Sub-rows to SKIP universally
# ---------------------------------------------------------------------------
SUBROW_SKIP_KEYWORDS = [
    # Universal prefix — catches all "of which X" variations
    "of which",
    # Explicit sugar sub-rows
    "naturally occurring sugar",
    "naturally occuring sugar",
    "naturally occurring",
    "added sugar",
    "added sugars",
    # Fiber sub-rows
    "soluble dietary fiber",
    "soluble dietary fibre",
    "soluble fiber",
    "soluble fibre",
    "insoluble dietary fiber",
    "insoluble dietary fibre",
    "insoluble fiber",
    "insoluble fibre",
    # Other sub-rows
    "salt",
    "potassium",
    # %RDA column headers that leak in
    "% rda", "%rda", "% rai", "% thai rdi", "% nrv", "%nrv",
    # Misc
    "energy from fat",
]

# ---------------------------------------------------------------------------
# Vitamin / mineral keywords — stop parsing macros when we hit these
# ---------------------------------------------------------------------------
VITAMIN_MINERAL_PREFIXES = [
    "vitamin", "vit.", "vit ",
    "zinc", "magnesium", "phosphorus", "phosphorous",
    "iodine", "selenium", "folate", "folic",
    "niacin", "riboflavin", "thiamine", "pantothenic",
    "biotin", "potassium", "chloride", "copper",
    "manganese", "chromium", "molybdenum",
    "minerals",  # section header
    "vitamins",  # section header
]

# New nutrient keywords — used to stop context scanning
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

        # Step 1 — isolate English/main table (handle two-table Thai labels etc.)
        lines = self._isolate_english_table(lines)

        # Step 2 — serving size
        self._extract_serving_size(lines, result)

        # Step 3 — detect layout, columns
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

        # Step 5 — truncate vitamin rows BEFORE nutrient extraction
        lines = self._truncate_at_vitamins(lines)

        # Step 6 — all other nutrients
        if mode == "stacked":
            self._extract_nutrients_stacked(lines, col_order, result)
        else:
            self._extract_nutrients_inline(lines, col_order, result, col_count)

        # Step 7 — sodium: handle "salt as NaCl in g" edge case
        result = self._fix_salt_as_sodium(result, lines)

        # Step 8 — column swap sanity check
        result = self._verify_and_fix_column_order(result)

        # Step 9 — impossible value sanity fix
        result = self._post_parse_sanity_fix(result)

        self._debug_print_result(result)
        return result

    # -----------------------------------------------------------------------
    # Vitamin/mineral truncation — works WITH or WITHOUT a section header
    # -----------------------------------------------------------------------

    def _truncate_at_vitamins(self, lines: List[str]) -> List[str]:
        """
        Remove vitamin/mineral rows from the line list so they can't
        corrupt macro nutrient extraction.

        Strategy:
          1. If we find a standalone "Vitamins" or "Minerals" header → truncate there.
          2. Otherwise, truncate at the FIRST line whose content starts with
             a vitamin/mineral keyword (e.g. "Vitamin A", "Zinc", "Calcium (mg)").
             EXCEPTION: "Calcium" and "Iron" ARE in the NUTRIENT_MAP — we only
             truncate at them if they appear AFTER we've already extracted all
             the main macros (protein, carbs, fat).  We detect this by checking
             whether the line is preceded by a macro like "sodium".
        """
        # Pass 1: named section header
        for i, line in enumerate(lines):
            lo = line.lower().strip()
            if lo in ("vitamins", "minerals", "vitamins and minerals",
                      "vitamins & minerals"):
                print(f"  ⚠ Vitamin/mineral section header at line {i} — truncating")
                return lines[:i]

        # Pass 2: first line that starts with a vitamin/mineral keyword
        # We skip calcium & iron here because they are mapped macros —
        # handle them via the NUTRIENT_MAP normally.
        skip_also = {"calcium", "iron"}   # keep in macro extraction
        sodium_seen = False
        for i, line in enumerate(lines):
            lo = line.lower().strip()
            if "sodium" in lo:
                sodium_seen = True
            # After sodium we are definitely in macro territory — now a
            # "Vitamin …" line is clearly a non-macro row
            if any(lo.startswith(p) for p in VITAMIN_MINERAL_PREFIXES
                   if p not in skip_also):
                print(f"  ⚠ Vitamin keyword '{line[:30]}' at line {i} — truncating")
                return lines[:i]

        return lines

    # -----------------------------------------------------------------------
    # Two-table isolation (Thai/foreign labels)
    # -----------------------------------------------------------------------

    def _isolate_english_table(self, lines: List[str]) -> List[str]:
        """If two nutrition tables exist, keep only the LAST / English one."""
        nutrition_indices = [i for i, l in enumerate(lines)
                             if re.search(r"\bnutrition\b", l.lower())]
        energy_indices    = [i for i, l in enumerate(lines)
                             if re.search(r"\benergy\b", l.lower())]

        if len(nutrition_indices) >= 2:
            print(f"  ⚠ Two tables detected — using table starting at line {nutrition_indices[-1]}")
            return lines[nutrition_indices[-1]:]

        if len(energy_indices) >= 2:
            split = energy_indices[1]
            for i in range(split - 1, max(split - 5, -1), -1):
                if re.search(r"nutrition|serving|composition", lines[i].lower()):
                    split = i
                    break
            print(f"  ⚠ Two energy rows detected — using section from line {split}")
            return lines[split:]

        return lines

    # -----------------------------------------------------------------------
    # Column count detection — handles 1, 2, 3, 4 columns
    # -----------------------------------------------------------------------

    def _detect_column_count(self, lines: List[str]) -> int:
        """Returns 1, 2, or 3 (treat 4-col as 3-col, we always take max 2 values)."""
        for line in lines:
            lo = line.lower()
            # Handle "Per100g" (no space), "per 100 g", "per 100ml" etc.
            has_100 = bool(re.search(
                r"per\s*100|100\s*m[lg]|per\s*100\s*g|per100", lo))
            # Handle "Per Serving", "per serve", "fer serving" (OCR typo f→p)
            has_srv = bool(re.search(
                r"per.{0,4}serv|per serve|fer\s*serv|[fp]er\s*serving", lo))
            has_pct = bool(re.search(
                r"%\s*r[da]|rda|rdi|%\s*nrv|%\s*per|nrv", lo))
            if has_100 and has_srv and has_pct:
                return 3
            if has_100 and has_srv:
                return 2

        # Stacked headers — scan all lines
        has_srv_anywhere = any(
            re.search(r"per.{0,4}serv|per serve|fer\s*serv", l.lower())
            for l in lines
        )
        if not has_srv_anywhere:
            return 1
        return 2

    # -----------------------------------------------------------------------
    # Layout mode detection
    # -----------------------------------------------------------------------

    def _detect_layout_mode(self, lines: List[str]) -> str:
        """
        Determine if values are inline (same line as nutrient name)
        or stacked (values on lines below the nutrient name).
        """
        for i, line in enumerate(lines):
            lo = line.lower()
            for kw in ["protein", "carbohydrate", "total fat", "fat-total",
                       "sodium", "total carbohydrate"]:
                if kw in lo:
                    nums = self._extract_numbers(line)
                    if len(nums) >= 1:
                        return "inline"
                    # Check next line for numbers
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

        re_100 = re.compile(r"per\s*100|100\s*m[lg]|100g|100ml|\bper\s+100\b")
        re_srv = re.compile(r"per.{0,4}serv|quantity\s+per\s+serv|per\s+serve\b")

        # Pass 1: inline header (both on same line)
        for line in lines:
            lo = line.lower()
            m100 = re_100.search(lo)
            msrv = re_srv.search(lo)
            if m100 and msrv:
                return "100_first" if m100.start() < msrv.start() else "srv_first"

        # Pass 2: stacked headers (look at consecutive non-numeric lines)
        for i, line in enumerate(lines):
            lo = line.lower()
            if not (re_100.search(lo) or re_srv.search(lo)):
                continue
            if re.search(r"\d", lo):  # has digits → not a pure header line
                continue
            if i + 1 < len(lines):
                next_lo = lines[i + 1].lower()
                if re_srv.search(lo) and re_100.search(next_lo):
                    return "srv_first"
                if re_100.search(lo) and re_srv.search(next_lo):
                    return "100_first"

        # Pass 3: infer from "quantity per serving | quantity per 100g" pattern
        for line in lines:
            lo = line.lower()
            if "quantity per serving" in lo and "quantity per 100" in lo:
                pos_srv = lo.find("quantity per serving")
                pos_100 = lo.find("quantity per 100")
                return "srv_first" if pos_srv < pos_100 else "100_first"
            if "per serving" in lo and "per 100" in lo:
                pos_srv = lo.find("per serving")
                pos_100 = lo.find("per 100")
                return "srv_first" if pos_srv < pos_100 else "100_first"

        return "100_first"

    # -----------------------------------------------------------------------
    # Serving size
    # -----------------------------------------------------------------------

    def _extract_serving_size(self, lines: List[str], result: Dict) -> None:
        for i, line in enumerate(lines):
            lo = line.lower()
            if "serving size" in lo or "serving size:" in lo:
                # Collect context: prev line, this line, next line
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
                    print(f"  ✓ Serving size : {result[FIELD_SERVING_SIZE]} "
                          f"{result[FIELD_SERVING_UNIT]}")
                return

        # Fallback: "Serving size is X ml/g" or "Serving size - X"
        for line in lines:
            m = re.search(r"serving\s+size\s*(?:is|:|-|–)?\s*(\d+(?:\.\d+)?)\s*(ml|g)\b",
                          line, re.I)
            if m:
                result[FIELD_SERVING_SIZE] = float(m.group(1))
                result[FIELD_SERVING_UNIT] = m.group(2).lower()
                print(f"  ✓ Serving size : {result[FIELD_SERVING_SIZE]} "
                      f"{result[FIELD_SERVING_UNIT]}")
                return

    # -----------------------------------------------------------------------
    # Number extraction — handles <0.01, ND, LOQ, "Not Detected"
    # -----------------------------------------------------------------------

    @staticmethod
    def _extract_numbers(text: str) -> List[float]:
        """Extract numeric values from a text string."""
        # Replace <N → 0, ND/LOQ → 0
        text = re.sub(r"<\s*(\d+\.?\d*)", r"0", text)
        text = re.sub(r"N\.?D\.?", "0", text, flags=re.I)
        text = re.sub(r"LOQ\s*(?:\([^)]*\))?", "0", text, flags=re.I)
        text = re.sub(r"not\s+detected", "0", text, flags=re.I)
        # Remove standalone "9" that is clearly a misread of the unit "g"
        # Only remove when "9" appears alone (not part of a larger number)
        text = re.sub(r"(?<!\d)9(?!\d)", " ", text)
        return [float(m) for m in re.findall(r"\d+\.?\d*", text)]

    @staticmethod
    def _normalize_ocr_units(text: str) -> str:
        """Fix common OCR misreads."""
        # kcal variants
        text = re.sub(r"\bk[ce][ae][al1iIl]\b", "kcal", text, flags=re.I)
        text = re.sub(r"\bkcai\b", "kcal", text, flags=re.I)
        text = re.sub(r"\bkeal\b", "kcal", text, flags=re.I)
        text = re.sub(r"\bKcal\b", "kcal", text)
        # Not Detected / LOQ → 0g
        text = re.sub(r"\bnot\s+detected\b", "0g", text, flags=re.I)
        text = re.sub(r"\bLOQ\s*\([^)]*\)", "0g", text, flags=re.I)
        text = re.sub(r"\bND\s*\(LOQ[^)]*\)", "0g", text, flags=re.I)
        return text

    @staticmethod
    def _is_subrow(line: str) -> bool:
        """
        Return True if this line is a sub-row that should be skipped.

        Uses startswith for most keywords to avoid false matches —
        e.g. "sugar" must not match "Total Sugar" (a mapped nutrient).
        """
        lo = line.lower().strip()
        # These must match at the START of the line (sub-row prefixes)
        PREFIX_KEYWORDS = [
            "of which",
            "naturally occurring",
            "naturally occuring",
            "added sugar",
            "added sugars",
            "soluble dietary fiber",
            "soluble dietary fibre",
            "soluble fiber",
            "soluble fibre",
            "insoluble dietary fiber",
            "insoluble dietary fibre",
            "insoluble fiber",
            "insoluble fibre",
            "energy from fat",
            "- saturated",
            "-saturated",
            "- trans",
            "-trans",
        ]
        # These match anywhere (column headers leaking in)
        ANYWHERE_KEYWORDS = [
            "% rda", "%rda", "% rai", "% thai rdi", "% nrv", "%nrv",
        ]
        for kw in PREFIX_KEYWORDS:
            if lo.startswith(kw):
                return True
        for kw in ANYWHERE_KEYWORDS:
            if kw in lo:
                return True
        return False

    @staticmethod
    def _is_new_nutrient_row(line: str) -> bool:
        lo = line.lower()
        return any(kw in lo for kw in NEW_ROW_KEYWORDS)

    # -----------------------------------------------------------------------
    # INLINE energy
    # -----------------------------------------------------------------------

    @staticmethod
    def _extract_paired_values_from_line(line: str, tagged_vals: list) -> list:
        """
        When a line has a unit-tagged value (e.g. "59.9kcal") AND
        additional untagged numbers (e.g. "545.2"), return all numbers
        on that line. The untagged numbers are the paired column values.

        Example: "59.9kcal  545.2" → tagged=[59.9], untagged=[545.2]
        This gives us both the srv and per-100g values from one line.
        """
        all_nums = [float(m) for m in re.findall(r"\d+\.?\d*", line)]
        # Return in original order — caller knows column assignment
        return all_nums

    def _extract_energy_inline(self, lines, col_order, result, col_count=2):
        for i, line in enumerate(lines):
            if not re.search(r"\benergy\b|\bcalories\b", line.lower()):
                continue

            window = [lines[i]]
            for wi in range(i + 1, min(i + 6, len(lines))):
                ln = lines[wi]
                if self._is_new_nutrient_row(ln) and "energy" not in ln.lower():
                    break
                window.append(ln)

            window_text = "\n".join(window).lower()

            # Extract kJ values — handle "J" (missing k prefix from OCR)
            kj_vals = [float(m) for m in re.findall(r"(\d+\.?\d*)\s*k?j(?!\w)", window_text)]

            # Extract kcal values — first pass: explicitly tagged
            kcal_vals = [float(m) for m in re.findall(r"(\d+\.?\d*)\s*kcal", window_text)]

            # Second pass: for each line that has a kcal-tagged number,
            # also grab any untagged numbers on the SAME line as the paired value.
            # Example: "59.9kcal  545.2" → both 59.9 and 545.2 are kcal values
            if len(kcal_vals) < 2:
                for sub in window:
                    sub_lo = sub.lower()
                    if "kcal" in sub_lo:
                        all_on_line = [float(m) for m in re.findall(r"\d+\.?\d*", sub_lo)]
                        tagged = [float(m) for m in re.findall(r"(\d+\.?\d*)\s*kcal", sub_lo)]
                        untagged = [n for n in all_on_line if n not in tagged and n > 0]
                        # Add untagged paired values not already in kcal_vals
                        for n in untagged:
                            if n not in kcal_vals:
                                kcal_vals.append(n)
                        if len(kcal_vals) >= 2:
                            break

            # Third pass: "Energy (kcal)" — all numbers on trigger line are kcal
            if not kcal_vals and "kcal" in lines[i].lower():
                kcal_vals = self._extract_numbers(lines[i])[:2]

            # Fourth pass: "Calories NNN" (US labels, single column)
            if not kcal_vals and re.search(r"\bcalories\b", lines[i].lower()):
                nums = self._extract_numbers(lines[i])
                if nums:
                    kcal_vals = nums[:1]

            # Fifth pass: fallback — untagged numbers on non-kJ lines
            if not kcal_vals:
                for sub in window[1:]:
                    nums = self._extract_numbers(sub)
                    if nums and "kj" not in sub.lower():
                        kcal_vals = nums[:2]
                        break

            # Cross-validate and repair OCR digit errors using kJ <-> kcal ratio
            kj_vals_r, kcal_vals_r = self._repair_energy_ocr(
                kj_vals[:2], kcal_vals[:2])

            if kj_vals_r:
                self._assign(kj_vals_r,   col_order, FIELD_ENERGY_KJ_100,
                             FIELD_ENERGY_KJ_SRV,   result)
            if kcal_vals_r:
                self._assign(kcal_vals_r, col_order, FIELD_ENERGY_KCAL_100,
                             FIELD_ENERGY_KCAL_SRV, result)
            self._log_energy(result)
            break

    # -----------------------------------------------------------------------
    # STACKED energy
    # -----------------------------------------------------------------------

    def _extract_energy_stacked(self, lines, col_order, result):
        for i, line in enumerate(lines):
            if not re.search(r"\benergy\b|\bcalories\b", line.lower()):
                continue
            value_lines = []
            for j in range(i + 1, min(i + 8, len(lines))):
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

            # Cross-validate and repair OCR digit errors using kJ <-> kcal ratio
            kj_vals, kcal_vals = self._repair_energy_ocr(kj_vals, kcal_vals)

            if kj_vals:
                self._assign(kj_vals,   col_order, FIELD_ENERGY_KJ_100,
                             FIELD_ENERGY_KJ_SRV,   result)
            if kcal_vals:
                self._assign(kcal_vals, col_order, FIELD_ENERGY_KCAL_100,
                             FIELD_ENERGY_KCAL_SRV, result)
            self._log_energy(result)
            break

    @staticmethod
    def _repair_energy_ocr(kj_vals: list, kcal_vals: list):
        """
        Cross-validate kJ and kcal values using the known ratio (1 kcal = 4.184 kJ).

        IMPORTANT: Only repair when both lists have the SAME length.
        If they differ, the values are from different columns and pairing
        them for comparison would produce false corrections.
        Example: kj=[2275.2] (per-100g only), kcal=[59.9, 545.2] (srv+100g)
        Comparing 2275.2 vs 59.9 looks like a digit error but it is not —
        they are from different columns entirely.
        """
        KJ_PER_KCAL = 4.184
        TOLERANCE   = 0.30
        OCR_FACTOR  = 10.0

        if not kj_vals or not kcal_vals:
            return kj_vals, kcal_vals

        # Safety: only repair matched pairs (same column count)
        if len(kj_vals) != len(kcal_vals):
            # Just do a basic plausibility filter — kcal/100g > 1000 is impossible
            kcal_clean = [v for v in kcal_vals if v <= 1000]
            kj_clean   = [v for v in kj_vals   if v <= 5000]
            return kj_clean or kj_vals, kcal_clean or kcal_vals

        repaired_kcal = list(kcal_vals)
        for idx, (kj, kcal) in enumerate(zip(kj_vals, kcal_vals)):
            if kj <= 0 or kcal <= 0:
                continue
            expected_kcal = kj / KJ_PER_KCAL
            ratio = kcal / expected_kcal

            # kcal is ~10x too large (extra digit appended by OCR, e.g. 77 -> 771)
            if abs(ratio - OCR_FACTOR) / OCR_FACTOR < TOLERANCE:
                fixed = round(kcal / OCR_FACTOR, 2)
                print(f"  ⚠ OCR digit fix: kcal {kcal} -> {fixed} "
                      f"(expected ~{round(expected_kcal,1)} from {kj} kJ)")
                repaired_kcal[idx] = fixed

            # kcal is ~10x too small (digit dropped by OCR)
            elif abs(ratio - 1.0/OCR_FACTOR) / (1.0/OCR_FACTOR) < TOLERANCE:
                fixed = round(kcal * OCR_FACTOR, 2)
                print(f"  ⚠ OCR digit fix: kcal {kcal} -> {fixed} "
                      f"(expected ~{round(expected_kcal,1)} from {kj} kJ)")
                repaired_kcal[idx] = fixed

        # Also check kJ against kcal in case kJ is the bad one
        repaired_kj = list(kj_vals)
        for idx, (kj, kcal) in enumerate(zip(kj_vals, repaired_kcal)):
            if kj <= 0 or kcal <= 0:
                continue
            expected_kj = kcal * KJ_PER_KCAL
            ratio = kj / expected_kj

            if abs(ratio - OCR_FACTOR) / OCR_FACTOR < TOLERANCE:
                fixed = round(kj / OCR_FACTOR, 2)
                print(f"  ⚠ OCR digit fix: kJ {kj} -> {fixed} "
                      f"(expected ~{round(expected_kj,1)} from {kcal} kcal)")
                repaired_kj[idx] = fixed
            elif abs(ratio - 1.0/OCR_FACTOR) / (1.0/OCR_FACTOR) < TOLERANCE:
                fixed = round(kj * OCR_FACTOR, 2)
                print(f"  ⚠ OCR digit fix: kJ {kj} -> {fixed} "
                      f"(expected ~{round(expected_kj,1)} from {kcal} kcal)")
                repaired_kj[idx] = fixed

        return repaired_kj, repaired_kcal

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
            if self._is_subrow(lines[idx]):
                # Special case: extract SUGAR from "of which Total Sugar" sub-row
                # even though we skip it for the parent carbs extraction
                if field_100 == FIELD_SUGAR_100 and FIELD_SUGAR_100 not in result:
                    vals = self._collect_inline_values(lines, idx, unit, col_count)
                    if vals:
                        self._assign(vals, col_order, field_100, field_srv, result)
                        print(f"  ✓ sugar (from sub-row)  /100g={result.get(field_100)} /srv={result.get(field_srv,'—')}")
                continue
            used.add(idx)
            vals = self._collect_inline_values(lines, idx, unit, col_count)
            if not vals:
                continue
            sodium_conv = (field_100 == FIELD_SODIUM_100 and
                           self._sodium_is_in_grams(lines, idx))
            self._assign(vals, col_order, field_100, field_srv, result,
                         sodium_conversion=sodium_conv)
            self._log_nutrient(keywords[0], field_100, field_srv, result)

    @staticmethod
    def _strip_energy_values(text: str) -> str:
        """Remove numbers that are explicitly tagged as energy units (kcal/kJ).
        Prevents e.g. "Carbohydr  385 kcal  193 kcal" from yielding carbs=385."""
        return re.sub(r"\d+\.?\d*\s*(?:kcal|kj)", " ", text, flags=re.I)

    def _collect_inline_values(self, lines, idx, unit, col_count=2) -> List[float]:
        """
        Extract up to 2 values for a nutrient.

        Key insight: when OCR produces stacked output, the carbohydrate keyword
        may be on line N with no numbers, values on lines N+1 and N+2, and the
        "of which Total Sugar" sub-row on line N+3.  We must NOT stop scanning
        when we hit a sub-row BEFORE we have collected enough values — sub-rows
        only matter once we already have the parent's values.

        We stop when:
          - We've collected 2 values (done), OR
          - We hit a NEW PARENT nutrient row (not a sub-row), OR
          - We hit a sub-row AND we already have at least 1 value (parent done)
        """
        vals = []
        for j in range(idx, min(idx + 5, len(lines))):
            line = lines[j]
            lo   = line.lower()

            if j > idx:
                # Stop at a new parent nutrient — never at a sub-row before values
                if self._is_new_nutrient_row(lo) and not self._is_subrow(lo):
                    break
                # Stop at a sub-row only AFTER we have the parent values
                if self._is_subrow(lo) and len(vals) >= 1:
                    break

            # Strip energy-unit-tagged numbers to avoid carb row stealing kcal values
            clean_line = self._strip_energy_values(line)
            nums = self._extract_numbers(clean_line)
            for n in nums:
                if unit == "g"  and n > 9999:
                    continue
                if unit == "mg" and n > 99999:
                    continue
                vals.append(n)
                if len(vals) == 2:
                    return vals
        # If still no values found, check if the NEXT line is a sub-row that has values
        # (happens when OCR merges the nutrient name with an unrelated energy row)
        if not vals:
            for j in range(idx + 1, min(idx + 4, len(lines))):
                sub = lines[j]
                if self._is_new_nutrient_row(sub) and not self._is_subrow(sub):
                    break
                clean = self._strip_energy_values(sub)
                nums = self._extract_numbers(clean)
                for n in nums:
                    if unit == "g"  and n > 9999:
                        continue
                    if unit == "mg" and n > 99999:
                        continue
                    vals.append(n)
                    if len(vals) == 2:
                        return vals
                if vals:
                    break
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
                # Extract sugar from "of which Total Sugar" even as a sub-row
                if field_100 == FIELD_SUGAR_100 and FIELD_SUGAR_100 not in result:
                    vals = self._collect_stacked_values(lines, idx, unit)
                    if vals:
                        self._assign(vals, col_order, field_100, field_srv, result)
                        print(f"  ✓ sugar (from sub-row)  /100g={result.get(field_100)} /srv={result.get(field_srv,'—')}")
                continue
            used.add(idx)
            vals = self._collect_stacked_values(lines, idx, unit)
            if not vals:
                continue
            sodium_win = lines[max(0, idx - 3): idx + 4]
            sodium_conv = (field_100 == FIELD_SODIUM_100 and
                           self._sodium_is_in_grams(sodium_win, 0))
            self._assign(vals, col_order, field_100, field_srv, result,
                         sodium_conversion=sodium_conv)
            self._log_nutrient(keywords[0], field_100, field_srv, result)

    def _collect_stacked_values(self, lines, idx, unit) -> List[float]:
        """
        Collect up to 2 values from lines below (or above) the trigger.

        Same rule as inline: sub-rows only terminate collection AFTER we
        have at least one parent value.  A new PARENT nutrient always stops.
        """
        vals = []
        for j in range(idx + 1, min(idx + 7, len(lines))):
            line = lines[j]
            lo   = line.lower()
            # New parent nutrient → always stop
            if self._is_new_nutrient_row(lo) and not self._is_subrow(lo):
                break
            # Sub-row → stop only after we have the parent value(s)
            if self._is_subrow(lo) and len(vals) >= 1:
                break
            nums = self._extract_numbers(line)
            if not nums:
                continue
            n = nums[0]
            if unit == "g"  and n > 9999:
                continue
            if unit == "mg" and n > 99999:
                continue
            vals.append(n)
            if len(vals) == 2:
                break
        if vals:
            return vals

        # Backward scan (OCR sometimes puts values before keyword)
        above = []
        for j in range(idx - 1, max(idx - 6, -1), -1):
            line = lines[j]
            lo   = line.lower()
            if self._is_new_nutrient_row(lo) and not self._is_subrow(lo):
                break
            nums = self._extract_numbers(line)
            if not nums:
                continue
            n = nums[0]
            if unit == "g"  and n > 9999:
                continue
            if unit == "mg" and n > 99999:
                continue
            above.insert(0, n)
            if len(above) == 2:
                break
        return above

    # -----------------------------------------------------------------------
    # Sodium unit detection — check for explicit "g" unit on the label
    # -----------------------------------------------------------------------

    @staticmethod
    def _sodium_is_in_grams(lines, idx) -> bool:
        """
        Return True only when sodium values on this label are in grams
        (requiring ×1000 conversion to get mg).

        Rules:
        - If "mg" appears anywhere in the sodium row context → already in mg, no conversion
        - If the values on the row are >= 1.0 → almost certainly already in mg
        - Only convert when value is tiny (< 1.0) AND explicit "g" unit is present
          without "mg" nearby
        """
        if not lines:
            return False
        end = min(idx + 3, len(lines))
        start = max(0, idx)
        window = " ".join(lines[start:end]).lower()

        # If mg is explicitly present anywhere near the row → no conversion needed
        if "mg" in window:
            return False

        # Extract the first number from the window to check its magnitude
        nums = re.findall(r"\d+\.?\d*", window)
        if nums:
            first_val = float(nums[0])
            # Values >= 1 in the sodium row are almost certainly already mg
            if first_val >= 1.0:
                return False

        # Only convert if explicit "g" unit and value is tiny
        if re.search(r"\bg\b", window):
            return True

        return False

    # -----------------------------------------------------------------------
    # Salt (NaCl) → Sodium conversion
    # -----------------------------------------------------------------------

    def _fix_salt_as_sodium(self, result: Dict, lines: List[str]) -> Dict:
        """
        Some labels (e.g. dried fish) report "Salt Content (as NaCl) g"
        instead of sodium mg.  Sodium (mg) = NaCl (g) × 393.4
        (or approximately ÷ 2.54 for g→mg of Na).
        We detect this when the sodium value is impossibly large (>10,000 mg/100g
        for a solid food) — which signals it's actually NaCl in mg, not Na in mg.
        """
        sodium = result.get(FIELD_SODIUM_100)
        if sodium is None:
            return result
        # Check if any line mentions "NaCl" or "salt content"
        nacl_label = any(
            re.search(r"nacl|salt content", l.lower()) for l in lines
        )
        if nacl_label and sodium > 100:
            # Convert NaCl mg → Na mg  (Na is 39.3% of NaCl)
            result[FIELD_SODIUM_100] = round(sodium * 0.393, 2)
            print(f"  ⚠ NaCl→Na conversion: {sodium} → {result[FIELD_SODIUM_100]} mg")
            if FIELD_SODIUM_SRV in result:
                result[FIELD_SODIUM_SRV] = round(result[FIELD_SODIUM_SRV] * 0.393, 2)
        return result

    # -----------------------------------------------------------------------
    # Column swap sanity check
    # -----------------------------------------------------------------------

    def _verify_and_fix_column_order(self, result: Dict) -> Dict:
        """
        For products with serving_size < 100g/ml, per_100g values must be
        larger than per_serving values.  If inverted → swap all paired values.
        """
        serving = result.get(FIELD_SERVING_SIZE, 100.0)
        if serving >= 100.0:
            return result

        swap_votes = 0
        check_pairs = [
            (FIELD_PROTEIN_100,       FIELD_PROTEIN_SRV),
            (FIELD_CARBS_100,         FIELD_CARBS_SRV),
            (FIELD_ENERGY_KCAL_100,   FIELD_ENERGY_KCAL_SRV),
        ]
        for f100, fsrv in check_pairs:
            v100 = result.get(f100)
            vsrv = result.get(fsrv)
            if v100 is not None and vsrv is not None and vsrv > 0:
                if v100 < vsrv:
                    swap_votes += 1

        e100 = result.get(FIELD_ENERGY_KCAL_100)
        esrv = result.get(FIELD_ENERGY_KCAL_SRV)
        energy_swapped = (e100 is not None and esrv is not None and e100 < esrv)

        # Special case: only one kcal value was found and it's suspiciously small
        # for a per-100g value (< 100 kcal) but serving < 30g — likely the serving value
        if e100 is not None and esrv is None and serving < 30:
            if e100 < 100:
                print(f"  ⚠ Single kcal value {e100} looks like serving value — marking as swapped")
                energy_swapped = True
                # Set a dummy serving value so swap logic works
                result[FIELD_ENERGY_KCAL_SRV] = e100

        # Extra guard: energy alone is NOT enough to trigger swap if kJ values
        # also exist and agree with the kcal ordering (i.e. kJ are correct order).
        if energy_swapped:
            kj100 = result.get(FIELD_ENERGY_KJ_100)
            kjsrv = result.get(FIELD_ENERGY_KJ_SRV)
            if kj100 is not None and kjsrv is not None:
                if kj100 > kjsrv:
                    print(f"  ℹ kJ order correct ({kj100} > {kjsrv}), "
                          f"kcal inversion is OCR error — NOT swapping")
                    energy_swapped = False

        if not energy_swapped and swap_votes < 2:
            return result

        if energy_swapped:
            print(f"  ⚠ Energy swapped ({e100} < {esrv}) — swapping all paired values")

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

    # -----------------------------------------------------------------------
    # Post-parse sanity fixes
    # -----------------------------------------------------------------------

    def _post_parse_sanity_fix(self, result: Dict) -> Dict:
        """Fix physically impossible values (sat fat > total fat, etc.)"""
        fat   = result.get(FIELD_FAT_100)
        sat   = result.get(FIELD_SAT_FAT_100)
        trans = result.get(FIELD_TRANS_100)

        if fat is not None and sat is not None and sat > fat and fat > 0:
            print(f"  ⚠ Sat fat ({sat}) > total fat ({fat}) — setting sat fat to 0")
            result[FIELD_SAT_FAT_100] = 0.0
            if FIELD_SAT_FAT_SRV in result:
                result[FIELD_SAT_FAT_SRV] = 0.0

        if fat is not None and trans is not None and trans > fat and fat > 0:
            print(f"  ⚠ Trans fat ({trans}) > total fat ({fat}) — setting trans fat to 0")
            result[FIELD_TRANS_100] = 0.0
            if FIELD_TRANS_SRV in result:
                result[FIELD_TRANS_SRV] = 0.0

        # Sodium sanity: if value > 50,000 mg/100g it's almost certainly an OCR
        # error (e.g. grabbed a barcode number).  Cap at 10,000 mg.
        sodium = result.get(FIELD_SODIUM_100)
        if sodium is not None and sodium > 10000:
            print(f"  ⚠ Sodium ({sodium}) looks like OCR error — clamping to 0")
            result[FIELD_SODIUM_100] = 0.0
            if FIELD_SODIUM_SRV in result:
                result[FIELD_SODIUM_SRV] = 0.0

        return result

    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        required = [FIELD_ENERGY_KCAL_100, FIELD_PROTEIN_100]
        missing  = [f for f in required if f not in data]
        return (len(missing) == 0, missing)

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
    def _assign(vals, col_order, field_100, field_srv, result,
                sodium_conversion=False):
        def maybe_mg(v):
            # Convert g → mg for sodium if values appear to be in grams
            if sodium_conversion and v < 10:
                return round(v * 1000, 3)
            return v

        if not vals:
            return
        if len(vals) == 1 or col_order == "single":
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