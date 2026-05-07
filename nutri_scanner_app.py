# ============================================================
# NUTRISCANNER - PROFESSIONAL HEALTH AI PLATFORM
# INTEGRATED WITH ML MODELS
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import joblib
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import bcrypt
import json
from pathlib import Path

# ── Resolve the project root at module level (works on Windows + Streamlit) ──
_UI_DIR = Path(__file__).resolve().parent
if str(_UI_DIR) not in sys.path:
    sys.path.insert(0, str(_UI_DIR))
os.chdir(str(_UI_DIR))

# ── Import database layer ──────────────────────────────────────────────────
from nutri_database import (
    init_db, create_user, login_user, get_user_by_id, update_user_profile,
    log_food, delete_food_log, get_food_logs_for_day,
    get_daily_summary, get_daily_summary_as_model_input,
    update_daily_activity, save_risk_assessment, get_risk_history,
    get_nutrition_trend, map_comp2_to_log, map_label_to_log, get_db,
)

init_db()

# ============================================================
# INIT SESSION STATE
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_profile = {}
    st.session_state.detected_food_list = []
    st.session_state.auth_page = "login"  # "login" | "register"
    # Food Photo Analyzer session states
    st.session_state.detected_foods = []
    st.session_state.detection_details = []
    st.session_state.detection_done = False
    st.session_state.show_analysis = False
    st.session_state.confirmed_foods = []
if "temp_selected_foods" not in st.session_state:
    st.session_state.temp_selected_foods = []
if "show_manual_correction" not in st.session_state:
    st.session_state.show_manual_correction = False
if "manual_correction_foods" not in st.session_state:
    st.session_state.manual_correction_foods = []
if "corrected_foods" not in st.session_state:
    st.session_state.corrected_foods = []
if "show_corrected_analysis" not in st.session_state:
    st.session_state.show_corrected_analysis = False
# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="NutriScanner Pro | AI Health Intelligence",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://nutriscanner.ai/help',
        'Report a bug': 'https://github.com/nutriscanner/issues',
        'About': "# NutriScanner Pro\nVersion 4.0.0\nAI-Powered Health Intelligence Platform"
    }
)


# ============================================================
# 2. TROPICAL FRUIT CSS THEME
# ============================================================
def apply_modern_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Fraunces:wght@700;800;900&display=swap');

    :root {
        --coral:      #E8553E;
        --amber:      #F4A24A;
        --teal:       #1F9E8E;
        --teal-dark:  #157870;
        --cream:      #FAF7F2;
        --card:       #FFFFFF;
        --border:     #EBE6DD;
        --sidebar-bg: #12201F;
        --sidebar-mid:#1A2E2C;
        --text-dark:  #1A1A1A;
        --text-mid:   #3D3D3D;
        --text-soft:  #6B7280;
        --success-bg: rgba(31,158,142,0.10);
        --warn-bg:    rgba(244,162,74,0.12);
        --danger-bg:  rgba(232,85,62,0.10);
        --shadow-card:0 1px 4px rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.08);
        --shadow-hover:0 8px 36px rgba(232,85,62,0.18), 0 2px 8px rgba(0,0,0,0.06);
        --gradient-main: linear-gradient(135deg, #E8553E 0%, #F4A24A 100%);
        --gradient-teal: linear-gradient(135deg, #1F9E8E 0%, #157870 100%);
    }

    /* ── Page background ── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main {
        font-family: 'DM Sans', sans-serif !important;
        background: var(--cream) !important;
        color: var(--text-dark) !important;
    }

    /* Subtle warm dot-pattern overlay on main */
    [data-testid="stAppViewContainer"] > .main::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: radial-gradient(circle, rgba(232,85,62,0.04) 1px, transparent 1px);
        background-size: 28px 28px;
        pointer-events: none;
        z-index: 0;
    }

    /* ── Sidebar ── */
[data-testid="stSidebar"] {
   background: linear-gradient(180deg, #2A4B4A 0%, #1A3A38 100%) !important;
    border-right: 1px solid rgba(31,158,142,0.3) !important;
    min-width: 270px !important;
    width: 270px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 16px !important; }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }  /* ← CHANGED to bright white */

