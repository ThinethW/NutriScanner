# ============================================================
# ensemble_detector.py - Sri Lankan Food Detection Ensemble
# ============================================================
"""
3-Model Smart Ensemble for Sri Lankan Food Detection

This module provides a smart ensemble detector that combines three YOLO models:
- V21: 75.5% mAP50 - Best overall detection
- V24: 70.9% mAP50 - Excellent for vegetable curries
- V25: 70.5% mAP50 - Specific food detection (46 classes)

Usage:
    from ensemble_detector import EnsembleFoodDetector
    
    # Initialize with paths to your models
    detector = EnsembleFoodDetector(
        v21_path="path/to/v21_model.pt",
        v24_path="path/to/v24_model.pt",
        v25_path="path/to/v25_model.pt"
    )
    
    # Detect foods in an image
    foods = detector.detect("image.jpg")
    print(foods)  # ['rice', 'dhal curry', 'chicken curry', ...]
    
    # Get detailed results
    details = detector.detect_with_details("image.jpg")
"""

import os
from collections import Counter
from ultralytics import YOLO
import cv2


class EnsembleFoodDetector:
    """
    Smart Ensemble Food Detector for Sri Lankan Cuisine
    
    Combines three YOLOv8 models with priority and voting system:
    - Specific foods (donut, cake, kiribath, etc.) -> ONLY from V25
    - Other foods -> Need 2 out of 3 models to agree
    - Obsolete categories (fried filled, etc.) -> IGNORED
    """
    
    def __init__(self, v21_path, v24_path, v25_path):
        """
        Initialize the ensemble detector with three models.
        
        Args:
            v21_path: Path to V21 model file (75.5% mAP50)
            v24_path: Path to V24 model file (70.9% mAP50)
            v25_path: Path to V25 model file (70.5% mAP50, 46 classes)
        """
        print("="*60)
        print("🚀 LOADING 3-MODEL SMART ENSEMBLE")
        print("="*60)
        
        # Load models
        self.v21 = YOLO(v21_path)
        self.v24 = YOLO(v24_path)
        self.v25 = YOLO(v25_path)
        
        # ============================================
        # SPECIFIC FOODS (ONLY from V25 - no voting)
        # ============================================
        self.specific_foods = [
            # Sweets & Snacks
            'donut', 'eclair', 'cake', 'brownie', 'pastry',
            'cutlets', 'roll',
            'cream bun', 'crocodile bun', 'fish bun',
            'sausage hotdog',
            # Traditional Foods
            'kiribath', 'kottu', 'hoppers', 'string hoppers', 'wade',
            'pittu', 'coconut roti', 'watalappam', 'lunu sambol', 'pol sambol',
            'papadam', 'gotukola mallum', 'moringa curry'
        ]
        
        # ============================================
        # OBSOLETE CATEGORIES (to be ignored)
        # ============================================
        self.obsolete_categories = [
            'fried filled', 'baked filled', 'baked sweet bun', 'sweets'
        ]
        
        print("\n✅ All 3 models loaded successfully!")
        print(f"   V21: 75.5% mAP50 - Best overall")
        print(f"   V24: 70.9% mAP50 - Excellent for curries")
        print(f"   V25: 70.5% mAP50 - {len(self.specific_foods)} specific foods")
        print("\n🎯 Strategy:")
        print("   - SPECIFIC FOODS: Only from V25 (no voting)")
        print("   - OTHER FOODS: Need 2/3 models to agree")
        print("   - OBSOLETE CATEGORIES: Ignored")
    
    def detect(self, image_path, confidence=0.25):
        """
        Detect foods in an image using smart ensemble.
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold (default: 0.25)
            
        Returns:
            List of detected food names
        """
        # Get detections from all models
        v21_results = self.v21(image_path, conf=confidence)[0]
        v24_results = self.v24(image_path, conf=confidence)[0]
        v25_results = self.v25(image_path, conf=confidence)[0]
        
        # Extract food names
        v21_foods = [v21_results.names[int(box.cls[0])].lower() 
                    for box in v21_results.boxes]
        v24_foods = [v24_results.names[int(box.cls[0])].lower() 
                    for box in v24_results.boxes]
        v25_foods = [v25_results.names[int(box.cls[0])].lower() 
                    for box in v25_results.boxes]
        
        # Remove duplicates in each model
        v21_unique = list(set(v21_foods))
        v24_unique = list(set(v24_foods))
        v25_unique = list(set(v25_foods))
        
        final_foods = []
        
        # RULE 1: SPECIFIC FOODS - ONLY from V25
        for food in v25_unique:
            if food in self.specific_foods:
                final_foods.append(food)
        
        # RULE 2: OTHER FOODS - Need 2/3 models to agree
        # Collect all foods (excluding specific ones already added)
        all_foods = []
        all_foods.extend(v21_unique)
        all_foods.extend(v24_unique)
        all_foods.extend(v25_unique)
        
        # Remove obsolete categories
        all_foods = [f for f in all_foods if f not in self.obsolete_categories]
        # Remove already added specific foods
        all_foods = [f for f in all_foods if f not in final_foods]
        
        # Count votes
        vote_count = Counter()
        for food in set(all_foods):
            votes = 0
            if food in v21_unique:
                votes += 1
            if food in v24_unique:
                votes += 1
            if food in v25_unique:
                votes += 1
            vote_count[food] = votes
        
        # Keep foods with at least 2 votes
        for food, votes in vote_count.items():
            if votes >= 2:
                final_foods.append(food)
        
        return list(set(final_foods))
    
    def detect_with_details(self, image_path, confidence=0.25):
        """
        Detect foods with detailed information.
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold
            
        Returns:
            Dictionary with individual model results and ensemble result
        """
        # Get detections from all models
        v21_results = self.v21(image_path, conf=confidence)[0]
        v24_results = self.v24(image_path, conf=confidence)[0]
        v25_results = self.v25(image_path, conf=confidence)[0]
        
        # Extract food names
        v21_foods = [v21_results.names[int(box.cls[0])] 
                    for box in v21_results.boxes]
        v24_foods = [v24_results.names[int(box.cls[0])] 
                    for box in v24_results.boxes]
        v25_foods = [v25_results.names[int(box.cls[0])] 
                    for box in v25_results.boxes]
        
        # Ensemble result
        ensemble_foods = self.detect(image_path, confidence)
        
        return {
            'v21': v21_foods,
            'v24': v24_foods,
            'v25': v25_foods,
            'ensemble': ensemble_foods
        }
    
    def show_detection(self, image_path, confidence=0.25):
        """
        Show image with detection overlays.
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold
            
        Returns:
            List of detected food names
        """
        foods = self.detect(image_path, confidence)
        
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 8))
        plt.imshow(img)
        plt.axis('off')
        plt.title(f"Detected: {', '.join(foods) if foods else 'No foods'}")
        plt.show()
        
        return foods


# ============================================================
# EXAMPLE USAGE
# ============================================================
if __name__ == "__main__":
    # Initialize detector with model paths
    detector = EnsembleFoodDetector(
        v21_path="models/srilankan_food_model_v21_74.5.pt",
        v24_path="models/srilankan_food_model_v24_71.9.pt",
        v25_path="models/srilankan_food_model_v25_70.5.pt"
    )
    
    # Test on an image
    test_image = "test_food.jpg"
    if os.path.exists(test_image):
        # Simple detection
        foods = detector.detect(test_image)
        print(f"\n🍛 Detected foods: {foods}")
        
        # Detailed detection
        details = detector.detect_with_details(test_image)
        print(f"\n📊 Details:")
        print(f"   V21: {details['v21']}")
        print(f"   V24: {details['v24']}")
        print(f"   V25: {details['v25']}")
        print(f"   ✅ Final: {details['ensemble']}")
        
        # Show image with boxes
        detector.show_detection(test_image)