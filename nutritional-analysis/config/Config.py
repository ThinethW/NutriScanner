"""Configuration for NutriScanner"""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Model paths
YOLO_MODEL_PATH = MODELS_DIR / "nutrition_label_detector" / "best.pt"
FOOD_DATABASE_PATH = DATA_DIR / "traditional food list.csv"

# Settings
YOLO_CONFIDENCE = 0.4
OCR_LANG = 'en'

# Create directories
OUTPUTS_DIR.mkdir(exist_ok=True)