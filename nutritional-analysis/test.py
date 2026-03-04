from ultralytics import YOLO
import cv2

# Load your trained model
model = YOLO('runs/detect/train/weights/best.pt')

# Test on an image (put your test image path here)
image_path = 'img.png'  # Replace with actual image
results = model.predict(image_path, conf=0.4, save=True)

# Show where result is saved
print(f"Result saved to: runs/detect/predict/")

# Get bounding box and crop nutrition label
for result in results:
    if len(result.boxes) > 0:
        box = result.boxes[0]
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        img = cv2.imread(image_path)
        cropped = img[y1:y2, x1:x2]
        cv2.imwrite('cropped_nutrition_label.jpg', cropped)
        print("✅ Cropped nutrition label saved!")