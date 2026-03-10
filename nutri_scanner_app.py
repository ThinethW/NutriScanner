# ============================================================
# NUTRISCANNER - PROFESSIONAL HEALTH AI PLATFORM
# Modern Enterprise-Grade Streamlit Application
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
from pathlib import Path
import time
from datetime import datetime, timedelta

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="NutriScanner Pro | AI Health Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://nutriscanner.ai/help',
        'Report a bug': 'https://github.com/nutriscanner/issues',
        'About': "# NutriScanner Pro\nVersion 4.0.0\nAI-Powered Health Intelligence Platform"
    }
)


# ============================================================
# 2. MODERN PROFESSIONAL CSS THEME
# ============================================================
def apply_modern_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* === GLOBAL VARIABLES === */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --dark-bg: #0f0f23;
        --card-bg: #1a1a2e;
        --card-border: #2d2d44;
        --text-primary: #ffffff;
        --text-secondary: #a0a0b0;
        --success: #00d9a5;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
    }

    /* === GLOBAL STYLING === */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: var(--dark-bg) !important;
        color: var(--text-primary) !important;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
        border-right: 1px solid var(--card-border) !important;
    }

    .sidebar-brand {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        padding: 30px 0;
        border-bottom: 2px solid var(--card-border);
        margin-bottom: 30px;
    }

    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255, 255, 255, 0.05);
        margin: 8px 0;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid transparent;
        transition: all 0.3s ease;
        color: var(--text-secondary) !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(102, 126, 234, 0.2);
        border-color: #667eea;
        color: white !important;
    }

    [data-testid="stSidebar"] .stRadio input:checked + label {
        background: var(--primary-gradient);
        color: white !important;
        border-color: transparent;
    }

    /* === HEADINGS === */
    h1, h2, h3, h4 {
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    h1 {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
    }

    h2 {
        color: var(--text-primary) !important;
        font-size: 2.2rem !important;
        border-left: 4px solid #667eea;
        padding-left: 20px;
        margin: 40px 0 20px 0;
    }

    h3 {
        color: var(--text-secondary) !important;
        font-size: 1.5rem !important;
    }

    /* === CARDS === */
    .metric-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 30px;
        margin: 10px 0;
        transition: all 0.4s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }

    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }

    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 10px;
    }

    .delta-positive {
        background: rgba(0, 217, 165, 0.2);
        color: var(--success);
    }

    .delta-negative {
        background: rgba(239, 68, 68, 0.2);
        color: var(--danger);
    }

    /* === HERO SECTION === */
    .hero-banner {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border: 1px solid var(--card-border);
        border-radius: 30px;
        padding: 60px;
        margin: 30px 0;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    .hero-banner h1 {
        margin-bottom: 20px;
    }

    .hero-banner p {
        color: var(--text-secondary);
        font-size: 1.2rem;
        max-width: 600px;
        margin: 0 auto;
    }

    /* === BUTTONS === */
    .stButton>button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 32px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }

    /* === PROGRESS BARS === */
    .stProgress > div > div {
        background: var(--primary-gradient);
        border-radius: 10px;
    }

    /* === DATAFRAMES === */
    .dataframe {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 15px;
        overflow: hidden;
    }

    /* === ALERTS === */
    .stAlert {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 15px;
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--card-bg);
        border-radius: 15px;
        padding: 5px;
        gap: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        border-radius: 10px;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary-gradient);
        color: white;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }

    /* === RISK INDICATORS === */
    .risk-high {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%);
        border: 2px solid var(--danger);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }

    .risk-medium {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.1) 100%);
        border: 2px solid var(--warning);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }

    .risk-low {
        background: linear-gradient(135deg, rgba(0, 217, 165, 0.2) 0%, rgba(0, 217, 165, 0.1) 100%);
        border: 2px solid var(--success);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }

    /* === LOADING ANIMATION === */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .loading-text {
        animation: pulse 1.5s ease-in-out infinite;
    }

    /* === FOOTER === */
    .footer {
        text-align: center;
        padding: 40px 0;
        margin-top: 60px;
        border-top: 1px solid var(--card-border);
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================
def create_risk_gauge(value, title):
    """Create a gauge chart for risk assessment"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#ffffff'}},
        delta={'reference': 50, 'increasing': {'color': '#ef4444'}, 'decreasing': {'color': '#00d9a5'}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': '#ffffff'},
            'bar': {'color': "#667eea"},
            'bgcolor': '#1a1a2e',
            'borderwidth': 2,
            'bordercolor': '#2d2d44',
            'steps': [
                {'range': [0, 40], 'color': 'rgba(0, 217, 165, 0.2)'},
                {'range': [40, 60], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [60, 100], 'color': 'rgba(239, 68, 68, 0.2)'}
            ],
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='#1a1a2e',
                      font={'color': '#ffffff'})
    return fig


def create_nutrition_pie_chart(data):
    """Create modern pie chart for nutrition breakdown"""
    fig = px.pie(
        data,
        values='Amount',
        names='Nutrient',
        color='Nutrient',
        color_discrete_map={
            'Protein': '#00d9a5',
            'Carbohydrates': '#667eea',
            'Fats': '#f59e0b',
            'Fiber': '#3b82f6'
        },
        hole=0.4,
        opacity=0.9
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
    fig.update_layout(
        height=350,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        paper_bgcolor='#1a1a2e',
        font={'color': '#ffffff', 'size': 12},
        margin=dict(l=20, r=20, t=50, b=50)
    )
    return fig


def create_trend_chart(dates, values, title, color='#667eea'):
    """Create interactive trend line chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)'
    ))
    fig.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#16213e',
        font={'color': '#ffffff'},
        xaxis=dict(showgrid=True, gridcolor='#2d2d44'),
        yaxis=dict(showgrid=True, gridcolor='#2d2d44'),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig


