"""
NutriScanner - Unified Interface
Handles BOTH packaged food AND meal plate analysis
"""
from pathlib import Path
import json
from typing import List, Dict, Union

from label_scanner import PackagedFoodScanner
from meal_analyzer import SriLankanNutritionalAnalyzer
from config.config import FOOD_DATABASE_PATH, OUTPUTS_DIR


class NutriScanner:
    """
    Unified nutrition scanner for:
    1. Packaged food labels (images)
    2. Traditional meal plates (food items list)
    """

    def __init__(self):
        # Initialize both scanners
        self.package_scanner = PackagedFoodScanner()
        self.meal_analyzer = SriLankanNutritionalAnalyzer(
            nutrition_database_path=FOOD_DATABASE_PATH,
            verbose=True
        )

    def scan_packaged_food(self, image_path: str) -> Dict:
        """
        Scan nutrition label from packaged food image

        Args:
            image_path: Path to package photo

        Returns:
            Dictionary with nutrition data
        """
        print("\n" + "=" * 60)
        print("SCANNING PACKAGED FOOD")
        print("=" * 60 + "\n")

        result = self.package_scanner.scan(image_path)

        if result['success']:
            print("✅ Scan successful!")
            print("\nNutrition Data:")
            print(json.dumps(result['data'], indent=2))
        else:
            print(f"❌ Scan failed: {result['error']}")

        return result

    def analyze_meal_plate(self, food_items: List[str]) -> Dict:
        """
        Analyze traditional Sri Lankan meal

        Args:
            food_items: List of food items on plate

        Returns:
            Complete nutritional analysis
        """
        print("\n" + "=" * 60)
        print("ANALYZING MEAL PLATE")
        print("=" * 60 + "\n")

        # Run analysis
        result = self.meal_analyzer.analyze_meal(food_items)

        # Generate report
        report = self.meal_analyzer.generate_text_report(result)
        print(report)

        # Save visualizations
        self._save_visualizations(result)

        # Return JSON
        return self.meal_analyzer.export_to_json(result)

    def compare_packaged_vs_meal(
            self,
            package_image: str,
            meal_items: List[str]
    ) -> Dict:
        """
        Compare packaged food with homemade meal

        Args:
            package_image: Path to package photo
            meal_items: List of meal items

        Returns:
            Comparison data
        """
        print("\n" + "=" * 60)
        print("COMPARISON: Packaged vs Homemade")
        print("=" * 60 + "\n")

        # Scan both
        package_data = self.scan_packaged_food(package_image)
        meal_data = self.analyze_meal_plate(meal_items)

        if not package_data['success']:
            return {"error": "Package scan failed"}

        # Compare
        comparison = self._generate_comparison(
            package_data['data'],
            meal_data['totals']
        )

        return {
            "packaged_food": package_data['data'],
            "meal_plate": meal_data['totals'],
            "comparison": comparison
        }

    def _save_visualizations(self, result):
        """Save analysis visualizations"""
        viz_dir = OUTPUTS_DIR / "visualizations"
        viz_dir.mkdir(exist_ok=True)

        for name, fig in result.figures.items():
            png_path = viz_dir / f"{name}.png"
            fig.savefig(png_path, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved: {png_path.name}")

    def _generate_comparison(self, package: Dict, meal: Dict) -> Dict:
        """Generate comparison metrics"""
        return {
            "energy_kcal": {
                "packaged": package.get('energy_kcal_per_100g', 0),
                "meal": meal.get('Energy (kcal)', 0)
            },
            "protein_g": {
                "packaged": package.get('protein_g', 0),
                "meal": meal.get('Protein (g)', 0)
            },
            "carbs_g": {
                "packaged": package.get('carbohydrates_g', 0),
                "meal": meal.get('Carbohydrates digestible (g)', 0)
            },
            "fat_g": {
                "packaged": package.get('total_fat_g', 0),
                "meal": meal.get('Fat (g)', 0)
            },
            "sodium_mg": {
                "packaged": package.get('sodium_mg', 0),
                "meal": meal.get('Sodium', 0)
            }
        }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    scanner = NutriScanner()

    # Example 1: Scan packaged food
    print("\n" + "#" * 60)
    print("# Example 1: Packaged Food Scan")
    print("#" * 60)

    package_result = scanner.scan_packaged_food("img.png")

    # Example 2: Analyze meal plate
    print("\n" + "#" * 60)
    print("# Example 2: Meal Plate Analysis")
    print("#" * 60)

    meal_result = scanner.analyze_meal_plate([
        "Boiled Rice, Keeri Samba",
        "Chicken curry",
        "Dhal curry, thick"
    ])

    # Example 3: Compare both
    print("\n" + "#" * 60)
    print("# Example 3: Comparison")
    print("#" * 60)

    comparison = scanner.compare_packaged_vs_meal(
        package_image="img.png",
        meal_items=["Boiled Rice", "Chicken curry"]
    )

    # Save all results
    results_file = OUTPUTS_DIR / "complete_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "packaged_food": package_result,
            "meal_analysis": meal_result,
            "comparison": comparison
        }, f, indent=2)

    print(f"\n✓ All results saved to: {results_file}")