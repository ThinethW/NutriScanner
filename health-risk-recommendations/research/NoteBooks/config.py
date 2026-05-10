# config.py
# ============================================================
# HEALTH RISK PREDICTOR - CONFIGURATION FILE
# ============================================================

import os

# ============ PATHS ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
PLOT_DIR = os.path.join(BASE_DIR, "plots")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

# Create directories if they don't exist
for dir_path in [DATA_DIR, MODEL_DIR, PLOT_DIR, REPORT_DIR]:
    os.makedirs(dir_path, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, "health_nutrition_disease_dataset_12000.xlsx")

# ============ FEATURES ============
DEMOGRAPHIC_FEATURES = ["Age", "Gender", "BMI"]

NUTRITION_FEATURES = [
    "Daily_Calories_kcal",
    "Carbohydrates_g",
    "Protein_g",
    "Total_Fat_g",
    "Saturated_Fat_g",
    "Trans_Fat_g",
    "Total_Sugar_g",
    "Added_Sugar_g",
    "Fiber_g",
    "Sodium_mg",
    "Potassium_mg",
    "Calcium_mg",
    "Iron_mg",
    "Vitamin_D_IU",
    "Vitamin_B12_mcg",
]

LIFESTYLE_FEATURES = ["Physical_Activity_min", "Water_Intake_L"]

ALL_FEATURES = DEMOGRAPHIC_FEATURES + NUTRITION_FEATURES + LIFESTYLE_FEATURES

# ============ TARGETS ============
DISEASE_COLUMNS = [
    "Diabetes_Risk",
    "Hypertension_Risk",
    "Heart_Disease_Risk",
    "Obesity_Risk",
    "Anemia_Risk",
    "Kidney_Disease_Risk",
]

# ============ MODEL PARAMS ============
TEST_SIZE = 0.2
RANDOM_STATE = 42
CROSS_VAL_FOLDS = 5

XGBOOST_PARAMS = {
    "n_estimators": 300,
    "max_depth": 5,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 3,
    "gamma": 0.1,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "eval_metric": "logloss",
    "random_state": RANDOM_STATE,
}

# ============ HEALTHY RANGES (Medical Standards) ============
HEALTHY_RANGES = {
    "BMI": {"min": 18.5, "max": 24.9, "unit": ""},
    "Daily_Calories_kcal": {"min": 1800, "max": 2200, "unit": "kcal"},
    "Carbohydrates_g": {"min": 225, "max": 325, "unit": "g"},
    "Protein_g": {"min": 50, "max": 175, "unit": "g"},
    "Total_Fat_g": {"min": 44, "max": 78, "unit": "g"},
    "Saturated_Fat_g": {"min": 0, "max": 20, "unit": "g"},
    "Trans_Fat_g": {"min": 0, "max": 0, "unit": "g"},
    "Total_Sugar_g": {"min": 0, "max": 50, "unit": "g"},
    "Added_Sugar_g": {"min": 0, "max": 25, "unit": "g"},
    "Fiber_g": {"min": 25, "max": 38, "unit": "g"},
    "Sodium_mg": {"min": 500, "max": 2300, "unit": "mg"},
    "Potassium_mg": {"min": 2600, "max": 4700, "unit": "mg"},
    "Calcium_mg": {"min": 1000, "max": 1300, "unit": "mg"},
    "Iron_mg": {"min": 8, "max": 18, "unit": "mg"},
    "Vitamin_D_IU": {"min": 600, "max": 4000, "unit": "IU"},
    "Vitamin_B12_mcg": {"min": 2.4, "max": 100, "unit": "mcg"},
    "Physical_Activity_min": {"min": 30, "max": 150, "unit": "min"},
    "Water_Intake_L": {"min": 2.0, "max": 3.7, "unit": "L"},
}

# ============ DISEASE-NUTRIENT MAPPING ============
DISEASE_NUTRIENT_MAP = {
    "Diabetes_Risk": {
        "critical": ["Added_Sugar_g", "Total_Sugar_g", "Fiber_g", "Daily_Calories_kcal"],
        "important": ["Carbohydrates_g", "BMI", "Physical_Activity_min", "Trans_Fat_g"],
        "description": "Diabetes is influenced by sugar intake, fiber deficiency, and sedentary lifestyle.",
    },
    "Hypertension_Risk": {
        "critical": ["Sodium_mg", "Potassium_mg", "Physical_Activity_min"],
        "important": ["BMI", "Calcium_mg", "Water_Intake_L", "Saturated_Fat_g"],
        "description": "Hypertension is driven by high sodium, low potassium, and inactivity.",
    },
    "Heart_Disease_Risk": {
        "critical": ["Saturated_Fat_g", "Trans_Fat_g", "Total_Fat_g", "Sodium_mg"],
        "important": ["Fiber_g", "Physical_Activity_min", "BMI", "Daily_Calories_kcal"],
        "description": "Heart disease risk increases with high fat intake and low physical activity.",
    },
    "Obesity_Risk": {
        "critical": ["Daily_Calories_kcal", "BMI", "Physical_Activity_min"],
        "important": ["Total_Fat_g", "Added_Sugar_g", "Fiber_g", "Water_Intake_L"],
        "description": "Obesity is primarily caused by excessive calorie intake and insufficient activity.",
    },
    "Anemia_Risk": {
        "critical": ["Iron_mg", "Vitamin_B12_mcg", "Vitamin_D_IU"],
        "important": ["Protein_g", "Calcium_mg", "Daily_Calories_kcal"],
        "description": "Anemia results from iron, Vitamin B12, and Vitamin D deficiencies.",
    },
    "Kidney_Disease_Risk": {
        "critical": ["Sodium_mg", "Protein_g", "Potassium_mg", "Water_Intake_L"],
        "important": ["Calcium_mg", "BMI", "Physical_Activity_min"],
        "description": "Kidney disease is linked to high sodium, excessive protein, and dehydration.",
    },
}

