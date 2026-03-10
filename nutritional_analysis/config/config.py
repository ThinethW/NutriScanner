"""
Configuration settings for NutriScanner
"""
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Model paths
YOLO_MODEL_PATH = PROJECT_ROOT / "models" / "nutrition_label_detector" / "best.pt"

# Data paths
FOOD_DATABASE_PATH = PROJECT_ROOT / "data" / "traditional food list.csv"

# Output paths
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# OCR settings
OCR_CONFIG = {
    'lang': 'en',
    'use_angle_cls': False,
    'show_log': False
}

# YOLO settings
YOLO_CONFIDENCE = 0.4

# Nutrient patterns for parsing
NUTRIENT_PATTERNS = {
    'serving_size_g': r'Serving size.*?(\d+\.?\d*)\s*g',
    'servings_per_pack': r'servings per pack.*?(\d+\.?\d*)',
    'energy_kj_per_100g': r'Energy.*?(\d+)\s*kJ',
    'energy_kcal_per_100g': r'Energy.*?\d+\s*kJ.*?(\d+)\s*kcal',
    'carbohydrates_g': r'Carbohydrates.*?(\d+\.?\d*)\s*g',
    'sugar_g': r'Total Sugar.*?(\d+\.?\d*)\s*g',
    'fiber_g': r'Dietary Fibre.*?(\d+\.?\d*)\s*g',
    'protein_g': r'Protein.*?(\d+\.?\d*)\s*g',
    'total_fat_g': r'Total Fat.*?(\d+\.?\d*)\s*g',
    'saturated_fat_g': r'Saturated Fatty Acids.*?(\d+\.?\d*)\s*g',
    'trans_fat_g': r'Trans Fatty Acids.*?(\d+\.?\d*)\s*g',
    'sodium_mg': r'Sodium.*?(\d+\.?\d*)\s*mg'
}