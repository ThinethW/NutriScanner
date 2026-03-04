"""
ROBUST Nutrition Label Parser - Final Version
Handles all label formats with proper column detection
"""
import re
from typing import Dict, Tuple, List


class NutritionParser:
    """Parse nutrition labels - auto-detect column order"""

    def parse(self, ocr_text: str) -> Dict:
        """Extract nutrition data with automatic column detection"""
        nutrition = {}

        print("\n🔍 OCR Text:")
        print("-" * 60)
        print(ocr_text)
        print("-" * 60 + "\n")

        # Clean text
        text = re.sub(r'\s+', ' ', ocr_text)
        text = text.replace('per Serving', 'per Serving')

        # ================================================================
        # STEP 1: Detect Column Order
        # ================================================================
        serving_pos = text.lower().find('per serving')
        hundred_pos = text.lower().find('per 100')

        # Also check for "Average Quantity" headers
        avg_serving_pos = text.lower().find('average quantity per serving')
        avg_100_pos = text.lower().find('average quantity per 100')

        if avg_serving_pos > 0 and avg_100_pos > 0:
            column_order = "serving_first" if avg_serving_pos < avg_100_pos else "100g_first"
        elif serving_pos > 0 and hundred_pos > 0:
            column_order = "serving_first" if serving_pos < hundred_pos else "100g_first"
        else:
            column_order = "serving_first"  # Default

        print(f"📊 Column Order: {'Per Serving | Per 100g' if column_order == 'serving_first' else 'Per 100g | Per Serving'}\n")

        # ================================================================
        # STEP 2: Extract Serving Size
        # ================================================================
        serving_patterns = [
            r'serving size[:\s]*(\d+\.?\d*)\s*(ml|g)',
            r'serving[:\s]*(\d+\.?\d*)\s*(ml|g)',
        ]

        for pattern in serving_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                nutrition['serving_size'] = float(match.group(1))
                nutrition['serving_unit'] = match.group(2).lower()
                print(f"✅ Serving: {nutrition['serving_size']}{nutrition['serving_unit']}\n")
                break

        # ================================================================
        # STEP 3: Extract Energy
        # ================================================================
        energy_pattern = r'energy[\s:]*([\d.\s]+kj[^a-z]*[\d.\s]+kj[^a-z]*[\d.\s]+kcal[^a-z]*[\d.\s]+)'
        energy_match = re.search(energy_pattern, text, re.IGNORECASE | re.DOTALL)

        if energy_match:
            section = energy_match.group(1)
            numbers = re.findall(r'(\d+\.?\d*)', section)

            if len(numbers) >= 4:
                nums = [float(n) for n in numbers[:4]]
                print(f"  Energy numbers found: {nums}")

                if column_order == "serving_first":
                    nutrition['energy_kj_per_serving'] = nums[0]
                    nutrition['energy_kj_per_100g'] = nums[1]
                    nutrition['energy_kcal_per_serving'] = nums[2]
                    nutrition['energy_kcal_per_100g'] = nums[3]
                else:
                    nutrition['energy_kj_per_100g'] = nums[0]
                    nutrition['energy_kj_per_serving'] = nums[1]
                    nutrition['energy_kcal_per_100g'] = nums[2]
                    nutrition['energy_kcal_per_serving'] = nums[3]

                print(f"  Energy: {nutrition.get('energy_kcal_per_100g')} kcal/100g, {nutrition.get('energy_kcal_per_serving')} kcal/serving")

        # ================================================================
        # STEP 4: Helper - Extract nutrients
        # ================================================================
        def extract_nutrient(name: str, unit: str = 'g') -> Dict:
            """Extract values for a nutrient"""
            pattern = rf'{name}[\s:-]*([\d.\s]+{unit}[^a-z]*[\d.\s]+{unit})'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

            if not match:
                return {}

            section = match.group(1)
            numbers = re.findall(r'(\d+\.?\d*)', section)

            if len(numbers) >= 2:
                nums = [float(n) for n in numbers[:2]]

                if column_order == "serving_first":
                    per_serving = nums[0]
                    per_100 = nums[1]
                else:
                    per_100 = nums[0]
                    per_serving = nums[1]

                print(f"  {name}: per 100={per_100}{unit}, per serving={per_serving}{unit}")

                return {
                    'per_100': per_100,
                    'per_serving': per_serving
                }

            return {}

        # ================================================================
        # STEP 5: Extract Macronutrients
        # ================================================================

        # Protein
        protein = extract_nutrient(r'protein', 'g')
        if protein:
            nutrition['protein_g'] = protein['per_100']
            nutrition['protein_per_serving_g'] = protein['per_serving']

        # Fat-Total (handle hyphen)
        fat = extract_nutrient(r'fat[\s-]*total', 'g')
        if not fat:
            fat = extract_nutrient(r'total[\s]*fat', 'g')
        if fat:
            nutrition['total_fat_g'] = fat['per_100']
            nutrition['fat_per_serving_g'] = fat['per_serving']

        # Saturated fatty acids
        sat_fat = extract_nutrient(r'saturated\s*fatty\s*acids', 'g')
        if sat_fat:
            nutrition['saturated_fat_g'] = sat_fat['per_100']
            nutrition['saturated_fat_per_serving_g'] = sat_fat['per_serving']

        # Carbohydrates-Total (handle hyphen and variations)
        carb_patterns = [
            r'carbohydrates?[\s-]*total?',
            r'total[\s]*carbohydrates?',
            r'carbs',
        ]

        carbs = None
        for carb_pattern in carb_patterns:
            carbs = extract_nutrient(carb_pattern, 'g')
            if carbs:
                break

        if carbs:
            nutrition['carbohydrates_g'] = carbs['per_100']
            nutrition['carbs_per_serving_g'] = carbs['per_serving']

        # Dietary fiber
        fiber = extract_nutrient(r'dietary\s*fi[bp]re', 'g')
        if fiber:
            nutrition['fiber_g'] = fiber['per_100']
            nutrition['fiber_per_serving_g'] = fiber['per_serving']

        # Sugar
        sugar = extract_nutrient(r'sugar', 'g')
        if sugar:
            nutrition['sugar_g'] = sugar['per_100']
            nutrition['sugar_per_serving_g'] = sugar['per_serving']

        # ================================================================
        # STEP 6: Extract Sodium (special handling for g vs mg)
        # ================================================================
        sodium_pattern = r'sodium[\s:\(Na\)]*(\d+\.?\d*)\s*(mg|g)[^a-z]*(\d+\.?\d*)\s*(mg|g)'
        sodium_match = re.search(sodium_pattern, text, re.IGNORECASE)

        if sodium_match:
            val1 = float(sodium_match.group(1))
            unit1 = sodium_match.group(2).lower()
            val2 = float(sodium_match.group(3))
            unit2 = sodium_match.group(4).lower()

            # Convert g to mg (0.02g = 20mg, 0.2g = 200mg)
            if unit1 == 'g':
                val1 = val1 * 1000
            if unit2 == 'g':
                val2 = val2 * 1000

            if column_order == "serving_first":
                nutrition['sodium_per_serving_mg'] = val1
                nutrition['sodium_mg'] = val2
            else:
                nutrition['sodium_mg'] = val1
                nutrition['sodium_per_serving_mg'] = val2

            print(f"  Sodium: per 100={nutrition['sodium_mg']} mg, per serving={nutrition['sodium_per_serving_mg']} mg")

        print("\n" + "=" * 60)
        print("✅ EXTRACTED DATA:")
        print("=" * 60)
        for key, val in nutrition.items():
            print(f"  {key}: {val}")
        print()

        return nutrition

    def validate(self, nutrition_data: Dict) -> Tuple[bool, List[str]]:
        """Validate required fields"""
        required = ['energy_kcal_per_100g', 'protein_g']
        missing = [f for f in required if f not in nutrition_data]
        return len(missing) == 0, missing