from paddleocr import PaddleOCR

# Initialize with simpler settings
ocr = PaddleOCR(use_angle_cls=False, lang='en', show_log=False)

# Read the cropped nutrition label
result = ocr.ocr('cropped_nutrition_label.jpg', cls=False)

# Print detected text
if result and result[0]:
    for line in result[0]:
        text = line[1][0]
        confidence = line[1][1]
        print(f"{text} (confidence: {confidence:.2f})")
else:
    print("No text detected")