def create_risk_bar_chart(diseases, probabilities):
    """Create horizontal bar chart for disease risks"""
    colors = ['#ef4444' if p >= 60 else '#f59e0b' if p >= 40 else '#00d9a5' for p in probabilities]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=diseases,
        x=probabilities,
        orientation='h',
        marker_color=colors,
        text=[f'{p:.1f}%' for p in probabilities],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Risk: %{x:.1f}%<extra></extra>'
    ))
    fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#16213e',
        font={'color': '#ffffff', 'size': 12},
        xaxis=dict(range=[0, 100], showgrid=True, gridcolor='#2d2d44', title='Risk Probability (%)'),
        yaxis=dict(showgrid=False, title='Disease'),
        margin=dict(l=150, r=40, t=40, b=40)
    )
    return fig


def create_radar_chart(labels, values, title):
    """Create radar chart for multi-dimensional analysis"""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        line=dict(color='#667eea', width=3),
        fillcolor='rgba(102, 126, 234, 0.3)',
        name=title
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickcolor='#ffffff',
                gridcolor='#2d2d44'
            )
        ),
        showlegend=False,
        height=350,
        paper_bgcolor='#1a1a2e',
        font={'color': '#ffffff'}
    )
    return fig


# ============================================================
# 4. APPLY STYLES
# ============================================================
apply_modern_styles()

