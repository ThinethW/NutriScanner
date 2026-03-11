# ============================================================
# NUTRISCANNER - PROFESSIONAL HEALTH AI PLATFORM
# Modern Enterprise-Grade Streamlit Application
# 🍊 DARK CREAM, ORANGE & GREEN THEME 🌿
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import time
from datetime import datetime, timedelta

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
# 2. DARK CREAM, ORANGE & GREEN CSS THEME
# ============================================================
def apply_modern_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* === GLOBAL VARIABLES - DARK CREAM, ORANGE & GREEN PALETTE === */
    :root {
        --primary-gradient: linear-gradient(135deg, #F97316 0%, #C2410C 100%);
        --secondary-gradient: linear-gradient(135deg, #22C55E 0%, #15803D 100%);
        --accent-gradient: linear-gradient(135deg, #FB923C 0%, #EA580C 100%);
        --warm-gradient: linear-gradient(135deg, #44372A 0%, #362C22 100%);

        --bg-darkest: #1C1612;
        --bg-darker: #251E18;
        --bg-dark: #2E251D;
        --bg-medium: #3D3128;
        --bg-light: #4A3C31;

        --card-bg: #332922;
        --card-bg-hover: #3D3128;
        --card-border: #4A3C31;
        --card-border-hover: #5C4A3A;
        --card-shadow: rgba(249, 115, 22, 0.15);

        --text-primary: #FAF5F0;
        --text-secondary: #D4C4B5;
        --text-muted: #A89585;
        --text-light: #8B7A6B;

        --orange-300: #FDBA74;
        --orange-400: #FB923C;
        --orange-500: #F97316;
        --orange-600: #EA580C;
        --orange-700: #C2410C;

        --green-400: #4ADE80;
        --green-500: #22C55E;
        --green-600: #16A34A;
        --green-700: #15803D;

        --success: #22C55E;
        --success-light: rgba(34, 197, 94, 0.2);
        --warning: #F97316;
        --warning-light: rgba(249, 115, 22, 0.2);
        --danger: #EF4444;
        --danger-light: rgba(239, 68, 68, 0.2);
        --info: #0EA5E9;
        --info-light: rgba(14, 165, 233, 0.2);
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background: linear-gradient(180deg, var(--bg-darkest) 0%, var(--bg-darker) 100%) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent !important;
    }

    .main .block-container {
        background: transparent !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E251D 0%, #251E18 50%, #1C1612 100%) !important;
        border-right: 2px solid var(--card-border) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    .sidebar-brand {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        padding: 30px 0;
        border-bottom: 2px solid var(--card-border);
        margin-bottom: 30px;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(74, 60, 49, 0.5) !important;
        margin: 4px 0 !important;
        padding: 15px 20px !important;
        border-radius: 14px !important;
        border: 2px solid transparent !important;
        transition: all 0.3s ease !important;
        color: var(--text-secondary) !important;
        backdrop-filter: blur(10px);
        cursor: pointer;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(249, 115, 22, 0.15) !important;
        border-color: var(--orange-500) !important;
        color: var(--orange-300) !important;
        transform: translateX(5px);
    }

    p, span, div, label, .stMarkdown, .stText {
        color: var(--text-primary) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        color: var(--text-primary) !important;
    }

    h1 {
        background: var(--primary-gradient) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-size: 3.5rem !important;
    }

    h2 {
        color: var(--text-primary) !important;
        font-size: 2.2rem !important;
        border-left: 5px solid var(--orange-500) !important;
        padding-left: 20px !important;
        margin: 40px 0 20px 0 !important;
        -webkit-text-fill-color: var(--text-primary) !important;
    }

    h3 {
        color: var(--text-secondary) !important;
        font-size: 1.5rem !important;
        -webkit-text-fill-color: var(--text-secondary) !important;
    }

    .metric-card {
        background: linear-gradient(145deg, #3D3128 0%, #332922 100%);
        border: 2px solid var(--card-border);
        border-radius: 24px;
        padding: 28px;
        margin: 10px 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 50px rgba(249, 115, 22, 0.25);
        border-color: var(--orange-500);
    }

    .metric-card:hover::before {
        opacity: 1;
    }

    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }

    .metric-label {
        color: var(--text-muted) !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 8px;
        font-weight: 600;
    }

    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 25px;
        display: inline-block;
        margin-top: 12px;
    }

    .delta-positive {
        background: var(--success-light);
        color: var(--green-400) !important;
    }

    .delta-negative {
        background: var(--danger-light);
        color: #F87171 !important;
    }

    .hero-banner {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.12) 0%, rgba(194, 65, 12, 0.08) 50%, rgba(34, 197, 94, 0.1) 100%);
        border: 2px solid var(--card-border);
        border-radius: 32px;
        padding: 60px;
        margin: 30px 0;
        text-align: center;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }

    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(249, 115, 22, 0.08) 0%, transparent 50%);
        animation: float 15s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(30px, -30px) rotate(120deg); }
        66% { transform: translate(-20px, 20px) rotate(240deg); }
    }

    .hero-banner h1 {
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
    }

    .hero-banner p {
        color: var(--text-secondary) !important;
        font-size: 1.2rem;
        max-width: 600px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }

    .stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 32px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(249, 115, 22, 0.4) !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(249, 115, 22, 0.5) !important;
    }

    .stProgress > div > div {
        background: var(--primary-gradient) !important;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 6px;
        gap: 6px;
        border: 2px solid var(--card-border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-muted) !important;
        border-radius: 12px;
        padding: 12px 24px;
        transition: all 0.3s ease;
        font-weight: 500;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--warning-light);
        color: var(--orange-300) !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary-gradient) !important;
        color: white !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--bg-medium) !important;
        border: 2px solid var(--card-border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
        padding: 12px 16px !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--orange-500) !important;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.2) !important;
        background: var(--bg-light) !important;
    }

    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stMultiSelect label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-medium) !important;
        border: 2px solid var(--card-border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--orange-500) !important;
    }

    .stSlider > div > div > div > div {
        background: var(--primary-gradient) !important;
    }

    .stSlider label {
        color: var(--text-primary) !important;
    }

    .stCheckbox > label {
        color: var(--text-primary) !important;
    }

    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-darker);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--orange-500), var(--orange-600));
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--orange-400), var(--orange-500));
    }

    .risk-high {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.08) 100%);
        border: 2px solid #EF4444;
        border-radius: 18px;
        padding: 22px 28px;
        margin: 14px 0;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.15);
    }

    .risk-medium {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(249, 115, 22, 0.08) 100%);
        border: 2px solid var(--orange-500);
        border-radius: 18px;
        padding: 22px 28px;
        margin: 14px 0;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 20px rgba(249, 115, 22, 0.15);
    }

    .risk-low {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.08) 100%);
        border: 2px solid var(--green-500);
        border-radius: 18px;
        padding: 22px 28px;
        margin: 14px 0;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 20px rgba(34, 197, 94, 0.15);
    }

    .risk-high strong, .risk-medium strong, .risk-low strong {
        color: var(--text-primary) !important;
    }

    .stSuccess {
        background: var(--success-light) !important;
        border-left: 4px solid var(--success) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    .stCaption, caption, figcaption {
        color: var(--text-muted) !important;
    }

    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--card-border), transparent);
        margin: 30px 0;
    }

    .footer {
        text-align: center;
        padding: 40px 0;
        margin-top: 60px;
        border-top: 2px solid var(--card-border);
        color: var(--text-muted) !important;
        font-size: 0.9rem;
        background: linear-gradient(180deg, transparent 0%, rgba(249, 115, 22, 0.05) 100%);
    }

    .footer p {
        color: var(--text-muted) !important;
    }

    .footer a {
        color: var(--orange-400) !important;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s ease;
    }

    .footer a:hover {
        color: var(--orange-300) !important;
    }

    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 3. HELPER FUNCTIONS - FIXED FOR PLOTLY COMPATIBILITY
