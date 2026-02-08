"""
Sri Lankan Meal Interpreter (Component 3)
- Assigns typical grams/servings from FBDG-style defaults
- Computes nutrients using per-100g composition table (CSV)
- Produces health-oriented indexes + matplotlib visuals

All nutrient values assumed per 100g COOKED edible portion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path  # ✅ FIX: for robust file paths
import re
import difflib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# -----------------------------
# Utilities
# -----------------------------

def _norm(s: str) -> str:
    s = str(s).lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s,()-]", "", s)
    return s

def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def _score_linear(value: float, good_max: float, bad_min: float, invert: bool = True) -> float:
    """
    Linear score 0..100.
    If invert=True: lower is better (value <= good_max => 100, value >= bad_min => 0)
    If invert=False: higher is better (value >= good_max => 100, value <= bad_min => 0)
    """
    if invert:
        if value <= good_max:
            return 100.0
        if value >= bad_min:
            return 0.0
        return 100.0 * (bad_min - value) / (bad_min - good_max)
    else:
        if value >= good_max:
            return 100.0
        if value <= bad_min:
            return 0.0
        return 100.0 * (value - bad_min) / (good_max - bad_min)


# -----------------------------
# Data structures
# -----------------------------

@dataclass
class PortionRule:
    standard_serving_g: float
    typical_servings_per_meal: float
    typical_amount_per_meal_g: float

@dataclass
class MealItem:
    input_name: str
    matched_food_item: str
    matched_category: str
    grams: float
    servings: float
    match_confidence: float
    nutrients: Dict[str, float]

@dataclass
class MealResult:
    items: List[MealItem]
    totals: Dict[str, float]
    indexes: Dict[str, float]
    indicators: Dict[str, float]
    figures: Dict[str, plt.Figure]


# -----------------------------
# Main engine
# -----------------------------

class SriLankanMealInterpreter:
    def __init__(
        self,
        nutrition_csv_path: str | Path,  # ✅ FIX: allow Path too
        portion_rules: Optional[Dict[str, PortionRule]] = None,
        category_defaults: Optional[Dict[str, PortionRule]] = None,
    ):
        # ✅ FIX: convert to Path + check exists (gives clearer errors)
        nutrition_csv_path = Path(nutrition_csv_path)
        if not nutrition_csv_path.exists():
            raise FileNotFoundError(f"CSV not found at: {nutrition_csv_path}")

        self.df = pd.read_csv(nutrition_csv_path).copy()

        # ✅ FIX: remove leading/trailing spaces in column names
        self.df.columns = self.df.columns.str.strip()

        # Now these columns will be found reliably
        self.df["__food_norm"] = self.df["Food item"].astype(str).map(_norm)
        self.df["__cat_norm"] = self.df["Food Category"].astype(str).map(_norm)

        self.portion_rules = portion_rules or self._default_portion_rules()
        self.category_defaults = category_defaults or self._default_category_defaults()

        self.nutrient_cols = [
            "Energy (kcal)",
            "Carbohydrates digestible (g)",
            "Protein (g)",
            "Fat (g)",
            "SFA", "MUFA", "PUFA",
            "Total fiber (g)",
            "Sodium",
            "Potassium",
            "Calcium",
            "Magnesium",
            "Iron",
            "Zinc",
            "Vitamin A(µg)",
            "Vitamin C",
            "Vitamin D(µg)",
            "Vitamin K(µg)",
            "Folate(µg)",
            "Selenium(µg)",
        ]
        self.nutrient_cols = [c for c in self.nutrient_cols if c in self.df.columns]

        self.dv = {
            "Protein (g)": 50.0,
            "Total fiber (g)": 28.0,
            "Potassium": 4700.0,
            "Calcium": 1300.0,
            "Magnesium": 420.0,
            "Iron": 18.0,
            "Vitamin A(µg)": 900.0,
            "Vitamin C": 90.0,
            "Vitamin D(µg)": 20.0,
            "Folate(µg)": 400.0,
            "Sodium": 2300.0,
            "SFA": 20.0,
        }

    def _default_category_defaults(self) -> Dict[str, PortionRule]:
        return {
            "rice": PortionRule(65, 2.5, 163),
            "cereal product": PortionRule(40, 1.0, 40),
            "starchy food": PortionRule(100, 0.5, 50),
            "vegetable curry": PortionRule(45, 1.0, 45),
            "boiled vegetable": PortionRule(75, 0.5, 38),
            "pulse curry": PortionRule(45, 1.0, 45),
            "fish/meat curry": PortionRule(30, 1.0, 30),
            "fish/meat (fried)": PortionRule(30, 1.0, 30),
            "sambol": PortionRule(30, 0.5, 15),
            "salad": PortionRule(75, 1.0, 75),
            "soup": PortionRule(200, 1.0, 200),
            "porridge": PortionRule(200, 1.0, 200),
            "snack": PortionRule(50, 1.0, 50),
            "gravy/sauce": PortionRule(30, 0.5, 15),
        }

    def _default_portion_rules(self) -> Dict[str, PortionRule]:
        return {
            _norm("Boiled Rice (all varieties)"): PortionRule(65, 2.5, 163),
            _norm("Dhal curry, thick"): PortionRule(45, 1.0, 45),
            _norm("Dhal curry, watery"): PortionRule(45, 1.0, 45),
            _norm("Chicken curry"): PortionRule(30, 1.0, 30),
            _norm("Brinjal curry"): PortionRule(45, 1.0, 45),
            _norm("Gotukola sambol"): PortionRule(30, 0.5, 15),
            _norm("Coconut sambol"): PortionRule(30, 0.5, 15),
        }

    def match_food(self, query: str) -> Tuple[pd.Series, float]:
        qn = _norm(query)
        candidates = self.df["__food_norm"].tolist()

        if qn in candidates:
            idx = candidates.index(qn)
            return self.df.iloc[idx], 1.0

        best = difflib.get_close_matches(qn, candidates, n=1, cutoff=0.60)
        if not best:
            contains = self.df[self.df["__food_norm"].str.contains(re.escape(qn), na=False)]
            if len(contains) > 0:
                return contains.iloc[0], 0.65
            raise ValueError(f"Food not found in nutrition DB: '{query}'")

        match_norm = best[0]
        ratio = difflib.SequenceMatcher(None, qn, match_norm).ratio()
        row = self.df[self.df["__food_norm"] == match_norm].iloc[0]
        return row, float(ratio)

    def portion_for(self, matched_row: pd.Series) -> PortionRule:
        food_norm = _norm(matched_row["Food item"])
        cat_norm = _norm(matched_row["Food Category"])

        if food_norm in self.portion_rules:
            return self.portion_rules[food_norm]

        if "boiled rice" in food_norm:
            return self.category_defaults["rice"]

        if cat_norm in self.category_defaults:
            return self.category_defaults[cat_norm]

        return PortionRule(50, 1.0, 50)

    def nutrients_for_grams(self, matched_row: pd.Series, grams: float) -> Dict[str, float]:
        factor = grams / 100.0
        out: Dict[str, float] = {}
        for col in self.nutrient_cols:
            v = matched_row.get(col, np.nan)
            if pd.isna(v):
                continue
            out[col] = float(v) * factor
        return out

    def sum_nutrients(self, items: List[MealItem]) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        for it in items:
            for k, v in it.nutrients.items():
                totals[k] = totals.get(k, 0.0) + float(v)
        totals["Total meal weight (g)"] = sum(i.grams for i in items)
        return totals

    def compute_indexes(self, totals: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        kcal = totals.get("Energy (kcal)", 0.0)
        grams = totals.get("Total meal weight (g)", 0.0)

        carbs = totals.get("Carbohydrates digestible (g)", 0.0)
        fiber = totals.get("Total fiber (g)", 0.0)
        net_carbs = max(0.0, carbs)
        sodium_mg = totals.get("Sodium", 0.0)
        sfa_g = totals.get("SFA", 0.0)
        mufa_g = totals.get("MUFA", 0.0)
        pufa_g = totals.get("PUFA", 0.0)
        protein = totals.get("Protein (g)", 0.0)

        base_carb_score = _score_linear(net_carbs, good_max=45.0, bad_min=90.0, invert=True)
        fiber_bonus = _clamp((fiber - 5.0) * 2.0, 0.0, 10.0)
        carb_impact_score = _clamp(base_carb_score + fiber_bonus, 0.0, 100.0)

        sodium_per_1000kcal = (sodium_mg / kcal * 1000.0) if kcal > 0 else 0.0
        sodium_density_score = _score_linear(sodium_per_1000kcal, good_max=1000.0, bad_min=2000.0, invert=True)

        energy_density = (kcal / grams * 100.0) if grams > 0 else 0.0
        energy_density_score = _score_linear(energy_density, good_max=120.0, bad_min=250.0, invert=True)

        encouraged = [
            "Protein (g)", "Total fiber (g)", "Potassium", "Calcium", "Magnesium", "Iron",
            "Vitamin A(µg)", "Vitamin C", "Folate(µg)"
        ]
        limited = ["Sodium", "SFA"]

        def pct_dv(nutr: str) -> float:
            v = totals.get(nutr, 0.0)
            dv = self.dv.get(nutr)
            if not dv or dv <= 0:
                return 0.0
            return 100.0 * (v / dv)

        pos = sum(_clamp(pct_dv(n), 0.0, 100.0) for n in encouraged if n in totals)
        neg = sum(_clamp(pct_dv(n), 0.0, 100.0) for n in limited if n in totals)

        pos_norm = (pos / (len(encouraged) * 100.0)) * 100.0
        neg_norm = (neg / (len(limited) * 100.0)) * 100.0
        nutrient_density_score = _clamp(pos_norm - 0.6 * neg_norm, 0.0, 100.0)

        unsat = max(0.0, mufa_g + pufa_g)
        if sfa_g <= 0.1:
            fat_quality_score = 90.0 if unsat > 0.5 else 70.0
        else:
            ratio = unsat / sfa_g
            fat_quality_score = _score_linear(ratio, good_max=2.0, bad_min=0.8, invert=False)

        indexes = {
            "Carbohydrate Impact Score": float(carb_impact_score),
            "Sodium Density Score": float(sodium_density_score),
            "Energy Density Score": float(energy_density_score),
            "Nutrient Density Score": float(nutrient_density_score),
            "Fat Quality Score": float(fat_quality_score),
        }

        indicators = {
            "Meal energy (kcal)": float(kcal),
            "Meal weight (g)": float(grams),
            "Digestible carbs (g)": float(net_carbs),
            "Fiber (g)": float(fiber),
            "Protein (g)": float(protein),
            "Sodium (mg)": float(sodium_mg),
            "Sodium per 1000 kcal (mg/1000kcal)": float(sodium_per_1000kcal),
            "Saturated fat (g)": float(sfa_g),
        }

        return indexes, indicators

    def make_figures(self, totals: Dict[str, float], indexes: Dict[str, float]) -> Dict[str, plt.Figure]:
        figs: Dict[str, plt.Figure] = {}

        carbs = totals.get("Carbohydrates digestible (g)", 0.0)
        protein = totals.get("Protein (g)", 0.0)
        fat = totals.get("Fat (g)", 0.0)
        cal_c = max(0.0, carbs) * 4.0
        cal_p = max(0.0, protein) * 4.0
        cal_f = max(0.0, fat) * 9.0
        total = cal_c + cal_p + cal_f

        fig1 = plt.figure()
        if total > 0:
            plt.pie([cal_c, cal_p, cal_f], labels=["Carbs", "Protein", "Fat"], autopct="%1.0f%%")
            plt.title("Macro calorie distribution")
        else:
            plt.text(0.5, 0.5, "Not enough macro data", ha="center")
        figs["macro_pie"] = fig1

        fig2 = plt.figure()
        vals = [
            totals.get("Carbohydrates digestible (g)", 0.0),
            totals.get("Total fiber (g)", 0.0),
            totals.get("Sodium", 0.0),
            totals.get("SFA", 0.0),
        ]
        labels = ["Digestible carbs (g)", "Fiber (g)", "Sodium (mg)", "SFA (g)"]
        plt.bar(labels, vals)
        plt.title("Key meal indicators")
        plt.xticks(rotation=20, ha="right")
        figs["key_indicators_bar"] = fig2

        fig3 = plt.figure()
        keys = list(indexes.keys())
        vals = [indexes[k] for k in keys]
        angles = np.linspace(0, 2*np.pi, len(keys), endpoint=False).tolist()
        vals += vals[:1]
        angles += angles[:1]

        ax = plt.subplot(111, polar=True)
        ax.plot(angles, vals)
        ax.fill(angles, vals, alpha=0.15)
        ax.set_thetagrids(np.degrees(angles[:-1]), keys)
        ax.set_ylim(0, 100)
        plt.title("Health-oriented indexes (0–100)")
        figs["indexes_radar"] = fig3

        return figs

    def interpret_meal(self, foods: List[str]) -> MealResult:
        items: List[MealItem] = []

        for f in foods:
            row, conf = self.match_food(f)
            rule = self.portion_for(row)

            grams = float(rule.typical_amount_per_meal_g)
            servings = float(rule.typical_servings_per_meal)

            nutrients = self.nutrients_for_grams(row, grams)

            items.append(
                MealItem(
                    input_name=f,
                    matched_food_item=str(row["Food item"]),
                    matched_category=str(row["Food Category"]),
                    grams=grams,
                    servings=servings,
                    match_confidence=float(conf),
                    nutrients=nutrients,
                )
            )

        totals = self.sum_nutrients(items)
        indexes, indicators = self.compute_indexes(totals)
        figs = self.make_figures(totals, indexes)

        return MealResult(items=items, totals=totals, indexes=indexes, indicators=indicators, figures=figs)

    def to_jsonable(self, result: MealResult) -> Dict[str, Any]:
        return {
            "items": [
                {
                    "input_name": it.input_name,
                    "matched_food_item": it.matched_food_item,
                    "matched_category": it.matched_category,
                    "grams": it.grams,
                    "servings": it.servings,
                    "match_confidence": it.match_confidence,
                    "nutrients": it.nutrients,
                }
                for it in result.items
            ],
            "totals": result.totals,
            "indexes": result.indexes,
            "indicators": result.indicators,
        }


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # ✅ FIX: robust path relative to this file (nutritional-analysis/)
    BASE_DIR = Path(__file__).resolve().parent
    DATA_PATH = BASE_DIR / "data" / "traditional food list.csv"

    interpreter = SriLankanMealInterpreter(DATA_PATH)

    meal = ["Boiled Rice, Keeri Samba", "Dhal curry, thick", "Chicken curry", "Brinjal curry"]
    res = interpreter.interpret_meal(meal)

    payload = interpreter.to_jsonable(res)
    print(payload)

    for _, fig in res.figures.items():
        fig.show()