# ============================================================
# 5. SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown('<p class="sidebar-brand">🔬 NutriScanner Pro</p>', unsafe_allow_html=True)

    st.write("")
    page = st.radio(
        "NAVIGATION",
        ["🏠 Dashboard", "🔍 Health Risk Assessment", "📊 Nutrition Analytics", "📈 Trends & Insights",
         "👤 Profile Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # User info card
    st.markdown("""
    <div class="metric-card" style="padding: 20px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 24px;">👤</div>
            <div>
                <div style="font-weight: 600; color: white;">Alex Rivers</div>
                <div style="font-size: 0.8rem; color: #a0a0b0;">Premium Member</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("📊 v4.0.0 Enterprise Edition")
    st.caption("🔒 AI Model: Active")

# ============================================================
# 6. PAGE ROUTING
# ============================================================

# === DASHBOARD ===
if page == "🏠 Dashboard":
    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <h1>Your Health Intelligence Hub</h1>
        <p>AI-powered nutrition analysis, disease risk prediction, and personalized health insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Key Metrics
    st.subheader("Today's Overview")
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2,180</div>
            <div class="metric-label">Calories</div>
            <div class="metric-delta delta-positive">↑ 12% vs avg</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">94g</div>
            <div class="metric-label">Protein</div>
            <div class="metric-delta delta-positive">↑ 8g vs goal</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">245g</div>
            <div class="metric-label">Carbs</div>
            <div class="metric-delta delta-negative">↓ 15g vs goal</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">68g</div>
            <div class="metric-label">Fats</div>
            <div class="metric-delta delta-positive">✓ On target</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2.4L</div>
            <div class="metric-label">Water</div>
            <div class="metric-delta delta-positive">↑ 95% of goal</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Main Charts Row
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📈 Weekly Nutrition Trends")
        dates = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(6)][::-1]
        calories = [1950, 2100, 1880, 2250, 2180, 2340]
        fig_trend = create_trend_chart(dates, calories, "Calories", '#667eea')
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.markdown("### 🥗 Macro Distribution")
        macro_data = pd.DataFrame({
            'Nutrient': ['Protein', 'Carbohydrates', 'Fats'],
            'Amount': [94, 245, 68]
        })
        fig_pie = create_nutrition_pie_chart(macro_data)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Risk Overview
    st.markdown("### ⚠️ Health Risk Overview")
    diseases = ['Diabetes', 'Hypertension', 'Heart Disease', 'Obesity', 'Anemia', 'Kidney']
    risks = [47.5, 25.7, 50.8, 15.2, 5.4, 13.1]
    fig_risk = create_risk_bar_chart(diseases, risks)
    st.plotly_chart(fig_risk, use_container_width=True)

    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📷 Scan Meal", use_container_width=True):
            st.switch_page("pages/2_📷_AI_Food_Scanner.py")
    with c2:
        if st.button("🔍 Risk Assessment", use_container_width=True):
            st.switch_page("pages/1_🔍_Health_Risk_Assessment.py")
    with c3:
        if st.button("📊 View Reports", use_container_width=True):
            st.switch_page("pages/3_📊_Nutrition_Analytics.py")
    with c4:
        if st.button("👤 Update Profile", use_container_width=True):
            st.switch_page("pages/4_👤_Profile_Settings.py")

# === HEALTH RISK ASSESSMENT ===
elif page == "🔍 Health Risk Assessment":
    st.title("🔍 AI Health Risk Assessment")
    st.markdown("Predict disease risks based on your nutritional profile and lifestyle")

    # Input Form
    with st.expander("📝 Enter Your Health Data", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.number_input("Age", min_value=18, max_value=100, value=35)
            gender = st.selectbox("Gender", ["Male", "Female"])
            weight = st.number_input("Weight (kg)", min_value=40, max_value=200, value=75)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=175)

        with col2:
            calories = st.number_input("Daily Calories", min_value=1000, max_value=5000, value=2200)
            protein = st.number_input("Protein (g)", min_value=20, max_value=300, value=80)
            carbs = st.number_input("Carbohydrates (g)", min_value=50, max_value=500, value=250)
            total_fat = st.number_input("Total Fat (g)", min_value=20, max_value=300, value=70)

        with col3:
            sodium = st.number_input("Sodium (mg)", min_value=500, max_value=10000, value=2300)
            fiber = st.number_input("Fiber (g)", min_value=5, max_value=100, value=25)
            activity = st.number_input("Physical Activity (min/day)", min_value=0, max_value=300, value=45)
            water = st.number_input("Water Intake (L)", min_value=0.5, max_value=5.0, value=2.0)

    if st.button("🔬 Analyze Health Risks", type="primary", use_container_width=True):
        with st.spinner("AI is analyzing your health profile..."):
            time.sleep(2)

            # Simulated predictions
            predictions = {
                'Diabetes': 47.5,
                'Hypertension': 25.7,
                'Heart Disease': 50.8,
                'Obesity': 15.2,
                'Anemia': 5.4,
                'Kidney Disease': 13.1
            }

            # Risk Gauges
            st.subheader("Risk Assessment Results")
            g1, g2, g3 = st.columns(3)
            with g1:
                st.plotly_chart(create_risk_gauge(predictions['Diabetes'], "Diabetes Risk"), use_container_width=True)
            with g2:
                st.plotly_chart(create_risk_gauge(predictions['Hypertension'], "Hypertension Risk"),
                                use_container_width=True)
            with g3:
                st.plotly_chart(create_risk_gauge(predictions['Heart Disease'], "Heart Disease Risk"),
                                use_container_width=True)

            # Risk Bar Chart
            st.subheader("All Disease Risks")
            fig = create_risk_bar_chart(list(predictions.keys()), list(predictions.values()))
            st.plotly_chart(fig, use_container_width=True)

            # Recommendations
            st.subheader(" Personalized Recommendations")
            if predictions['Diabetes'] > 40:
                st.markdown(
                    '<div class="risk-medium">⚠️ <strong>Diabetes Prevention:</strong> Reduce added sugar intake, increase fiber, and maintain regular physical activity</div>',
                    unsafe_allow_html=True)
            if predictions['Heart Disease'] > 40:
                st.markdown(
                    '<div class="risk-medium">⚠️ <strong>Heart Health:</strong> Lower saturated fat, increase omega-3, and monitor sodium intake</div>',
                    unsafe_allow_html=True)
            if predictions['Hypertension'] > 40:
                st.markdown(
                    '<div class="risk-medium">⚠️ <strong>Blood Pressure:</strong> Reduce sodium, increase potassium-rich foods, and stay hydrated</div>',
                    unsafe_allow_html=True)

# === NUTRITION ANALYTICS ===
elif page == "📊 Nutrition Analytics":
    st.title("📊 Advanced Nutrition Analytics")
    st.markdown("Deep dive into your nutritional patterns and deficiencies")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🥗 Macros", "💊 Micronutrients", "📈 Trends", "⚠️ Deficiencies"])

    with tab1:
        st.subheader("Macronutrient Breakdown")
        col1, col2 = st.columns(2)

        with col1:
            macro_data = pd.DataFrame({
                'Nutrient': ['Protein', 'Carbohydrates', 'Fats', 'Fiber'],
                'Amount': [94, 245, 68, 28],
                'Goal': [100, 275, 75, 35]
            })
            fig_pie = create_nutrition_pie_chart(macro_data)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_radar = create_radar_chart(
                ['Protein', 'Carbs', 'Fats', 'Fiber', 'Water', 'Activity'],
                [94, 89, 91, 80, 95, 75],
                "Nutrition Score"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    with tab2:
        st.subheader("Micronutrient Analysis")
        micro_data = pd.DataFrame({
            'Nutrient': ['Vitamin D', 'Vitamin B12', 'Iron', 'Calcium', 'Potassium'],
            'Intake': [600, 2.4, 12, 800, 3200],
            'Recommended': [800, 3.0, 18, 1000, 4700]
        })

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Intake',
            y=micro_data['Nutrient'],
            x=micro_data['Intake'],
            orientation='h',
            marker_color='#667eea'
        ))
        fig.add_trace(go.Bar(
            name='Recommended',
            y=micro_data['Nutrient'],
            x=micro_data['Recommended'],
            orientation='h',
            marker_color='#2d2d44'
        ))
        fig.update_layout(
            barmode='group',
            height=400,
            paper_bgcolor='#1a1a2e',
            font={'color': '#ffffff'},
            xaxis=dict(showgrid=True, gridcolor='#2d2d44'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("30-Day Nutrition Trends")
        dates = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(29)][::-1]

        tab3_1, tab3_2 = st.tabs(["Calories", "Macros"])
        with tab3_1:
            calories_trend = np.random.randint(1800, 2500, 30).tolist()
            fig = create_trend_chart(dates, calories_trend, "Daily Calories", '#667eea')
            st.plotly_chart(fig, use_container_width=True)

        with tab3_2:
            protein_trend = np.random.randint(70, 120, 30).tolist()
            fig = create_trend_chart(dates, protein_trend, "Protein (g)", '#00d9a5')
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Nutrient Deficiency Alerts")

        st.markdown(
            '<div class="risk-medium">⚠️ <strong>Vitamin D:</strong> Your intake (600 IU) is below recommended (800 IU). Consider sunlight exposure or supplementation</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="risk-medium">⚠️ <strong>Iron:</strong> Your intake (12mg) is below recommended (18mg). Include more red meat, spinach, or fortified cereals</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="risk-low">✅ <strong>Calcium:</strong> Good intake! Keep consuming dairy and leafy greens</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="risk-low">✅ <strong>Potassium:</strong> Excellent! Your intake supports healthy blood pressure</div>',
            unsafe_allow_html=True)

# === TRENDS & INSIGHTS ===
elif page == "📈 Trends & Insights":
    st.title("📈 Trends & AI Insights")
    st.markdown("Long-term health patterns and predictive analytics")

    # Time Range Selector
    col1, col2 = st.columns([3, 1])
    with col1:
        time_range = st.slider("Select Time Range", 7, 90, 30, label_visibility="collapsed")
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    # Key Insights
    st.subheader("🧠 AI-Generated Insights")
    insights = [
        ("📈 Calorie Trend", "Your average calorie intake increased by 8% over the past 2 weeks", "positive"),
        ("💪 Protein Goal", "You've met your protein target 18 out of 30 days", "positive"),
        ("⚠️ Sodium Alert", "Sodium intake is 40% above recommended levels on weekends", "warning"),
        ("💧 Hydration", "Water intake consistency improved by 25% this month", "positive")
    ]

    for title, desc, status in insights:
        if status == "positive":
            st.markdown(f'<div class="risk-low"><strong>{title}:</strong> {desc}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="risk-medium"><strong>{title}:</strong> {desc}</div>', unsafe_allow_html=True)

    # Correlation Heatmap
    st.subheader("🔗 Nutrient Correlation Analysis")
    corr_data = pd.DataFrame(
        np.random.rand(6, 6),
        columns=['Calories', 'Protein', 'Carbs', 'Fat', 'Sodium', 'Fiber'],
        index=['Calories', 'Protein', 'Carbs', 'Fat', 'Sodium', 'Fiber']
    )

    fig_corr = px.imshow(
        corr_data,
        color_continuous_scale='RdBu_r',
        aspect='auto',
        text_auto='.2f'
    )
    fig_corr.update_layout(
        height=500,
        paper_bgcolor='#1a1a2e',
        font={'color': '#ffffff'}
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# === PROFILE SETTINGS ===
elif page == "👤 Profile Settings":
    st.title("👤 Profile Settings")
    st.markdown("Manage your health profile and preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Personal Information")
        st.text_input("Full Name", "Alex Rivers")
        st.number_input("Age", min_value=18, max_value=100, value=30)
        st.selectbox("Gender", ["Male", "Female", "Other"])
        st.number_input("Weight (kg)", min_value=40, max_value=200, value=75)
        st.number_input("Height (cm)", min_value=100, max_value=250, value=180)

    with col2:
        st.subheader("Health Goals")
        st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Athlete"])
        st.selectbox("Primary Goal", ["Weight Loss", "Muscle Gain", "Maintenance", "Better Health"])
        st.multiselect("Dietary Preferences", ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", "Paleo"])
        st.number_input("Daily Calorie Goal", min_value=1000, max_value=5000, value=2200)

    st.markdown("---")

    st.subheader("Notification Preferences")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.checkbox("Daily Reminders", value=True)
    with c2:
        st.checkbox("Weekly Reports", value=True)
    with c3:
        st.checkbox("Risk Alerts", value=True)

    st.markdown("---")

    if st.button("💾 Save Changes", type="primary", use_container_width=True):
        st.success("✅ Profile updated successfully!")
        st.balloons()

# ============================================================
# 7. FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    <p>🔬 NutriScanner Pro v4.0.0 | AI-Powered Health Intelligence Platform</p>
    <p>© 2026 NutriScanner Inc. | <a href="#" style="color: #667eea;">Privacy Policy</a> | <a href="#" style="color: #667eea;">Terms of Service</a></p>
</div>
""", unsafe_allow_html=True)