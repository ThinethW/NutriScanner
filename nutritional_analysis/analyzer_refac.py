"""
NutriScanner - Sri Lankan Nutritional Analysis and Interpretation System
============================================================================

Component 3: Nutritional Analysis and Interpretation

This module provides comprehensive nutritional analysis for Sri Lankan meals by:
- Matching food items to a standardized composition database
- Assigning appropriate portion sizes based on dietary guidelines
- Computing meal-level nutritional totals
- Calculating health-oriented interpretive indexes
- Generating professional visualizations

Author: Student Project
Version: 2.0
License: Educational Use

All nutrient values are per 100g COOKED edible portion unless otherwise specified.
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


import matplotlib.pyplot as plt


# Suppress unnecessary warnings
warnings.filterwarnings('ignore', category=FutureWarning)
plt.style.use('seaborn-v0_8-darkgrid')


# ============================================================================
# ENUMERATIONS AND CONSTANTS
# ============================================================================

class HealthIndexType(Enum):
    """Health-oriented index categories for nutritional assessment."""
    CARBOHYDRATE_IMPACT = "Carbohydrate Impact Score"
    SODIUM_DENSITY = "Sodium Density Score"
    ENERGY_DENSITY = "Energy Density Score"
    NUTRIENT_DENSITY = "Nutrient Density Score"
    FAT_QUALITY = "Fat Quality Score"


class NutrientCategory(Enum):
    """Categorization of nutrients for analysis."""
    MACRONUTRIENT = "macronutrient"
    MICRONUTRIENT = "micronutrient"
    BENEFICIAL = "beneficial"
    LIMITED = "limited"


# Recommended Daily Values (based on FDA/WHO guidelines adapted for Sri Lankan context)
DAILY_VALUES: Dict[str, float] = {
    "Protein (g)": 50.0,
    "Total fiber (g)": 28.0,
    "Potassium": 4700.0,
    "Calcium": 1300.0,
    "Magnesium": 420.0,
    "Iron": 18.0,
    "Zinc": 11.0,
    "Vitamin A(µg)": 900.0,
    "Vitamin C": 90.0,
    "Vitamin D(µg)": 20.0,
    "Vitamin K(µg)": 120.0,
    "Folate(µg)": 400.0,
    "Selenium(µg)": 55.0,
    "Sodium": 2300.0,
    "SFA": 20.0,
}

# Nutrients that should be maximized for health
ENCOURAGED_NUTRIENTS = [
    "Protein (g)", "Total fiber (g)", "Potassium", "Calcium",
    "Magnesium", "Iron", "Zinc", "Vitamin A(µg)", "Vitamin C",
    "Vitamin D(µg)", "Folate(µg)", "Selenium(µg)"
]

# Nutrients that should be limited
LIMITED_NUTRIENTS = ["Sodium", "SFA"]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for robust string matching.

    Args:
        text: Input string to normalize

    Returns:
        Normalized lowercase string with standardized whitespace
    """
    text = str(text).lower().strip()
    text = re.sub(r"\s+", " ", text)  # Collapse multiple spaces
    text = re.sub(r"[^\w\s,()-]", "", text)  # Remove special chars except common punctuation
    return text


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Restrict a value to a specified range.

    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def linear_score(
    value: float,
    optimal_threshold: float,
    limit_threshold: float,
    higher_is_better: bool = False
) -> float:
    """
    Compute a linear health score (0-100) based on thresholds.

    Args:
        value: The measured value
        optimal_threshold: The threshold for optimal score (100)
        limit_threshold: The threshold for minimum score (0)
        higher_is_better: If True, higher values score better. If False, lower is better.

    Returns:
        Score between 0 and 100
    """
    if higher_is_better:
        if value >= optimal_threshold:
            return 100.0
        if value <= limit_threshold:
            return 0.0
        return 100.0 * (value - limit_threshold) / (optimal_threshold - limit_threshold)
    else:
        if value <= optimal_threshold:
            return 100.0
        if value >= limit_threshold:
            return 0.0
        return 100.0 * (limit_threshold - value) / (limit_threshold - optimal_threshold)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely perform division, returning default value if denominator is zero.

    Args:
        numerator: Dividend
        denominator: Divisor
        default: Value to return if denominator is zero

    Returns:
        Result of division or default value
    """
    return (numerator / denominator) if denominator > 0 else default


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PortionRule:
    """
    Defines standard serving sizes and typical meal portions.

    Attributes:
        standard_serving_g: Weight of one standard serving in grams
        typical_servings_per_meal: Number of servings typically consumed per meal
        typical_amount_per_meal_g: Total grams typically consumed per meal
    """
    standard_serving_g: float
    typical_servings_per_meal: float
    typical_amount_per_meal_g: float

    def __post_init__(self):
        """Validate portion rule values."""
        if self.standard_serving_g <= 0:
            raise ValueError("Standard serving must be positive")
        if self.typical_servings_per_meal <= 0:
            raise ValueError("Servings per meal must be positive")


@dataclass
class MealItem:
    """
    Represents a single food item within a meal.

    Attributes:
        input_name: Original food name as provided by user
        matched_food_item: Matched food name from database
        matched_category: Food category from database
        grams: Portion size in grams
        servings: Number of standard servings
        match_confidence: Confidence score of the match (0.0-1.0)
        nutrients: Dictionary of nutrient amounts for this item
    """
    input_name: str
    matched_food_item: str
    matched_category: str
    grams: float
    servings: float
    match_confidence: float
    nutrients: Dict[str, float] = field(default_factory=dict)

    @property
    def match_quality(self) -> str:
        """Return human-readable match quality."""
        if self.match_confidence >= 0.95:
            return "Exact"
        elif self.match_confidence >= 0.80:
            return "High"
        elif self.match_confidence >= 0.65:
            return "Moderate"
        else:
            return "Low"


@dataclass
class MealAnalysisResult:
    """
    Complete analysis results for a meal.

    Attributes:
        items: List of individual meal items
        totals: Total nutrient amounts across all items
        indexes: Computed health-oriented index scores
        indicators: Key nutritional indicators
        figures: Generated matplotlib figures
        metadata: Additional analysis metadata
    """
    items: List[MealItem]
    totals: Dict[str, float]
    indexes: Dict[str, float]
    indicators: Dict[str, float]
    figures: Dict[str, plt.Figure]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_items(self) -> int:
        """Return total number of items in meal."""
        return len(self.items)

    @property
    def average_match_confidence(self) -> float:
        """Return average match confidence across all items."""
        if not self.items:
            return 0.0
        return sum(item.match_confidence for item in self.items) / len(self.items)



def compute_health_indexes(
        totals: Dict[str, float]
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Compute health-oriented interpretive indexes from nutrient totals.

        This method does NOT classify foods as "healthy" or "unhealthy."
        Instead, it computes standardized indicators that help users and
        downstream models make informed decisions.

        Args:
            totals: Dictionary of total nutrient amounts

        Returns:
            Tuple of (index scores, key indicators)
        """
        # Extract key values
        energy_kcal = totals.get("Energy (kcal)", 0.0)
        meal_weight_g = totals.get("Total meal weight (g)", 0.0)
        carbs_g = totals.get("Carbohydrates digestible (g)", 0.0)
        fiber_g = totals.get("Total fiber (g)", 0.0)
        protein_g = totals.get("Protein (g)", 0.0)
        sodium_mg = totals.get("Sodium", 0.0)
        sfa_g = totals.get("SFA", 0.0)
        mufa_g = totals.get("MUFA", 0.0)
        pufa_g = totals.get("PUFA", 0.0)

        # ====================================================================
        # INDEX 1: Carbohydrate Impact Score (Proxy for Glycemic Load)
        # ====================================================================
        # Lower digestible carbs and higher fiber is better for blood sugar management
        net_carbs = max(0.0, carbs_g)
        base_carb_score = linear_score(
            net_carbs,
            optimal_threshold=45.0,  # ≤45g is excellent
            limit_threshold=90.0,     # ≥90g is concerning
            higher_is_better=False
        )

        # Bonus for fiber content (fiber slows glucose absorption)
        fiber_bonus = clamp((fiber_g - 5.0) * 2.0, 0.0, 10.0)
        carb_impact_score = clamp(base_carb_score + fiber_bonus, 0.0, 100.0)

        # ====================================================================
        # INDEX 2: Sodium Density Score (Hypertension Indicator)
        # ====================================================================
        # Evaluates sodium per 1000 kcal (accounts for meal size)
        sodium_per_1000kcal = safe_divide(sodium_mg, energy_kcal) * 1000.0
        sodium_density_score = linear_score(
            sodium_per_1000kcal,
            optimal_threshold=1000.0,  # ≤1000mg/1000kcal is excellent
            limit_threshold=2000.0,     # ≥2000mg/1000kcal is concerning
            higher_is_better=False
        )

        # ====================================================================
        # INDEX 3: Energy Density Score
        # ====================================================================
        # Lower energy density (kcal per 100g) is associated with better satiety
        energy_density = safe_divide(energy_kcal, meal_weight_g) * 100.0
        energy_density_score = linear_score(
            energy_density,
            optimal_threshold=120.0,   # ≤120 kcal/100g is excellent
            limit_threshold=250.0,      # ≥250 kcal/100g is concerning
            higher_is_better=False
        )

        # ====================================================================
        # INDEX 4: Nutrient Density Score
        # ====================================================================
        # Balance of beneficial nutrients vs. nutrients to limit
        def percent_dv(nutrient: str) -> float:
            """Calculate percentage of daily value."""
            value = totals.get(nutrient, 0.0)
            dv = DAILY_VALUES.get(nutrient, 0.0)
            return safe_divide(value, dv) * 100.0

        # Sum encouraged nutrients (capped at 100% each)
        encouraged_sum = sum(
            clamp(percent_dv(n), 0.0, 100.0)
            for n in ENCOURAGED_NUTRIENTS
            if n in totals
        )

        # Sum limited nutrients (capped at 100% each)
        limited_sum = sum(
            clamp(percent_dv(n), 0.0, 100.0)
            for n in LIMITED_NUTRIENTS
            if n in totals
        )

        # Normalize to 0-100 scale
        encouraged_normalized = safe_divide(encouraged_sum, len(ENCOURAGED_NUTRIENTS) * 100.0) * 100.0
        limited_normalized = safe_divide(limited_sum, len(LIMITED_NUTRIENTS) * 100.0) * 100.0

        # Score: reward beneficial nutrients, penalize limited nutrients
        nutrient_density_score = clamp(encouraged_normalized - 0.6 * limited_normalized, 0.0, 100.0)

        # ====================================================================
        # INDEX 5: Fat Quality Score
        # ====================================================================
        # Ratio of unsaturated to saturated fats
        unsaturated_fat = max(0.0, mufa_g + pufa_g)

        if sfa_g <= 0.1:  # Negligible saturated fat
            fat_quality_score = 90.0 if unsaturated_fat > 0.5 else 70.0
        else:
            unsat_to_sat_ratio = safe_divide(unsaturated_fat, sfa_g)
            fat_quality_score = linear_score(
                unsat_to_sat_ratio,
                optimal_threshold=2.0,  # Ratio ≥2.0 is excellent
                limit_threshold=0.8,    # Ratio ≤0.8 is concerning
                higher_is_better=True
            )

        # ====================================================================
        # Compile Results
        # ====================================================================
        indexes = {
            HealthIndexType.CARBOHYDRATE_IMPACT.value: round(carb_impact_score, 1),
            HealthIndexType.SODIUM_DENSITY.value: round(sodium_density_score, 1),
            HealthIndexType.ENERGY_DENSITY.value: round(energy_density_score, 1),
            HealthIndexType.NUTRIENT_DENSITY.value: round(nutrient_density_score, 1),
            HealthIndexType.FAT_QUALITY.value: round(fat_quality_score, 1),
        }

        indicators = {
            "Meal energy (kcal)": round(energy_kcal, 1),
            "Meal weight (g)": round(meal_weight_g, 1),
            "Energy density (kcal/100g)": round(energy_density, 1),
            "Digestible carbs (g)": round(net_carbs, 1),
            "Fiber (g)": round(fiber_g, 1),
            "Protein (g)": round(protein_g, 1),
            "Total fat (g)": round(totals.get("Fat (g)", 0.0), 1),
            "Saturated fat (g)": round(sfa_g, 1),
            "Unsaturated fat (g)": round(unsaturated_fat, 1),
            "Sodium (mg)": round(sodium_mg, 1),
            "Sodium density (mg/1000kcal)": round(sodium_per_1000kcal, 1),
            "Unsat:Sat ratio": round(safe_divide(unsaturated_fat, sfa_g), 2),
        }

        return indexes, indicators
