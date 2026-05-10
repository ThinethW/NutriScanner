"""
NutriScanner - Unified Interface
"""
from pathlib import Path
import json
from typing import List, Dict, Union
import sys

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

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
        1. Scan label (extract nutrition data)
        2. Analyze nutrition (generate health insights)

        Returns dict with keys:
            success        : bool
            error          : str  (only if success=False)
            scan_data      : dict of raw nutrition values
            analysis       : dict with health_indexes, report, visualizations
        """
        print("\n" + "=" * 60)
        print("PACKAGED FOOD ANALYSIS")
        print("=" * 60 + "\n")

        # ── Step 1: Scan label ────────────────────────────────────────
        scan_result = self.package_scanner.scan(image_path)

        if not scan_result.get('success'):
            return {
                "success": False,
                "error": scan_result.get('error', 'Unknown scan error'),
                "scan_data": {},
                "analysis": {}
            }

        print("✅ Label scan successful!")

        # scan_result uses key 'data' internally — extract it safely
        nutrition_data = scan_result.get('data', scan_result.get('scan_data', {}))

        # ── Step 2: Analyze nutrition ─────────────────────────────────
        try:
            analysis_result = self.meal_analyzer.analyze_packaged_food(
                nutrition_data
            )
            report = self.meal_analyzer.generate_text_report(analysis_result)
            print(report)
            viz_paths = self._save_visualizations(analysis_result)

            # Build analysis sub-dict so both result['health_indexes']
            # AND result['analysis']['health_indexes'] work
            analysis_dict = {
                "health_indexes": analysis_result.indexes,
                "report": report,
                "visualizations": viz_paths
            }

        except Exception as e:
            print(f"⚠ Analysis step failed: {e}")
            analysis_dict = {
                "health_indexes": {},
                "report": "Analysis unavailable.",
                "visualizations": {}
            }

        return {
            "success": True,
            "scan_data": nutrition_data,
            # Flat access: result['health_indexes']
            "health_indexes": analysis_dict["health_indexes"],
            "report": analysis_dict["report"],
            "visualizations": analysis_dict.get("visualizations", {}),
            # Nested access: result['analysis']['health_indexes']
            "analysis": analysis_dict
        }

    def analyze_meal_plate(self, food_items: List[str]) -> Dict:
        """
        Analyze a traditional meal from a list of food names.

        Returns dict with keys:
            success        : bool
            error          : str  (only if success=False)
            items          : list of matched food items
            health_indexes : dict
            analysis       : dict with health_indexes, report, visualizations
            report         : str
        """
        print("\n" + "=" * 60)
        print("MEAL PLATE ANALYSIS")
        print("=" * 60 + "\n")

        try:
            result = self.meal_analyzer.analyze_meal(food_items)
            report = self.meal_analyzer.generate_text_report(result)
            print(report)
            viz_paths = self._save_visualizations(result)

            analysis_dict = {
                "health_indexes": result.indexes,
                "report": report,
                "visualizations": viz_paths
            }

            return {
                "success": True,
                "items": [
                    {
                        "name":       item.input_name,
                        "matched":    item.matched_food_item,
                        "portion_g":  item.grams,
                        "confidence": item.match_confidence
                    }
                    for item in result.items
                ],
                "health_indexes": result.indexes,
                "report": report,
                "visualizations": viz_paths,
                "analysis": analysis_dict
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "items": [],
                "health_indexes": {},
                "analysis": {}
            }

    def analyze(self, input_data) -> Dict:
        """
        Smart analyzer — detects input type automatically.

        Args:
            input_data: image path (str) or food item list (list)
        """
        if isinstance(input_data, str):
            return self.scan_and_analyze_package(input_data)
        elif isinstance(input_data, list):
            return self.analyze_meal_plate(input_data)
        else:
            return {
                "success": False,
                "error": "Invalid input. Expected image path (str) or food list (list).",
                "scan_data": {},
                "analysis": {}
            }

    def _save_visualizations(self, result) -> Dict[str, str]:
        """Save analysis visualizations and return file paths."""
        viz_dir = OUTPUTS_DIR / "visualizations"
        viz_dir.mkdir(exist_ok=True)

        viz_paths = {}
        figures = getattr(result, 'figures', {})
        for name, fig in figures.items():
            png_path = viz_dir / f"{name}.png"
            fig.savefig(png_path, dpi=300, bbox_inches='tight')
            viz_paths[name] = str(png_path)
            print(f"  ✓ Saved: {png_path.name}")

        return viz_paths


if __name__ == "__main__":
    scanner = NutriScanner()
    print("✅ NutriScanner initialized successfully!")