# ============================================================
def create_risk_gauge(value, title):
    """Create a gauge chart for risk assessment"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#FAF5F0'}},
        delta={'reference': 50, 'increasing': {'color': '#EF4444'}, 'decreasing': {'color': '#22C55E'}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': '#D4C4B5', 'tickfont': {'color': '#D4C4B5'}},
            'bar': {'color': "#F97316"},
            'bgcolor': '#2E251D',
            'borderwidth': 2,
            'bordercolor': '#4A3C31',
            'steps': [
                {'range': [0, 40], 'color': 'rgba(34, 197, 94, 0.25)'},
                {'range': [40, 60], 'color': 'rgba(249, 115, 22, 0.25)'},
                {'range': [60, 100], 'color': 'rgba(239, 68, 68, 0.25)'}
            ],
        }
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='#332922',
        font={'color': '#FAF5F0'}
    )
    return fig


def create_nutrition_pie_chart(data):
    """Create modern pie chart for nutrition breakdown"""
    fig = px.pie(
        data,
        values='Amount',
        names='Nutrient',
        color='Nutrient',
        color_discrete_map={
            'Protein': '#22C55E',
            'Carbohydrates': '#F97316',
            'Fats': '#FDBA74',
            'Fiber': '#16A34A'
        },
        hole=0.45,
        opacity=0.95
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12,
        textfont_color='#FAF5F0',
        marker=dict(line=dict(color='#332922', width=3))
    )
    fig.update_layout(
        height=350,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color='#D4C4B5', size=12)
        ),
        paper_bgcolor='#332922',
        font={'color': '#FAF5F0', 'size': 12},
        margin=dict(l=20, r=20, t=50, b=50)
    )
    return fig


def create_trend_chart(dates, values, title, color='#F97316'):
    """Create interactive trend line chart"""
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3, shape='spline'),
        marker=dict(size=10, color=color, line=dict(color='#332922', width=2)),
        fill='tozeroy',
        fillcolor=f'rgba({r}, {g}, {b}, 0.2)'
    ))
    fig.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor='#332922',
        plot_bgcolor='#2E251D',
        font={'color': '#FAF5F0'},
        xaxis=dict(
            showgrid=True,
            gridcolor='#4A3C31',
            linecolor='#4A3C31',
            tickfont=dict(color='#D4C4B5')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#4A3C31',
            linecolor='#4A3C31',
            tickfont=dict(color='#D4C4B5')
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig


def create_risk_bar_chart(diseases, probabilities):
    """Create horizontal bar chart for disease risks"""
    colors = ['#EF4444' if p >= 60 else '#F97316' if p >= 40 else '#22C55E' for p in probabilities]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=diseases,
        x=probabilities,
        orientation='h',
        marker_color=colors,
        marker_line=dict(color='#332922', width=2),
        text=[f'{p:.1f}%' for p in probabilities],
        textposition='outside',
        textfont=dict(color='#FAF5F0', size=13, family='Plus Jakarta Sans'),
        hovertemplate='<b>%{y}</b><br>Risk: %{x:.1f}%<extra></extra>'
    ))
    fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='#332922',
        plot_bgcolor='#2E251D',
        font={'color': '#FAF5F0', 'size': 12},
        xaxis=dict(
            range=[0, 100],
            showgrid=True,
            gridcolor='#4A3C31',
            tickfont=dict(color='#D4C4B5'),
            title=dict(text='Risk Probability (%)', font=dict(color='#D4C4B5'))
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color='#FAF5F0', size=13)
        ),
        margin=dict(l=150, r=60, t=40, b=50)
    )
    return fig


def create_radar_chart(labels, values, title):
    """Create radar chart for multi-dimensional analysis"""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill='toself',
        line=dict(color='#F97316', width=3),
        fillcolor='rgba(249, 115, 22, 0.25)',
        name=title
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickcolor='#D4C4B5',
                gridcolor='#4A3C31',
                linecolor='#4A3C31',
                tickfont=dict(color='#D4C4B5')
            ),
            angularaxis=dict(
                tickcolor='#D4C4B5',
                gridcolor='#4A3C31',
                linecolor='#4A3C31',
                tickfont=dict(color='#FAF5F0')
            ),
            bgcolor='#2E251D'
        ),
        showlegend=False,
        height=350,
        paper_bgcolor='#332922',
        font={'color': '#FAF5F0'}
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
    st.markdown('<p class="sidebar-brand">🥗 NutriScanner Pro</p>', unsafe_allow_html=True)

    st.write("")
    page = st.radio(
        "NAVIGATION",
        ["🏠 Dashboard", "🔍 Health Risk Assessment", "📊 Nutrition Analytics", "📈 Trends & Insights",
         "👤 Profile Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("""
    <div class="metric-card" style="padding: 20px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #F97316 0%, #C2410C 100%); display: flex; align-items: center; justify-content: center; font-size: 24px; color: white;">👤</div>
            <div>
                <div style="font-weight: 600; color: #FAF5F0;">Alex Rivers</div>
                <div style="font-size: 0.8rem; color: #A89585;">Premium Member</div>
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

