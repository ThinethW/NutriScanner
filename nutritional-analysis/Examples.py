"""
NutriScanner - Example Usage Scenarios
========================================

This script demonstrates various ways to use the Sri Lankan Nutritional Analyzer
for different meal analysis scenarios.
"""

from pathlib import Path
import json
import matplotlib.pyplot as plt
from NutritionalAnalyzer import (
    SriLankanNutritionalAnalyzer,
    PortionRule
)


def example_1_basic_analysis():
    """Example 1: Basic meal analysis with standard settings."""

    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Meal Analysis")
    print("=" * 80 + "\n")

    # Initialize analyzer
    # Use relative path - adjust based on your project structure
    csv_path = Path(__file__).parent / "data" / "traditional food list.csv"
    if not csv_path.exists():
        csv_path = Path(__file__).parent / "traditional food list.csv"

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=csv_path,
        verbose=True
    )

    # Define a typical Sri Lankan breakfast
    breakfast = [
        "Boiled Rice, Keeri Samba",
        "Dhal curry, thick",
        "Coconut sambol"
    ]

    # Analyze
    result = analyzer.analyze_meal(breakfast)

    # Print summary
    print("\n" + "-" * 80)
    print("ANALYSIS SUMMARY")
    print("-" * 80)
    print(f"Total items: {result.total_items}")
    print(f"Average match confidence: {result.average_match_confidence:.2%}")
    print(f"Total energy: {result.totals.get('Energy (kcal)', 0):.1f} kcal")
    print(f"Total weight: {result.totals.get('Total meal weight (g)', 0):.1f}g")

    print("\nHealth Index Scores:")
    for name, score in result.indexes.items():
        print(f"  {name}: {score:.1f}/100")

    return result


def example_2_lunch_analysis():
    """Example 2: Comprehensive lunch analysis with full reporting."""

    print("\n" + "=" * 80)
    print("EXAMPLE 2: Comprehensive Lunch Analysis")
    print("=" * 80 + "\n")

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=Path("traditional_food_list.csv"),
        verbose=False  # Silent mode
    )

    # Traditional rice and curry meal
    lunch = [
        "Boiled Rice, Nadu, White",
        "Dhal curry, watery",
        "Chicken curry",
        "Brinjal curry",
        "Gotukola sambol"
    ]

    result = analyzer.analyze_meal(lunch)

    # Generate full text report
    report = analyzer.generate_text_report(result)
    print(report)

    # Save report to file
    output_dir = Path("/mnt/user-data/outputs")
    output_dir.mkdir(exist_ok=True)

    report_path = output_dir / "lunch_analysis_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n✓ Report saved to: {report_path}")

    return result


def example_3_json_export():
    """Example 3: JSON export for API integration."""

    print("\n" + "=" * 80)
    print("EXAMPLE 3: JSON Export for API Integration")
    print("=" * 80 + "\n")

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=Path("traditional_food_list.csv"),
        verbose=False
    )

    meal = [
        "Boiled Rice, Kekulu, Red",
        "Fish curry",
        "Pol sambol"
    ]

    result = analyzer.analyze_meal(meal)

    # Export to JSON
    json_data = analyzer.export_to_json(result)

    # Save to file
    output_path = Path("/mnt/user-data/outputs/meal_analysis.json")
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    print("✓ JSON data exported successfully")
    print(f"✓ Saved to: {output_path}")

    # Print sample of JSON structure
    print("\nSample JSON Structure:")
    print("-" * 80)
    print("Metadata:", json.dumps(json_data['metadata'], indent=2))
    print("\nFirst item:", json.dumps(json_data['items'][0], indent=2))
    print("\nHealth indexes:", json.dumps(json_data['health_indexes'], indent=2))

    return result


