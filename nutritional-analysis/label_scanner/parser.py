"""
Parse nutrition data from OCR text
"""
import re
from typing import Dict, Tuple, Any

from config.config import NUTRIENT_PATTERNS


class NutritionParser:
    """Parses structured nutrition data from OCR text"""

    def __init__(self):
        self.patterns = NUTRIENT_PATTERNS

    def parse(self, ocr_text: str) -> Dict[str, Any]:
        """
        Extract nutrition values from OCR text

        Args:
            ocr_text: Raw text from OCR

        Returns:
            Dictionary of nutrition data
        """
        nutrition = {}

        # Extract serving size
        serving_match = re.search(
            self.patterns['serving_size_g'],
            ocr_text,
            re.IGNORECASE
        )
        if serving_match:
            nutrition['serving_size_g'] = float(serving_match.group(1))

        # Extract servings per pack
        servings_match = re.search(
            self.patterns['servings_per_pack'],
            ocr_text,
            re.IGNORECASE
        )
        if servings_match:
            nutrition['servings_per_pack'] = float(servings_match.group(1))

        # Extract energy
        self._extract_energy(ocr_text, nutrition)

        # Extract other nutrients
        self._extract_nutrients(ocr_text, nutrition)

        return nutrition

    def _extract_energy(self, text: str, nutrition: Dict):
        """Extract energy values (kJ and kcal)"""
        # Try to find both kJ and kcal
        energy_match = re.search(
            r'Energy.*?(\d+)\s*kJ.*?(\d+)\s*kcal',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if energy_match:
            nutrition['energy_kj_per_100g'] = int(energy_match.group(1))
            nutrition['energy_kcal_per_100g'] = int(energy_match.group(2))

    def _extract_nutrients(self, text: str, nutrition: Dict):
        """Extract macro and micronutrients"""
        nutrient_keys = [
            'carbohydrates_g', 'sugar_g', 'fiber_g', 'protein_g',
            'total_fat_g', 'saturated_fat_g', 'trans_fat_g', 'sodium_mg'
        ]

        for key in nutrient_keys:
            pattern = self.patterns.get(key)
            if pattern:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    nutrition[key] = float(match.group(1))

    def validate(self, nutrition_data: Dict) -> Tuple[bool, list]:
        """
        Validate parsed nutrition data

        Returns:
            Tuple of (is_valid, missing_fields)
        """
        required_fields = ['energy_kcal_per_100g', 'carbohydrates_g',
                           'protein_g', 'total_fat_g']

        missing = [field for field in required_fields
                   if field not in nutrition_data]

        return len(missing) == 0, missing