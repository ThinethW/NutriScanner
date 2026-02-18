import roboflow


from roboflow import Roboflow
from ultralytics import YOLO

rf = Roboflow(api_key="S8QmhjablDkzwhnYiLFJ")
project = rf.workspace("food-detection-model-nb0pz").project("nutrition-label-detector")
version = project.version(3)
dataset = version.download("yolov8")

# Train the model
model = YOLO('yolov8n.pt')
results = model.train(
    data=f'{dataset.location}/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)

print("✅ Training complete!")
print(f"Model saved at: runs/detect/train/weights/best.pt")

