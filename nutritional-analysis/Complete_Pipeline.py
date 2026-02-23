from ultralytics import YOLO
from paddleocr import PaddleOCR
import cv2
import re
import json

# Load models
yolo_model = YOLO('runs/detect/train/weights/best.pt')
ocr = PaddleOCR(use_angle_cls=False, lang='en', show_log=False)


def detect_and_crop_label(image_path):
    """Step 1: Detect nutrition label and crop it"""
    results = yolo_model.predict(image_path, conf=0.4, verbose=False)

    if len(results[0].boxes) == 0:
        return None, "No nutrition label detected"

    # Get first detection
    box = results[0].boxes[0]
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

    # Crop label
    img = cv2.imread(image_path)
    cropped = img[y1:y2, x1:x2]

    # Save cropped image
    cv2.imwrite('temp_cropped_label.jpg', cropped)
    return 'temp_cropped_label.jpg', None


def extract_text_from_label(label_image_path):
    """Step 2: Extract text using OCR"""
    result = ocr.ocr(label_image_path, cls=False)

    if not result or not result[0]:
        return None, "OCR failed to extract text"

    # Combine all text lines
    text_lines = [line[1][0] for line in result[0]]
    full_text = ' '.join(text_lines)

    return full_text, None


def parse_nutrition_data(ocr_text):
    """Step 3: Parse nutrition values from text"""
    nutrition = {}

    # Serving size
    serving_match = re.search(r'Serving size.*?(\d+\.?\d*)\s*g', ocr_text, re.IGNORECASE)
    if serving_match:
        nutrition['serving_size_g'] = float(serving_match.group(1))

    # Servings per pack
    servings_match = re.search(r'servings per pack.*?(\d+\.?\d*)', ocr_text, re.IGNORECASE)
    if servings_match:
        nutrition['servings_per_pack'] = float(servings_match.group(1))

    # Energy
    energy_kj = re.search(r'Energy.*?(\d+)\s*kJ.*?(\d+)\s*kcal', ocr_text, re.IGNORECASE | re.DOTALL)
    if energy_kj:
        nutrition['energy_kj_per_100g'] = int(energy_kj.group(1))
        nutrition['energy_kcal_per_100g'] = int(energy_kj.group(2))

    # Nutrients
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


def scan_nutrition_label(image_path):
    """
    Complete pipeline: Image → Detection → OCR → Parsed Data
    """
    print(f"Processing: {image_path}")
    print("-" * 50)

    # Step 1: Detect and crop
    print("Step 1: Detecting nutrition label...")
    cropped_path, error = detect_and_crop_label(image_path)
    if error:
        return {"error": error}
    print("✅ Label detected and cropped")

    # Step 2: OCR
    print("Step 2: Extracting text with OCR...")
    ocr_text, error = extract_text_from_label(cropped_path)
    if error:
        return {"error": error}
    print("✅ Text extracted")

    # Step 3: Parse
    print("Step 3: Parsing nutrition data...")
    nutrition_data = parse_nutrition_data(ocr_text)
    print("✅ Data parsed")

    return nutrition_data


# Test it
if __name__ == "__main__":
    # Replace with your test image
    result = scan_nutrition_label('img.png')

    print("\n" + "=" * 50)
    print("FINAL NUTRITION DATA:")
    print("=" * 50)
    print(json.dumps(result, indent=2))

    # Save to JSON file
    with open('nutrition_output.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\n✅ Saved to nutrition_output.json")