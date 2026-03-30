# smart_food_detector.py
# ============================================================
# 3-MODEL SMART ENSEMBLE WITH VOTING SYSTEM + FOOD CHECK
# ============================================================

import os
import cv2
import json
import datetime
from collections import Counter
from ultralytics import YOLO
import torch
from torchvision import transforms, models
from PIL import Image
import matplotlib.pyplot as plt

class SmartFoodDetector:
    """Integrated 3-model smart ensemble detector with food/non-food check."""

    def __init__(self, v21_path, v24_path, v25_path):
        # Model paths
        self.model_paths = {'V21': v21_path, 'V24': v24_path, 'V25': v25_path}

        # Load ensemble
        self.ensemble = self.ThreeModelEnsemble(v21_path, v24_path, v25_path)

        # Load food/non-food classifier
        self.food_classifier = self.FoodPlateClassifier()

        print("\nIntegrated Food Detector ready!")

    # ============================================================
    # PRETRAINED FOOD/NON-FOOD CLASSIFIER
    # ============================================================
    class FoodPlateClassifier:
        """Checks if an image contains food using pretrained ResNet18 (ImageNet weights)"""
        def __init__(self):
            print("Loading pretrained image classifier...")
            self.model = models.resnet18(pretrained=True)
            self.model.eval()

            # Common food-related words
            self.food_classes = [
                'pizza', 'cheeseburger', 'hotdog', 'burrito', 'taco', 'sandwich',
                'bagel', 'croissant', 'doughnut', 'pretzel', 'pancake', 'waffle',
                'omelet', 'custard', 'ice cream', 'cake', 'cupcake', 'cookie',
                'chocolate', 'pie', 'bread', 'loaf', 'banana', 'apple', 'orange',
                'strawberry', 'grape', 'pineapple', 'mushroom', 'broccoli', 'carrot',
                'cucumber', 'lettuce', 'tomato', 'potato', 'rice', 'pasta', 'soup',
                'salad', 'curry', 'dish', 'meal', 'plate', 'dinner', 'lunch',
                'breakfast', 'food', 'snack', 'dessert', 'fruit', 'vegetable'
            ]

            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
            ])
            print("Pretrained classifier ready!")

        def is_food_image(self, image_path, verbose=False):
            try:
                img = Image.open(image_path).convert('RGB')
                img_tensor = self.transform(img).unsqueeze(0)
                with torch.no_grad():
                    outputs = self.model(img_tensor)
                    probs = torch.softmax(outputs, dim=1)

                top_probs, top_indices = torch.topk(probs, 10)

                import urllib.request
                url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
                try:
                    imagenet_labels = json.load(urllib.request.urlopen(url))
                except:
                    imagenet_labels = [f"class_{i}" for i in range(1000)]

                for i in range(10):
                    class_idx = top_indices[0][i].item()
                    class_name = imagenet_labels[class_idx].lower()
                    confidence = top_probs[0][i].item()
                    if verbose:
                        print(f"   [Classifier] {class_name}: {confidence:.3f}")
                    for food_word in self.food_classes:
                        if food_word in class_name:
                            if verbose:
                                print(f"[Classifier] Found food-related class: {class_name}")
                            return True
                return False
            except Exception as e:
                print(f"Error in food detection: {e}")
                return False

    # ============================================================
    # 3-MODEL SMART ENSEMBLE WITH VOTING
    # ============================================================
    class ThreeModelEnsemble:
        def __init__(self, v21_path, v24_path, v25_path):
            print("="*60)
            print("LOADING 3-MODEL SMART ENSEMBLE")
            print("="*60)

            self.v21 = YOLO(v21_path)
            self.v24 = YOLO(v24_path)
            self.v25 = YOLO(v25_path)

            self.specific_foods = [
                'donut', 'eclair', 'cake', 'brownie', 'pastry',
                'cutlets', 'roll',
                'cream bun', 'crocodile bun', 'fish bun',
                'sausage hotdog',
                'kiribath', 'kottu', 'hoppers', 'string hoppers', 'wade',
                'pittu', 'coconut roti', 'watalappam', 'lunu sambol', 'pol sambol',
                'papadam', 'gotukola mallum', 'moringa curry'
            ]

            self.obsolete_categories = [
                'fried filled', 'baked filled', 'baked sweet bun', 'sweets'
            ]

            print("\nAll 3 models loaded successfully!")
            print(f"   V21: 75.5% mAP50")
            print(f"   V24: 70.9% mAP50")
            print(f"   V25: 70.5% mAP50")
            print(f"\nStrategy:")
            print(f"   - SPECIFIC FOODS: Only from V25 (no voting)")
            print(f"   - OTHER FOODS: Need 2/3 models to agree (voting)")

        # ---------- Detection Logic ----------
        def detect(self, image_path, confidence=0.25, verbose=True):
            v21_results = self.v21(image_path, conf=confidence)[0]
            v24_results = self.v24(image_path, conf=confidence)[0]
            v25_results = self.v25(image_path, conf=confidence)[0]

            v21_foods = [v21_results.names[int(box.cls[0])].lower() for box in v21_results.boxes]
            v24_foods = [v24_results.names[int(box.cls[0])].lower() for box in v24_results.boxes]
            v25_foods = [v25_results.names[int(box.cls[0])].lower() for box in v25_results.boxes]

            v21_foods_unique = list(set(v21_foods))
            v24_foods_unique = list(set(v24_foods))
            v25_foods_unique = list(set(v25_foods))

            final_foods = []

            specific_detected = []
            for food in v25_foods_unique:
                if food in self.specific_foods:
                    specific_detected.append(food)
                    final_foods.append(food)
                    if verbose:
                        print(f"SPECIFIC ({food}): V25 only")

            all_foods = v21_foods_unique + v24_foods_unique + v25_foods_unique
            all_foods = [f for f in all_foods if f not in self.obsolete_categories]
            all_foods = [f for f in all_foods if f not in specific_detected]

            vote_count = Counter()
            for food in set(all_foods):
                votes = (food in v21_foods_unique) + (food in v24_foods_unique) + (food in v25_foods_unique)
                vote_count[food] = votes

            for food, votes in vote_count.items():
                if votes >= 2:
                    final_foods.append(food)
                    if verbose:
                        print(f"VOTED ({food}): {votes}/3 models agreed")

            if verbose:
                single_vote_foods = [f for f, v in vote_count.items() if v == 1 and f not in final_foods]
                if single_vote_foods:
                    print(f"SINGLE VOTE (ignored): {single_vote_foods}")
                print(f"\nFINAL DETECTION: {list(set(final_foods))}")

            return list(set(final_foods))

        def detect_with_details(self, image_path, confidence=0.25):
            v21_results = self.v21(image_path, conf=confidence)[0]
            v21_foods = [v21_results.names[int(box.cls[0])] for box in v21_results.boxes]

            v24_results = self.v24(image_path, conf=confidence)[0]
            v24_foods = [v24_results.names[int(box.cls[0])] for box in v24_results.boxes]

            v25_results = self.v25(image_path, conf=confidence)[0]
            v25_foods = [v25_results.names[int(box.cls[0])] for box in v25_results.boxes]

            final_foods = self.detect(image_path, confidence)

            return {'v21': v21_foods, 'v24': v24_foods, 'v25': v25_foods, 'ensemble': final_foods}

        def show_detection(self, image_path, confidence=0.25):
            foods = self.detect(image_path, confidence, verbose=False)
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(12, 8))
            plt.imshow(img)
            plt.axis('off')
            plt.title(f"Detected: {', '.join(foods) if foods else 'No foods'}")
            plt.show()
            return foods

    # ============================================================
    # INTEGRATED DETECTOR FUNCTIONS
    # ============================================================
    def detect(self, image_path, confidence=0.25):
        if not self.food_classifier.is_food_image(image_path):
            print(f"Image '{os.path.basename(image_path)}' does not appear to be food. Skipping.")
            return []
        return self.ensemble.detect(image_path, confidence)

    def detect_with_details(self, image_path, confidence=0.25):
        if not self.food_classifier.is_food_image(image_path, verbose=True):
            print(f"Image '{os.path.basename(image_path)}' does not appear to be food. Skipping.")
            return {'v21': [], 'v24': [], 'v25': [], 'ensemble': []}
        return self.ensemble.detect_with_details(image_path, confidence)

    def show_detection(self, image_path, confidence=0.25):
        if not self.food_classifier.is_food_image(image_path):
            print(f"Skipping display: '{os.path.basename(image_path)}' is not food.")
            return []
        return self.ensemble.show_detection(image_path, confidence)