# ============ RECOMMENDATION TEMPLATES ============
RECOMMENDATIONS = {
    "BMI": {
        "high": "Your BMI is above normal. Focus on calorie deficit and regular exercise.",
        "low": "Your BMI is below normal. Increase nutrient-dense calorie intake.",
        "normal": "Your BMI is within healthy range. Maintain current lifestyle.",
    },
    "Daily_Calories_kcal": {
        "high": "Reduce daily calorie intake. Cut portion sizes and avoid processed foods.",
        "low": "Increase calorie intake with nutrient-rich foods like nuts, avocados, whole grains.",
        "normal": "Calorie intake is appropriate. Maintain balanced diet.",
    },
    "Carbohydrates_g": {
        "high": "Reduce refined carbs. Switch to whole grains, vegetables, and legumes.",
        "low": "Include more complex carbohydrates like oats, brown rice, sweet potatoes.",
        "normal": "Carbohydrate intake is balanced.",
    },
    "Protein_g": {
        "high": "Excessive protein can strain kidneys. Moderate intake from lean sources.",
        "low": "Increase protein with eggs, fish, chicken, lentils, and dairy.",
        "normal": "Protein intake is adequate.",
    },
    "Total_Fat_g": {
        "high": "Reduce total fat. Avoid fried foods, use olive oil instead of butter.",
        "low": "Include healthy fats from nuts, seeds, avocado, and fatty fish.",
        "normal": "Fat intake is within healthy limits.",
    },
    "Saturated_Fat_g": {
        "high": "Cut saturated fat. Reduce red meat, cheese, and butter consumption.",
        "low": "Saturated fat is well controlled.",
        "normal": "Saturated fat intake is appropriate.",
    },
    "Trans_Fat_g": {
        "high": "ELIMINATE trans fats immediately. Avoid processed/packaged foods and margarine.",
        "low": "Trans fat intake is minimal. Good job!",
        "normal": "Keep avoiding trans fats.",
    },
    "Total_Sugar_g": {
        "high": "Reduce sugar intake. Avoid sugary drinks, candies, and desserts.",
        "low": "Sugar intake is well managed.",
        "normal": "Sugar consumption is within limits.",
    },
    "Added_Sugar_g": {
        "high": "Cut added sugars drastically. Read food labels and avoid hidden sugars.",
        "low": "Added sugar intake is healthy.",
        "normal": "Added sugar is within recommended limits.",
    },
    "Fiber_g": {
        "high": "Fiber intake is good but don't overdo it to avoid digestive issues.",
        "low": "INCREASE fiber urgently. Eat more vegetables, fruits, whole grains, and beans.",
        "normal": "Excellent fiber intake! Keep it up.",
    },
    "Sodium_mg": {
        "high": "REDUCE sodium immediately. Avoid processed foods, canned soups, and excess salt.",
        "low": "Sodium is well controlled.",
        "normal": "Sodium intake is healthy.",
    },
    "Potassium_mg": {
        "high": "Monitor potassium if you have kidney issues.",
        "low": "INCREASE potassium. Eat more bananas, spinach, sweet potatoes, and avocados.",
        "normal": "Potassium intake is adequate.",
    },
    "Calcium_mg": {
        "high": "Don't exceed calcium limits to avoid kidney stones.",
        "low": "INCREASE calcium. Add milk, yogurt, cheese, and leafy greens to diet.",
        "normal": "Calcium intake is sufficient.",
    },
    "Iron_mg": {
        "high": "Monitor iron levels. Excessive iron can damage organs.",
        "low": "INCREASE iron intake. Eat red meat, spinach, lentils, and fortified cereals.",
        "normal": "Iron intake is adequate.",
    },
    "Vitamin_D_IU": {
        "high": "Very high Vitamin D can be toxic. Consult doctor.",
        "low": "INCREASE Vitamin D. Get sunlight, eat fatty fish, and consider supplements.",
        "normal": "Vitamin D levels are good.",
    },
    "Vitamin_B12_mcg": {
        "high": "B12 excess is usually harmless but consult doctor if supplementing heavily.",
        "low": "INCREASE Vitamin B12. Eat eggs, dairy, fish, and consider supplements.",
        "normal": "Vitamin B12 intake is sufficient.",
    },
    "Physical_Activity_min": {
        "high": "Great activity level! Ensure proper rest and recovery.",
        "low": "INCREASE physical activity. Aim for at least 30 min daily walking/exercise.",
        "normal": "Physical activity level is good.",
    },
    "Water_Intake_L": {
        "high": "Good hydration! Don't overhydrate though.",
        "low": "DRINK MORE WATER. Aim for at least 2-3 liters daily.",
        "normal": "Hydration level is appropriate.",
    },
}