def example_4_custom_portions():
    """Example 4: Using custom portion rules."""

    print("\n" + "=" * 80)
    print("EXAMPLE 4: Custom Portion Rules")
    print("=" * 80 + "\n")

    # Define custom portions for specific foods
    custom_portions = {
        "boiled rice, keeri samba": PortionRule(
            standard_serving_g=80,
            typical_servings_per_meal=3.0,
            typical_amount_per_meal_g=240  # Larger rice portion
        ),
        "chicken curry": PortionRule(
            standard_serving_g=40,
            typical_servings_per_meal=1.5,
            typical_amount_per_meal_g=60  # More chicken
        )
    }

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=Path("traditional_food_list.csv"),
        portion_rules=custom_portions,
        verbose=True
    )

    meal = [
        "Boiled Rice, Keeri Samba",
        "Chicken curry",
        "Dhal curry, thick"
    ]

    result = analyzer.analyze_meal(meal)

    print("\nCustom Portion Results:")
    print("-" * 80)
    for item in result.items:
        print(f"{item.matched_food_item}")
        print(f"  Portion: {item.grams}g ({item.servings} servings)")
        print(f"  Energy: {item.nutrients.get('Energy (kcal)', 0):.1f} kcal")
        print()

    return result


def example_5_comparison_analysis():
    """Example 5: Compare multiple meal options."""

    print("\n" + "=" * 80)
    print("EXAMPLE 5: Meal Comparison Analysis")
    print("=" * 80 + "\n")

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=Path("traditional_food_list.csv"),
        verbose=False
    )

    # Define two meal options
    meal_option_1 = [
        "Boiled Rice, Keeri Samba",
        "Dhal curry, thick",
        "Chicken curry",
        "Gotukola sambol"
    ]

    meal_option_2 = [
        "Boiled Rice, Kekulu, Red",  # Red rice (more fiber)
        "Dhal curry, watery",
        "Fish curry",
        "Coconut sambol"
    ]

    # Analyze both
    result_1 = analyzer.analyze_meal(meal_option_1)
    result_2 = analyzer.analyze_meal(meal_option_2)

    # Compare key metrics
    print("COMPARISON RESULTS")
    print("-" * 80)
    print(f"{'Metric':<30} {'Option 1':>15} {'Option 2':>15}")
    print("-" * 80)

    metrics = [
        ('Energy (kcal)', 'Energy (kcal)'),
        ('Carbs (g)', 'Carbohydrates digestible (g)'),
        ('Fiber (g)', 'Total fiber (g)'),
        ('Protein (g)', 'Protein (g)'),
        ('Sodium (mg)', 'Sodium'),
    ]

    for display_name, key in metrics:
        val1 = result_1.totals.get(key, 0)
        val2 = result_2.totals.get(key, 0)
        print(f"{display_name:<30} {val1:>15.1f} {val2:>15.1f}")

    print("\n" + "-" * 80)
    print("Health Index Comparison")
    print("-" * 80)

    for index_name in result_1.indexes.keys():
        score1 = result_1.indexes[index_name]
        score2 = result_2.indexes[index_name]
        diff = score2 - score1
        arrow = "→" if abs(diff) < 5 else ("↑" if diff > 0 else "↓")
        print(f"{index_name:<35} {score1:>6.1f} {arrow:^5} {score2:>6.1f}")

    return result_1, result_2


