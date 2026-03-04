import pandas as pd
import joblib
import numpy as np

# 1. Configuration & Load Artifacts
disease_columns = [
    "Diabetes_Risk", "Hypertension_Risk", "Heart_Disease_Risk",
    "Obesity_Risk", "Anemia_Risk", "Kidney_Disease_Risk"
]

features = [
    "Age", "Gender", "BMI", "Daily_Calories_kcal", "Carbohydrates_g",
    "Protein_g", "Total_Fat_g", "Saturated_Fat_g", "Trans_Fat_g",
    "Total_Sugar_g", "Added_Sugar_g", "Fiber_g", "Sodium_mg",
    "Potassium_mg", "Calcium_mg", "Iron_mg", "Vitamin_D_IU",
    "Vitamin_B12_mcg", "Physical_Activity_min", "Water_Intake_L"
]

# Load the scaler and all models
scaler = joblib.load("models/scaler.pkl")
models = {disease: joblib.load(f"models\\{disease}_model.pkl") for disease in disease_columns}


# 2. Helper Functions
def calculate_bmi(weight_kg, height_cm):
    return round(weight_kg / ((height_cm / 100) ** 2), 1)


def run_inference(patient_data):
    """
    Takes a raw patient dictionary, processes it, and returns predictions.
    """
    # Auto-calculate BMI if not provided or to ensure accuracy
    patient_data["BMI"] = calculate_bmi(patient_data["Height_cm"], patient_data["Weight_kg"])

    # Convert to DataFrame in the correct feature order
    input_df = pd.DataFrame([patient_data])[features]

    # Scale features
    input_scaled = scaler.transform(input_df)

    # Predict for each disease
    results = {}
    for disease, model in models.items():
        pred = model.predict(input_scaled)[0]
        prob = model.predict_proba(input_scaled)[0][1]  # Probability of "High Risk"
        results[disease] = {
            "Label": "High Risk" if pred == 1 else "Low Risk",
            "Confidence": f"{prob:.2%}"
        }
    return results


# 3. Example Execution
new_patient = {
    "Age": 52,
    "Gender": 0,  # Male
    "Weight_kg": 95,
    "Height_cm": 175,
    "Daily_Calories_kcal": 3200,
    "Carbohydrates_g": 400,
    "Protein_g": 80,
    "Total_Fat_g": 150,
    "Saturated_Fat_g": 60,
    "Trans_Fat_g": 5,
    "Total_Sugar_g": 150,
    "Added_Sugar_g": 100,
    "Fiber_g": 10,
    "Sodium_mg": 4500,
    "Potassium_mg": 1500,
    "Calcium_mg": 400,
    "Iron_mg": 10,
    "Vitamin_D_IU": 1000,
    "Vitamin_B12_mcg": 1.2,
    "Physical_Activity_min": 10,
    "Water_Intake_L": 1.0
}

predictions = run_inference(new_patient)

print(f"{'Disease':<25} | {'Status':<12} | {'Probability'}")
print("-" * 55)
for disease, data in predictions.items():
    print(f"{disease.replace('_', ' '):<25} | {data['Label']:<12} | {data['Confidence']}")