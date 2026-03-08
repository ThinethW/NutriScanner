# ============================================================
# ensemble_detector.py - Python class for PyCharm
# ============================================================
"""
Ensemble Food Detector for Sri Lankan Food Detection
Combines V21 (74.5%) and V24 (71.9%) models for best results

Usage:
    from ensemble_detector import EnsembleFoodDetector
    
    detector = EnsembleFoodDetector([
        "path/to/v21_model.pt",
        "path/to/v24_model.pt"
    ])
    
    # Quick detect
    foods = detector.quick_detect("test_image.jpg")
    print(foods)
    
    # Get detailed results
    results = detector.analyze("test_image.jpg")
"""

import os
import cv2
import numpy as np
from collections import Counter
from ultralytics import YOLO
import matplotlib.pyplot as plt


class EnsembleFoodDetector:
    """
    Ensemble Food Detector combining multiple YOLO models
    Uses model's own class names to avoid mapping errors
    """
    
    def __init__(self, model_paths):
        """
        Initialize the ensemble detector
        
        Args:
            model_paths: List of paths to .pt model files
        """
        self.models = []
        self.model_names = []
        
        print("=" * 60)
        print("🚀 ENSEMBLE FOOD DETECTOR INITIALIZING")
        print("=" * 60)
        
        for i, path in enumerate(model_paths):
            if not os.path.exists(path):
                raise FileNotFoundError(f"Model not found: {path}")
            
            print(f"📥 Loading model {i+1}: {os.path.basename(path)}")
            model = YOLO(path)
            self.models.append(model)
            self.model_names.append(os.path.basename(path))
        
        print(f"\n✅ Loaded {len(self.models)} models successfully!")
        print("=" * 60)
    
    def detect_average(self, image_path, confidence=0.25):
        """
        Average confidence from all models
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold (0-1)
            
        Returns:
            List of dictionaries with class_name and confidence
        """
        all_predictions = []
        
        for i, model in enumerate(self.models):
            results = model(image_path, conf=confidence)[0]
            for box in results.boxes:
                class_id = int(box.cls[0])
                class_name = results.names[class_id]
                conf = float(box.conf[0])
                all_predictions.append({
                    'class_name': class_name,
                    'confidence': conf,
                    'model': i
                })
        
        # Group by class name and average confidence
        class_groups = {}
        for pred in all_predictions:
            key = pred['class_name']
            if key not in class_groups:
                class_groups[key] = []
            class_groups[key].append(pred['confidence'])
        
        # Calculate averages
        results = []
        for class_name, confs in class_groups.items():
            avg_conf = np.mean(confs)
            if avg_conf >= confidence:
                results.append({
                    'class_name': class_name,
                    'confidence': round(avg_conf, 3),
                    'method': 'average'
                })
        
        return results
    
    def detect_voting(self, image_path, min_votes=2, confidence=0.25):
        """
        Voting method - food must be detected by min_votes models
        
        Args:
            image_path: Path to image file
            min_votes: Minimum number of models that must agree
            confidence: Confidence threshold
            
        Returns:
            List of dictionaries with class_name and votes
        """
        all_votes = []
        
        for model in self.models:
            results = model(image_path, conf=confidence)[0]
            for box in results.boxes:
                class_name = results.names[int(box.cls[0])]
                all_votes.append(class_name)
        
        # Count votes
        vote_count = Counter(all_votes)
        
        # Keep foods with enough votes
        results = []
        for class_name, votes in vote_count.items():
            if votes >= min_votes:
                results.append({
                    'class_name': class_name,
                    'votes': votes,
                    'method': 'voting'
                })
        
        return results
    
    def quick_detect(self, image_path, confidence=0.25):
        """
        Simple detection - returns just food names
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold
            
        Returns:
            List of food names
        """
        results = self.detect_average(image_path, confidence)
        return [r['class_name'] for r in results]
    
    def analyze(self, image_path, confidence=0.25):
        """
        Complete analysis with all methods
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold
            
        Returns:
            Dictionary with all detection results
        """
        results = {}
        
        # Individual model results
        results['individual'] = []
        for i, model in enumerate(self.models):
            model_results = model(image_path, conf=confidence)[0]
            foods = [model_results.names[int(box.cls[0])] for box in model_results.boxes]
            results['individual'].append({
                'model': self.model_names[i],
                'foods': foods
            })
        
        # Ensemble methods
        results['average'] = self.detect_average(image_path, confidence)
        results['voting_2'] = self.detect_voting(image_path, min_votes=2, confidence=confidence)
        results['voting_3'] = self.detect_voting(image_path, min_votes=3, confidence=confidence)
        results['quick'] = self.quick_detect(image_path, confidence)
        
        return results
    
    def debug_detection(self, image_path, confidence=0.25):
        """
        Debug function to see detailed model outputs
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold
        """
        print("\n" + "=" * 50)
        print(f"🔍 DEBUG - Image: {os.path.basename(image_path)}")
        print("=" * 50)
        
        for i, model in enumerate(self.models):
            results = model(image_path, conf=confidence)[0]
            print(f"\n📊 Model {i+1} ({self.model_names[i]}):")
            print("-" * 40)
            
            if len(results.boxes) == 0:
                print("   No foods detected")
            else:
                for box in results.boxes:
                    class_id = int(box.cls[0])
                    class_name = results.names[class_id]
                    confidence_score = float(box.conf[0])
                    print(f"   • {class_name}: {confidence_score:.3f}")
        
        print("\n" + "=" * 50)
    
    def show_detection(self, image_path, confidence=0.25, save_path=None):
        """
        Show image with detection overlays
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold
            save_path: Optional path to save the output image
        """
        # Get detection from first model (or you can use ensemble)
        results = self.models[0](image_path, conf=confidence)[0]
        
        # Get image with detections
        img_with_boxes = results.plot()
        img_rgb = cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB)
        
        # Display
        plt.figure(figsize=(12, 8))
        plt.imshow(img_rgb)
        plt.axis('off')
        plt.title(f"Detected Foods - {os.path.basename(image_path)}")
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
            print(f"✅ Saved to: {save_path}")
        
        plt.show()
        
        # Print detected foods
        foods = self.quick_detect(image_path, confidence)
        print(f"\n✅ Detected: {foods}")
    
    def batch_detect(self, image_folder, confidence=0.25):
        """
        Detect foods in all images in a folder
        
        Args:
            image_folder: Path to folder containing images
            confidence: Confidence threshold
            
        Returns:
            Dictionary with results for each image
        """
        results = {}
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
        image_files = []
        
        for file in os.listdir(image_folder):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(image_folder, file))
        
        print(f"📸 Found {len(image_files)} images to process")
        
        # Process each image
        for img_path in image_files:
            foods = self.quick_detect(img_path, confidence)
            results[os.path.basename(img_path)] = foods
            print(f"   {os.path.basename(img_path)}: {foods}")
        
        return results


# ============================================================
# EXAMPLE USAGE
# ============================================================
if __name__ == "__main__":
    # Example paths - UPDATE THESE TO YOUR ACTUAL PATHS
    model_paths = [
        r"srilankan_food_model_v21_74.5.pt",
        r"srilankan_food_model_v24_71.9.pt"
    ]
    
    # Create detector
    detector = EnsembleFoodDetector(model_paths)
    
    # Test on a single image
    test_image = r"image1.jpg"
    
    if os.path.exists(test_image):
        # Quick detection
        foods = detector.quick_detect(test_image)
        print(f"\n✅ Quick detect: {foods}")
        
        # Detailed analysis
        results = detector.analyze(test_image)
        print(f"\n📊 Detailed results: {results}")
        
        # Debug mode
        detector.debug_detection(test_image)
        
        # Show image with boxes
        detector.show_detection(test_image)
    else:
        print(f"⚠️ Test image not found: {test_image}")
        print("Please update the test_image path")