def example_6_visualization_export():
    """Example 6: Export high-quality visualizations."""

    print("\n" + "=" * 80)
    print("EXAMPLE 6: Export High-Quality Visualizations")
    print("=" * 80 + "\n")

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=Path("traditional_food_list.csv"),
        verbose=False
    )

    meal = [
        "Boiled Rice, Nadu, White",
        "Dhal curry, thick",
        "Chicken curry",
        "Brinjal curry",
        "Pol sambol"
    ]

    result = analyzer.analyze_meal(meal)

    # Create output directory
    output_dir = Path("/mnt/user-data/outputs/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save all figures in multiple formats
    for name, fig in result.figures.items():
        # High-resolution PNG
        png_path = output_dir / f"{name}.png"
        fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Saved PNG: {png_path}")

        # Vector PDF (for publications)
        pdf_path = output_dir / f"{name}.pdf"
        fig.savefig(pdf_path, format='pdf', bbox_inches='tight')
        print(f"✓ Saved PDF: {pdf_path}")

    print(f"\n✓ All visualizations saved to: {output_dir}")

    return result


def example_7_batch_processing():
    """Example 7: Batch process multiple meals."""

    print("\n" + "=" * 80)
    print("EXAMPLE 7: Batch Processing Multiple Meals")
    print("=" * 80 + "\n")

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=Path("traditional_food_list.csv"),
        verbose=False
    )

    # Define meals for a day
    meals = {
        "Breakfast": ["Boiled Rice, Keeri Samba", "Dhal curry, thick", "Pol sambol"],
        "Lunch": ["Boiled Rice, Nadu, White", "Chicken curry", "Brinjal curry", "Gotukola sambol"],
        "Dinner": ["Boiled Rice, Kekulu, Red", "Fish curry", "Dhal curry, watery"]
    }

    # Process all meals
    results = {}
    for meal_name, food_items in meals.items():
        print(f"Processing {meal_name}...")
        results[meal_name] = analyzer.analyze_meal(food_items)

    # Summary report
    print("\n" + "=" * 80)
    print("DAILY NUTRITION SUMMARY")
    print("=" * 80 + "\n")

    total_energy = sum(r.totals.get('Energy (kcal)', 0) for r in results.values())
    total_protein = sum(r.totals.get('Protein (g)', 0) for r in results.values())
    total_fiber = sum(r.totals.get('Total fiber (g)', 0) for r in results.values())
    total_sodium = sum(r.totals.get('Sodium', 0) for r in results.values())

    print(f"Total Daily Energy: {total_energy:.1f} kcal")
    print(f"Total Daily Protein: {total_protein:.1f}g")
    print(f"Total Daily Fiber: {total_fiber:.1f}g")
    print(f"Total Daily Sodium: {total_sodium:.1f}mg")

    print("\nMeal-by-Meal Breakdown:")
    print("-" * 80)
    for meal_name, result in results.items():
        energy = result.totals.get('Energy (kcal)', 0)
        avg_score = sum(result.indexes.values()) / len(result.indexes)
        print(f"{meal_name:<15} {energy:>8.1f} kcal    Avg Health Score: {avg_score:.1f}/100")

    return results


def example_8_error_handling():
    """Example 8: Demonstrate error handling."""

    print("\n" + "=" * 80)
    print("EXAMPLE 8: Error Handling Demonstration")
    print("=" * 80 + "\n")

    analyzer = SriLankanNutritionalAnalyzer(
        nutrition_database_path=Path("traditional_food_list.csv"),
        verbose=True
    )

    # Test various error scenarios
    test_meals = [
        (["Unknown Food Item 123"], "Unknown food item"),
        (["Boiled Rice, Keeri Samba"], "Valid single item"),
        (["Rice", "Curry", "Sambol"], "Generic terms"),
    ]

    for food_items, description in test_meals:
        print(f"\nTesting: {description}")
        print(f"Input: {food_items}")
        print("-" * 60)

        try:
            result = analyzer.analyze_meal(food_items)
            print(f"✓ Success! Energy: {result.totals.get('Energy (kcal)', 0):.1f} kcal")
        except Exception as e:
            print(f"✗ Error: {str(e)}")


def run_all_examples():
    """Run all example scenarios."""

    print("\n" + "=" * 80)
    print("NUTRISCANNER - COMPREHENSIVE EXAMPLE DEMONSTRATION")
    print("=" * 80)

    examples = [
        ("Basic Analysis", example_1_basic_analysis),
        ("Lunch Analysis with Report", example_2_lunch_analysis),
        ("JSON Export", example_3_json_export),
        ("Custom Portions", example_4_custom_portions),
        ("Meal Comparison", example_5_comparison_analysis),
        ("Visualization Export", example_6_visualization_export),
        ("Batch Processing", example_7_batch_processing),
        ("Error Handling", example_8_error_handling),
    ]

    for i, (name, func) in enumerate(examples, 1):
        print(f"\n\n{'#' * 80}")
        print(f"# Example {i}/{len(examples)}: {name}")
        print(f"{'#' * 80}")

        try:
            func()
        except Exception as e:
            print(f"\n⚠ Example failed with error: {str(e)}")

    print("\n\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)
    print("\nCheck /mnt/user-data/outputs/ for generated files.")


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # Display all generated plots
    # plt.show()