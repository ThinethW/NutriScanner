# Nutri Scanner: Personalized Nutrition Tracking and Health Risk Prediction

Nutri Scanner is an AI-powered health and nutrition management platform designed to address the unique dietary challenges of the Sri Lankan context. By utilizing advanced Computer Vision (CV), Optical Character Recognition (OCR), and Machine Learning (ML), it empowers users to interpret complex, multilingual food labels and analyze traditional homemade meals to make informed, healthy choices.



## Key Features

* **Multilingual Label Analysis**: Uses high-accuracy OCR to extract and interpret printed nutritional information from bilingual (Sinhala and English) food labels.
* **Homemade Meal Scanning**: Employs Computer Vision to classify and analyze plated Sri Lankan meals (e.g., rice and curry, dhal curry) for calorie and nutrient estimation.
* **Health Risk Prediction**: Leverages machine learning models (XGBoost) to predict personalized risks for conditions such as **Type 2 Diabetes, Hypertension, Obesity, and Cardiovascular Disease**.
* **Personalized Recommendations**: Generates actionable dietary interventions based on specific nutrient triggers (e.g., high Sodium or low Fiber).
* **Localized Nutrition Database**: Integrates data from local manufacturers with canonical databases for accurate nutrient standardization.



## Technical Architecture

The system operates through four core automated processes:

1.  **Detection**: Capture of food label or meal plate images with automatic enhancement.
2.  **Normalization**: Text parsing via Named Entity Recognition (NER) and mapping to standardized food ontologies.
3.  **Analysis**: Caloric breakdown and benchmarking against FAO/WHO and Sri Lankan Recommended Dietary Allowances (RDAs).
4.  **Prediction**: Risk scoring and recommendation generation based on cumulative dietary patterns.





##  Model Training Performance

The models utilize optimized gradient boosting with anti-overfitting measures (L1/L2 regularization) and balanced weight strategies.

| Target Disease | Train Acc | Test Acc | Gap |
| :--- | :--- | :--- | :--- |
| **Diabetes Risk** | 0.998 | 0.998 | 0.000 |
| **Hypertension Risk** | 0.999 | 1.000 | -0.001 |
| **Heart Disease Risk** | 1.000 | 1.000 | 0.000 |
| **Obesity Risk** | 0.999 | 0.999 | 0.001 |
| **Anemia Risk** | 1.000 | 1.000 | 0.000 |
| **Kidney Disease Risk** | 1.000 | 1.000 | 0.000 |


##  Recommendation Logic

The system generates actionable medical advice when a risk is detected. Examples include:

* **Diabetes**: Reducing added sugars (<25g/day) and increasing fiber intake.
* **Hypertension**: Lowering Sodium intake (<1500mg/day) and increasing Potassium.
* **Heart Health**: Swapping saturated fats for Omega-3 fatty acids.



-