/* Nav items */
[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.08) !important;  /* ← CHANGED to lighter */
    border: 1px solid rgba(255,255,255,0.25) !important;  /* ← CHANGED to white border */
    border-radius: 10px !important;
    padding: 9px 14px !important;
    margin-bottom: 4px !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(31,158,142,0.25) !important;
    border-color: #FFFFFF !important;  /* ← CHANGED */
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.93rem !important;
    font-weight: 500 !important;
    color: #FFFFFF !important;  /* ← CHANGED to bright white */
    line-height: 1.4 !important;
}
    [data-testid="stSidebar"] .stRadio [role="radio"] {
    border: 2px solid #FFFFFF !important;  /* Make border white for visibility */
    background: transparent !important;
    min-width: 16px !important;
    min-height: 16px !important;
}
    [data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] {
        background: #E8553E !important;
        border-color: #E8553E !important;
        box-shadow: 0 0 0 3px rgba(232,85,62,0.30) !important;
    }
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small { color: #6EADA7 !important; font-size: 0.80rem !important; }

    /* Sidebar brand */
    .sidebar-brand {
        font-family: 'Fraunces', serif !important;
        font-size: 26px; font-weight: 900;
        background: var(--gradient-main);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 26px 0 18px;
        border-bottom: 1px solid rgba(31,158,142,0.22);
        margin-bottom: 20px;
        letter-spacing: -0.5px;
    }

    /* User greeting chip */
    .user-greeting {
        background: rgba(31,158,142,0.12) !important;
        border: 1px solid rgba(31,158,142,0.25) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        margin-bottom: 16px !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        color: #E8F5F4 !important;
        line-height: 1.5 !important;
    }

    /* ── Cards ── */
    .metric-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 22px 20px;
        margin: 6px 0;
        transition: all 0.28s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        box-shadow: var(--shadow-card);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--gradient-main);
        border-radius: 18px 18px 0 0;
        opacity: 0;
        transition: opacity 0.28s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-hover);
        border-color: rgba(232,85,62,0.3);
    }
    .metric-card:hover::before { opacity: 1; }

    .metric-value {
        font-family: 'Fraunces', serif !important;
        font-size: 2.2rem; font-weight: 800;
        background: var(--gradient-main);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin: 6px 0 4px;
    }
    .metric-label {
        color: var(--text-soft) !important;
        font-size: 0.73rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    .metric-delta {
        font-size: 0.78rem; font-weight: 600;
        padding: 3px 10px; border-radius: 20px;
        display: inline-block; margin-top: 8px;
    }
    .delta-positive { background: var(--success-bg); color: #157870 !important; }
    .delta-negative { background: var(--danger-bg);  color: #C04030 !important; }

    /* ── Hero banner ── */
    .hero-banner {
        background: linear-gradient(135deg,
            rgba(232,85,62,0.06) 0%,
            rgba(244,162,74,0.05) 40%,
            rgba(31,158,142,0.08) 100%);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 44px 40px;
        margin: 16px 0 28px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -30px; right: -30px;
        width: 160px; height: 160px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(31,158,142,0.10), transparent 70%);
    }

    /* ── Buttons ── */
    .stButton > button {
        background: var(--gradient-main) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 26px !important;
        font-weight: 700 !important;
        font-size: 0.93rem !important;
        letter-spacing: 0.2px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 3px 14px rgba(232,85,62,0.30) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 7px 24px rgba(232,85,62,0.42) !important;
        filter: brightness(1.04) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: transparent;
        border-bottom: 2px solid var(--border);
        padding-bottom: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        font-size: 0.90rem !important;
        color: var(--text-soft) !important;
        border: none !important;
        transition: all 0.2s !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--gradient-main) !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* ── Typography ── */
    h1 {
        font-family: 'Fraunces', serif !important;
        background: var(--gradient-main) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        letter-spacing: -1px !important;
        line-height: 1.1 !important;
    }
    h2 {
        font-family: 'Fraunces', serif !important;
        color: var(--text-dark) !important;
        -webkit-text-fill-color: var(--text-dark) !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        border-left: 4px solid var(--coral) !important;
        padding-left: 14px !important;
        letter-spacing: -0.5px !important;
    }
    h3 {
        font-family: 'Fraunces', serif !important;
        color: var(--text-dark) !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        -webkit-text-fill-color: var(--text-dark) !important;
    }

    /* ── Risk boxes ── */
    .risk-high {
        background: linear-gradient(135deg, rgba(232,85,62,0.10), rgba(232,85,62,0.04));
        border: 1.5px solid #E8553E;
        border-radius: 14px; padding: 16px 22px; margin: 10px 0;
        color: var(--text-dark) !important;
    }
    .risk-medium {
        background: linear-gradient(135deg, rgba(244,162,74,0.12), rgba(244,162,74,0.04));
        border: 1.5px solid #F4A24A;
        border-radius: 14px; padding: 16px 22px; margin: 10px 0;
        color: var(--text-dark) !important;
    }
    .risk-low {
        background: linear-gradient(135deg, rgba(31,158,142,0.10), rgba(31,158,142,0.04));
        border: 1.5px solid #1F9E8E;
        border-radius: 14px; padding: 16px 22px; margin: 10px 0;
        color: var(--text-dark) !important;
    }
    .risk-high *, .risk-medium *, .risk-low * { color: var(--text-dark) !important; }

    /* ── Footer ── */
    .footer {
        text-align: center; padding: 30px 0; margin-top: 48px;
        border-top: 1px solid var(--border);
        color: var(--text-soft) !important;
        font-size: 0.84rem;
    }
    .footer a { color: var(--teal) !important; text-decoration: none; }

    /* ── Alert text fix ── */
    .stAlert, .stWarning, [data-testid="stAlert"],
    .stAlert p, .stAlert div, .stAlert span,
    .stWarning p, .stWarning div, .stWarning span,
    [data-testid="stAlert"] p, [data-testid="stAlert"] div,
    [data-testid="stAlert"] span {
        color: #1A1A1A !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 7px; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #E8553E, #F4A24A);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-track { background: var(--cream); }

    /* ── Input labels — always black ── */
    .stNumberInput label, .stSelectbox label, .stSlider label,
    .stTextInput label, .stTextArea label, .stRadio label,
    .stCheckbox label, .stMultiSelect label, .stDateInput label,
    .stTimeInput label, .stFileUploader label,
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span,
    div[data-testid="stWidgetLabel"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 500 !important;
    }

    /* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border: none !important;
    background: #FFFFFF !important;
    color: #1A1A1A !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;

}
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0  rgba(31,158,142,0.15) !important;
    }

.stTextInput [data-testid="stTextInputRootElement"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow-card) !important;
    }

    /* ── Plotly charts — black axis text ── */
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .angular text,
    .js-plotly-plot .plotly .radial text,
    .js-plotly-plot .plotly text { fill: #000000 !important; }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: var(--text-dark) !important;
        padding: 14px 18px !important;
    }

    /* ── Metric widget ── */
    [data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: var(--shadow-card);
    }
    [data-testid="stMetricValue"] {
        color: var(--text-dark) !important;
        font-weight: 700 !important;
    }
    /* ULTRA SPECIFIC - LAST RESORT */
.css-1d391kg, .css-1633tjr, .css-1y4p8pa {
    color: #FFFFFF !important;
}
    </style>
    """, unsafe_allow_html=True)


apply_modern_styles()

# ============================================================
# 3. COLOR CONSTANTS
# ============================================================
PASTEQUE = '#E8553E'
ZESTE = '#F4A24A'
LAGOON = '#1F9E8E'
MELON = '#F4A24A'
CARD_BG = '#FFFFFF'
PLOT_BG = '#FAF7F2'
FONT_CLR = '#1A1A1A'
GRID_CLR = '#EBE6DD'
TICK_CLR = '#1A1A1A'

DISEASE_COLUMNS = [
    "Diabetes_Risk", "Hypertension_Risk", "Heart_Disease_Risk",
    "Obesity_Risk", "Anemia_Risk", "Kidney_Disease_Risk"
]

# Exact 19 features all 6 models were trained on (no BMI)
MODEL_FEATURES = [
    "Age", "Gender", "Daily_Calories_kcal", "Carbohydrates_g", "Protein_g",
    "Total_Fat_g", "Saturated_Fat_g", "Trans_Fat_g", "Total_Sugar_g",
    "Added_Sugar_g", "Fiber_g", "Sodium_mg", "Potassium_mg", "Calcium_mg",
    "Iron_mg", "Vitamin_D_IU", "Vitamin_B12_mcg", "Physical_Activity_min",
    "Water_Intake_L"
]

DISEASE_FEATURES = {disease: MODEL_FEATURES for disease in DISEASE_COLUMNS}


# ============================================================
# 4. MODEL LOADING — cached so it only loads once at startup
# ============================================================
@st.cache_resource
def load_models():
    """
    Loads all 6 trained XGBoost .pkl files.
    Place your model files in a folder called 'models/' next to this script.
    """
    MODEL_DIR = Path("models")

    models = {}
    missing = []

    for disease in DISEASE_COLUMNS:
        model_path = MODEL_DIR / f"{disease}_model.pkl"
        if model_path.exists():
            models[disease] = joblib.load(model_path)
        else:
            missing.append(model_path.name)

    return models, missing


models, missing_models = load_models()


# ============================================================
# 5. RULE-BASED HYBRID PREDICTION FUNCTIONS
# ============================================================
def calculate_bmi(weight_kg, height_cm):
    return round(weight_kg / (height_cm / 100) ** 2, 1)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "🟢", "LOW", 0.05
    elif bmi < 25.0:
        return "Normal Weight", "🟢", "LOW", 0.15
    elif bmi < 30.0:
        return "Overweight", "🟡", "MODERATE", 0.50
    elif bmi < 35.0:
        return "Obese Class I", "🔴", "HIGH", 0.78
    elif bmi < 40.0:
        return "Obese Class II", "🔴", "HIGH", 0.90
    else:
        return "Obese Class III", "🔴", "HIGH", 0.98


def combined_hypertension_risk(model_prob, sodium_mg, potassium_mg):
    if sodium_mg > 4000 and potassium_mg < 1500:
        rule_prob = 0.85
    elif sodium_mg > 3000:
        rule_prob = 0.60
    elif sodium_mg < 1500 and potassium_mg > 3000:
        rule_prob = 0.10
    else:
        rule_prob = 0.35
    return round((0.5 * model_prob) + (0.5 * rule_prob), 3)


def combined_anemia_risk(model_prob, iron_mg, b12_mcg):
    if iron_mg < 5 or b12_mcg < 1.0:
        rule_prob = 0.90
    elif iron_mg < 8 or b12_mcg < 2.0:
        rule_prob = 0.60
    elif iron_mg > 15 and b12_mcg > 3.0:
        rule_prob = 0.08
    else:
        rule_prob = 0.30
    return round((0.5 * model_prob) + (0.5 * rule_prob), 3)


def combined_diabetes_risk(model_prob, total_sugar_g, added_sugar_g, bmi):
    if added_sugar_g > 60 or total_sugar_g > 100:
        rule_prob = 0.85
    elif added_sugar_g > 40 or total_sugar_g > 70:
        rule_prob = 0.65
    elif added_sugar_g < 10 and total_sugar_g < 30:
        rule_prob = 0.08
    else:
        rule_prob = 0.35
    if bmi >= 30: rule_prob = min(rule_prob + 0.10, 0.98)
    return round((0.5 * model_prob) + (0.5 * rule_prob), 3)


def combined_heart_risk(model_prob, saturated_fat_g, trans_fat_g, total_fat_g):
    if trans_fat_g > 3.5 or saturated_fat_g > 50:
        rule_prob = 0.88
    elif trans_fat_g > 2.0 or saturated_fat_g > 30:
        rule_prob = 0.62
    elif saturated_fat_g < 15 and trans_fat_g < 1.0:
        rule_prob = 0.10
    else:
        rule_prob = 0.35
    return round((0.5 * model_prob) + (0.5 * rule_prob), 3)


def combined_kidney_risk(model_prob, sodium_mg, protein_g, water_intake_l):
    if sodium_mg > 4500 and protein_g > 130:
        rule_prob = 0.88
    elif sodium_mg > 3500 or protein_g > 110:
        rule_prob = 0.62
    elif water_intake_l < 0.8:
        rule_prob = 0.55
    elif sodium_mg < 1500 and protein_g < 80 and water_intake_l > 2.5:
        rule_prob = 0.08
    else:
        rule_prob = 0.30
    return round((0.5 * model_prob) + (0.5 * rule_prob), 3)


def get_risk_level(prob):
    if prob >= 0.70:
        return "HIGH", "🔴"
    elif prob >= 0.40:
        return "MODERATE", "🟡"
    else:
        return "LOW", "🟢"


def run_prediction(patient_data, models):
    """Run all 6 disease predictions. Returns dict of results and BMI."""
    bmi = calculate_bmi(patient_data["weight_kg"], patient_data["height_cm"])

    predictions = {}

    # Obesity — WHO BMI rule only
    bmi_cat, bmi_icon, bmi_level, ob_prob = bmi_category(bmi)
    predictions["Obesity_Risk"] = {
        "prob": ob_prob, "prob_pct": round(ob_prob * 100, 1),
        "level": bmi_level, "icon": bmi_icon, "label": "Obesity"
    }

    # Other 5 diseases — hybrid model + rule
    for disease in ["Diabetes_Risk", "Hypertension_Risk", "Heart_Disease_Risk", "Anemia_Risk", "Kidney_Disease_Risk"]:
        if disease not in models:
            predictions[disease] = {"prob": 0, "prob_pct": 0, "level": "UNKNOWN", "icon": "⚪",
                                    "label": disease.replace("_Risk", "").replace("_", " ")}
            continue

        features_used = DISEASE_FEATURES[disease]
        p_df = pd.DataFrame([{f: patient_data[f] for f in features_used if f in patient_data}])
        model_prob = models[disease].predict_proba(p_df)[0][1]

        if disease == "Diabetes_Risk":
            final = combined_diabetes_risk(model_prob, patient_data["Total_Sugar_g"], patient_data["Added_Sugar_g"],
                                           bmi)
        elif disease == "Hypertension_Risk":
            final = combined_hypertension_risk(model_prob, patient_data["Sodium_mg"], patient_data["Potassium_mg"])
        elif disease == "Heart_Disease_Risk":
            final = combined_heart_risk(model_prob, patient_data["Saturated_Fat_g"], patient_data["Trans_Fat_g"],
                                        patient_data["Total_Fat_g"])
        elif disease == "Anemia_Risk":
            final = combined_anemia_risk(model_prob, patient_data["Iron_mg"], patient_data["Vitamin_B12_mcg"])
        elif disease == "Kidney_Disease_Risk":
            final = combined_kidney_risk(model_prob, patient_data["Sodium_mg"], patient_data["Protein_g"],
                                         patient_data["Water_Intake_L"])
        else:
            final = model_prob

        level, icon = get_risk_level(final)
        predictions[disease] = {
            "prob": final, "prob_pct": round(final * 100, 1),
            "level": level, "icon": icon,
            "label": disease.replace("_Risk", "").replace("_", " ")
        }

    return predictions, bmi


# ============================================================
# 6. CHART HELPERS
# ============================================================
def create_risk_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 14, 'color': FONT_CLR, 'family': 'Fraunces'}},
        number={'suffix': '%', 'font': {'size': 28, 'color': FONT_CLR, 'family': 'Fraunces'}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': TICK_CLR,
                     'tickfont': {'size': 10, 'color': FONT_CLR}, 'dtick': 25},
            'bar': {'color': PASTEQUE, 'thickness': 0.28},
            'bgcolor': PLOT_BG,
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(31,158,142,0.18)'},
                {'range': [40, 70], 'color': 'rgba(244,162,74,0.18)'},
                {'range': [70, 100], 'color': 'rgba(232,85,62,0.18)'}
            ],
            'threshold': {
                'line': {'color': FONT_CLR, 'width': 2},
                'thickness': 0.75, 'value': 70
            }
        }
    ))
    fig.update_layout(
        height=220, margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor=CARD_BG, font={'color': FONT_CLR, 'family': 'DM Sans'}
    )
    return fig


def create_nutrition_pie_chart(data):
    colors = [LAGOON, ZESTE, PASTEQUE, '#A78BFA']
    fig = px.pie(data, values='Amount', names='Nutrient', color='Nutrient',
                 color_discrete_sequence=colors,
                 hole=0.52, opacity=0.95)
    fig.update_traces(
        textposition='outside', textinfo='percent+label',
        marker=dict(line=dict(color=CARD_BG, width=3)),
        hovertemplate='<b>%{label}</b><br>%{value:.1f}g (%{percent})<extra></extra>',
        pull=[0.03, 0, 0.03, 0]
    )
    fig.update_layout(
        height=320, paper_bgcolor=CARD_BG,
        font={'color': FONT_CLR, 'family': 'DM Sans', 'size': 12},
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.18, xanchor='center', x=0.5,
                    font=dict(size=11, color=FONT_CLR)),
        margin=dict(l=20, r=20, t=20, b=60),
        annotations=[dict(text='Macros', x=0.5, y=0.5, font_size=13,
                          font_color=FONT_CLR, showarrow=False)]
    )
    return fig


def create_trend_chart(dates, values, title, color=PASTEQUE):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    fig = go.Figure()
    # Filled area
    fig.add_trace(go.Scatter(
        x=dates, y=values, mode='lines',
        line=dict(color=color, width=0),
        fill='tozeroy', fillcolor=f'rgba({r},{g},{b},0.10)',
        showlegend=False, hoverinfo='skip'
    ))
    # Line + markers
    fig.add_trace(go.Scatter(
        x=dates, y=values, mode='lines+markers', name=title,
        line=dict(color=color, width=2.5, shape='spline'),
        marker=dict(size=7, color=CARD_BG, line=dict(color=color, width=2.5)),
        hovertemplate='<b>%{x}</b><br>%{y:.0f}<extra></extra>'
    ))
    fig.update_layout(
        height=280, showlegend=False,
        paper_bgcolor=CARD_BG, plot_bgcolor=PLOT_BG,
        font={'color': FONT_CLR, 'family': 'DM Sans'},
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11, color=FONT_CLR)),
        yaxis=dict(showgrid=True, gridcolor=GRID_CLR, zeroline=False,
                   tickfont=dict(size=11, color=FONT_CLR)),
        margin=dict(l=50, r=20, t=20, b=40),
        hovermode='x unified'
    )
    return fig


def create_risk_bar_chart(diseases, probabilities):
    colors = [PASTEQUE if p >= 70 else ZESTE if p >= 40 else LAGOON for p in probabilities]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=diseases, x=probabilities, orientation='h',
        marker=dict(
            color=colors,
            line=dict(color=CARD_BG, width=0),
            cornerradius=6
        ),
        text=[f'{p:.1f}%' for p in probabilities],
        textposition='outside',
        textfont=dict(size=12, color=FONT_CLR, family='DM Sans'),
        hovertemplate='<b>%{y}</b><br>Risk: %{x:.1f}%<extra></extra>'
    ))
    fig.update_layout(
        height=380, showlegend=False,
        paper_bgcolor=CARD_BG, plot_bgcolor=PLOT_BG,
        font={'color': FONT_CLR, 'family': 'DM Sans'},
        xaxis=dict(range=[0, 115], showgrid=True, gridcolor=GRID_CLR,
                   ticksuffix='%', tickfont=dict(size=11, color=FONT_CLR)),
        yaxis=dict(showgrid=False, tickfont=dict(size=12, color=FONT_CLR)),
        margin=dict(l=140, r=70, t=20, b=40)
    )
    return fig


def create_radar_chart(labels, values, title):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=labels + [labels[0]],
        fill='toself',
        line=dict(color=PASTEQUE, width=2.5),
        fillcolor='rgba(232, 85, 62, 0.15)',
        name=title,
        hovertemplate='<b>%{theta}</b><br>Score: %{r}<extra></extra>'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(color=FONT_CLR, size=10),
                            gridcolor=GRID_CLR),
            angularaxis=dict(tickfont=dict(color=FONT_CLR, size=12))
        ),
        showlegend=False, height=320,
        paper_bgcolor=CARD_BG,
        font={'color': FONT_CLR, 'family': 'DM Sans'},
        margin=dict(l=40, r=40, t=30, b=30)
    )
    return fig


# ============================================================
# COMPONENT 2 — Nutrition DB Search (Estimation_Search)
# ============================================================
@st.cache_resource
def load_estimation_search():
    """
    Finds and loads Estimation_Search.py, caches the result.
    Returns (get_item_values_fn, error_string_or_None).
    """
    import importlib.util, traceback

    # Common expected locations
    candidates = [
        _UI_DIR / "data_extraction_estimation" / "Estimation_Search.py",
    ]
    # Add any rglob found
    for found in _UI_DIR.rglob("Estimation_Search.py"):
        if found not in candidates:
            candidates.append(found)

    for es_path in candidates:
        if not es_path.exists():
            continue

        inferred_proj_dir = Path(es_path.parent.parent)
        try:
            spec = importlib.util.spec_from_file_location("Estimation_Search", es_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Resolve absolute CSV paths
            def _find_csv(filename: str) -> str:
                candidates = [
                    _UI_DIR / filename.replace("/", os.sep),
                    inferred_proj_dir / filename.replace("/", os.sep),
                ]
                for c in candidates:
                    if c.exists():
                        return str(c)
                fname = Path(filename).name
                for found in _UI_DIR.rglob(fname):
                    return str(found)
                return filename

            abs_freq = _find_csv("FrequentedData.csv")
            abs_ird = _find_csv("module_2_datasets/IRD.csv")
            abs_usda = _find_csv("module_2_datasets/USDA.csv")

            # Patch the module with absolute paths and custom _append_to_frequented
            _orig_get = module.get_item_values
            _orig_hail = module.hail_mary
            _orig_append = module._append_to_frequented
            _abs_csv_files = [
                (abs_freq, True, True),
                (abs_ird, False, True),
                (abs_usda, False, True),
            ]
            _abs_freq_path = abs_freq

            def _patched_append(values: tuple, _p=_abs_freq_path, _orig=_orig_append):
                import csv as _csv
                file_exists = os.path.exists(_p)
                with open(_p, 'a', newline='', encoding='utf-8') as f:
                    writer = _csv.writer(f)
                    if not file_exists or os.path.getsize(_p) == 0:
                        writer.writerow([
                            "description", "calories", "proteins", "fats", "carbohydrates",
                            "sodium", "Magnesium", "calcium", "iron", "zinc",
                            "vitamin A", "vitamin C", "vitamin D", "vitamin E", "vitamin K",
                            "vitamin B1", "vitamin B2", "vitamin B3", "vitamin B6", "vitamin B12",
                            "SFA", "MUFA", "PUFA"
                        ])
                    writer.writerow(list(values))
                with open(_p, newline='', encoding='utf-8') as f:
                    rows = list(_csv.reader(f))
                if not rows: return
                header, data_rows = rows[0], rows[1:]
                seen = {}
                for row in data_rows:
                    if row: seen[row[0].strip().lower()] = row
                with open(_p, 'w', newline='', encoding='utf-8') as f:
                    writer = _csv.writer(f)
                    writer.writerow(header)
                    writer.writerows(seen.values())

            module._append_to_frequented = _patched_append

            def _patched_get_item_values(item_name: str,
                                         _csv_files=_abs_csv_files,
                                         _append=_patched_append,
                                         _hail=_orig_hail) -> tuple:
                import csv as _csv
                best_candidate, best_score = (), 0.0
                for filename, reverse, yoda in _csv_files:
                    if not yoda: continue
                    if not os.path.exists(filename):
                        continue
                    with open(filename, newline='', encoding='utf-8') as f:
                        rows = list(_csv.reader(f))
                    data_rows = rows[1:] if rows and rows[0][0].lower() == 'description' else rows
                    search_order = reversed(data_rows) if reverse else iter(data_rows)
                    for row in search_order:
                        if not row: continue
                        score = module.match_rate(item_name, row[0])
                        if score >= 0.80:
                            values = tuple(row)
                            _append(values)
                            return values
                        if score > best_score and score >= 0.51:
                            best_score = score
                            best_candidate = tuple(row)
                if best_candidate:
                    _append(best_candidate)
                    return best_candidate
                hail_result = _hail(item_name, _csv_files)
                if hail_result:
                    _append(hail_result)
                    return hail_result
                return ()

            return _patched_get_item_values, None

        except Exception as e:
            continue

    return None, f"Estimation_Search.py not found. Searched: {candidates}"


_comp2_search_fn, comp2_error = load_estimation_search()

COMP2_HEADERS = [
    "Description", "Calories", "Proteins (g)", "Fats (g)", "Carbohydrates (g)",
    "Sodium (mg)", "Magnesium (mg)", "Calcium (mg)", "Iron (mg)", "Zinc (mg)",
    "Vitamin A (µg)", "Vitamin C (mg)", "Vitamin D (µg)", "Vitamin E (mg)", "Vitamin K (µg)",
    "Vitamin B1 (mg)", "Vitamin B2 (mg)", "Vitamin B3 (mg)", "Vitamin B6 (mg)", "Vitamin B12 (µg)",
    "SFA (g)", "MUFA (g)", "PUFA (g)"
]


def comp2_lookup(food_name: str):
    if _comp2_search_fn is None:
        return None
    try:
        result = _comp2_search_fn(food_name)
        if not result:
            return None
        return dict(zip(COMP2_HEADERS, result))
    except Exception as e:
        return None


def comp2_lookup_bulk(food_names: list):
    found, not_found = [], []
    for name in food_names:
        data = comp2_lookup(name)
        if data:
            found.append({"food": name, "data": data})
        else:
            not_found.append(name)
    return found, not_found


def aggregate_comp2_nutrition(found_list: list) -> dict:
    totals = {h: 0.0 for h in COMP2_HEADERS[1:]}
    for entry in found_list:
        for key in totals:
            try:
                totals[key] += float(entry["data"].get(key, 0) or 0)
            except (ValueError, TypeError):
                pass
    return totals


# ============================================================
# COMPONENT 1 — YOLO Ensemble Food Detector
# ============================================================
# ============================================================
# COMPONENT 1 — SMART FOOD DETECTOR (3-Model Ensemble + Food Check)
# ============================================================
@st.cache_resource
def load_food_detector():
    """
    Load the SMART 3-model ensemble food detector with food/non-food classification.
    Uses smart_food_detector.py which includes:
    - Food/non-food pre-filtering using ResNet18
    - 3-model YOLO ensemble (V21, V24, V25)
    - Smart voting: specific foods from V25 only, others need 2/3 agreement
    """
    try:
        from smart_food_detector import SmartFoodDetector
        import os

        # Paths to your three models (adjust if necessary)
        v21_path = "models/srilankan_food_model_v21_74.5.pt"
        v24_path = "models/srilankan_food_model_v24_71.9.pt"
        v25_path = "models/srilankan_food_model_v25_70.5.pt"

        # Check if all files exist
        missing = []
        for path in [v21_path, v24_path, v25_path]:
            if not os.path.exists(path):
                missing.append(path)

        if missing:
            return None, f"Missing model files: {', '.join(missing)}"

        # Create the SmartFoodDetector (integrates food classifier + 3-model ensemble)
        detector = SmartFoodDetector(v21_path, v24_path, v25_path)
        return detector, None

    except ImportError as e:
        return None, f"smart_food_detector.py not found. Error: {e}"
    except Exception as e:
        return None, str(e)


def detect_foods_ensemble(image_array, smart_detector, confidence=0.25):
    """
    Use the SmartFoodDetector (3-model ensemble + food check) to detect foods.

    Args:
        image_array: numpy array of the image
        smart_detector: SmartFoodDetector instance
        confidence: detection confidence threshold (0.25 default)

    Returns:
        final_foods: list of {'food': name, 'confidence': 1.0} dicts
        detection_details: list for debugging with per-model results
    """
    if smart_detector is None:
        return [], []

    # Save image temporarily (the SmartFoodDetector expects a file path)
    import tempfile
    from PIL import Image
    import os as _os

    # Convert numpy array to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_path = temp_file.name
    temp_file.close()

    # Save image to temp file
    img = Image.fromarray(image_array)
    img.save(temp_path)

    try:
        # Use the SmartFoodDetector's detect_with_details method
        # This returns a dict with v21, v24, v25, and ensemble lists
        # Note: SmartFoodDetector.detect_with_details expects a file path, not an array
        details = smart_detector.detect_with_details(temp_path, confidence)

        # The ensemble result is a list of food names (already filtered by food classifier)
        ensemble_foods = details.get('ensemble', [])

        # Convert to the expected format
        final_foods = [{'food': f, 'confidence': 1.0} for f in ensemble_foods]

        # For debugging, collect per-model detection details
        detection_details = []
        for model in ['v21', 'v24', 'v25']:
            for food in details.get(model, []):
                detection_details.append({'model': model.upper(), 'food': food})

        return final_foods, detection_details

    except Exception as e:
        print(f"Detection error: {e}")
        import traceback
        traceback.print_exc()
        return [], []
    finally:
        # Clean up temp file
        try:
            _os.unlink(temp_path)
        except:
            pass


# Load the detector (cached to avoid reloading on every rerun)
ensemble_detector, detector_error = load_food_detector()


# ============================================================
# COMPONENT 3 — Sri Lankan Meal Analyzer
# ============================================================
@st.cache_resource
def load_meal_analyzer():
    """
    Load SriLankanNutritionalAnalyzer, cache the instance.
    Returns (analyzer_instance_or_None, error_str_or_None)
    """
    import importlib.util, traceback, sys as _sys

    def _load_file(module_name: str, filepath: Path):
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        mod = importlib.util.module_from_spec(spec)
        _sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        return mod

    def _find_by_filename(filename: str) -> Path | None:
        # Try common locations
        common = [
            _UI_DIR / filename,
            _UI_DIR / "meal_analyzer" / filename,
        ]
        for p in common:
            if p.exists():
                return p
        # Fallback: search tree
        for p in _UI_DIR.rglob(filename):
            return p
        return None

    viz_path = _find_by_filename("visualizations.py")
    viz_mod = None
    if viz_path:
        try:
            viz_mod = _load_file("visualizations", viz_path)
            _sys.modules["analyzer.visualizations"] = viz_mod
        except Exception:
            pass

    analyzer_path = _find_by_filename("analyzer.py")
    if analyzer_path is None:
        return None, "analyzer.py not found. Place it next to the UI file or in a subfolder."

    try:
        analyzer_mod = _load_file("analyzer", analyzer_path)
    except Exception as e:
        return None, traceback.format_exc()

    # Find food database CSV
    db_path = None
    db_candidates = [
        _UI_DIR / "data" / "traditional food list.csv",
        analyzer_path.parent / "data" / "traditional food list.csv",
        analyzer_path.parent / "traditional food list.csv",
    ]
    for p in _UI_DIR.rglob("*.csv"):
        if "traditional" in p.name.lower() and "food" in p.name.lower():
            db_candidates.insert(0, p)
    for candidate in db_candidates:
        if Path(candidate).exists():
            db_path = Path(candidate)
            break

    if db_path is None:
        return None, "traditional food list.csv not found."

    try:
        analyzer = analyzer_mod.SriLankanNutritionalAnalyzer(
            nutrition_database_path=db_path,
            verbose=False
        )

        # Patch generate_visualizations if needed
        if viz_mod is not None:
            _gen_viz = viz_mod.generate_beautiful_visualizations

            def _patched_generate_visualizations(self, totals, indexes, items,
                                                 _fn=_gen_viz):
                return _fn(totals, indexes, items)

            import types
            analyzer.generate_visualizations = types.MethodType(
                _patched_generate_visualizations, analyzer
            )

        return analyzer, None
    except Exception as e:
        return None, traceback.format_exc()


meal_analyzer, analyzer_error = load_meal_analyzer()


# ============================================================
# COMPONENT 4 — Packaged Food Label Scanner
# ============================================================
@st.cache_resource
def load_label_scanner():
    """
    Load the v2 Label Scanner pipeline (YOLO → OCR structured → RowBasedParser).
    Returns (scanner_or_None, flat_parser_or_None, error_or_None)
    """
    import importlib.util, traceback, types, sys as _sys

    def _load_file(module_name: str, filepath: Path):
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        mod = importlib.util.module_from_spec(spec)
        _sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        return mod

    def _find_file(filename: str, must_contain: str = "") -> Path | None:
        common = [
            _UI_DIR / filename,
            _UI_DIR / "label_scanner" / filename,
        ]
        for p in common:
            if p.exists():
                if not must_contain or must_contain in p.read_text(encoding="utf-8", errors="ignore"):
                    return p
        for p in _UI_DIR.rglob("*.py"):
            if p.name.lower() == filename.lower():
                if not must_contain or must_contain in p.read_text(encoding="utf-8", errors="ignore"):
                    return p
        return None

    # ── Inject config stub so imports inside scanner modules don't fail ──
    if "config" not in _sys.modules:
        cfg_mod = types.ModuleType("config")
        cfg_cfg_mod = types.ModuleType("config.config")
        cfg_cfg_mod.YOLO_MODEL_PATH = _UI_DIR / "models" / "best.pt"
        cfg_cfg_mod.YOLO_CONFIDENCE = 0.25
        cfg_cfg_mod.OCR_CONFIG = {"use_angle_cls": False, "lang": "en", "show_log": False}
        cfg_mod.config = cfg_cfg_mod
        _sys.modules["config"] = cfg_mod
        _sys.modules["config.config"] = cfg_cfg_mod

    # ── Load parser.py (flat NutritionParser — also used by RowBasedParser) ──
    parser_path = _find_file("parser.py", must_contain="NutritionParser")
    if parser_path is None:
        return None, None, "parser.py not found."

    try:
        parser_mod = _load_file("label_scanner.parser", parser_path)
        # Make it importable as plain "parser" so row_parser's `from parser import …` works
        _sys.modules["parser"] = parser_mod
        label_parser = parser_mod.NutritionParser()
    except Exception as e:
        return None, None, f"Parser load failed: {e}"

    # ── Load row_parser.py (RowBasedParser — v2 primary parser) ──
    row_parser_mod = None
    row_parser_path = _find_file("row_parser.py", must_contain="RowBasedParser")
    if row_parser_path:
        try:
            row_parser_mod = _load_file("label_scanner.row_parser", row_parser_path)
        except Exception as e:
            pass  # graceful — will fall back to flat parser only

    # ── Load ocr_engine.py ──
    ocr_mod = None
    ocr_path = _find_file("ocr_engine.py", must_contain="OCREngine")
    if ocr_path:
        try:
            ocr_mod = _load_file("label_scanner.ocr_engine", ocr_path)
        except Exception:
            pass

    # ── Load detector.py ──
    detector_mod = None
    detector_path = _find_file("detector.py", must_contain="NutritionLabelDetector")
    if detector_path:
        try:
            detector_mod = _load_file("label_scanner.detector", detector_path)
        except Exception:
            pass

    # ── Assemble full v2 pipeline if all parts are available ──
    if ocr_mod and detector_mod and row_parser_mod:
        try:
            # Auto-discover YOLO .pt file
            yolo_path = _sys.modules["config.config"].YOLO_MODEL_PATH
            if not Path(yolo_path).exists():
                pt_files = list(_UI_DIR.rglob("*.pt"))
                priority = [p for p in pt_files if any(
                    kw in p.name.lower() for kw in ["best", "last", "label", "detect", "nutri"]
                )]
                yolo_path = priority[0] if priority else (pt_files[0] if pt_files else yolo_path)
            if Path(yolo_path).exists():
                _sys.modules["config.config"].YOLO_MODEL_PATH = yolo_path

            class PackagedFoodScannerV2:
                """
                v2 pipeline:
                  detect_and_crop() → extract_structured() → group_into_rows()
                  → RowBasedParser.parse_from_rows()  (falls back to NutritionParser)
                """

                def __init__(self):
                    self.detector = detector_mod.NutritionLabelDetector()
                    self.ocr = ocr_mod.OCREngine()
                    self.row_parser = row_parser_mod.RowBasedParser()

                def scan(self, image_path: str, save_cropped: bool = False) -> dict:
                    # Step 1 — detect & crop label region
                    cropped, err = self.detector.detect_and_crop(image_path, padding_px=8)
                    if err:
                        return {"success": False, "error": err}
                    if save_cropped:
                        self.detector.save_cropped_label(cropped, "temp_cropped_label.jpg")

                    # Step 2 — structured OCR (returns OCRResult list with coordinates)
                    ocr_results, err = self.ocr.extract_structured(cropped)
                    if err:
                        return {"success": False, "error": err}

                    # Step 3 — group into spatial rows
                    rows = self.ocr.group_into_rows(ocr_results)
                    # Also build flat text for fallback and raw display
                    raw_text = self.ocr.rows_to_text(rows)

                    # Step 4 — row-based parse (falls back to flat parser internally)
                    data = self.row_parser.parse_from_rows(rows, raw_text)
                    is_valid, missing = label_parser.validate(data)

                    return {
                        "success": True,
                        "data": data,
                        "is_complete": is_valid,
                        "missing_fields": missing if not is_valid else [],
                        "raw_text": raw_text,
                        "pipeline": "YOLO + PaddleOCR (structured) + RowBasedParser v2",
                    }

            scanner = PackagedFoodScannerV2()
            return scanner, label_parser, None

        except Exception as e:
            return None, label_parser, f"v2 scanner assembly error: {e}"

    elif ocr_mod and detector_mod:
        # Partial: no RowBasedParser — fall back to flat NutritionParser
        try:
            yolo_path = _sys.modules["config.config"].YOLO_MODEL_PATH
            if not Path(yolo_path).exists():
                pt_files = list(_UI_DIR.rglob("*.pt"))
                if pt_files:
                    yolo_path = pt_files[0]
            if Path(yolo_path).exists():
                _sys.modules["config.config"].YOLO_MODEL_PATH = yolo_path

            class PackagedFoodScannerFlat:
                def __init__(self):
                    self.detector = detector_mod.NutritionLabelDetector()
                    self.ocr = ocr_mod.OCREngine()
                    self.parser = label_parser

                def scan(self, image_path: str, save_cropped: bool = False) -> dict:
                    cropped, err = self.detector.detect_and_crop(image_path, padding_px=8)
                    if err:
                        return {"success": False, "error": err}
                    ocr_results, err = self.ocr.extract_structured(cropped)
                    if err:
                        return {"success": False, "error": err}
                    rows = self.ocr.group_into_rows(ocr_results)
                    raw_text = self.ocr.rows_to_text(rows)
                    data = self.parser.parse(raw_text)
                    is_valid, missing = self.parser.validate(data)
                    return {
                        "success": True,
                        "data": data,
                        "is_complete": is_valid,
                        "missing_fields": missing if not is_valid else [],
                        "raw_text": raw_text,
                        "pipeline": "YOLO + PaddleOCR (structured) + NutritionParser (flat)",
                    }

            return PackagedFoodScannerFlat(), label_parser, \
                "row_parser.py not found — using flat parser fallback"
        except Exception as e:
            return None, label_parser, f"Flat scanner assembly error: {e}"

    else:
        missing_parts = []
        if not ocr_mod:      missing_parts.append("ocr_engine.py")
        if not detector_mod: missing_parts.append("detector.py")
        return None, label_parser, f"Missing: {', '.join(missing_parts)}"


_label_scanner, _label_parser, _label_scanner_error = load_label_scanner()


# ============================================================
# 7. AUTH GATE  (Login / Register)
# ============================================================
def _build_auth_ui():
    """Full-screen login / registration form. Replaces the main app when not logged in."""
    st.markdown("""
    <div style="max-width:480px;margin:50px auto 0;text-align:center">
        <div style="font-family:'Fraunces',serif;font-size:2.4rem;font-weight:900;
                    background:linear-gradient(135deg,#E8553E,#F4A24A);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;letter-spacing:-1px;margin-bottom:6px">
            🥗 NutriScanner Pro
        </div>
        <p style="color:#6B7280;font-size:1rem;font-family:'DM Sans',sans-serif;
                  margin:0 0 32px">Your AI-powered nutrition & health companion</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        tab_login, tab_reg = st.tabs(["Sign In", "Create Account"])

        # ── LOGIN ──────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("#### Welcome back")
            uname = st.text_input("Username", key="login_uname", placeholder="your_username")
            pwd = st.text_input("Password", key="login_pwd", type="password", placeholder="••••••••")
            if st.button("Sign In", type="primary", use_container_width=True, key="btn_login"):
                if not uname or not pwd:
                    st.error("Please enter your username and password.")
                else:
                    ok, user_row = login_user(uname, pwd)
                    if ok:
                        import json as _json
                        u = dict(user_row) if not isinstance(user_row, dict) else user_row
                        st.session_state.logged_in = True
                        st.session_state.user_id = u.get("id") or u.get(0)
                        st.session_state.username = u.get("username", uname)
                        st.session_state.user_profile = {
                            "full_name": u.get("full_name", "User"),
                            "first_name": u.get("full_name", "User").split()[0],
                            "email": u.get("email", ""),
                            "age": u.get("age", 25),
                            "gender": u.get("gender", "Male"),
                            "weight_kg": u.get("weight_kg", 70.0),
                            "height_cm": u.get("height_cm", 170.0),
                            "activity": u.get("activity_level", "Moderately Active"),
                            "goal": u.get("goal", "Maintenance"),
                            "conditions": _json.loads(u.get("conditions") or "[]"),
                            "diet": u.get("diet_type", "No Restriction"),
                            "daily_water_l": u.get("daily_water_l", 2.0),
                            "created_at": u.get("created_at", ""),
                        }
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        # ── REGISTER ───────────────────────────────────────────────────────
        with tab_reg:
            st.markdown("#### Create your free account")

            r_name = st.text_input("Full Name *", key="r_name", placeholder="Kasun Perera")
            r_email = st.text_input("Email *", key="r_email", placeholder="you@example.com")
            r_uname = st.text_input("Username *", key="r_uname", placeholder="kasun123")
            r_pwd = st.text_input("Password *", key="r_pwd", type="password")
            r_pwd2 = st.text_input("Confirm Password *", key="r_pwd2", type="password")

            st.markdown("---")
            st.markdown("##### Body & Lifestyle")
            c1, c2 = st.columns(2)
            with c1:
                r_age = st.number_input("Age *", min_value=10, max_value=100, value=25, key="r_age")
                r_weight = st.number_input("Weight (kg) *", min_value=20.0, max_value=300.0, value=65.0, step=0.5,
                                           key="r_wt")
                r_water = st.number_input("Daily Water (L) *", min_value=0.5, max_value=6.0, value=2.0, step=0.1,
                                          key="r_water")
            with c2:
                r_gender = st.selectbox("Gender *", ["Male", "Female", "Other"], key="r_gen")
                r_height = st.number_input("Height (cm) *", min_value=80.0, max_value=250.0, value=165.0, step=0.5,
                                           key="r_ht")
                r_activity = st.selectbox("Activity Level *",
                                          ["Sedentary", "Lightly Active", "Moderately Active", "Very Active",
                                           "Super Active"],
                                          index=2, key="r_act")

            r_goal = st.selectbox("Health Goal",
                                  ["Weight Loss", "Muscle Gain", "Maintenance", "Improved Endurance", "General Health"],
                                  index=2, key="r_goal")
            r_conditions = st.multiselect("Existing Conditions (optional)",
                                          ["None", "Diabetes", "Hypertension", "Heart Disease", "Obesity", "Anemia",
                                           "Kidney Disease", "Thyroid"],
                                          default=["None"], key="r_cond")
            r_diet = st.selectbox("Dietary Preference",
                                  ["No Restriction", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Gluten-Free"],
                                  key="r_diet")

            if st.button("🚀 Create Account", type="primary", use_container_width=True, key="btn_register"):
                errors = []
                if not all([r_name, r_email, r_uname, r_pwd]):
                    errors.append("All fields marked * are required.")
                if r_pwd != r_pwd2:
                    errors.append("Passwords do not match.")
                if len(r_pwd) < 6:
                    errors.append("Password must be at least 6 characters.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    ok, msg = create_user(
                        username=r_uname, password=r_pwd,
                        full_name=r_name, email=r_email,
                        age=int(r_age), gender=r_gender,
                        weight_kg=float(r_weight), height_cm=float(r_height),
                        activity_level=r_activity, daily_water_l=float(r_water),
                        goal=r_goal, conditions=r_conditions, diet_type=r_diet,
                    )
                    if ok:
                        st.success("✅ Account created! Please sign in.")
                    else:
                        st.error(f"❌ {msg}")


# Show auth wall if not logged in
if not st.session_state.logged_in:
    _build_auth_ui()
    st.stop()

# ============================================================
# 7b. SIDEBAR NAVIGATION  (shown only when logged in)
# ============================================================
with st.sidebar:
    st.markdown('<p class="sidebar-brand">🥗 NutriScanner Pro</p>', unsafe_allow_html=True)
    st.write("")

    prof = st.session_state.user_profile
    st.markdown(
        f'<div class="user-greeting">👤 {prof.get("full_name", "Guest User")}<br>'
        f'<span style="font-size:0.8rem;font-weight:400">{prof.get("email", "")}</span></div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "NAVIGATION",
        ["🏠 Dashboard", "🔍 Health Risk Assessment", "📸 Food Photo Analyzer",
         "🔎 Nutrition Search", "📷 Label Scanner",
         "📊 Nutrition Analytics",
         "🗓️ Today's Food Log", "📅 Monthly Report", "⚙️ My Profile"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button(" Sign Out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    model_status = f" {len(models)}/6 Loaded" if models else " No Models Found"
    comp2_status = " Ready" if _comp2_search_fn else " Not Found"
    comp3_status = " Ready" if meal_analyzer else " Not Found"
    comp4_status = (" v2 Pipeline" if (_label_scanner and not _label_scanner_error)
                    else " Full (flat)" if _label_scanner
    else "️ Parser-only" if _label_parser
    else " Not Found")

# Override if redirected from Food Photo Analyzer
if st.session_state.get("redirect_to_meal"):
    page = "🍽️ Meal Analyzer"
if st.session_state.get("redirect_to_bulk"):
    page = "🔎 Nutrition Search"


# ============================================================
# 8. PAGE ROUTING
# ============================================================
def _display_label_results(nutrition_data: dict):
    """Shared display function for both scan and manual entry results."""
    if st.session_state.get("user_id"):
        # Use a unique key based on hash of nutrition data to avoid duplicate key errors
        _key_suffix = abs(hash(str(sorted(nutrition_data.items())))) % 100000
        scan_food_name = st.text_input(
            "Food name for diary",
            value="Scanned Label Food",
            key=f"label_log_name_{_key_suffix}"
        )
        if st.button("📝 Add to Food Log", type="primary", key=f"add_label_to_log_{_key_suffix}"):
            log_food(
                st.session_state.user_id,
                scan_food_name,
                map_label_to_log(nutrition_data),
                source="label"
            )
            st.success(f"✅ '{scan_food_name}' added to today's food log!")
    per_100 = {
        "🔥 Energy": nutrition_data.get("energy_kcal_per_100g", 0),
        "💪 Protein": nutrition_data.get("protein_g", 0),
        "🍞 Carbs": nutrition_data.get("carbohydrates_g", 0),
        "🥑 Total Fat": nutrition_data.get("total_fat_g", 0),
        "🧈 Sat. Fat": nutrition_data.get("saturated_fat_g", 0),
        "🌾 Fiber": nutrition_data.get("fiber_g", 0),
        "🍬 Sugar": nutrition_data.get("sugar_g", 0),
        "🧂 Sodium (mg)": nutrition_data.get("sodium_mg", 0),
    }
    cols = st.columns(4)
    for i, (label, val) in enumerate(per_100.items()):
        unit = "kcal" if "Energy" in label else ("mg" if "Sodium" in label else "g")
        try:
            display_val = f"{float(val or 0):.1f} {unit}"
        except (ValueError, TypeError):
            display_val = "—"
        with cols[i % 4]:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:1.4rem">{label.split()[0]}</div>'
                f'<div class="metric-value" style="font-size:1.4rem">{display_val}</div>'
                f'<div class="metric-label">{" ".join(label.split()[1:])}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    srv = nutrition_data.get("serving_size")
    if srv:
        st.markdown(f"**Serving size: {srv} {nutrition_data.get('serving_unit', 'g')}**")
        srv_cols = st.columns(4)
        srv_fields = [
            ("⚡ Energy/srv", nutrition_data.get("energy_kcal_per_serving"), "kcal"),
            ("💪 Protein/srv", nutrition_data.get("protein_per_serving_g"), "g"),
            ("🍞 Carbs/srv", nutrition_data.get("carbs_per_serving_g"), "g"),
            ("🥑 Fat/srv", nutrition_data.get("fat_per_serving_g"), "g"),
        ]
        for i, (label, val, unit) in enumerate(srv_fields):
            if val is not None:
                with srv_cols[i % 4]:
                    st.metric(label, f"{float(val or 0):.1f} {unit}")

    st.write("")

    col_chart, col_micro = st.columns(2)
    with col_chart:
        st.markdown("#### 🥗 Macro Distribution (per 100g)")
        macro_df = pd.DataFrame({
            "Nutrient": ["Protein", "Carbohydrates", "Fat", "Fiber"],
            "Amount": [
                float(nutrition_data.get("protein_g", 0) or 0),
                float(nutrition_data.get("carbohydrates_g", 0) or 0),
                float(nutrition_data.get("total_fat_g", 0) or 0),
                float(nutrition_data.get("fiber_g", 0) or 0),
            ]
        })
        st.plotly_chart(create_nutrition_pie_chart(macro_df), use_container_width=True)

    with col_micro:
        st.markdown("#### 🧂 Fat Breakdown (per 100g)")
        fat_df = pd.DataFrame({
            "Type": ["Saturated", "MUFA", "PUFA", "Trans"],
            "Amount": [
                float(nutrition_data.get("saturated_fat_g", 0) or 0),
                float(nutrition_data.get("mufa_g", 0) or 0),
                float(nutrition_data.get("pufa_g", 0) or 0),
                float(nutrition_data.get("trans_fat_g", 0) or 0),
            ]
        })
        fig_fat = go.Figure(go.Bar(
            x=fat_df["Type"], y=fat_df["Amount"],
            marker_color=[PASTEQUE, LAGOON, MELON, ZESTE],
            text=[f"{v:.2f}g" for v in fat_df["Amount"]],
            textposition="outside"
        ))
        fig_fat.update_layout(
            height=300, showlegend=False,
            paper_bgcolor=CARD_BG, plot_bgcolor=PLOT_BG,
            font={"color": FONT_CLR, "family": "Nunito"},
            yaxis=dict(showgrid=True, gridcolor=GRID_CLR, title="g per 100g"),
            margin=dict(l=20, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_fat, use_container_width=True)

    with st.expander("📄 Full Extracted Data"):
        rows = [
            {"Field": k.replace("_", " ").title(), "Value": v}
            for k, v in nutrition_data.items()
            if isinstance(v, (int, float))
        ]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if meal_analyzer:
        st.subheader("🏥 Health Index Scores (via Meal Analyzer)")
        try:
            result = meal_analyzer.analyze_packaged_food(nutrition_data)
            vc1, vc2 = st.columns(2)
            with vc1:
                if 'health_scorecard' in result.figures:
                    st.pyplot(result.figures['health_scorecard'])
            with vc2:
                if 'macronutrient_donut' in result.figures:
                    st.pyplot(result.figures['macronutrient_donut'])
            index_labels = list(result.indexes.keys())
            index_values = list(result.indexes.values())
            st.plotly_chart(
                create_risk_bar_chart([l.replace(" Score", "") for l in index_labels], index_values),
                use_container_width=True
            )
            with st.expander("📄 Full Nutrition Report"):
                st.text(meal_analyzer.generate_text_report(result))
        except Exception as e:
            st.error(f"❌ Health analysis error: {e}")


# ------ DASHBOARD ------
if page == "🏠 Dashboard":
    prof = st.session_state.user_profile
    name = prof.get("first_name", prof.get("full_name", "there"))
    st.markdown(f"""
    <div class="hero-banner">
        <div style="font-family:'Fraunces',serif;font-size:1rem;font-weight:600;
                    color:#1F9E8E;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px">
            Good day
        </div>
        <h1 style="font-size:2.6rem!important;margin:0 0 10px">👋 {name}</h1>
        <p style="color:#6B7280;font-size:1rem;margin:0;font-family:'DM Sans',sans-serif">
            Track your nutrition, scan your meals, and stay on top of your health goals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if prof:
        bmi = None
        if prof.get("weight_kg") and prof.get("height_cm"):
            bmi = round(prof["weight_kg"] / (prof["height_cm"] / 100) ** 2, 1)
        pc1, pc2, pc3, pc4, pc5 = st.columns(5)
        for col, emoji, val, lbl in [
            (pc1, "🎂", prof.get("age", "—"), "Age"),
            (pc2, "⚖️", f'{prof.get("weight_kg", "—")} kg', "Weight"),
            (pc3, "📏", f'{prof.get("height_cm", "—")} cm', "Height"),
            (pc4, "📊", str(bmi) if bmi else "—", "BMI"),
            (pc5, "🎯", prof.get("goal", "—"), "Goal"),
        ]:
            with col:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div style="font-size:1.6rem">{emoji}</div>'
                    f'<div class="metric-value" style="font-size:1.4rem">{val}</div>'
                    f'<div class="metric-label">{lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        st.write("")

    st.subheader("Today's Overview")
    # Pull real data from DB
    _today_summary = get_daily_summary(st.session_state.get("user_id"),
                                       date.today().isoformat()) if st.session_state.get("user_id") else None
    _cal = f'{_today_summary["total_calories"]:.0f}' if _today_summary else "0"
    _pro = f'{_today_summary["total_protein_g"]:.1f}g' if _today_summary else "0g"
    _carb = f'{_today_summary["total_carbs_g"]:.1f}g' if _today_summary else "0g"
    _fat = f'{_today_summary["total_fat_g"]:.1f}g' if _today_summary else "0g"
    _wat = f'{_today_summary["total_water_l"]:.1f}L' if _today_summary else "—"
    _items = _today_summary["item_count"] if _today_summary else 0
    m1, m2, m3, m4, m5 = st.columns(5)
    for col, emoji, val, lbl, delta, cls in [
        (m1, "🔥", _cal, "Calories", f"{_items} items logged", "positive"),
        (m2, "💪", _pro, "Protein", "Today's total", "positive"),
        (m3, "🍞", _carb, "Carbs", "Today's total", "positive"),
        (m4, "🥑", _fat, "Fats", "Today's total", "positive"),
        (m5, "💧", _wat, "Water", "From profile", "positive"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card"><div style="font-size:1.8rem">{emoji}</div><div class="metric-value">{val}</div><div class="metric-label">{lbl}</div><div class="metric-delta delta-{cls}">{delta}</div></div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Calorie Trend — Last 7 Days")
        dates = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(6)][::-1]
        st.plotly_chart(create_trend_chart(dates, [1950, 2100, 1880, 2250, 2180, 2340], "Calories", PASTEQUE),
                        use_container_width=True)
    with col2:
        st.markdown("### Today's Macros")
        macro_data = pd.DataFrame({'Nutrient': ['Protein', 'Carbohydrates', 'Fats'], 'Amount': [94, 245, 68]})
        st.plotly_chart(create_nutrition_pie_chart(macro_data), use_container_width=True)

# ------ HEALTH RISK ASSESSMENT ------
elif page == "🔍 Health Risk Assessment":
    st.title("🔍 Health Risk Assessment")
    st.markdown(
        "Your today's nutritional data is automatically loaded from your food log. Adjust values if needed, then run the assessment.")

    _prof = st.session_state.user_profile
    _user_id_hra = st.session_state.user_id
    _today_hra = date.today().isoformat()

    # ── Pull today's nutritional summary from the database (scanned/logged foods) ──
    _db_summary = get_daily_summary(_user_id_hra, _today_hra) if _user_id_hra else None
    _db_model_input = get_daily_summary_as_model_input(_user_id_hra, _today_hra) if _user_id_hra else None
    _has_scanned_data = _db_summary is not None and _db_summary.get("item_count", 0) > 0

    # Show data source banner
    if _has_scanned_data:
        _item_count = _db_summary["item_count"]
        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(42,176,163,0.15),rgba(42,176,163,0.05));'
            f'border:2px solid #2AB0A3;border-radius:16px;padding:14px 20px;margin-bottom:16px;">'
            f'<b>✅ Nutritional values auto-filled from today\'s food log</b> '
            f'({_item_count} item{"s" if _item_count != 1 else ""} scanned/logged today). '
            f'You can adjust any value below before running the assessment.'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(254,154,52,0.12),rgba(255,228,88,0.06));'
            f'border:2px solid #FE9A34;border-radius:16px;padding:14px 20px;margin-bottom:16px;">'
            f'<b>ℹ️ No food scanned today.</b> Nutritional values are set to <b>0</b>. '
            f'The model will predict risk based on your profile and lifestyle data only. '
            f'Scan or log food items first for a more accurate assessment.'
            f'</div>',
            unsafe_allow_html=True
        )


    # ── Helper: get value from DB summary or default to 0 ──
    def _db_val(key, default=0.0):
        """Return value from DB model input if food has been scanned, else 0."""
        if _has_scanned_data and _db_model_input and key in _db_model_input:
            return float(_db_model_input[key])
        return float(default)


    def _db_val_lifestyle(key, fallback):
        """For lifestyle fields, always prefer DB model input (includes activity/water from profile)."""
        if _db_model_input and key in _db_model_input:
            return float(_db_model_input[key])
        return float(fallback)


    with st.expander("📝 Enter Your Health Data", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**👤 Basic Info**")
            age = st.number_input("Age", min_value=18, max_value=100, value=int(_prof.get("age", 35)))
            gender = st.selectbox("Gender", ["Male", "Female"],
                                  index=0 if _prof.get("gender", "Male") == "Male" else 1)
            weight = st.number_input("Weight (kg)", min_value=40, max_value=200, value=int(_prof.get("weight_kg", 75)))
            height = st.number_input("Height (cm)", min_value=100, max_value=250,
                                     value=int(_prof.get("height_cm", 175)))

        with col2:
            st.markdown("**🍽️ Macronutrients**")
            if _has_scanned_data:
                st.caption("🟢 Values loaded from today's scanned food log")
            else:
                st.caption("⚪ No food scanned — values default to 0")
            calories = st.number_input("Daily Calories (kcal)", min_value=0, max_value=10000,
                                       value=int(_db_val("Daily_Calories_kcal", 0)))
            carbs = st.number_input("Carbohydrates (g)", min_value=0, max_value=1000,
                                    value=int(_db_val("Carbohydrates_g", 0)))
            protein = st.number_input("Protein (g)", min_value=0, max_value=500,
                                      value=int(_db_val("Protein_g", 0)))
            total_fat = st.number_input("Total Fat (g)", min_value=0, max_value=500,
                                        value=int(_db_val("Total_Fat_g", 0)))
            saturated_fat = st.number_input("Saturated Fat (g)", min_value=0, max_value=300,
                                            value=int(_db_val("Saturated_Fat_g", 0)))
            trans_fat = st.number_input("Trans Fat (g)", min_value=0.0, max_value=20.0,
                                        value=round(_db_val("Trans_Fat_g", 0.0), 2), step=0.1)
            total_sugar = st.number_input("Total Sugar (g)", min_value=0, max_value=500,
                                          value=int(_db_val("Total_Sugar_g", 0)))
            added_sugar = st.number_input("Added Sugar (g)", min_value=0, max_value=300,
                                          value=int(_db_val("Added_Sugar_g", 0)))
            fiber = st.number_input("Fiber (g)", min_value=0, max_value=200,
                                    value=int(_db_val("Fiber_g", 0)))

        with col3:
            st.markdown("**💊 Micronutrients & Lifestyle**")
            if _has_scanned_data:
                st.caption("🟢 Micronutrients from DB where available")
            else:
                st.caption("⚪ Micronutrients default to 0; lifestyle from profile")
            sodium = st.number_input("Sodium (mg)", min_value=0, max_value=20000,
                                     value=int(_db_val("Sodium_mg", 0)))
            potassium = st.number_input("Potassium (mg)", min_value=0, max_value=15000,
                                        value=int(_db_val("Potassium_mg", 0)))
            calcium = st.number_input("Calcium (mg)", min_value=0, max_value=5000,
                                      value=int(_db_val("Calcium_mg", 0)))
            iron = st.number_input("Iron (mg)", min_value=0, max_value=100,
                                   value=int(_db_val("Iron_mg", 0)))
            vitamin_d = st.number_input("Vitamin D (IU)", min_value=0, max_value=10000,
                                        value=int(_db_val("Vitamin_D_IU", 0)))
            vitamin_b12 = st.number_input("Vitamin B12 (mcg)", min_value=0.0, max_value=20.0,
                                          value=round(_db_val("Vitamin_B12_mcg", 0.0), 2), step=0.1)
            activity = st.number_input("Physical Activity (min/day)", min_value=0, max_value=600,
                                       value=int(_db_val_lifestyle("Physical_Activity_min",
                                                                   _prof.get("activity_min", 45))))
            water = st.number_input("Water Intake (L)", min_value=0.0, max_value=10.0,
                                    value=round(_db_val_lifestyle("Water_Intake_L",
                                                                  _prof.get("daily_water_l", 2.0)), 1),
                                    step=0.1)

    # ── Always show the Analyze button — works even with all-zero nutrition ──
    if st.button("🔬 Analyze Health Risks", type="primary", use_container_width=True):
        if not models:
            st.error("❌ No models loaded. Place your `.pkl` files in the `models/` folder and restart.")
        else:
            if not _has_scanned_data:
                st.info(
                    "ℹ️ Predicting with zero nutritional intake (no food scanned today). "
                    "Results reflect risk based on profile and lifestyle only. "
                    "Log food items for a full dietary risk assessment."
                )
            patient_data = {
                "Age": age,
                "Gender": 1 if gender == "Male" else 0,
                "Daily_Calories_kcal": calories,
                "Carbohydrates_g": carbs,
                "Protein_g": protein,
                "Total_Fat_g": total_fat,
                "Saturated_Fat_g": saturated_fat,
                "Trans_Fat_g": trans_fat,
                "Total_Sugar_g": total_sugar,
                "Added_Sugar_g": added_sugar,
                "Fiber_g": fiber,
                "Sodium_mg": sodium,
                "Potassium_mg": potassium,
                "Calcium_mg": calcium,
                "Iron_mg": iron,
                "Vitamin_D_IU": vitamin_d,
                "Vitamin_B12_mcg": vitamin_b12,
                "Physical_Activity_min": activity,
                "Water_Intake_L": water,
                "weight_kg": weight,
                "height_cm": height,
            }

            with st.spinner("🤖 AI models analyzing your health profile..."):
                predictions, bmi = run_prediction(patient_data, models)

            bmi_cat, bmi_icon, bmi_level, _ = bmi_category(bmi)
            st.success(f"✅ Analysis complete!  BMI: **{bmi}** — {bmi_icon} {bmi_cat} ({bmi_level})")

            # ── Data source summary ──
            _src_label = (
                f"🟢 Based on **{_db_summary['item_count']} food item(s)** scanned/logged today"
                if _has_scanned_data
                else "🟡 No food scanned — prediction based on profile & lifestyle data with zero nutritional intake"
            )
            st.caption(_src_label)

            # ── Nutritional snapshot used for this assessment ──
            with st.expander("📋 Nutritional Data Used in This Assessment"):
                _snap_rows = [
                    {"Nutrient": "Calories (kcal)", "Value": calories,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Carbohydrates (g)", "Value": carbs,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Protein (g)", "Value": protein,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Total Fat (g)", "Value": total_fat,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Saturated Fat (g)", "Value": saturated_fat,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Trans Fat (g)", "Value": trans_fat,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Total Sugar (g)", "Value": total_sugar,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Added Sugar (g)", "Value": added_sugar,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Fiber (g)", "Value": fiber,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Sodium (mg)", "Value": sodium,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Potassium (mg)", "Value": potassium,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Calcium (mg)", "Value": calcium,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Iron (mg)", "Value": iron,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Vitamin D (IU)", "Value": vitamin_d,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Vitamin B12 (mcg)", "Value": vitamin_b12,
                     "Source": "Food Log" if _has_scanned_data else "Not scanned (0)"},
                    {"Nutrient": "Physical Activity (min)", "Value": activity, "Source": "Profile / Log"},
                    {"Nutrient": "Water Intake (L)", "Value": water, "Source": "Profile"},
                ]
                st.dataframe(pd.DataFrame(_snap_rows), use_container_width=True, hide_index=True)

            st.subheader("📊 Risk Assessment Results")
            g1, g2, g3 = st.columns(3)
            for col, disease in zip([g1, g2, g3], ["Diabetes_Risk", "Hypertension_Risk", "Heart_Disease_Risk"]):
                p = predictions[disease]
                with col:
                    st.plotly_chart(create_risk_gauge(p["prob_pct"], f"{p['label']} Risk"), use_container_width=True)

            st.subheader("📋 All Disease Risks")
            labels = [predictions[d]["label"] for d in DISEASE_COLUMNS]
            probs = [predictions[d]["prob_pct"] for d in DISEASE_COLUMNS]
            st.plotly_chart(create_risk_bar_chart(labels, probs), use_container_width=True)

            st.subheader("📄 Detailed Breakdown")
            rows = [{"Disease": predictions[d]["label"],
                     "Risk Level": f"{predictions[d]['icon']} {predictions[d]['level']}",
                     "Probability": f"{predictions[d]['prob_pct']:.1f}%",
                     "Data Source": "Food Log + Profile" if _has_scanned_data else "Profile Only (no food scanned)"
                     } for d in DISEASE_COLUMNS]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.subheader("🌿 Personalized Recommendations")
            tips = {
                "Diabetes": {
                    "HIGH": "🔴 **High Diabetes Risk:** Drastically reduce added sugar and refined carbs. Increase fiber and daily exercise.",
                    "MODERATE": "🟡 **Moderate Diabetes Risk:** Monitor sugar, favor whole grains, aim for 30+ min exercise daily.",
                    "LOW": "🟢 **Low Diabetes Risk:** Great! Keep maintaining a balanced diet low in added sugars."},
                "Hypertension": {
                    "HIGH": "🔴 **High Hypertension Risk:** Reduce sodium (<1500 mg/day). Increase potassium-rich foods (bananas, spinach).",
                    "MODERATE": "🟡 **Moderate Hypertension Risk:** Aim for <2300 mg sodium/day and stay hydrated.",
                    "LOW": "🟢 **Low Hypertension Risk:** Good sodium/potassium balance. Keep it up!"},
                "Heart Disease": {
                    "HIGH": "🔴 **High Heart Disease Risk:** Eliminate trans fats, reduce saturated fat. Add omega-3 rich foods.",
                    "MODERATE": "🟡 **Moderate Heart Disease Risk:** Reduce saturated fat and increase cardio activity.",
                    "LOW": "🟢 **Low Heart Disease Risk:** Heart-healthy diet maintained. Keep limiting unhealthy fats."},
                "Obesity": {
                    "HIGH": "🔴 **High Obesity Risk (BMI):** Consider working with a dietitian. Aim for calorie deficit + more activity.",
                    "MODERATE": "🟡 **Moderate Obesity Risk:** Focus on portion control and increasing daily movement.",
                    "LOW": "🟢 **Healthy Weight:** Great BMI range! Maintain your current habits."},
                "Anemia": {
                    "HIGH": "🔴 **High Anemia Risk:** Iron and/or B12 critically low. Consult a doctor about supplementation.",
                    "MODERATE": "🟡 **Moderate Anemia Risk:** Increase iron-rich foods (red meat, spinach, lentils) and B12 sources.",
                    "LOW": "🟢 **Low Anemia Risk:** Good iron and B12 levels. Keep including diverse protein sources."},
                "Kidney Disease": {
                    "HIGH": "🔴 **High Kidney Risk:** Reduce sodium and excessive protein. Increase water intake to >2L/day.",
                    "MODERATE": "🟡 **Moderate Kidney Risk:** Monitor sodium and protein. Stay well hydrated.",
                    "LOW": "🟢 **Low Kidney Risk:** Good hydration and balanced sodium. Keep it up!"},
            }
            for disease in DISEASE_COLUMNS:
                p = predictions[disease]
                label, level = p["label"], p["level"]
                css_class = "risk-high" if level == "HIGH" else "risk-medium" if level == "MODERATE" else "risk-low"
                if label in tips and level in tips[label]:
                    st.markdown(f'<div class="{css_class}">{tips[label][level]}</div>', unsafe_allow_html=True)

# ------ NUTRITION ANALYTICS ------
elif page == "📊 Nutrition Analytics":
    st.title("📊 Advanced Nutrition Analytics")

    user_id = st.session_state.user_id
    today = date.today()

    # Fetch last 7 days of data for trends
    last_7_days = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

    # Get summaries for last 7 days
    weekly_data = []
    for day in last_7_days:
        summary = get_daily_summary(user_id, day)
        if summary and summary["item_count"] > 0:
            weekly_data.append({
                "date": day,
                "calories": summary["total_calories"],
                "protein": summary["total_protein_g"],
                "carbs": summary["total_carbs_g"],
                "fat": summary["total_fat_g"],
                "water": summary["total_water_l"],
                "items": summary["item_count"]
            })
        else:
            weekly_data.append({
                "date": day,
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "water": 0,
                "items": 0
            })

    # Get today's summary for current macros
    today_summary = get_daily_summary(user_id, today.isoformat())

    tab1, tab2, tab4 = st.tabs(["🥗 Macros", "💊 Micronutrients", "⚠️ Deficiencies"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Today's Macro Distribution")
            if today_summary and today_summary["item_count"] > 0:
                # Use real data from today's food log
                macro_data = pd.DataFrame({
                    'Nutrient': ['Protein', 'Carbohydrates', 'Fats', 'Fiber'],
                    'Amount': [
                        today_summary["total_protein_g"],
                        today_summary["total_carbs_g"],
                        today_summary["total_fat_g"],
                        today_summary.get("total_fiber_g", 0)  # Add fiber if available
                    ]
                })
                # Filter out zero values for pie chart
                macro_data = macro_data[macro_data['Amount'] > 0]
                if len(macro_data) > 0:
                    st.plotly_chart(create_nutrition_pie_chart(macro_data), use_container_width=True)
                else:
                    st.info("📭 No food logged today. Add some food items to see your macro distribution.")
            else:
                # Show placeholder graph with zero values
                macro_data = pd.DataFrame({
                    'Nutrient': ['Protein', 'Carbohydrates', 'Fats', 'Fiber'],
                    'Amount': [0, 0, 0, 0]
                })
                st.plotly_chart(create_nutrition_pie_chart(macro_data), use_container_width=True)
                st.info("📭 No data logged today. Your macro distribution will appear here once you log food items.")

        with col2:
            st.markdown("#### Weekly Nutrition Score")
            # Calculate weekly averages
            avg_protein = np.mean([d["protein"] for d in weekly_data]) if any(
                d["protein"] > 0 for d in weekly_data) else 0
            avg_carbs = np.mean([d["carbs"] for d in weekly_data]) if any(d["carbs"] > 0 for d in weekly_data) else 0
            avg_fat = np.mean([d["fat"] for d in weekly_data]) if any(d["fat"] > 0 for d in weekly_data) else 0
            avg_fiber = 0  # Add fiber tracking if available

            # Calculate scores (normalized to recommended values)
            # Recommended daily: Protein 50g, Carbs 250g, Fat 70g, Fiber 25g, Water 2L, Activity 30min
            protein_score = min(100, (avg_protein / 50) * 100) if avg_protein > 0 else 0
            carbs_score = min(100, (avg_carbs / 250) * 100) if avg_carbs > 0 else 0
            fat_score = min(100, (avg_fat / 70) * 100) if avg_fat > 0 else 0
            fiber_score = 0
            water_score = 0
            activity_score = 0

            radar_values = [protein_score, carbs_score, fat_score, fiber_score, water_score, activity_score]
            radar_labels = ['Protein', 'Carbs', 'Fats', 'Fiber', 'Water', 'Activity']

            st.plotly_chart(create_radar_chart(radar_labels, radar_values, "Weekly Nutrition Score"),
                            use_container_width=True)
            if all(v == 0 for v in radar_values):
                st.caption("📭 Log food for 7 days to see your nutrition radar chart")

    with tab2:
        st.markdown("#### Micronutrient Intake vs Recommendations")

        # Get micronutrient data from today's food log or last 7 days average
        if today_summary and today_summary["item_count"] > 0:
            # Use today's data if available
            # Note: You'll need to modify get_daily_summary to include micronutrients
            # For now, using placeholder - you'll need to extend your database schema
            micro_data = pd.DataFrame({
                'Nutrient': ['Vitamin D', 'Vitamin B12', 'Iron', 'Calcium', 'Potassium', 'Sodium'],
                'Intake': [
                    today_summary.get("total_vitamin_d_iu", 0),
                    today_summary.get("total_vitamin_b12_mcg", 0),
                    today_summary.get("total_iron_mg", 0),
                    today_summary.get("total_calcium_mg", 0),
                    today_summary.get("total_potassium_mg", 0),
                    today_summary.get("total_sodium_mg", 0)
                ],
                'Recommended': [800, 2.4, 18, 1000, 4700, 2300]
            })
        else:
            # Show placeholder with zeros
            micro_data = pd.DataFrame({
                'Nutrient': ['Vitamin D', 'Vitamin B12', 'Iron', 'Calcium', 'Potassium', 'Sodium'],
                'Intake': [0, 0, 0, 0, 0, 0],
                'Recommended': [800, 2.4, 18, 1000, 4700, 2300]
            })

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Your Intake',
            y=micro_data['Nutrient'],
            x=micro_data['Intake'],
            orientation='h',
            marker=dict(color=PASTEQUE, cornerradius=5),
            hovertemplate='<b>%{y}</b><br>Intake: %{x}<extra></extra>'
        ))
        fig.add_trace(go.Bar(
            name='Recommended',
            y=micro_data['Nutrient'],
            x=micro_data['Recommended'],
            orientation='h',
            marker=dict(color=LAGOON, opacity=0.55, cornerradius=5),
            hovertemplate='<b>%{y}</b><br>Recommended: %{x}<extra></extra>'
        ))
        fig.update_layout(
            barmode='overlay',
            height=400,
            paper_bgcolor=CARD_BG,
            plot_bgcolor=PLOT_BG,
            font={'color': FONT_CLR, 'family': 'DM Sans'},
            xaxis=dict(showgrid=True, gridcolor=GRID_CLR, tickfont=dict(size=11, color=FONT_CLR)),
            yaxis=dict(showgrid=False, tickfont=dict(size=12, color=FONT_CLR)),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                        font=dict(color=FONT_CLR)),
            margin=dict(l=120, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

        if all(micro_data['Intake'] == 0):
            st.info("📭 No micronutrient data available. Log more diverse foods to see your micronutrient intake.")

    with tab4:
        st.markdown("#### ⚠️ Nutrient Deficiencies & Warnings")

        # Calculate deficiencies based on actual data
        deficiencies_found = False

        if today_summary and today_summary["item_count"] > 0:
            # Check Vitamin D (Recommended: 800 IU)
            vitamin_d = today_summary.get("total_vitamin_d_iu", 0)
            if vitamin_d < 800:
                st.markdown(
                    f'<div class="risk-medium">⚠️ <strong>Vitamin D:</strong> Your intake ({vitamin_d:.0f} IU) is below recommended (800 IU). Consider sun exposure or supplementation.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True

            # Check Iron (Recommended: 18mg for adults)
            iron = today_summary.get("total_iron_mg", 0)
            if iron < 18:
                st.markdown(
                    f'<div class="risk-medium">⚠️ <strong>Iron:</strong> Your intake ({iron:.1f}mg) is below recommended (18mg). Eat more leafy greens and lean meats.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True

            # Check Calcium (Recommended: 1000mg)
            calcium = today_summary.get("total_calcium_mg", 0)
            if calcium > 0 and calcium < 1000:
                st.markdown(
                    f'<div class="risk-medium">⚠️ <strong>Calcium:</strong> Your intake ({calcium:.0f}mg) is below recommended (1000mg). Include dairy or fortified alternatives.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True
            elif calcium >= 1000:
                st.markdown(
                    f'<div class="risk-low">✅ <strong>Calcium:</strong> Good intake ({calcium:.0f}mg)! Keep consuming dairy and leafy greens.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True

            # Check Potassium (Recommended: 4700mg)
            potassium = today_summary.get("total_potassium_mg", 0)
            if potassium > 0 and potassium >= 3500:
                st.markdown(
                    f'<div class="risk-low">✅ <strong>Potassium:</strong> Excellent ({potassium:.0f}mg)! Supports healthy blood pressure.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True
            elif potassium > 0 and potassium < 3500:
                st.markdown(
                    f'<div class="risk-medium">⚠️ <strong>Potassium:</strong> Your intake ({potassium:.0f}mg) could be improved. Add bananas, potatoes, or beans.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True

            # Check Fiber (Recommended: 25g)
            fiber = today_summary.get("total_fiber_g", 0)
            if fiber > 0 and fiber < 25:
                st.markdown(
                    f'<div class="risk-medium">⚠️ <strong>Fiber:</strong> Your intake ({fiber:.1f}g) is below recommended (25g). Add more whole grains and vegetables.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True
            elif fiber >= 25:
                st.markdown(
                    f'<div class="risk-low">✅ <strong>Fiber:</strong> Great intake ({fiber:.1f}g)! Excellent for digestive health.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True

            # Check Protein (Recommended: 50g minimum)
            protein = today_summary.get("total_protein_g", 0)
            if protein > 0 and protein < 50:
                st.markdown(
                    f'<div class="risk-medium">⚠️ <strong>Protein:</strong> Your intake ({protein:.1f}g) is below minimum recommendation (50g). Include more protein-rich foods.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True
            elif protein >= 80:
                st.markdown(
                    f'<div class="risk-low">✅ <strong>Protein:</strong> Excellent intake ({protein:.1f}g)! Great for muscle maintenance.</div>',
                    unsafe_allow_html=True)
                deficiencies_found = True

            if not deficiencies_found:
                st.markdown(
                    '<div class="risk-low">✅ <strong>Great job!</strong> All your micronutrients are meeting or exceeding recommendations. Keep up the balanced diet!</div>',
                    unsafe_allow_html=True)
        else:
            # No data logged
            st.markdown(
                '<div class="risk-medium">📭 <strong>No food logged today.</strong> Start logging your meals to see personalized deficiency analysis and recommendations.</div>',
                unsafe_allow_html=True)
            st.info(
                "💡 **Tip:** Use the Food Photo Analyzer or Nutrition Search to quickly log your meals and track your nutrient intake.")
# ============================================================
# FOOD PHOTO ANALYZER - FIXED VERSION
# ============================================================
# ============================================================
# FOOD PHOTO ANALYZER - WITH PHOTO CLEARING
# ============================================================

elif page == "📸 Food Photo Analyzer":
    st.title("Food Photo Analyzer")

    # Check for success message from previous log action
    if st.session_state.get("log_success_msg"):
        st.success(st.session_state["log_success_msg"])
        # Clear after displaying
        st.session_state.log_success_msg = None

    # Check if we're in manual correction mode
    if st.session_state.get("show_manual_correction", False):
        # ========== MANUAL CORRECTION MODE WITH CHECKBOX SELECTION ==========
        st.markdown("### Correct Food Items Manually")
        st.markdown("Select the correct food items from the list below, then click **Analyze Nutrition**.")

        # Load available food items
        # COMPLETE AVAILABLE FOOD LIST - All Sri Lankan foods
        # COMPLETE AVAILABLE FOOD LIST - Matches your model's output names exactly
        available_foods = [
            # Rice & Rice Dishes
            "White rice", "Red rice", "Yellow rice", "Fried rice", "Kiribath", "Kottu",
            # Bread & Roti
            "Coconut roti", "Pol sambol", "Lunu sambol",
            # Hoppers & String Hoppers
            "Hoppers", "String hoppers", "Pittu",
            # Curries - Vegetable (matches model output)
            "Beans curry", "Beetroot curry", "Cabbage curry", "Carrot curry", "Cashew curry",
            "Dhal curry", "Egg curry", "Fish curry", "Gotukola mallum", "Moringa curry",
            "Mango curry", "Okra curry", "Polos curry", "Potato curry", "Soya curry", "Sprats curry",
            # Curries - Meat & Seafood
            "Chicken curry", "Prawns curry",
            # Snacks & Appetizers (matches model output)
            "Papadam", "Wade",
            # Fried items (matches model output - these are what your model detects)
            "cutlets", "patties", "rolls",
            # Baked items (matches model output)
            "fish buns", "pastries", "plain bun"
            # Baked sweet buns (matches model output)
                                     "kibula", "cream buns",
            # Other items
            "Sausage hotdog",
            # Desserts & Sweets (matches model output)
            "Watalappam", "donuts", "éclairs", "cake slices", "brownies"
        ]

        st.markdown("#### Select Food Items (click to select multiple):")

        # Create a box with checkboxes for food selection
        selected_foods = []
        cols_per_row = 3
        num_cols = cols_per_row

        # Get previously selected foods from session state
        previously_selected = st.session_state.get("temp_selected_foods", [])

        # Create checkboxes in a grid
        for i in range(0, len(available_foods), num_cols):
            cols = st.columns(num_cols)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(available_foods):
                    food = available_foods[idx]
                    is_checked = food in previously_selected
                    if col.checkbox(food, value=is_checked, key=f"food_check_{idx}"):
                        selected_foods.append(food)

        # Store selected foods in session state
        st.session_state.temp_selected_foods = selected_foods

        # Display selected foods summary
        if selected_foods:
            st.markdown("#### Selected Foods:")
            selected_html = '<div style="background:#F0F7F5; border-radius:12px; padding:12px 16px; margin:10px 0;">'
            for food in selected_foods:
                selected_html += f'<span style="background:#1F9E8E; color:white; border-radius:20px; padding:5px 12px; margin:4px; display:inline-block; font-size:0.85rem;">{food}</span>'
            selected_html += '</div>'
            st.markdown(selected_html, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Analyze Nutrition", type="primary", use_container_width=True):
                if selected_foods:
                    st.session_state.corrected_foods = selected_foods
                    st.session_state.show_corrected_analysis = True
                    st.rerun()
                else:
                    st.warning("Please select at least one food item.")

        with col2:
            if st.button("Back to Scan", use_container_width=True):
                st.session_state.show_manual_correction = False
                st.session_state.manual_correction_foods = []
                st.session_state.temp_selected_foods = []
                st.session_state.detection_done = False
                st.rerun()

        # Show analysis results for corrected foods
        if st.session_state.get("show_corrected_analysis", False):
            food_names = st.session_state.get("corrected_foods", [])
            st.markdown("---")
            st.subheader("Nutritional Analysis Results")

            if analyzer_error and comp2_error:
                st.error("Neither Meal Analyzer nor Nutrition DB are available. Cannot compute nutrition.")
            else:
                # Step 1: Try Estimation_Search (comp2)
                comp2_found, comp2_not_found = [], list(food_names)
                if not comp2_error and _comp2_search_fn:
                    with st.spinner("Looking up nutritional values..."):
                        comp2_found, comp2_not_found = comp2_lookup_bulk(food_names)

                # Step 2: Try meal_analyzer for remaining items
                analyzer_found_items = []
                if comp2_not_found and not analyzer_error and meal_analyzer:
                    with st.spinner("Checking Sri Lankan food database..."):
                        try:
                            partial_result = meal_analyzer.analyze_meal(comp2_not_found)
                            for it in partial_result.items:
                                energy = it.nutrients.get("Energy (kcal)", 0)
                                if energy and float(energy) > 0:
                                    analyzer_found_items.append({
                                        "food": it.input_name,
                                        "data": {
                                            "Description": it.matched_food_item or it.input_name,
                                            "Calories": energy,
                                            "Proteins (g)": it.nutrients.get("Protein (g)", 0),
                                            "Carbohydrates (g)": it.nutrients.get("Digestible carbs (g)", 0),
                                            "Fats (g)": it.nutrients.get("Total fat (g)", 0),
                                        }
                                    })
                        except Exception as e:
                            st.warning(f"Meal analyzer error: {e}")

                # Merge results
                all_found = comp2_found + analyzer_found_items
                not_found_names = [n for n in comp2_not_found if
                                   n.lower() not in {e["food"].lower() for e in analyzer_found_items}]

                if not_found_names:
                    st.warning(f"Not found in any database: {', '.join(not_found_names)}")

                if not all_found:
                    st.warning("No nutritional data found for any food item.")
                else:
                    totals = aggregate_comp2_nutrition(all_found)

                    # Display metrics
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("Calories", f"{totals.get('Calories', 0):.0f} kcal")
                    with col_b:
                        st.metric("Protein", f"{totals.get('Proteins (g)', 0):.1f} g")
                    with col_c:
                        st.metric("Carbs", f"{totals.get('Carbohydrates (g)', 0):.1f} g")
                    with col_d:
                        st.metric("Fat", f"{totals.get('Fats (g)', 0):.1f} g")

                    # Show macro pie chart
                    st.markdown("#### Macro Distribution")
                    macro_df = pd.DataFrame({
                        "Nutrient": ["Protein", "Carbohydrates", "Fats"],
                        "Amount": [
                            totals.get("Proteins (g)", 0),
                            totals.get("Carbohydrates (g)", 0),
                            totals.get("Fats (g)", 0)
                        ]
                    })
                    if macro_df["Amount"].sum() > 0:
                        st.plotly_chart(create_nutrition_pie_chart(macro_df), use_container_width=True)

                    # Show per-food breakdown
                    st.markdown("#### Per-Food Breakdown")
                    breakdown = []
                    for entry in all_found:
                        d = entry["data"]
                        breakdown.append({
                            "Food": entry["food"].title(),
                            "Calories": f"{float(d.get('Calories', 0)):.0f}",
                            "Protein (g)": f"{float(d.get('Proteins (g)', 0)):.1f}",
                            "Carbs (g)": f"{float(d.get('Carbohydrates (g)', 0)):.1f}",
                            "Fat (g)": f"{float(d.get('Fats (g)', 0)):.1f}"
                        })
                    st.dataframe(pd.DataFrame(breakdown), use_container_width=True, hide_index=True)

                    # Option to log to diary
                    if st.session_state.get("user_id"):
                        if st.button("Log All to Food Diary", type="primary", key="log_corrected_foods"):
                            for entry in all_found:
                                d = entry["data"]
                                log_food(
                                    st.session_state.user_id,
                                    entry["food"],
                                    {
                                        "calories_kcal": float(d.get("Calories", 0) or 0),
                                        "protein_g": float(d.get("Proteins (g)", 0) or 0),
                                        "carbs_g": float(d.get("Carbohydrates (g)", 0) or 0),
                                        "fat_g": float(d.get("Fats (g)", 0) or 0),
                                        "fiber_g": 0.0,
                                        "sodium_mg": float(d.get("Sodium (mg)", 0) or 0),
                                    },
                                    source="manual"
                                )
                            # Store success message in session state
                            st.session_state.log_success_msg = f" Successfully logged {len(all_found)} food(s) to your diary!"

                            # Reset all session states including photo
                            st.session_state.show_corrected_analysis = False
                            st.session_state.show_manual_correction = False
                            st.session_state.manual_correction_foods = []
                            st.session_state.temp_selected_foods = []
                            st.session_state.detection_done = False
                            st.session_state.show_analysis = False
                            st.session_state.detected_foods = []
                            st.session_state.confirmed_foods = []
                            # Clear the uploaded photo by removing from session state
                            if "photo_uploader_main" in st.session_state:
                                del st.session_state.photo_uploader_main
                            st.rerun()

    else:
        # ========== NORMAL SCAN MODE ==========
        st.markdown(
            "Take a photo of your Sri Lankan meal — our AI will detect the foods and analyze the nutrition automatically!")

        if detector_error:
            st.error(f"Food Detector not available: {detector_error}")
            st.info("""
            **To enable this feature:**
            1. Copy `srilankan_food_model_v21_74_5.pt` into your `models/` folder
            2. Copy `srilankan_food_model_v24_71_9_.pt` into your `models/` folder
            3. Run: `pip install ultralytics opencv-python`
            4. Restart the app
            """)
        else:
            st.markdown("### Upload Your Meal Photo")

            # Use a unique key that can be reset
            photo_key = "photo_uploader_main"

            uploaded_photo = st.file_uploader(
                "Choose a photo of your meal",
                type=["jpg", "jpeg", "png", "bmp", "webp"],
                help="Upload a clear photo of your Sri Lankan meal",
                key=photo_key
            )

            col1, col2 = st.columns(2)
            with col1:
                confidence = st.slider("Detection Confidence", 0.10, 0.90, 0.25, 0.05,
                                       help="Lower = detect more items, Higher = only confident detections")
            with col2:
                method = st.selectbox("Detection Method",
                                      ["Average (Recommended)", "Voting (Both models must agree)"])

            if uploaded_photo:
                from PIL import Image
                import numpy as np

                image = Image.open(uploaded_photo).convert("RGB")
                img_array = np.array(image)
                st.image(image, caption="Your Meal Photo", use_container_width=True)

                if st.button("Detect Foods", type="primary", use_container_width=True, key="detect_btn_main"):
                    with st.spinner("AI is analyzing your meal photo..."):
                        try:
                            detected_foods, details = detect_foods_ensemble(
                                img_array, ensemble_detector, confidence
                            )
                            st.session_state.detected_foods = detected_foods
                            st.session_state.detection_details = details
                            st.session_state.detection_done = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Detection failed: {str(e)}")

                if st.session_state.get("detection_done", False):
                    detected_foods = st.session_state.get("detected_foods", [])

                    if not detected_foods:
                        st.markdown(
                            '<div style="background:#fff3cd;border:2px solid #ffc107;border-radius:12px;padding:16px 20px;color:#1C2B2A;font-weight:600;font-size:0.95rem;"> No foods detected. Try lowering the confidence threshold or use a clearer photo.</div>',
                            unsafe_allow_html=True)
                        st.session_state.detection_done = False
                    else:
                        st.subheader(f"Detected {len(detected_foods)} Food Item(s)")
                        det_cols = st.columns(min(len(detected_foods), 4))
                        for i, item in enumerate(detected_foods):
                            with det_cols[i % 4]:
                                conf_pct = item['confidence'] * 100
                                color = "delta-positive" if conf_pct >= 60 else "delta-negative"
                                st.markdown(
                                    f'<div class="metric-card"><div style="font-weight:700;font-size:1rem">{item["food"]}</div><div class="metric-delta {color}">{conf_pct:.0f}% confident</div></div>',
                                    unsafe_allow_html=True)

                        st.write("")
                        st.markdown("---")
                        st.markdown("### Are these detections correct?")

                        conf_c1, conf_c2 = st.columns(2)
                        with conf_c1:
                            if st.button("Yes, analyze nutrition!", type="primary", use_container_width=True,
                                         key="yes_analyze_main"):
                                food_names = [f["food"] for f in detected_foods]
                                st.session_state.confirmed_foods = food_names
                                st.session_state.show_analysis = True
                                st.rerun()

                        with conf_c2:
                            if st.button("No, correct manually", use_container_width=True, key="no_correct_main"):
                                st.session_state.manual_correction_foods = [f["food"] for f in detected_foods]
                                st.session_state.show_manual_correction = True
                                st.rerun()

                # Show analysis when Yes is clicked
                if st.session_state.get("show_analysis", False):
                    food_names = st.session_state.get("confirmed_foods", [])
                    st.markdown("---")
                    st.subheader("Nutritional Analysis Results")

                    if analyzer_error and comp2_error:
                        st.error("Neither Meal Analyzer nor Nutrition DB are available. Cannot compute nutrition.")
                    else:
                        comp2_found, comp2_not_found = [], list(food_names)
                        if not comp2_error and _comp2_search_fn:
                            with st.spinner("Looking up nutritional values..."):
                                comp2_found, comp2_not_found = comp2_lookup_bulk(food_names)

                        analyzer_found_items = []
                        if comp2_not_found and not analyzer_error and meal_analyzer:
                            with st.spinner("Checking Sri Lankan food database..."):
                                try:
                                    partial_result = meal_analyzer.analyze_meal(comp2_not_found)
                                    for it in partial_result.items:
                                        energy = it.nutrients.get("Energy (kcal)", 0)
                                        if energy and float(energy) > 0:
                                            analyzer_found_items.append({
                                                "food": it.input_name,
                                                "data": {
                                                    "Description": it.matched_food_item or it.input_name,
                                                    "Calories": energy,
                                                    "Proteins (g)": it.nutrients.get("Protein (g)", 0),
                                                    "Carbohydrates (g)": it.nutrients.get("Digestible carbs (g)", 0),
                                                    "Fats (g)": it.nutrients.get("Total fat (g)", 0),
                                                }
                                            })
                                except Exception as e:
                                    st.warning(f"Meal analyzer error: {e}")

                        all_found = comp2_found + analyzer_found_items
                        not_found_names = [n for n in comp2_not_found if
                                           n.lower() not in {e["food"].lower() for e in analyzer_found_items}]

                        if not_found_names:
                            st.warning(f"Not found in any database: {', '.join(not_found_names)}")

                        if not all_found:
                            st.warning("No nutritional data found for any detected food.")
                        else:
                            totals = aggregate_comp2_nutrition(all_found)

                            col_a, col_b, col_c, col_d = st.columns(4)
                            with col_a:
                                st.metric("Calories", f"{totals.get('Calories', 0):.0f} kcal")
                            with col_b:
                                st.metric("Protein", f"{totals.get('Proteins (g)', 0):.1f} g")
                            with col_c:
                                st.metric("Carbs", f"{totals.get('Carbohydrates (g)', 0):.1f} g")
                            with col_d:
                                st.metric("Fat", f"{totals.get('Fats (g)', 0):.1f} g")

                            st.markdown("#### Macro Distribution")
                            macro_df = pd.DataFrame({
                                "Nutrient": ["Protein", "Carbohydrates", "Fats"],
                                "Amount": [
                                    totals.get("Proteins (g)", 0),
                                    totals.get("Carbohydrates (g)", 0),
                                    totals.get("Fats (g)", 0)
                                ]
                            })
                            if macro_df["Amount"].sum() > 0:
                                st.plotly_chart(create_nutrition_pie_chart(macro_df), use_container_width=True)

                            st.markdown("#### Per-Food Breakdown")
                            breakdown = []
                            for entry in all_found:
                                d = entry["data"]
                                breakdown.append({
                                    "Food": entry["food"].title(),
                                    "Calories": f"{float(d.get('Calories', 0)):.0f}",
                                    "Protein (g)": f"{float(d.get('Proteins (g)', 0)):.1f}",
                                    "Carbs (g)": f"{float(d.get('Carbohydrates (g)', 0)):.1f}",
                                    "Fat (g)": f"{float(d.get('Fats (g)', 0)):.1f}"
                                })
                            st.dataframe(pd.DataFrame(breakdown), use_container_width=True, hide_index=True)

                            if st.session_state.get("user_id"):
                                if st.button("Log All to Food Diary", type="primary", key="log_detected_foods"):
                                    for entry in all_found:
                                        d = entry["data"]
                                        log_food(
                                            st.session_state.user_id,
                                            entry["food"],
                                            {
                                                "calories_kcal": float(d.get("Calories", 0) or 0),
                                                "protein_g": float(d.get("Proteins (g)", 0) or 0),
                                                "carbs_g": float(d.get("Carbohydrates (g)", 0) or 0),
                                                "fat_g": float(d.get("Fats (g)", 0) or 0),
                                                "fiber_g": 0.0,
                                                "sodium_mg": float(d.get("Sodium (mg)", 0) or 0),
                                            },
                                            source="photo"
                                        )
                                    # Store success message in session state
                                    st.session_state.log_success_msg = f" Successfully logged {len(all_found)} food(s) to your diary!"

                                    # Reset all session states and clear photo
                                    st.session_state.show_analysis = False
                                    st.session_state.detection_done = False
                                    st.session_state.detected_foods = []
                                    st.session_state.confirmed_foods = []
                                    st.session_state.manual_correction_foods = []
                                    st.session_state.show_manual_correction = False
                                    # Clear the uploaded photo by removing from session state
                                    if "photo_uploader_main" in st.session_state:
                                        del st.session_state.photo_uploader_main
                                    st.rerun()
# ------ LABEL SCANNER ------
elif page == "📷 Label Scanner":
    st.title("📷 Nutrition Label Scanner")
    st.markdown("Upload a photo of a packaged food nutrition label — AI detects, reads, and analyzes it instantly.")

    if _label_scanner and not _label_scanner_error:
        st.success(" v2 Pipeline ready — YOLO detection + PaddleOCR (structured) + RowBasedParser")
    elif _label_scanner and _label_scanner_error:
        st.warning(f"⚠️ Pipeline loaded with notice: {_label_scanner_error}")
    elif _label_parser:
        st.warning(
            "️ Parser-only mode ")

    if _label_parser:
        tab1, tab2 = st.tabs(["📷 Scan Label", "✏️ Manual Entry"])

        with tab1:
            st.markdown("**Upload a clear photo of a nutrition label:**")
            uploaded_image = st.file_uploader(
                "Choose an image",
                type=["jpg", "jpeg", "png", "bmp", "tiff"],
                help="Upload a clear photo of the nutrition facts panel"
            )

            if uploaded_image:
                from PIL import Image as _PILImage
                import numpy as np

                image = _PILImage.open(uploaded_image).convert("RGB")
                st.image(image, caption="Uploaded Image", use_container_width=True)

                # Clear previous scan result when new image is uploaded
                if st.session_state.get("last_uploaded_image") != uploaded_image.name:
                    st.session_state["last_uploaded_image"] = uploaded_image.name
                    st.session_state.pop("scan_label_data", None)
                    st.session_state.pop("scan_pipeline_used", None)

                if st.button("🔬 Scan & Analyze", type="primary", use_container_width=True):
                    img_array = np.array(image)
                    nutrition_data = {}
                    pipeline_used = "none"

                    if _label_scanner:
                        with st.spinner("🤖 Running full pipeline: detect → OCR → parse…"):
                            try:
                                import tempfile, os as _os

                                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                                    tmp_path = tmp.name
                                    image.save(tmp_path)

                                scan_result = _label_scanner.scan(tmp_path, save_cropped=False)
                                _os.unlink(tmp_path)

                                if scan_result["success"]:
                                    nutrition_data = scan_result["data"]
                                    pipeline_used = scan_result.get(
                                        "pipeline", "YOLO + PaddleOCR + RowBasedParser v2")
                                    st.success(f" Full pipeline complete!")
                                    with st.expander("🔍 Raw OCR Text"):
                                        st.text(scan_result.get("raw_text", ""))
                                    if not scan_result["is_complete"]:
                                        st.warning(
                                            f"⚠️ Some fields missing: {', '.join(scan_result['missing_fields'])}")
                                else:
                                    st.warning(
                                        f"⚠️ Pipeline error: {scan_result['error']} — falling back to OCR-only mode.")
                            except Exception as e:
                                st.warning(f"⚠️ Full pipeline failed: {e} — trying OCR fallback.")

                    if not nutrition_data:
                        with st.spinner("🔍 Reading label with OCR…"):
                            ocr_text = None
                            try:
                                from paddleocr import PaddleOCR

                                _ocr = PaddleOCR(use_angle_cls=False, lang="en", show_log=False)
                                _result = _ocr.ocr(img_array, cls=False)
                                if _result and _result[0]:
                                    items = []
                                    for line in _result[0]:
                                        box = line[0];
                                        txt = line[1][0]
                                        items.append((box[0][1], box[0][0], txt))
                                    items.sort(key=lambda t: (t[0], t[1]))
                                    ocr_text = "\n".join(t[2] for t in items)
                                    st.success(f" PaddleOCR: {len(items)} lines")
                            except Exception:
                                pass

                            if not ocr_text:
                                try:
                                    import easyocr

                                    _reader = easyocr.Reader(['en'], verbose=False)
                                    _raw = _reader.readtext(img_array, detail=1, paragraph=False)
                                    _sorted = sorted(_raw, key=lambda x: x[0][0][1])
                                    ocr_text = "\n".join(r[1] for r in _sorted)

                                except ImportError:
                                    st.error(
                                        "❌ No OCR engine available. Install: `pip install paddleocr paddlepaddle` or `pip install easyocr`")
                                except Exception as e:
                                    st.error(f"❌ OCR failed: {e}")

                        if ocr_text:
                            with st.expander("🔍 Raw OCR Text"):
                                st.text(ocr_text)
                            with st.spinner("📊 Parsing nutrition values…"):
                                try:
                                    nutrition_data = _label_parser.parse(ocr_text)
                                    pipeline_used = "OCR + NutritionParser v4"
                                except Exception as e:
                                    st.error(f"❌ Parser failed: {e}")

                    if nutrition_data:
                        st.session_state["scan_label_data"] = nutrition_data
                        st.session_state["scan_pipeline_used"] = pipeline_used
                    else:
                        st.error("❌ Could not extract nutrition values from this image.")
                        st.info(
                            "**Tips:** Ensure the nutrition facts panel is clearly visible, "
                            "well-lit, and not at an angle. Try the **✏️ Manual Entry** tab."
                        )

                if st.session_state.get("scan_label_data"):
                    st.success(
                        f"Extracted successfully!")
                    _display_label_results(st.session_state["scan_label_data"])

        with tab2:
            st.markdown("**Enter nutrition values manually from the label (per 100g):**")
            c1, c2, c3 = st.columns(3)
            with c1:
                energy_100 = st.number_input("Energy (kcal/100g)", min_value=0.0, value=200.0)
                protein_100 = st.number_input("Protein (g/100g)", min_value=0.0, value=5.0)
                carbs_100 = st.number_input("Carbs (g/100g)", min_value=0.0, value=30.0)
                fiber_100 = st.number_input("Fiber (g/100g)", min_value=0.0, value=2.0)
            with c2:
                fat_100 = st.number_input("Total Fat (g/100g)", min_value=0.0, value=8.0)
                sat_fat_100 = st.number_input("Saturated Fat (g/100g)", min_value=0.0, value=3.0)
                sugar_100 = st.number_input("Sugar (g/100g)", min_value=0.0, value=5.0)
                sodium_100 = st.number_input("Sodium (mg/100g)", min_value=0.0, value=300.0)
            with c3:
                serving_size = st.number_input("Serving Size (g)", min_value=1.0, value=30.0)
                energy_srv = st.number_input("Energy (kcal/serving)", min_value=0.0, value=60.0)
                protein_srv = st.number_input("Protein (g/serving)", min_value=0.0, value=1.5)
                carbs_srv = st.number_input("Carbs (g/serving)", min_value=0.0, value=9.0)

            if st.button("🔬 Analyze Label Data", type="primary", use_container_width=True):
                st.session_state["manual_label_data"] = {
                    "energy_kcal_per_100g": energy_100,
                    "protein_g": protein_100,
                    "carbohydrates_g": carbs_100,
                    "fiber_g": fiber_100,
                    "total_fat_g": fat_100,
                    "saturated_fat_g": sat_fat_100,
                    "sugar_g": sugar_100,
                    "sodium_mg": sodium_100,
                    "serving_size": serving_size,
                    "serving_unit": "g",
                    "energy_kcal_per_serving": energy_srv,
                    "protein_per_serving_g": protein_srv,
                    "carbs_per_serving_g": carbs_srv,
                    "fat_per_serving_g": fat_100 * serving_size / 100,
                    "sodium_per_serving_mg": sodium_100 * serving_size / 100,
                }
                st.rerun()

    # ── Show manual label results OUTSIDE the tabs block so they persist after rerun ──
    if st.session_state.get("manual_label_data"):
        st.markdown("---")
        st.markdown("### 📊 Manual Entry — Nutritional Results")
        if st.button("🗑️ Clear Results", key="clear_manual_label"):
            del st.session_state["manual_label_data"]
            st.rerun()
        else:
            _display_label_results(st.session_state["manual_label_data"])

# ------ NUTRITION SEARCH ------
elif page == "🔎 Nutrition Search":
    st.title("🔎 Nutrition Search")
    st.markdown(
        "Search our multi-source nutrition database (FrequentedData, IRD & USDA) "
        "using smart fuzzy matching — word order and exact spelling don't matter."
    )

    if comp2_error:
        st.error(f"❌ Nutrition DB not available: {comp2_error}")
        st.info(
            "**To enable this feature:**\n"
            "1. Create a `data_extraction_estimation/` folder next to `NutriUI_intigrated.py`\n"
            "2. Place `Estimation_Search.py` and `__init__.py` inside it\n"
            "3. Place `FrequentedData.csv` in the root folder\n"
            "4. Create `module_2_datasets/` and place `IRD.csv` and `USDA.csv` inside it\n"
            "5. Restart the app"
        )
    else:
        st.success(" ")

        search_tab, bulk_tab, compare_tab = st.tabs(
            ["🔍 Single Item Search", "📋 Bulk Lookup", "⚖️ Compare Items"]
        )

        with search_tab:
            st.markdown("### 🍽️ Search for a food item")
            col_input, col_btn = st.columns([4, 1])
            with col_input:
                query = st.text_input(
                    "Food name",
                    placeholder="e.g. chicken curry, fried rice, pol sambol…",
                    label_visibility="collapsed"
                )
            with col_btn:
                search_btn = st.button("🔍 Search", type="primary", use_container_width=True)

            with st.expander("⚡ Quick search — common Sri Lankan items"):
                available = [
                    # Rice & Rice Dishes
                    "White rice", "Red rice", "Yellow rice", "Fried rice", "Kiribath", "Kottu",
                    # Bread & Roti
                    "Coconut roti", "Pol sambol", "Lunu sambol",
                    # Hoppers & String Hoppers
                    "Hoppers", "String hoppers", "Pittu",
                    # Curries - Vegetable
                    "Beans curry", "Beetroot curry", "Cabbage curry", "Carrot curry", "Cashew curry",
                    "Dhal curry", "Egg curry", "Fish curry", "Gotukola mallum", "Moringa curry",
                    "Mango curry", "Okra curry", "Polos curry", "Potato curry",
                    "Soya curry",
                    # Curries - Meat & Seafood
                    "Chicken curry", "Prawns curry", "Sprats curry",
                    # Snacks & Appetizers
                    "Papadam", "Wade",
                    # Fried items (what your model detects)
                    "cutlets", "patties", "rolls",
                    # Baked items
                    "fish buns", "pastries",
                    # Baked sweet buns
                    "kibula", "cream buns",
                    # Other
                    "Sausage hotdog",
                    # Desserts & Sweets
                    "Watalappam", "donuts", "éclairs", "cake slices", "brownies"
                ]
                btn_cols = st.columns(5)
                for i, item in enumerate(available):
                    if btn_cols[i % 5].button(item, key=f"quick_{i}", use_container_width=True):
                        query = item
                        search_btn = True

            if search_btn and query:
                with st.spinner(f"🔍 Searching for **{query}**…"):
                    result = comp2_lookup(query)

                if result is None:
                    st.session_state.pop("search_result", None)
                    st.session_state.pop("search_query", None)
                    st.error(f" **'{query}'** was not found in any database.")
                    st.info(
                        " Try a simpler name, e.g. 'chicken curry' instead of 'spicy chicken curry with coconut milk'.")
                else:
                    st.session_state["search_result"] = result
                    st.session_state["search_query"] = query

            # ── Show results from session state so they persist after Log button rerun ──
            result = st.session_state.get("search_result")
            if result:
                matched_name = result.get("Description", st.session_state.get("search_query", ""))
                st.success(f"Found: **{matched_name}**")
                if st.session_state.get("search_log_success"):
                    st.success(st.session_state.pop("search_log_success"))

                if st.session_state.get("user_id"):
                    if st.button("📝 Log to Today's Food Diary", key="log_search_item"):
                        log_food(
                            st.session_state.user_id, matched_name,
                            map_comp2_to_log(result), source="search"
                        )
                        st.session_state["search_log_success"] = f"✅ '{matched_name}' added to today's food log!"
                        st.rerun()

                c1, c2, c3, c4, c5 = st.columns(5)
                metrics = [
                    (c1, "🔥", result.get("Calories", 0), "Calories (kcal)"),
                    (c2, "💪", result.get("Proteins (g)", 0), "Protein (g)"),
                    (c3, "🍞", result.get("Carbohydrates (g)", 0), "Carbs (g)"),
                    (c4, "🥑", result.get("Fats (g)", 0), "Fats (g)"),
                    (c5, "🧂", result.get("Sodium (mg)", 0), "Sodium (mg)"),
                ]
                for col, emoji, val, label in metrics:
                    with col:
                        try:
                            display = f"{float(val or 0):.1f}"
                        except (ValueError, TypeError):
                            display = "—"
                        st.markdown(
                            f'<div class="metric-card">'
                            f'<div style="font-size:1.6rem">{emoji}</div>'
                            f'<div class="metric-value" style="font-size:1.6rem">{display}</div>'
                            f'<div class="metric-label">{label}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                st.write("")
                col_chart, col_micro = st.columns(2)
                with col_chart:
                    st.markdown("#### 🥗 Macro Distribution")
                    macro_df = pd.DataFrame({
                        "Nutrient": ["Protein", "Carbohydrates", "Fats"],
                        "Amount": [
                            float(result.get("Proteins (g)", 0) or 0),
                            float(result.get("Carbohydrates (g)", 0) or 0),
                            float(result.get("Fats (g)", 0) or 0),
                        ]
                    })
                    st.plotly_chart(create_nutrition_pie_chart(macro_df), use_container_width=True)

                with col_micro:
                    st.markdown("#### 💊 Key Micronutrients")
                    micro_keys = ["Calcium (mg)", "Iron (mg)", "Zinc (mg)",
                                  "Vitamin C (mg)", "Vitamin D (µg)", "Vitamin B12 (µg)"]
                    micro_df = pd.DataFrame({
                        "Nutrient": micro_keys,
                        "Amount": [float(result.get(k, 0) or 0) for k in micro_keys]
                    })
                    fig_micro = go.Figure(go.Bar(
                        x=micro_df["Nutrient"], y=micro_df["Amount"],
                        marker_color=[PASTEQUE, LAGOON, MELON, ZESTE, PASTEQUE, LAGOON],
                        text=[f"{v:.2f}" for v in micro_df["Amount"]],
                        textposition="outside"
                    ))
                    fig_micro.update_layout(
                        height=300, showlegend=False,
                        paper_bgcolor=CARD_BG, plot_bgcolor=PLOT_BG,
                        font={"color": FONT_CLR, "family": "Nunito"},
                        yaxis=dict(showgrid=True, gridcolor=GRID_CLR),
                        margin=dict(l=20, r=20, t=20, b=60)
                    )
                    st.plotly_chart(fig_micro, use_container_width=True)

                with st.expander(" Full Nutrient Profile"):
                    rows = [
                        {"Nutrient": k, "Value": v}
                        for k, v in result.items() if k != "Description"
                    ]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        with bulk_tab:
            st.markdown("###  Look up multiple food items at once")
            st.markdown("Enter one food item per line:")
            auto_foods = "\n".join(st.session_state.pop("redirect_to_bulk", []))
            bulk_input = st.text_area(
                "Food items",
                value=auto_foods,
                placeholder="Chicken curry\nWhite rice\nPol sambol\nDhal curry",
                height=160,
                label_visibility="collapsed"
            )
            if st.button(" Look Up All Items", type="primary", use_container_width=True):
                items = [ln.strip() for ln in bulk_input.strip().splitlines() if ln.strip()]
                if not items:
                    st.warning("Please enter at least one food item.")
                else:
                    with st.spinner(f"Looking up {len(items)} items…"):
                        found, not_found = comp2_lookup_bulk(items)
                    st.session_state["bulk_found"] = found
                    st.session_state["bulk_not_found"] = not_found
                    st.session_state["bulk_items_count"] = len(items)
                    st.rerun()

            # ── Show bulk results from session state so they persist after Log button rerun ──
            found = st.session_state.get("bulk_found")
            not_found = st.session_state.get("bulk_not_found", [])
            bulk_items_count = st.session_state.get("bulk_items_count", 0)

            if found is not None:
                if st.session_state.get("bulk_log_success"):
                    st.success(st.session_state.pop("bulk_log_success"))

                if not_found:
                    st.markdown(
                        f"<div style='background:#fff3cd;border:2px solid #ffc107;"
                        f"border-radius:12px;padding:12px 18px;color:#1C2B2A;"
                        f"font-weight:600;font-size:0.9rem;'>"
                        f" Not found ({len(not_found)}): {', '.join(not_found)}</div>",
                        unsafe_allow_html=True
                    )
                    st.write("")

                if found:
                    totals = aggregate_comp2_nutrition(found)
                    st.subheader(f"Found {len(found)} / {bulk_items_count} items")

                    if st.session_state.get("user_id"):
                        if st.button("📝 Log All Found Items to Today's Diary", key="log_bulk"):
                            for entry in found:
                                log_food(st.session_state.user_id, entry["food"],
                                         map_comp2_to_log(entry["data"]), source="search")
                            st.session_state["bulk_log_success"] = f"✅ {len(found)} items logged to your diary!"
                            st.rerun()

                    c1, c2, c3, c4 = st.columns(4)
                    for col, emoji, key, label in [
                        (c1, "🔥", "Calories", "Total Calories"),
                        (c2, "💪", "Proteins (g)", "Total Protein (g)"),
                        (c3, "🍞", "Carbohydrates (g)", "Total Carbs (g)"),
                        (c4, "🥑", "Fats (g)", "Total Fats (g)"),
                    ]:
                        with col:
                            st.markdown(
                                f'<div class="metric-card">'
                                f'<div style="font-size:1.6rem">{emoji}</div>'
                                f'<div class="metric-value" style="font-size:1.6rem">{totals[key]:.1f}</div>'
                                f'<div class="metric-label">{label}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                    st.write("")
                    st.subheader("📋 Item Breakdown")
                    rows = []
                    for entry in found:
                        d = entry["data"]
                        rows.append({
                            "Food Item": entry["food"],
                            "Matched As": d.get("Description", entry["food"]),
                            "Calories": f'{float(d.get("Calories", 0) or 0):.1f}',
                            "Protein (g)": f'{float(d.get("Proteins (g)", 0) or 0):.1f}',
                            "Carbs (g)": f'{float(d.get("Carbohydrates (g)", 0) or 0):.1f}',
                            "Fats (g)": f'{float(d.get("Fats (g)", 0) or 0):.1f}',
                            "Sodium (mg)": f'{float(d.get("Sodium (mg)", 0) or 0):.1f}',
                            "Iron (mg)": f'{float(d.get("Iron (mg)", 0) or 0):.2f}',
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                    macro_df = pd.DataFrame({
                        "Nutrient": ["Protein", "Carbohydrates", "Fats"],
                        "Amount": [totals["Proteins (g)"], totals["Carbohydrates (g)"], totals["Fats (g)"]]
                    })
                    st.plotly_chart(create_nutrition_pie_chart(macro_df), use_container_width=True)

        with compare_tab:
            st.markdown("### ⚖️ Compare nutritional profiles side-by-side")
            col_a, col_b = st.columns(2)
            with col_a:
                item_a = st.text_input("Food Item A", placeholder="e.g. White rice", key="cmp_a")
            with col_b:
                item_b = st.text_input("Food Item B", placeholder="e.g. Red rice", key="cmp_b")

            if st.button("⚖️ Compare", type="primary", use_container_width=True):
                if not item_a or not item_b:
                    st.warning("Please enter both food items.")
                else:
                    with st.spinner("Looking up both items…"):
                        data_a = comp2_lookup(item_a)
                        data_b = comp2_lookup(item_b)

                    missing = [n for n, d in [(item_a, data_a), (item_b, data_b)] if d is None]
                    if missing:
                        st.error(f"❌ Not found: {', '.join(missing)}")
                    else:
                        name_a = data_a.get("Description", item_a)
                        name_b = data_b.get("Description", item_b)

                        st.success(f"Comparing **{name_a}** vs **{name_b}**")

                        compare_keys = [
                            "Calories", "Proteins (g)", "Carbohydrates (g)", "Fats (g)",
                            "Sodium (mg)", "Calcium (mg)", "Iron (mg)", "Zinc (mg)",
                            "Vitamin C (mg)", "Vitamin D (µg)", "Vitamin B12 (µg)",
                            "SFA (g)", "MUFA (g)", "PUFA (g)"
                        ]
                        vals_a = [float(data_a.get(k, 0) or 0) for k in compare_keys]
                        vals_b = [float(data_b.get(k, 0) or 0) for k in compare_keys]

                        fig_cmp = go.Figure()
                        fig_cmp.add_trace(go.Bar(
                            name=name_a, y=compare_keys, x=vals_a,
                            orientation="h", marker_color=PASTEQUE,
                            text=[f"{v:.2f}" for v in vals_a], textposition="outside"
                        ))
                        fig_cmp.add_trace(go.Bar(
                            name=name_b, y=compare_keys, x=vals_b,
                            orientation="h", marker_color=LAGOON,
                            text=[f"{v:.2f}" for v in vals_b], textposition="outside"
                        ))
                        fig_cmp.update_layout(
                            barmode="group", height=520,
                            paper_bgcolor=CARD_BG, plot_bgcolor=PLOT_BG,
                            font={"color": FONT_CLR, "family": "Nunito"},
                            xaxis=dict(showgrid=True, gridcolor=GRID_CLR),
                            yaxis=dict(showgrid=False),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            margin=dict(l=180, r=100, t=60, b=40)
                        )
                        st.plotly_chart(fig_cmp, use_container_width=True)

                        st.subheader(" Nutrient Comparison Table")
                        cmp_rows = []
                        for key, va, vb in zip(compare_keys, vals_a, vals_b):
                            winner = "—"
                            if va > vb:
                                winner = f"⬆️ {name_a}"
                            elif vb > va:
                                winner = f"⬆️ {name_b}"
                            cmp_rows.append({
                                "Nutrient": key,
                                name_a: f"{va:.2f}",
                                name_b: f"{vb:.2f}",
                                "Higher In": winner
                            })
                        st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True, hide_index=True)


# ------ TODAY'S FOOD LOG ------
elif page == "🗓️ Today's Food Log":
    st.title("🗓️ Today's Food Log")
    user_id = st.session_state.user_id
    today = date.today().isoformat()

    st.markdown(f"**Date:** {today}")

    # Activity minutes input
    col_act, _ = st.columns([2, 3])
    with col_act:
        act_min = st.number_input("Physical Activity today (minutes)", min_value=0, max_value=600, value=45, step=5)
        if st.button("💾 Save Activity", key="save_act"):
            update_daily_activity(user_id, act_min)
            st.success("Activity saved!")

    st.markdown("---")

    # Today's summary
    summary = get_daily_summary(user_id, today)
    if summary and summary["item_count"] > 0:
        st.subheader("📊 Today's Totals")
        c1, c2, c3, c4, c5 = st.columns(5)
        for col, emoji, val, lbl in [
            (c1, "🔥", f'{summary["total_calories"]:.0f}', "Calories"),
            (c2, "💪", f'{summary["total_protein_g"]:.1f}g', "Protein"),
            (c3, "🍞", f'{summary["total_carbs_g"]:.1f}g', "Carbs"),
            (c4, "🥑", f'{summary["total_fat_g"]:.1f}g', "Fat"),
            (c5, "🧂", f'{summary["total_sodium_mg"]:.0f}mg', "Sodium"),
        ]:
            with col:
                st.markdown(
                    f'''<div class="metric-card"><div style="font-size:1.6rem">{emoji}</div>
                    <div class="metric-value" style="font-size:1.4rem">{val}</div>
                    <div class="metric-label">{lbl}</div></div>''',
                    unsafe_allow_html=True
                )

        # Run end-of-day risk prediction from DB
        st.markdown("---")
        st.subheader("Risk Assessment")
        if st.button("Run Today's Risk Assessment", type="primary"):
            if not models:
                st.error("Models not loaded. Place your .pkl files in the models/ folder and restart.")
            else:
                model_input = get_daily_summary_as_model_input(user_id, today)
                if model_input:
                    with st.spinner("Running AI prediction on today's nutrition..."):
                        predictions, bmi = run_prediction(model_input, models)
                    save_risk_assessment(user_id, predictions, bmi,
                                         input_snapshot=model_input, source="daily_summary")
                    st.success(f" Assessment saved! BMI: **{bmi}**")
                    labels = [predictions[d]["label"] for d in DISEASE_COLUMNS]
                    probs = [predictions[d]["prob_pct"] for d in DISEASE_COLUMNS]
                    st.plotly_chart(create_risk_bar_chart(labels, probs), use_container_width=True)

    st.markdown("---")

    # Manual food addition
    with st.expander("➕ Add Food Manually", expanded=True):
        st.markdown("Quickly log a food item and its nutrition:")
        mf_col1, mf_col2 = st.columns(2)
        with mf_col1:
            mf_name = st.text_input("Food Name", placeholder="e.g. Chicken Curry")
            mf_cal = st.number_input("Calories (kcal)", min_value=0.0, value=0.0)
            mf_pro = st.number_input("Protein (g)", min_value=0.0, value=0.0)
            mf_carb = st.number_input("Carbs (g)", min_value=0.0, value=0.0)
        with mf_col2:
            mf_fat = st.number_input("Fat (g)", min_value=0.0, value=0.0)
            mf_fib = st.number_input("Fiber (g)", min_value=0.0, value=0.0)
            mf_sod = st.number_input("Sodium (mg)", min_value=0.0, value=0.0)
            mf_src = st.selectbox("Source", ["manual", "search", "photo", "label"])
        if st.button("➕ Add to Log", type="primary", key="add_manual_food"):
            if mf_name:
                log_food(user_id, mf_name, {
                    "calories_kcal": mf_cal, "protein_g": mf_pro,
                    "carbs_g": mf_carb, "fat_g": mf_fat,
                    "fiber_g": mf_fib, "sodium_mg": mf_sod,
                }, source=mf_src)
                st.success(f" '{mf_name}' logged!")
                st.rerun()
            else:
                st.warning("Please enter a food name.")


# ------ MY PROFILE ------
elif page == "⚙️ My Profile":
    st.title("⚙️ My Profile")
    user_id = st.session_state.user_id
    user = get_user_by_id(user_id)
    if not user:
        st.error("Could not load profile.")
    else:
        import json as _json

        st.subheader("👤 Personal Information")
        p1, p2 = st.columns(2)
        with p1:
            up_name = st.text_input("Full Name", value=user["full_name"])
            up_email = st.text_input("Email", value=user["email"])
            up_age = st.number_input("Age", min_value=10, max_value=100, value=user["age"])
            up_gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                                     index=["Male", "Female", "Other"].index(user["gender"]))
        with p2:
            up_weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=user["weight_kg"],
                                        step=0.5)
            up_height = st.number_input("Height (cm)", min_value=80.0, max_value=250.0, value=user["height_cm"],
                                        step=0.5)
            up_water = st.number_input("Daily Water (L)", min_value=0.5, max_value=6.0, value=user["daily_water_l"],
                                       step=0.1)
            up_act = st.selectbox("Activity Level",
                                  ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Super Active"],
                                  index=["Sedentary", "Lightly Active", "Moderately Active", "Very Active",
                                         "Super Active"].index(
                                      user["activity_level"] if user["activity_level"] in
                                                                ["Sedentary", "Lightly Active", "Moderately Active",
                                                                 "Very Active", "Super Active"]
                                      else "Moderately Active"))
        up_goal = st.selectbox("Health Goal",
                               ["Weight Loss", "Muscle Gain", "Maintenance", "Improved Endurance", "General Health"],
                               index=["Weight Loss", "Muscle Gain", "Maintenance", "Improved Endurance",
                                      "General Health"].index(
                                   user["goal"] if user["goal"] in
                                                   ["Weight Loss", "Muscle Gain", "Maintenance", "Improved Endurance",
                                                    "General Health"]
                                   else "Maintenance"))
        up_cond = st.multiselect("Existing Conditions",
                                 ["None", "Diabetes", "Hypertension", "Heart Disease", "Obesity", "Anemia",
                                  "Kidney Disease", "Thyroid"],
                                 default=_json.loads(user["conditions"] or '["None"]'))
        up_diet = st.selectbox("Dietary Preference",
                               ["No Restriction", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Gluten-Free"],
                               index=["No Restriction", "Vegetarian", "Vegan", "Pescatarian", "Keto",
                                      "Gluten-Free"].index(
                                   user["diet_type"] if user["diet_type"] in
                                                        ["No Restriction", "Vegetarian", "Vegan", "Pescatarian", "Keto",
                                                         "Gluten-Free"]
                                   else "No Restriction"))

        if st.button("💾 Save Profile", type="primary"):
            ok = update_user_profile(user_id,
                                     full_name=up_name, email=up_email, age=int(up_age), gender=up_gender,
                                     weight_kg=float(up_weight), height_cm=float(up_height),
                                     daily_water_l=float(up_water), activity_level=up_act,
                                     goal=up_goal, conditions=up_cond, diet_type=up_diet)
            if ok:
                # Refresh session profile
                updated = get_user_by_id(user_id)
                st.session_state.user_profile.update({
                    "full_name": updated["full_name"],
                    "first_name": updated["full_name"].split()[0],
                    "email": updated["email"],
                    "age": updated["age"],
                    "gender": updated["gender"],
                    "weight_kg": updated["weight_kg"],
                    "height_cm": updated["height_cm"],
                    "activity": updated["activity_level"],
                    "goal": updated["goal"],
                    "daily_water_l": updated["daily_water_l"],
                })
                st.success(" Profile updated!")
            else:
                st.error("Update failed.")
# ------ MONTHLY REPORT ------
elif page == "📅 Monthly Report":
    st.title("📅 Monthly Nutrition Report")

    user_id = st.session_state.user_id

    # Month selector
    col_m, col_y, _ = st.columns([1, 1, 2])
    with col_m:
        month = st.selectbox("Month", list(range(1, 13)),
                             format_func=lambda m: datetime(2026, m, 1).strftime("%B"),
                             index=date.today().month - 1)
    with col_y:
        year = st.selectbox("Year", [2025, 2026], index=1)

    # Query all food logs for selected month
    with get_db() as conn:
        rows = conn.execute("""
            SELECT scan_date,
                   SUM(calories_kcal) as cal,
                   SUM(protein_g)     as pro,
                   SUM(carbs_g)       as carb,
                   SUM(fat_g)         as fat,
                   COUNT(*)           as items
            FROM food_logs
            WHERE user_id = ?
              AND strftime('%Y', scan_date) = ?
              AND strftime('%m', scan_date) = ?
            GROUP BY scan_date
            ORDER BY scan_date ASC
        """, (user_id, str(year), f"{month:02d}")).fetchall()

    rows = [dict(r) for r in rows]

    if not rows:
        st.info(f"No food logs found for {datetime(year, month, 1).strftime('%B %Y')}. Start logging your meals!")
    else:
        month_name = datetime(year, month, 1).strftime("%B %Y")
        st.markdown(f"### 📊 Summary for {month_name}")

        # Calculate stats
        days_logged = len(rows)
        avg_cal = sum(r["cal"] for r in rows) / days_logged
        avg_pro = sum(r["pro"] for r in rows) / days_logged
        avg_carb = sum(r["carb"] for r in rows) / days_logged
        avg_fat = sum(r["fat"] for r in rows) / days_logged
        total_items = sum(r["items"] for r in rows)

        max_day = max(rows, key=lambda r: r["cal"])
        min_day = min(rows, key=lambda r: r["cal"])

        # ── Headline metrics ──
        st.markdown("#### 📈 Daily Averages")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🔥 Avg Calories", f"{avg_cal:.0f} kcal")
        with c2:
            st.metric("💪 Avg Protein", f"{avg_pro:.1f} g")
        with c3:
            st.metric("🍞 Avg Carbs", f"{avg_carb:.1f} g")
        with c4:
            st.metric("🥑 Avg Fat", f"{avg_fat:.1f} g")

        st.write("")

        # ── Key highlights ──
        st.markdown("Highlights")
        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:1.4rem">📅</div>'
                f'<div class="metric-value" style="font-size:1.6rem">{days_logged}</div>'
                f'<div class="metric-label">Days Logged</div>'
                f'</div>', unsafe_allow_html=True)
        with h2:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:1.4rem">🍽️</div>'
                f'<div class="metric-value" style="font-size:1.6rem">{total_items}</div>'
                f'<div class="metric-label">Total Foods Logged</div>'
                f'</div>', unsafe_allow_html=True)
        with h3:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:1.4rem">📊</div>'
                f'<div class="metric-value" style="font-size:1.6rem">{total_items // days_logged}</div>'
                f'<div class="metric-label">Avg Items Per Day</div>'
                f'</div>', unsafe_allow_html=True)

        st.write("")

        # ── Best and worst days ──
        st.markdown("####  Notable Days")
        nd1, nd2 = st.columns(2)
        with nd1:
            st.markdown(
                f'<div class="risk-low">'
                f'🟢 <strong>Highest Calorie Day:</strong> {max_day["scan_date"]} — '
                f'{max_day["cal"]:.0f} kcal ({max_day["items"]} items logged)'
                f'</div>', unsafe_allow_html=True)
        with nd2:
            st.markdown(
                f'<div class="risk-medium">'
                f'🟡 <strong>Lowest Calorie Day:</strong> {min_day["scan_date"]} — '
                f'{min_day["cal"]:.0f} kcal ({min_day["items"]} items logged)'
                f'</div>', unsafe_allow_html=True)

        st.write("")

        # ── Day by day table ──
        st.markdown("#### 📋 Day-by-Day Breakdown")
        table_rows = [{
            "Date": r["scan_date"],
            "Calories": f'{r["cal"]:.0f} kcal',
            "Protein (g)": f'{r["pro"]:.1f}',
            "Carbs (g)": f'{r["carb"]:.1f}',
            "Fat (g)": f'{r["fat"]:.1f}',
            "Items Logged": r["items"],
        } for r in rows]
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        # ── Simple calorie trend ──
        st.markdown("#### 📈 Calorie Trend")
        dates = [r["scan_date"] for r in rows]
        cals = [r["cal"] for r in rows]
        st.plotly_chart(create_trend_chart(dates, cals, "Daily Calories", PASTEQUE),
                        use_container_width=True)
# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    <p style="font-weight:600;color:#3D3D3D">NutriScanner Pro — AI Health Intelligence</p>
    <p>© 2026 NutriScanner Inc. &nbsp;·&nbsp; <a href="#">Privacy</a> &nbsp;·&nbsp; <a href="#">Terms</a></p>
</div>
""", unsafe_allow_html=True)