if page == "🏠 Dashboard":
    st.markdown("""
    <div class="hero-banner">
        <h1>🍊 Your Health Intelligence Hub 🌿</h1>
        <p>AI-powered nutrition analysis, disease risk prediction, and personalized health insights</p>
    </div>
    """, unsafe_allow_html=True)

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

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📈 Weekly Nutrition Trends")
        dates = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(6)][::-1]
        calories = [1950, 2100, 1880, 2250, 2180, 2340]
        fig_trend = create_trend_chart(dates, calories, "Calories", '#F97316')
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.markdown("### 🥗 Macro Distribution")
        macro_data = pd.DataFrame({
            'Nutrient': ['Protein', 'Carbohydrates', 'Fats'],
            'Amount': [94, 245, 68]
        })
        fig_pie = create_nutrition_pie_chart(macro_data)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### ⚠️ Health Risk Overview")
    diseases = ['Diabetes', 'Hypertension', 'Heart Disease', 'Obesity', 'Anemia', 'Kidney']
    risks = [47.5, 25.7, 50.8, 15.2, 5.4, 13.1]
    fig_risk = create_risk_bar_chart(diseases, risks)
    st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown("### ⚡ Quick Actions")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.button("📷 Scan Meal", use_container_width=True)
    with c2:
        st.button("🔍 Risk Assessment", use_container_width=True)
    with c3:
        st.button("📊 View Reports", use_container_width=True)
    with c4:
        st.button("👤 Update Profile", use_container_width=True)

