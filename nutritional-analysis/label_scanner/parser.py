# -*- coding: utf-8 -*-
"""
Nutrition Label Parser - FIXED
"""
import re
from typing import Dict, Tuple, List


class NutritionParser:
    """Parse nutrition labels"""

    def parse(self, ocr_text: str) -> Dict:
        """Extract nutrition data"""
        nutrition = {}

        print("\nOCR Text:")
        print("-" * 60)
        print(ocr_text)
        print("-" * 60 + "\n")

        lines = [l.strip() for l in ocr_text.split('\n') if l.strip()]

        # Serving size - check line AND previous line
        for i, line in enumerate(lines):
            if 'serving size' in line.lower():
                # Check this line and previous line for number
                search_lines = []
                if i > 0:
                    search_lines.append(lines[i - 1])
                search_lines.append(line)
                if i < len(lines) - 1:
                    search_lines.append(lines[i + 1])

                for sl in search_lines:
                    match = re.search(r'(\d+)\s*g', sl)
                    if match:
                        nutrition['serving_size'] = float(match.group(1))
                        nutrition['serving_unit'] = 'g'
                        print(f"✓ Serving: {nutrition['serving_size']}g\n")
                        break
                break

        # Energy - grab MORE lines
        for i, line in enumerate(lines):
            if 'energy' in line.lower():
                # Get next 5 lines to capture all energy values
                context = lines[i:min(i + 6, len(lines))]
                all_nums = []
                for ctx_line in context:
                    nums = re.findall(r'(\d+\.?\d*)', ctx_line)
                    all_nums.extend([float(n) for n in nums])

                # Find kcal values (typically 50-600 range)
                kcal_vals = [n for n in all_nums if 50 <= n < 2000]

                if len(kcal_vals) >= 2:
                    sorted_kcals = sorted(kcal_vals)
                    nutrition['energy_kcal_per_serving'] = sorted_kcals[0]
                    nutrition['energy_kcal_per_100g'] = sorted_kcals[1]
                    print(f"✓ Energy: {sorted_kcals[0]} kcal (serving), {sorted_kcals[1]} kcal (100g)")
                break

        # Protein - grab 3 lines
        for i, line in enumerate(lines):
            if 'protein' in line.lower() and 'vitamin' not in line.lower():
                context = lines[i:min(i + 3, len(lines))]
                all_nums = []
                for ctx_line in context:
                    nums = re.findall(r'(\d+\.?\d*)', ctx_line)
                    all_nums.extend([float(n) for n in nums])

                # Filter: protein values are usually 0-100g
                protein_vals = [n for n in all_nums if 0 < n < 100]

                if len(protein_vals) >= 2:
                    # Smaller = per serving, larger = per 100g
                    sorted_vals = sorted(protein_vals)
                    nutrition['protein_per_serving_g'] = sorted_vals[0]
                    nutrition['protein_g'] = sorted_vals[1]
                    print(f"✓ Protein: {sorted_vals[0]}g (serving), {sorted_vals[1]}g (100g)")
                elif len(protein_vals) == 1:
                    nutrition['protein_g'] = protein_vals[0]
                break

        # Carbohydrates - grab 3 lines
        for i, line in enumerate(lines):
            if 'carbohydrate' in line.lower():
                context = lines[i:min(i + 3, len(lines))]
                all_nums = []
                for ctx_line in context:
                    nums = re.findall(r'(\d+\.?\d*)', ctx_line)
                    all_nums.extend([float(n) for n in nums])

                carb_vals = [n for n in all_nums if 0 < n < 200]

                if len(carb_vals) >= 2:
                    sorted_vals = sorted(carb_vals)
                    nutrition['carbs_per_serving_g'] = sorted_vals[0]
                    nutrition['carbohydrates_g'] = sorted_vals[1]
                    print(f"✓ Carbs: {sorted_vals[0]}g (serving), {sorted_vals[1]}g (100g)")
                break

        # Total Fat - grab 4 lines (fat values span multiple lines)
        for i, line in enumerate(lines):
            # Match "Total Fat" OR "Fat-Total" OR just "Fat" (but not "Saturated" or "Trans")
            if ('total fat' in line.lower() or 'fat-total' in line.lower() or
                    ('fat' in line.lower() and 'saturated' not in line.lower() and 'trans' not in line.lower())):
                context = lines[i:min(i + 4, len(lines))]
                all_nums = []
                for ctx_line in context:
                    nums = re.findall(r'(\d+\.?\d*)', ctx_line)
                    all_nums.extend([float(n) for n in nums])

                fat_vals = [n for n in all_nums if 0 < n < 100]

                if len(fat_vals) >= 2:
                    sorted_vals = sorted(fat_vals)
                    nutrition['fat_per_serving_g'] = sorted_vals[0]
                    nutrition['total_fat_g'] = sorted_vals[1]
                    print(f"✓ Fat: {sorted_vals[0]}g (serving), {sorted_vals[1]}g (100g)")
                break

        # Fiber - grab 3 lines to get both values
        for i, line in enumerate(lines):
            if 'fibre' in line.lower() or 'fiber' in line.lower():
                context = lines[i:min(i + 3, len(lines))]  # ← Changed from 2 to 3
                all_nums = []
                for ctx_line in context:
                    nums = re.findall(r'(\d+\.?\d*)', ctx_line)
                    all_nums.extend([float(n) for n in nums])

                fiber_vals = [n for n in all_nums if 0 < n < 20]  # Filter reasonable fiber values

                if len(fiber_vals) >= 2:
                    sorted_vals = sorted(fiber_vals)
                    nutrition['fiber_per_serving_g'] = sorted_vals[0]
                    nutrition['fiber_g'] = sorted_vals[1]
                    print(f"✓ Fiber: {sorted_vals[0]}g (serving), {sorted_vals[1]}g (100g)")
                elif len(fiber_vals) == 1:
                    nutrition['fiber_g'] = fiber_vals[0]
                    print(f"✓ Fiber: {fiber_vals[0]}g")
                break

        # Sodium - values are AFTER the keyword, often in grams
        for i, line in enumerate(lines):
            if 'sodium' in line.lower():
                # Check if "g" unit is mentioned in this line or next lines
                context = lines[i:min(i + 4, len(lines))]
                context_text = ' '.join(context)

                # Extract numbers
                all_nums = []
                for ctx_line in context[1:]:  # Skip sodium line itself
                    nums = re.findall(r'(\d+\.?\d*)', ctx_line)
                    all_nums.extend([float(n) for n in nums])

                sodium_vals = [n for n in all_nums if n > 0]

                if len(sodium_vals) >= 2:
                    sorted_vals = sorted(sodium_vals)
                    val1, val2 = sorted_vals[0], sorted_vals[1]

                    # If values are very small (< 5), they're likely in grams - convert to mg
                    if val1 < 5:
                        val1 = val1 * 1000
                    if val2 < 5:
                        val2 = val2 * 1000

                    nutrition['sodium_per_serving_mg'] = val1
                    nutrition['sodium_mg'] = val2
                    print(f"✓ Sodium: {val1}mg (serving), {val2}mg (100g)")
                break

        print("\n" + "=" * 60)
        print("EXTRACTED DATA:")
        print("=" * 60)
        for key, val in nutrition.items():
            print(f"  {key}: {val}")
        print()

        return nutrition

    def validate(self, nutrition_data: Dict) -> Tuple[bool, List[str]]:
        """Validate required fields"""
        required = ['protein_g']
        missing = [f for f in required if f not in nutrition_data]
        return len(missing) == 0, missing