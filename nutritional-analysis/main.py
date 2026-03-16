"""
NutriScanner - Unified Interface
"""
from pathlib import Path
import json
from typing import List, Dict, Union
import sys

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Now use absolute imports
from label_scanner import PackagedFoodScanner
from meal_analyzer.analyzer import SriLankanNutritionalAnalyzer
from config.config import FOOD_DATABASE_PATH, OUTPUTS_DIR


class NutriScanner:
    """
    Unified nutrition scanner for:
    1. Packaged food labels (images) → Extract + Analyze
    2. Traditional meal plates (food items list) → Calculate + Analyze
    """

    def __init__(self):
        self.package_scanner = PackagedFoodScanner()
        self.meal_analyzer = SriLankanNutritionalAnalyzer(
            nutrition_database_path=FOOD_DATABASE_PATH,
            verbose=True
        )

    def scan_and_analyze_package(self, image_path: str) -> Dict:
        """
        Complete packaged food analysis:
        1. Scan label (extract data)
        2. Analyze nutrition (generate insights)

        Args:
            image_path: Path to package photo

        Returns:
            Complete analysis with insights
        """
        print("\n" + "=" * 60)
        print("PACKAGED FOOD ANALYSIS")
        print("=" * 60 + "\n")

        # Step 1: Scan label
        scan_result = self.package_scanner.scan(image_path)

        if not scan_result['success']:
            return {"success": False, "error": scan_result['error']}

        print("✅ Label scan successful!")

        # Step 2: Analyze nutrition
        analysis_result = self.meal_analyzer.analyze_packaged_food(
            scan_result['data']
        )

        # Generate report
        report = self.meal_analyzer.generate_text_report(analysis_result)
        print(report)

        # Save visualizations
        viz_paths = self._save_visualizations(analysis_result)

        return {
            "success": True,
            "scan_data": scan_result['data'],
            "health_indexes": analysis_result.indexes,
            "report": report,
            "visualizations": viz_paths
        }

    def analyze_meal_plate(self, food_items: List[str]) -> Dict:
        """
        Analyze traditional meal
        """
        print("\n" + "=" * 60)
        print("MEAL PLATE ANALYSIS")
        print("=" * 60 + "\n")

        result = self.meal_analyzer.analyze_meal(food_items)
        report = self.meal_analyzer.generate_text_report(result)
        print(report)

        viz_paths = self._save_visualizations(result)

        return {
            "success": True,
            "items": [
                {
                    "name": item.input_name,
                    "matched": item.matched_food_item,
                    "portion_g": item.grams,
                    "confidence": item.match_confidence
                }
                for item in result.items
            ],
            "health_indexes": result.indexes,
            "report": report,
            "visualizations": viz_paths
        }

    def analyze(self, input_data) -> Dict:
        """
        Smart analyzer - detects input type automatically

        Args:
            input_data: Either image path (str) or food items (list)

        Returns:
            Complete analysis
        """
        if isinstance(input_data, str):
            # It's an image path → packaged food
            return self.scan_and_analyze_package(input_data)
        elif isinstance(input_data, list):
            # It's a list of foods → meal plate
            return self.analyze_meal_plate(input_data)
        else:
            return {
                "success": False,
                "error": "Invalid input type. Expected image path (str) or food items (list)"
            }

    def _save_visualizations(self, result) -> Dict[str, str]:
        """Save analysis visualizations and return paths"""
        viz_dir = OUTPUTS_DIR / "visualizations"
        viz_dir.mkdir(exist_ok=True)

        viz_paths = {}

        for name, fig in result.figures.items():
            png_path = viz_dir / f"{name}.png"
            fig.savefig(png_path, dpi=300, bbox_inches='tight')
            viz_paths[name] = str(png_path)
            print(f"  ✓ Saved: {png_path.name}")

        return viz_paths


# Allow testing
if __name__ == "__main__":
    scanner = NutriScanner()
    print("✅ NutriScanner initialized successfully!")