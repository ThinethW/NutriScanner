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

