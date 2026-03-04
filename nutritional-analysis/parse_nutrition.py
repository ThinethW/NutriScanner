import re


def parse_nutrition_data(ocr_text):
    """
    Extract nutrition values from OCR text into structured dictionary
    """
    nutrition = {}

    # Extract serving size
    serving_match = re.search(r'Serving size.*?(\d+\.?\d*)\s*g', ocr_text, re.IGNORECASE)
    if serving_match:
        nutrition['serving_size_g'] = float(serving_match.group(1))

    # Extract servings per pack
    servings_match = re.search(r'servings per pack.*?(\d+\.?\d*)', ocr_text, re.IGNORECASE)
    if servings_match:
        nutrition['servings_per_pack'] = float(servings_match.group(1))

    # Extract energy (kJ and kcal) - look for Per 100g column
    energy_kj = re.search(r'Energy.*?(\d+)\s*kJ.*?(\d+)\s*kcal', ocr_text, re.IGNORECASE | re.DOTALL)
    if energy_kj:
        nutrition['energy_kj_per_100g'] = int(energy_kj.group(1))
        nutrition['energy_kcal_per_100g'] = int(energy_kj.group(2))

    # Extract nutrients (Per 100g values)
    # Pattern: find nutrient name, then capture first number with unit
    patterns = {
        'carbohydrates_g': r'Carbohydrates.*?(\d+\.?\d*)\s*g',
        'sugar_g': r'Total Sugar.*?(\d+\.?\d*)\s*g',
        'fiber_g': r'Dietary Fibre.*?(\d+\.?\d*)\s*g',
        'protein_g': r'Protein.*?(\d+\.?\d*)\s*g',
        'total_fat_g': r'Total Fat.*?(\d+\.?\d*)\s*g',
        'saturated_fat_g': r'Saturated Fatty Acids.*?(\d+\.?\d*)\s*g',
        'trans_fat_g': r'Trans Fatty Acids.*?(\d+\.?\d*)\s*g',
        'sodium_mg': r'Sodium.*?(\d+\.?\d*)\s*mg'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            nutrition[key] = float(match.group(1))

    return nutrition


# Test it with your OCR output
if __name__ == "__main__":
    # Your actual OCR text
    ocr_output = """
    NUTRITION INFORMATION (Average Composition)
    Serving size: 22.5g
    Number of servings per pack 5Biscuits 14.4
    TypicalValues Per 100 g Per Serving
    Energy 1931kJ 434kJ
    461 kcal 104 kcal
    Carbohydrates 74.29 g 16.72 g
    of which Total Sugar 18.32 g 4.12 g
    Dietary Fibre 1.69 g 0.38 g
    Protein 7.24 g 1.63 g
    Total Fat 15.01 g 3.38 g
    of which
    Saturated Fatty Acids 6.16 g 1.39 g
    Trans Fatty Acids 0.01 g 0.00 g
    Sodium (Na 458mg 103.17 mg
    """

    result = parse_nutrition_data(ocr_output)

    print("Extracted Nutrition Data:")
    print("-" * 40)
    for key, value in result.items():
        print(f"{key}: {value}")