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
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import difflib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

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


# ============================================================================
# MAIN ANALYZER CLASS
# ============================================================================

class SriLankanNutritionalAnalyzer:
    """
    Comprehensive nutritional analyzer for Sri Lankan meals.

    This class provides:
    - Food item matching against composition database
    - Portion size assignment based on dietary guidelines
    - Nutrient calculation and aggregation
    - Health-oriented index computation
    - Professional visualization generation
    """

    def __init__(
        self,
        nutrition_database_path: str | Path,
        portion_rules: Optional[Dict[str, PortionRule]] = None,
        category_defaults: Optional[Dict[str, PortionRule]] = None,
        verbose: bool = False
    ):
        """
        Initialize the nutritional analyzer.

        Args:
            nutrition_database_path: Path to CSV file containing food composition data
            portion_rules: Custom portion rules for specific foods
            category_defaults: Default portion rules by food category
            verbose: Enable verbose logging

        Raises:
            FileNotFoundError: If database file doesn't exist
            ValueError: If database format is invalid
        """
        self.verbose = verbose
        self._log("Initializing Sri Lankan Nutritional Analyzer...")

        # Load and validate database
        self.database_path = Path(nutrition_database_path)
        if not self.database_path.exists():
            raise FileNotFoundError(f"Nutrition database not found: {self.database_path}")

        self._load_database()

        # Initialize portion rules
        self.portion_rules = portion_rules or self._get_default_portion_rules()
        self.category_defaults = category_defaults or self._get_default_category_rules()

        # Extract available nutrient columns
        self._identify_nutrient_columns()

        self._log(f"✓ Loaded {len(self.df)} food items from database")
        self._log(f"✓ Tracking {len(self.nutrient_columns)} nutrient parameters")

    def _log(self, message: str) -> None:
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[NutriScanner] {message}")

    def _load_database(self) -> None:
        """Load and preprocess the nutrition database."""
        try:
            self.df = pd.read_csv(self.database_path, encoding='utf-8-sig')

            # Clean column names
            self.df.columns = self.df.columns.str.strip()

            # Validate required columns
            required_cols = ["Food item", "Food Category"]
            missing_cols = [col for col in required_cols if col not in self.df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            # Create normalized search columns
            self.df["__food_normalized"] = self.df["Food item"].astype(str).map(normalize_text)
            self.df["__category_normalized"] = self.df["Food Category"].astype(str).map(normalize_text)

            # Remove any duplicate entries
            initial_count = len(self.df)
            self.df = self.df.drop_duplicates(subset=["__food_normalized"], keep="first")
            if len(self.df) < initial_count:
                self._log(f"⚠ Removed {initial_count - len(self.df)} duplicate entries")

        except Exception as e:
            raise ValueError(f"Failed to load nutrition database: {str(e)}")

    def _identify_nutrient_columns(self) -> None:
        """Identify available nutrient columns in the database."""
        # Standard nutrient columns to look for
        standard_nutrients = [
            "Energy (kcal)", "Energy (kJ)", "Water (g)",
            "Carbohydrates digestible (g)", "Protein (g)", "Fat (g)",
            "SFA", "MUFA", "PUFA", "Total fiber (g)",
            "Sodium", "Potassium", "Calcium", "Magnesium", "Phosphrous",
            "Iron", "Zinc", "Selenium(µg)", "Copper", "Manganese",
            "Vitamin A(µg)", "Vitamin B1", "Vitamin B2", "Vitamin B3",
            "Vitamin B6", "Vitamin B12", "Folate(µg)", "Vitamin C",
            "Vitamin D(µg)", "Vitamin E", "Vitamin K(µg)",
        ]

        self.nutrient_columns = [col for col in standard_nutrients if col in self.df.columns]

    def _get_default_portion_rules(self) -> Dict[str, PortionRule]:
        """
        Get default portion rules for specific food items.

        Returns:
            Dictionary mapping normalized food names to portion rules
        """
        return {
            normalize_text("Boiled Rice (all varieties)"): PortionRule(65, 2.5, 163),
            normalize_text("Boiled Rice, Keeri Samba"): PortionRule(65, 2.5, 163),
            normalize_text("boiled Rice, Kekulu, Red"): PortionRule(65, 2.5, 163),
            normalize_text("boiled Rice, Kekulu, White"): PortionRule(65, 2.5, 163),
            normalize_text("Boiled Rice, Nadu, White"): PortionRule(65, 2.5, 163),
            normalize_text("Dhal curry, thick"): PortionRule(45, 1.0, 45),
            normalize_text("Dhal curry, watery"): PortionRule(45, 1.0, 45),
            normalize_text("Chicken curry"): PortionRule(30, 1.0, 30),
            normalize_text("Fish curry"): PortionRule(30, 1.0, 30),
            normalize_text("Brinjal curry"): PortionRule(45, 1.0, 45),
            normalize_text("Gotukola sambol"): PortionRule(30, 0.5, 15),
            normalize_text("Coconut sambol"): PortionRule(30, 0.5, 15),
            normalize_text("Pol sambol"): PortionRule(30, 0.5, 15),
        }

    def _get_default_category_rules(self) -> Dict[str, PortionRule]:
        """
        Get default portion rules by food category.

        Returns:
            Dictionary mapping normalized category names to portion rules
        """
        return {
            normalize_text("rice"): PortionRule(65, 2.5, 163),
            normalize_text("cereal product"): PortionRule(40, 1.0, 40),
            normalize_text("starchy food"): PortionRule(100, 0.5, 50),
            normalize_text("vegetable curry"): PortionRule(45, 1.0, 45),
            normalize_text("boiled vegetable"): PortionRule(75, 0.5, 38),
            normalize_text("pulse curry"): PortionRule(45, 1.0, 45),
            normalize_text("fish/meat curry"): PortionRule(30, 1.0, 30),
            normalize_text("fish/meat (fried)"): PortionRule(30, 1.0, 30),
            normalize_text("sambol"): PortionRule(30, 0.5, 15),
            normalize_text("salad"): PortionRule(75, 1.0, 75),
            normalize_text("soup"): PortionRule(200, 1.0, 200),
            normalize_text("porridge"): PortionRule(200, 1.0, 200),
            normalize_text("snack"): PortionRule(50, 1.0, 50),
            normalize_text("gravy/sauce"): PortionRule(30, 0.5, 15),
        }

    def match_food_item(self, query: str) -> Tuple[pd.Series, float]:
        """
        Match a food query to the best entry in the database.

        Args:
            query: Food name to search for

        Returns:
            Tuple of (matched database row, confidence score)

        Raises:
            ValueError: If no reasonable match is found
        """
        query_normalized = normalize_text(query)
        candidates = self.df["__food_normalized"].tolist()

        # Check for exact match first
        if query_normalized in candidates:
            idx = candidates.index(query_normalized)
            self._log(f"  ✓ Exact match: '{query}' → '{self.df.iloc[idx]['Food item']}'")
            return self.df.iloc[idx], 1.0

        # Try fuzzy matching
        close_matches = difflib.get_close_matches(
            query_normalized,
            candidates,
            n=1,
            cutoff=0.60
        )

        if close_matches:
            match_normalized = close_matches[0]
            confidence = difflib.SequenceMatcher(None, query_normalized, match_normalized).ratio()
            row = self.df[self.df["__food_normalized"] == match_normalized].iloc[0]
            self._log(f"  ≈ Fuzzy match: '{query}' → '{row['Food item']}' (confidence: {confidence:.2f})")
            return row, float(confidence)

        # Try substring matching as last resort
        substring_matches = self.df[
            self.df["__food_normalized"].str.contains(re.escape(query_normalized), na=False)
        ]

        if len(substring_matches) > 0:
            row = substring_matches.iloc[0]
            self._log(f"  ⚠ Substring match: '{query}' → '{row['Food item']}' (confidence: 0.65)")
            return row, 0.65

        # No match found
        raise ValueError(
            f"Could not find a match for '{query}' in nutrition database. "
            f"Please check spelling or use a more generic term."
        )

    def get_portion_rule(self, matched_row: pd.Series) -> PortionRule:
        """
        Determine the appropriate portion rule for a matched food item.

        Args:
            matched_row: Database row for the matched food

        Returns:
            Applicable portion rule
        """
        food_normalized = normalize_text(matched_row["Food item"])
        category_normalized = normalize_text(matched_row["Food Category"])

        # Check item-specific rules first
        if food_normalized in self.portion_rules:
            return self.portion_rules[food_normalized]

        # Special handling for rice variations
        if "boiled rice" in food_normalized or "rice" in food_normalized:
            return self.category_defaults.get(normalize_text("rice"), PortionRule(50, 1.0, 50))

        # Check category-level rules
        if category_normalized in self.category_defaults:
            return self.category_defaults[category_normalized]

        # Default fallback
        self._log(f"  ⚠ Using default portion for: {matched_row['Food item']}")
        return PortionRule(50, 1.0, 50)

    def calculate_nutrients_for_portion(
        self,
        matched_row: pd.Series,
        portion_grams: float
    ) -> Dict[str, float]:
        """
        Calculate nutrient amounts for a specific portion size.

        Args:
            matched_row: Database row with per-100g nutrient values
            portion_grams: Portion size in grams

        Returns:
            Dictionary of nutrient amounts for the portion
        """
        scaling_factor = portion_grams / 100.0
        nutrients = {}

        for nutrient_col in self.nutrient_columns:
            value = matched_row.get(nutrient_col, np.nan)

            # Skip if value is missing
            if pd.isna(value):
                continue

            # Convert to float and validate
            try:
                numeric_value = float(value)
                if numeric_value >= 0:  # Only include non-negative values
                    nutrients[nutrient_col] = numeric_value * scaling_factor
            except (ValueError, TypeError):
                # Skip non-numeric values
                continue

        return nutrients

    def aggregate_meal_nutrients(self, items: List[MealItem]) -> Dict[str, float]:
        """
        Sum nutrients across all meal items.

        Args:
            items: List of meal items

        Returns:
            Dictionary of total nutrient amounts
        """
        totals: Dict[str, float] = {}

        for item in items:
            for nutrient, amount in item.nutrients.items():
                totals[nutrient] = totals.get(nutrient, 0.0) + float(amount)

        # Add meta-information
        totals["Total meal weight (g)"] = sum(item.grams for item in items)
        totals["Number of items"] = float(len(items))

        return totals

    def compute_health_indexes(
        self,
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

    def generate_visualizations(self, totals, indexes, items):
        """Generate both standard and comparison visualizations"""
        from .visualizations import generate_beautiful_visualizations
        from .comparison_charts import generate_comparison_visualizations

        # Get standard visualizations
        figures = generate_beautiful_visualizations(totals, indexes, items)

        # Add comparison visualizations
        comparison_figs = generate_comparison_visualizations(totals)
        figures.update(comparison_figs)

        return figures


    def analyze_meal(self, food_items: List[str]) -> MealAnalysisResult:
        """
        Perform comprehensive nutritional analysis on a meal.

        Args:
            food_items: List of food item names

        Returns:
            Complete meal analysis results

        Raises:
            ValueError: If no valid food items are provided
        """
        if not food_items:
            raise ValueError("No food items provided for analysis")

        self._log(f"\n{'='*60}")
        self._log(f"Analyzing meal with {len(food_items)} items...")
        self._log(f"{'='*60}\n")

        meal_items: List[MealItem] = []

        for i, food_name in enumerate(food_items, 1):
            self._log(f"[{i}/{len(food_items)}] Processing: '{food_name}'")

            try:
                # Match food item
                matched_row, confidence = self.match_food_item(food_name)

                # Get portion rule
                portion_rule = self.get_portion_rule(matched_row)

                # Calculate nutrients
                nutrients = self.calculate_nutrients_for_portion(
                    matched_row,
                    portion_rule.typical_amount_per_meal_g
                )

                # Create meal item
                item = MealItem(
                    input_name=food_name,
                    matched_food_item=str(matched_row["Food item"]),
                    matched_category=str(matched_row["Food Category"]),
                    grams=portion_rule.typical_amount_per_meal_g,
                    servings=portion_rule.typical_servings_per_meal,
                    match_confidence=confidence,
                    nutrients=nutrients
                )

                meal_items.append(item)
                self._log(f"  → Portion: {item.grams}g ({item.servings} servings)")
                self._log(f"  → Energy: {nutrients.get('Energy (kcal)', 0):.1f} kcal\n")

            except Exception as e:
                self._log(f"  ✗ Error: {str(e)}\n")
                raise

        # Aggregate nutrients
        self._log("Aggregating nutritional totals...")
        totals = self.aggregate_meal_nutrients(meal_items)

        # Compute health indexes
        self._log("Computing health-oriented indexes...")
        indexes, indicators = self.compute_health_indexes(totals)

        # Generate visualizations
        self._log("Generating visualizations...")
        figures = self.generate_visualizations(totals, indexes, meal_items)

        # Compile metadata
        metadata = {
            'analysis_version': '2.0',
            'database_path': str(self.database_path),
            'total_items_analyzed': len(meal_items),
            'average_match_confidence': sum(item.match_confidence for item in meal_items) / len(meal_items),
        }

        self._log(f"\n{'='*60}")
        self._log("✓ Analysis complete!")
        self._log(f"{'='*60}\n")

        return MealAnalysisResult(
            items=meal_items,
            totals=totals,
            indexes=indexes,
            indicators=indicators,
            figures=figures,
            metadata=metadata
        )

    def export_to_json(self, result: MealAnalysisResult) -> Dict[str, Any]:
        """
        Export analysis results to JSON-serializable format.

        Args:
            result: Meal analysis result

        Returns:
            JSON-serializable dictionary
        """
        return {
            "metadata": result.metadata,
            "items": [
                {
                    "input_name": item.input_name,
                    "matched_food_item": item.matched_food_item,
                    "matched_category": item.matched_category,
                    "portion_grams": item.grams,
                    "servings": item.servings,
                    "match_confidence": item.match_confidence,
                    "match_quality": item.match_quality,
                    "nutrients": item.nutrients,
                }
                for item in result.items
            ],
            "totals": result.totals,
            "health_indexes": result.indexes,
            "key_indicators": result.indicators,
        }

    def generate_text_report(self, result: MealAnalysisResult) -> str:
        """Generate a formatted text report of the analysis"""
        lines = []
        lines.append("=" * 80)
        lines.append("NUTRISCANNER - NUTRITIONAL ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Check if it's packaged food
        is_packaged = result.metadata.get('source') == 'nutrition_label'

        # Meal composition
        lines.append("FOOD COMPOSITION:")
        lines.append("-" * 80)
        for i, item in enumerate(result.items, 1):
            lines.append(f"{i}. {item.input_name}")
            lines.append(f"   → Matched: {item.matched_food_item} ({item.match_quality} confidence)")
            lines.append(f"   → Category: {item.matched_category}")

            if is_packaged:
                # Get values from scan data (not from nutrients)
                serving_size = result.totals.get('serving_size', item.grams)
                serving_unit = result.totals.get('serving_unit', 'g')

                # Get per-serving values from totals
                energy_per_serving = result.totals.get('energy_kcal_per_serving', 0)
                protein_per_serving = result.totals.get('protein_per_serving_g', 0)
                carbs_per_serving = result.totals.get('carbs_per_serving_g', 0)
                fat_per_serving = result.totals.get('fat_per_serving_g', 0)
                sodium_per_serving = result.totals.get('sodium_per_serving_mg', 0)

                lines.append(f"   → Serving Size: {serving_size}{serving_unit}")
                lines.append(f"   → Per Serving:")
                lines.append(f"      • Energy: {energy_per_serving:.1f} kcal")
                lines.append(f"      • Protein: {protein_per_serving:.1f}g")
                lines.append(f"      • Carbs: {carbs_per_serving:.1f}g")
                lines.append(f"      • Fat: {fat_per_serving:.1f}g")
                lines.append(f"      • Sodium: {sodium_per_serving:.1f}mg")
            else:
                lines.append(f"   → Portion: {item.grams}g ({item.servings} servings)")
                lines.append(f"   → Energy: {item.nutrients.get('Energy (kcal)', 0):.1f} kcal")

            lines.append("")

        # Nutritional totals (per 100g for comparison)
        lines.append("NUTRITIONAL TOTALS (Per 100g for standardized comparison):")
        lines.append("-" * 80)
        lines.append(f"Total Energy: {result.totals.get('Energy (kcal)', 0):.1f} kcal")
        lines.append(f"Carbohydrates: {result.totals.get('Carbohydrates digestible (g)', 0):.1f}g")
        lines.append(f"Protein: {result.totals.get('Protein (g)', 0):.1f}g")
        lines.append(f"Fat: {result.totals.get('Fat (g)', 0):.1f}g")
        lines.append(f"Fiber: {result.totals.get('Total fiber (g)', 0):.1f}g")
        lines.append(f"Sodium: {result.totals.get('Sodium', 0):.1f}mg")
        lines.append("")

        # Health indexes
        lines.append("HEALTH-ORIENTED INDEX SCORES (0-100):")
        lines.append("-" * 80)
        for index_name, score in result.indexes.items():
            if score >= 75:
                rating = "Excellent"
            elif score >= 50:
                rating = "Good"
            else:
                rating = "Needs Attention"
            lines.append(f"{index_name}: {score:.1f}/100 ({rating})")
        lines.append("")

        lines.append("=" * 80)
        lines.append("Note: Scores are interpretive indicators, not medical diagnoses.")
        lines.append("Consult a healthcare professional for personalized dietary advice.")
        lines.append("=" * 80)

        return "\n".join(lines)

    def analyze_packaged_food(self, nutrition_data: Dict[str, float]) -> MealAnalysisResult:
        """
        Analyze packaged food from extracted label data

        Args:
            nutrition_data: Dictionary from label scanner
                {
                    "energy_kcal_per_100g": 461,
                    "protein_g": 7.24,
                    "carbohydrates_g": 74.29,
                    "fiber_g": 1.69,
                    "total_fat_g": 15.01,
                    "saturated_fat_g": 6.16,
                    "sodium_mg": 458,
                    ...
                }

        Returns:
            Complete analysis with insights and visualizations
        """
        self._log("\n" + "=" * 60)
        self._log("Analyzing packaged food from nutrition label...")
        self._log("=" * 60 + "\n")

        # Convert label data to analyzer format
        totals = self._convert_label_to_totals(nutrition_data)

        # Compute health indexes (same as meals)
        self._log("Computing health-oriented indexes...")
        indexes, indicators = self.compute_health_indexes(totals)

        # Generate visualizations (same as meals)
        self._log("Generating visualizations...")
        figures = self.generate_visualizations(totals, indexes, [])

        # Create a pseudo meal item for the package
        package_item = MealItem(
            input_name="Packaged Food",
            matched_food_item="Nutrition Label Data",
            matched_category="Packaged Food",
            grams=totals.get("Total meal weight (g)", 100.0),
            servings=1.0,
            match_confidence=1.0,
            nutrients=totals
        )

        # Compile metadata
        metadata = {
            'analysis_version': '2.0',
            'source': 'nutrition_label',
            'data_type': 'packaged_food'
        }

        self._log("\n" + "=" * 60)
        self._log("✓ Analysis complete!")
        self._log("=" * 60 + "\n")

        return MealAnalysisResult(
            items=[package_item],
            totals=totals,
            indexes=indexes,
            indicators=indicators,
            figures=figures,
            metadata=metadata
        )

    def _convert_label_to_totals(self, nutrition_data: Dict) -> Dict[str, float]:
        """Convert label data to analyzer format"""

        totals = {}

        # Per-100g values (for analysis/comparison)
        totals['Energy (kcal)'] = nutrition_data.get('energy_kcal_per_100g', 0)
        totals['Energy (kJ)'] = nutrition_data.get('energy_kj_per_100g', 0)
        totals['Protein (g)'] = nutrition_data.get('protein_g', 0)
        totals['Carbohydrates digestible (g)'] = nutrition_data.get('carbohydrates_g', 0)
        totals['Total fiber (g)'] = nutrition_data.get('fiber_g', 0)
        totals['Fat (g)'] = nutrition_data.get('total_fat_g', 0)
        totals['SFA'] = nutrition_data.get('saturated_fat_g', 0)
        totals['Sugar (g)'] = nutrition_data.get('sugar_g', 0)
        totals['Sodium'] = nutrition_data.get('sodium_mg', 0)

        # Per-serving values (for user display)
        totals['serving_size'] = nutrition_data.get('serving_size', 100)
        totals['serving_unit'] = nutrition_data.get('serving_unit', 'g')
        totals['energy_kcal_per_serving'] = nutrition_data.get('energy_kcal_per_serving', 0)
        totals['energy_kj_per_serving'] = nutrition_data.get('energy_kj_per_serving', 0)
        totals['protein_per_serving_g'] = nutrition_data.get('protein_per_serving_g', 0)
        totals['carbs_per_serving_g'] = nutrition_data.get('carbs_per_serving_g', 0)
        totals['fat_per_serving_g'] = nutrition_data.get('fat_per_serving_g', 0)
        totals['sodium_per_serving_mg'] = nutrition_data.get('sodium_per_serving_mg', 0)
        totals['fiber_per_serving_g'] = nutrition_data.get('fiber_per_serving_g', 0)
        totals['sugar_per_serving_g'] = nutrition_data.get('sugar_per_serving_g', 0)

        # CRITICAL FIX: Use 100g for meal weight (not serving size!)
        # This ensures health scores are calculated correctly
        totals["Total meal weight (g)"] = 100.0  # ← CHANGED FROM serving_size
        totals["Number of items"] = 1.0

        # Add zeros for missing micronutrients
        for nutrient in ['MUFA', 'PUFA', 'Potassium', 'Calcium', 'Iron',
                         'Magnesium', 'Zinc', 'Vitamin A(µg)', 'Vitamin C',
                         'Vitamin D(µg)', 'Folate(µg)']:
            if nutrient not in totals:
                totals[nutrient] = 0.0

        return totals

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Demonstration of the nutritional analyzer."""

    # Initialize analyzer
    # Use relative path - assumes CSV is in same directory or in data/ subdirectory
    # Adjust this path based on your project structure
    database_path = Path(__file__).parent / "data" / "traditional food list.csv"

    # Alternative: if CSV is in the same directory as this script
    if not database_path.exists():
        database_path = Path(__file__).parent / "traditional food list.csv"

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=database_path,
        verbose=True
    )

    # Define a sample meal
    sample_meal = [
        "Boiled Rice, Keeri Samba",
        "Dhal curry, thick",
        "Chicken curry",
        "Brinjal curry",
        "Coconut sambol"
    ]

    print("\n" + "="*80)
    print("SAMPLE ANALYSIS: Traditional Sri Lankan Meal")
    print("="*80 + "\n")

    # Perform analysis
    result = analyzer.analyze_meal(sample_meal)

    # Generate and print text report
    report = analyzer.generate_text_report(result)
    print("\n" + report)

    # Export to JSON
    json_data = analyzer.export_to_json(result)
    print("\nJSON Export Sample:")
    print("-" * 80)
    import json
    print(json.dumps(json_data['health_indexes'], indent=2))

    # Save visualizations to outputs folder
    print("\nGenerating and saving visualizations...")

    # Create outputs directory
    outputs_dir = Path(__file__).parent / "outputs" / "visualizations"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Save each figure
    saved_files = []
    for name, fig in result.figures.items():
        # Save as high-resolution PNG
        png_path = outputs_dir / f"{name}.png"
        fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
        saved_files.append(png_path)
        print(f"  ✓ Saved: {png_path}")

        # Also save as PDF (vector format for publications)
        pdf_path = outputs_dir / f"{name}.pdf"
        fig.savefig(pdf_path, format='pdf', bbox_inches='tight')
        saved_files.append(pdf_path)
        print(f"  ✓ Saved: {pdf_path}")

    print(f"\n✓ All visualizations saved to: {outputs_dir.absolute()}")
    print(f"  Total files: {len(saved_files)}")

    # Optionally display the figures (comment out if you don't want to show them)
    # plt.show()

    return result


if __name__ == "__main__":
    main()