elif page == "🔍 Health Risk Assessment":
    st.title("🔍 AI Health Risk Assessment")
    st.markdown("Predict disease risks based on your nutritional profile and lifestyle")

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

            predictions = {
                'Diabetes': 47.5,
                'Hypertension': 25.7,
                'Heart Disease': 50.8,
                'Obesity': 15.2,
                'Anemia': 5.4,
                'Kidney Disease': 13.1
            }

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

            st.subheader("All Disease Risks")
            fig = create_risk_bar_chart(list(predictions.keys()), list(predictions.values()))
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🌿 Personalized Recommendations")
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

elif page == "📊 Nutrition Analytics":
    st.title("📊 Advanced Nutrition Analytics")
    st.markdown("Deep dive into your nutritional patterns and deficiencies")

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
            name='Your Intake',
            y=micro_data['Nutrient'],
            x=micro_data['Intake'],
            orientation='h',
            marker_color='#F97316',
            marker_line=dict(color='#332922', width=2)
        ))
        fig.add_trace(go.Bar(
            name='Recommended',
            y=micro_data['Nutrient'],
            x=micro_data['Recommended'],
            orientation='h',
            marker_color='#22C55E',
            marker_line=dict(color='#332922', width=2),
            opacity=0.7
        ))
        fig.update_layout(
            barmode='group',
            height=400,
            paper_bgcolor='#332922',
            plot_bgcolor='#2E251D',
            font={'color': '#FAF5F0'},
            xaxis=dict(showgrid=True, gridcolor='#4A3C31', tickfont=dict(color='#D4C4B5')),
            yaxis=dict(showgrid=False, tickfont=dict(color='#FAF5F0')),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(color='#D4C4B5'))
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("30-Day Nutrition Trends")
        dates = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(29)][::-1]

        tab3_1, tab3_2 = st.tabs(["🔥 Calories", "💪 Macros"])
        with tab3_1:
            calories_trend = np.random.randint(1800, 2500, 30).tolist()
            fig = create_trend_chart(dates, calories_trend, "Daily Calories", '#F97316')
            st.plotly_chart(fig, use_container_width=True)

        with tab3_2:
            protein_trend = np.random.randint(70, 120, 30).tolist()
            fig = create_trend_chart(dates, protein_trend, "Protein (g)", '#22C55E')
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

elif page == "📈 Trends & Insights":
    st.title("📈 Trends & AI Insights")
    st.markdown("Long-term health patterns and predictive analytics")

    col1, col2 = st.columns([3, 1])
    with col1:
        time_range = st.slider("Select Time Range (Days)", 7, 90, 30)
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

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

    st.subheader("🔗 Nutrient Correlation Analysis")
    corr_data = pd.DataFrame(
        np.random.rand(6, 6),
        columns=['Calories', 'Protein', 'Carbs', 'Fat', 'Sodium', 'Fiber'],
        index=['Calories', 'Protein', 'Carbs', 'Fat', 'Sodium', 'Fiber']
    )

    fig_corr = px.imshow(
        corr_data,
        color_continuous_scale=[[0, '#15803D'], [0.5, '#4A3C31'], [1, '#EA580C']],
        aspect='auto',
        text_auto='.2f'
    )
    fig_corr.update_layout(
        height=500,
        paper_bgcolor='#332922',
        font={'color': '#FAF5F0'}
    )
    fig_corr.update_traces(textfont=dict(color='#FAF5F0'))
    st.plotly_chart(fig_corr, use_container_width=True)

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
    <p>🥗 NutriScanner Pro v4.0.0 | AI-Powered Health Intelligence Platform</p>
    <p>© 2026 NutriScanner Inc. | <a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a></p>
</div>
""", unsafe_allow_html=True)