# ============================================================
# NUTRISCANNER - PROFESSIONAL HEALTH AI PLATFORM
# 🍉 TROPICAL FRUIT THEME - Pastèque, Zeste, Lagoon, Melon 🍋
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
# 2. TROPICAL FRUIT CSS THEME
# ============================================================
def apply_modern_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@700;800&display=swap');

    /* === GLOBAL VARIABLES - TROPICAL FRUIT PALETTE === */
    :root {
        /* Core Brand Colors */
        --pasteque:   #FF544C;   /* Watermelon red */
        --zeste:      #FFE458;   /* Lemon yellow   */
        --lagoon:     #2AB0A3;   /* Teal green     */
        --melon:      #FE9A34;   /* Melon orange   */

        /* Gradients */
        --primary-gradient:   linear-gradient(135deg, #FF544C 0%, #FE9A34 100%);
        --secondary-gradient: linear-gradient(135deg, #2AB0A3 0%, #1D8A80 100%);
        --zeste-gradient:     linear-gradient(135deg, #FFE458 0%, #FFC800 100%);
        --warm-gradient:      linear-gradient(135deg, #FF544C 0%, #FFE458 100%);
        --cool-gradient:      linear-gradient(135deg, #2AB0A3 0%, #FFE458 100%);

        /* Backgrounds — light cream base for freshness */
        --bg-page:      #FDFAF3;
        --bg-section:   #F8F3E8;
        --bg-card:      #FFFFFF;
        --bg-card-alt:  #FFF9EE;
        --bg-sidebar:   #1A3C3A;

        /* Borders */
        --border-light:  #EDE7D4;
        --border-medium: #D4C9AD;
        --border-accent: #FF544C;

        /* Text */
        --text-primary:   #1C2B2A;
        --text-secondary: #3D5250;
        --text-muted:     #7A9290;
        --text-on-dark:   #F0FAF9;
        --text-on-accent: #FFFFFF;

        /* Status */
        --success:       #2AB0A3;
        --success-light: rgba(42, 176, 163, 0.15);
        --warning:       #FE9A34;
        --warning-light: rgba(254, 154, 52, 0.15);
        --danger:        #FF544C;
        --danger-light:  rgba(255, 84, 76, 0.15);
        --info:          #FFE458;
        --info-light:    rgba(255, 228, 88, 0.2);

        /* Shadows */
        --shadow-sm:  0 2px 12px rgba(255, 84, 76, 0.10);
        --shadow-md:  0 6px 30px rgba(255, 84, 76, 0.15);
        --shadow-lg:  0 12px 50px rgba(42, 176, 163, 0.18);
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Nunito', sans-serif !important;
        background: var(--bg-page) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent !important;
    }

    .main .block-container {
        background: transparent !important;
        padding-top: 2rem !important;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A3C3A 0%, #122B29 60%, #0D1F1E 100%) !important;
        border-right: 3px solid rgba(42, 176, 163, 0.3) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-on-dark) !important;
    }

    .sidebar-brand {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Playfair Display', serif !important;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        padding: 28px 0 20px;
        border-bottom: 2px solid rgba(42, 176, 163, 0.25);
        margin-bottom: 24px;
        letter-spacing: -0.5px;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 6px;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(42, 176, 163, 0.08) !important;
        margin: 3px 0 !important;
        padding: 14px 18px !important;
        border-radius: 14px !important;
        border: 2px solid transparent !important;
        transition: all 0.3s ease !important;
        color: rgba(240, 250, 249, 0.75) !important;
        cursor: pointer;
        font-weight: 600;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255, 84, 76, 0.15) !important;
        border-color: var(--pasteque) !important;
        color: #FFB5B2 !important;
        transform: translateX(6px);
    }

    /* ===== TYPOGRAPHY ===== */
    p, span, div, label, .stMarkdown, .stText {
        color: var(--text-primary) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif !important;
        letter-spacing: -0.3px;
        color: var(--text-primary) !important;
    }

    h1 {
        background: var(--primary-gradient) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-size: 3.2rem !important;
    }

    h2 {
        color: var(--text-primary) !important;
        font-size: 2rem !important;
        border-left: 5px solid var(--pasteque) !important;
        padding-left: 18px !important;
        margin: 36px 0 18px 0 !important;
        -webkit-text-fill-color: var(--text-primary) !important;
    }

    h3 {
        color: var(--text-secondary) !important;
        font-size: 1.4rem !important;
        -webkit-text-fill-color: var(--text-secondary) !important;
    }

    /* ===== METRIC CARDS ===== */
    .metric-card {
        background: var(--bg-card);
        border: 2px solid var(--border-light);
        border-radius: 22px;
        padding: 26px 24px;
        margin: 8px 0;
        transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: var(--primary-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .metric-card::after {
        content: '';
        position: absolute;
        bottom: -30px; right: -30px;
        width: 100px; height: 100px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,84,76,0.06) 0%, transparent 70%);
        pointer-events: none;
    }

    .metric-card:hover {
        transform: translateY(-7px);
        box-shadow: var(--shadow-md);
        border-color: var(--pasteque);
    }

    .metric-card:hover::before {
        opacity: 1;
    }

    .metric-value {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.6rem;
        font-weight: 800;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }

    .metric-label {
        color: var(--text-muted) !important;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        margin-top: 6px;
        font-weight: 700;
    }

    .metric-delta {
        font-size: 0.82rem;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 10px;
        font-family: 'Nunito', sans-serif !important;
    }

    .delta-positive {
        background: var(--success-light);
        color: #1A8078 !important;
    }

    .delta-negative {
        background: var(--danger-light);
        color: #CC2A23 !important;
    }

    /* ===== HERO BANNER ===== */
    .hero-banner {
        background: linear-gradient(135deg, 
            rgba(255, 84, 76, 0.07) 0%, 
            rgba(255, 228, 88, 0.07) 40%, 
            rgba(42, 176, 163, 0.10) 100%);
        border: 2px solid var(--border-light);
        border-radius: 28px;
        padding: 56px 48px;
        margin: 20px 0 32px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .hero-banner::before {
        content: '';
        position: absolute;
        top: -40%; left: -40%;
        width: 180%; height: 180%;
        background: radial-gradient(ellipse at center, 
            rgba(255, 228, 88, 0.08) 0%, 
            rgba(42, 176, 163, 0.05) 40%,
            transparent 70%);
        animation: pulse-bg 12s ease-in-out infinite;
    }

    @keyframes pulse-bg {
        0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.6; }
        50% { transform: scale(1.1) rotate(5deg); opacity: 1; }
    }

    /* Fruit decorations */
    .hero-banner::after {
        content: '🍉🍋🍈🍊';
        position: absolute;
        top: 14px; right: 24px;
        font-size: 28px;
        letter-spacing: 6px;
        opacity: 0.45;
        animation: float-fruits 8s ease-in-out infinite;
    }

    @keyframes float-fruits {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .hero-banner h1 {
        margin-bottom: 16px;
        position: relative;
        z-index: 1;
    }

    .hero-banner p {
        color: var(--text-secondary) !important;
        font-size: 1.15rem;
        max-width: 580px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
        line-height: 1.7;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 13px 28px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        font-family: 'Nunito', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 18px rgba(255, 84, 76, 0.35) !important;
        letter-spacing: 0.3px;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 28px rgba(255, 84, 76, 0.45) !important;
    }

    /* ===== PROGRESS BARS ===== */
    .stProgress > div > div {
        background: var(--primary-gradient) !important;
        border-radius: 10px;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-section);
        border-radius: 16px;
        padding: 6px;
        gap: 5px;
        border: 2px solid var(--border-light);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-muted) !important;
        border-radius: 12px;
        padding: 11px 22px;
        transition: all 0.3s ease;
        font-weight: 600;
        font-family: 'Nunito', sans-serif !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--warning-light);
        color: #C4710D !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary-gradient) !important;
        color: white !important;
    }

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--bg-card) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
        padding: 11px 15px !important;
        font-family: 'Nunito', sans-serif !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--pasteque) !important;
        box-shadow: 0 0 0 3px rgba(255, 84, 76, 0.15) !important;
    }

    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stMultiSelect label {
        color: var(--text-secondary) !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.4px;
    }

    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-card) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--pasteque) !important;
    }

    .stSlider label {
        color: var(--text-secondary) !important;
        font-weight: 700 !important;
    }

    .stCheckbox > label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: var(--bg-section); border-radius: 5px; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(180deg, var(--pasteque), var(--melon)); 
        border-radius: 5px; 
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: linear-gradient(180deg, #e8403a, #e07a18); 
    }

    /* ===== RISK ALERTS ===== */
    .risk-high {
        background: linear-gradient(135deg, rgba(255, 84, 76, 0.12) 0%, rgba(255, 84, 76, 0.05) 100%);
        border: 2px solid var(--pasteque);
        border-radius: 16px;
        padding: 20px 26px;
        margin: 12px 0;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 18px rgba(255, 84, 76, 0.12);
    }

    .risk-medium {
        background: linear-gradient(135deg, rgba(254, 154, 52, 0.12) 0%, rgba(255, 228, 88, 0.06) 100%);
        border: 2px solid var(--melon);
        border-radius: 16px;
        padding: 20px 26px;
        margin: 12px 0;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 18px rgba(254, 154, 52, 0.12);
    }

    .risk-low {
        background: linear-gradient(135deg, rgba(42, 176, 163, 0.12) 0%, rgba(42, 176, 163, 0.05) 100%);
        border: 2px solid var(--lagoon);
        border-radius: 16px;
        padding: 20px 26px;
        margin: 12px 0;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 18px rgba(42, 176, 163, 0.12);
    }

    .risk-high strong, .risk-medium strong, .risk-low strong {
        color: var(--text-primary) !important;
    }

    /* ===== SUCCESS MESSAGE ===== */
    .stSuccess {
        background: var(--success-light) !important;
        border-left: 4px solid var(--lagoon) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    .stCaption, caption, figcaption {
        color: var(--text-muted) !important;
    }

    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--border-medium), transparent);
        margin: 28px 0;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 36px 0;
        margin-top: 56px;
        border-top: 2px solid var(--border-light);
        color: var(--text-muted) !important;
        font-size: 0.88rem;
        background: linear-gradient(180deg, transparent 0%, rgba(255, 228, 88, 0.04) 100%);
    }

    .footer p { color: var(--text-muted) !important; }

    .footer a {
        color: var(--pasteque) !important;
        text-decoration: none;
        font-weight: 700;
        transition: color 0.3s ease;
    }

    .footer a:hover { color: var(--melon) !important; }

    .js-plotly-plot { border-radius: 16px; overflow: hidden; }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: var(--bg-section) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-card-alt) !important;
        border: 2px solid var(--border-light) !important;
        border-top: none !important;
        border-radius: 0 0 14px 14px !important;
    }

    /* Spinner color */
    .stSpinner > div > div {
        border-top-color: var(--pasteque) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 3. HELPER FUNCTIONS — TROPICAL PALETTE
# ============================================================
PASTEQUE  = '#FF544C'
ZESTE     = '#FFE458'
LAGOON    = '#2AB0A3'
MELON     = '#FE9A34'
CARD_BG   = '#FFFFFF'
PLOT_BG   = '#FDFAF3'
FONT_CLR  = '#1C2B2A'
GRID_CLR  = '#EDE7D4'
TICK_CLR  = '#7A9290'


def create_risk_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 15, 'color': FONT_CLR, 'family': 'Playfair Display'}},
        delta={'reference': 50,
               'increasing': {'color': PASTEQUE},
               'decreasing': {'color': LAGOON}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': TICK_CLR, 'tickfont': {'color': TICK_CLR}},
            'bar': {'color': MELON},
            'bgcolor': PLOT_BG,
            'borderwidth': 2,
            'bordercolor': GRID_CLR,
            'steps': [
                {'range': [0, 40],  'color': 'rgba(42, 176, 163, 0.20)'},
                {'range': [40, 60], 'color': 'rgba(254, 154, 52, 0.20)'},
                {'range': [60, 100],'color': 'rgba(255, 84, 76, 0.20)'}
            ],
        }
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor=CARD_BG,
        font={'color': FONT_CLR, 'family': 'Nunito'}
    )
    return fig


def create_nutrition_pie_chart(data):
    fig = px.pie(
        data,
        values='Amount',
        names='Nutrient',
        color='Nutrient',
        color_discrete_map={
            'Protein':       LAGOON,
            'Carbohydrates': MELON,
            'Fats':          PASTEQUE,
            'Fiber':         ZESTE
        },
        hole=0.45,
        opacity=0.92
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12,
        textfont_color='white',
        marker=dict(line=dict(color=CARD_BG, width=3))
    )
    fig.update_layout(
        height=350,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25,
                    xanchor="center", x=0.5,
                    font=dict(color=FONT_CLR, size=12, family='Nunito')),
        paper_bgcolor=CARD_BG,
        font={'color': FONT_CLR, 'size': 12, 'family': 'Nunito'},
        margin=dict(l=20, r=20, t=50, b=60)
    )
    return fig


def create_trend_chart(dates, values, title, color=PASTEQUE):
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=values,
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3, shape='spline'),
        marker=dict(size=9, color=color, line=dict(color=CARD_BG, width=2)),
        fill='tozeroy',
        fillcolor=f'rgba({r},{g},{b},0.12)'
    ))
    fig.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=PLOT_BG,
        font={'color': FONT_CLR, 'family': 'Nunito'},
        xaxis=dict(showgrid=True, gridcolor=GRID_CLR, linecolor=GRID_CLR,
                   tickfont=dict(color=TICK_CLR)),
        yaxis=dict(showgrid=True, gridcolor=GRID_CLR, linecolor=GRID_CLR,
                   tickfont=dict(color=TICK_CLR)),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig


def create_risk_bar_chart(diseases, probabilities):
    colors = [PASTEQUE if p >= 60 else MELON if p >= 40 else LAGOON for p in probabilities]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=diseases,
        x=probabilities,
        orientation='h',
        marker_color=colors,
        marker_line=dict(color=CARD_BG, width=2),
        text=[f'{p:.1f}%' for p in probabilities],
        textposition='outside',
        textfont=dict(color=FONT_CLR, size=13, family='Nunito'),
        hovertemplate='<b>%{y}</b><br>Risk: %{x:.1f}%<extra></extra>'
    ))
    fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=PLOT_BG,
        font={'color': FONT_CLR, 'size': 12, 'family': 'Nunito'},
        xaxis=dict(range=[0, 100], showgrid=True, gridcolor=GRID_CLR,
                   tickfont=dict(color=TICK_CLR),
                   title=dict(text='Risk Probability (%)', font=dict(color=TICK_CLR))),
        yaxis=dict(showgrid=False, tickfont=dict(color=FONT_CLR, size=13)),
        margin=dict(l=150, r=60, t=40, b=50)
    )
    return fig


def create_radar_chart(labels, values, title):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill='toself',
        line=dict(color=PASTEQUE, width=3),
        fillcolor='rgba(255, 84, 76, 0.18)',
        name=title
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            tickcolor=TICK_CLR, gridcolor=GRID_CLR,
                            linecolor=GRID_CLR, tickfont=dict(color=TICK_CLR)),
            angularaxis=dict(tickcolor=TICK_CLR, gridcolor=GRID_CLR,
                             linecolor=GRID_CLR, tickfont=dict(color=FONT_CLR)),
            bgcolor=PLOT_BG
        ),
        showlegend=False,
        height=350,
        paper_bgcolor=CARD_BG,
        font={'color': FONT_CLR, 'family': 'Nunito'}
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
        ["🏠 Dashboard", "🔍 Health Risk Assessment", "📊 Nutrition Analytics",
         "📈 Trends & Insights", "👤 Profile Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("""
    <div style="
        background: rgba(42,176,163,0.12);
        border: 2px solid rgba(42,176,163,0.3);
        border-radius: 18px;
        padding: 18px 16px;
        display: flex;
        align-items: center;
        gap: 14px;
    ">
        <div style="
            width: 46px; height: 46px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF544C 0%, #FE9A34 100%);
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
        ">👤</div>
        <div>
            <div style="font-weight: 700; color: #F0FAF9; font-family: Nunito, sans-serif;">Alex Rivers</div>
            <div style="font-size: 0.78rem; color: rgba(240,250,249,0.55); font-family: Nunito, sans-serif;">Premium Member</div>
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
        <h1>🍉 Your Health Intelligence Hub 🍋</h1>
        <p>AI-powered nutrition analysis, disease risk prediction, and personalized health insights — all in one vibrant place</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Today's Overview")
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:1.8rem; margin-bottom:4px;">🔥</div>
            <div class="metric-value">2,180</div>
            <div class="metric-label">Calories</div>
            <div class="metric-delta delta-positive">↑ 12% vs avg</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:1.8rem; margin-bottom:4px;">💪</div>
            <div class="metric-value">94g</div>
            <div class="metric-label">Protein</div>
            <div class="metric-delta delta-positive">↑ 8g vs goal</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:1.8rem; margin-bottom:4px;">🍞</div>
            <div class="metric-value">245g</div>
            <div class="metric-label">Carbs</div>
            <div class="metric-delta delta-negative">↓ 15g vs goal</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:1.8rem; margin-bottom:4px;">🥑</div>
            <div class="metric-value">68g</div>
            <div class="metric-label">Fats</div>
            <div class="metric-delta delta-positive">✓ On target</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:1.8rem; margin-bottom:4px;">💧</div>
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
        fig_trend = create_trend_chart(dates, calories, "Calories", PASTEQUE)
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
    risks    = [47.5, 25.7, 50.8, 15.2, 5.4, 13.1]
    fig_risk = create_risk_bar_chart(diseases, risks)
    st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown("### ⚡ Quick Actions")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.button("📷 Scan Meal",       use_container_width=True)
    with c2: st.button("🔍 Risk Assessment",  use_container_width=True)
    with c3: st.button("📊 View Reports",     use_container_width=True)
    with c4: st.button("👤 Update Profile",   use_container_width=True)

elif page == "🔍 Health Risk Assessment":
    st.title("🔍 AI Health Risk Assessment")
    st.markdown("Predict disease risks based on your nutritional profile and lifestyle")

    with st.expander("📝 Enter Your Health Data", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            age    = st.number_input("Age",         min_value=18,  max_value=100,  value=35)
            gender = st.selectbox("Gender",          ["Male", "Female"])
            weight = st.number_input("Weight (kg)", min_value=40,  max_value=200,  value=75)
            height = st.number_input("Height (cm)", min_value=100, max_value=250,  value=175)
        with col2:
            calories   = st.number_input("Daily Calories",    min_value=1000, max_value=5000, value=2200)
            protein    = st.number_input("Protein (g)",        min_value=20,   max_value=300,  value=80)
            carbs      = st.number_input("Carbohydrates (g)", min_value=50,   max_value=500,  value=250)
            total_fat  = st.number_input("Total Fat (g)",     min_value=20,   max_value=300,  value=70)
        with col3:
            sodium   = st.number_input("Sodium (mg)",               min_value=500, max_value=10000, value=2300)
            fiber    = st.number_input("Fiber (g)",                  min_value=5,   max_value=100,   value=25)
            activity = st.number_input("Physical Activity (min/day)",min_value=0,   max_value=300,   value=45)
            water    = st.number_input("Water Intake (L)",           min_value=0.5, max_value=5.0,   value=2.0)

    if st.button("🔬 Analyze Health Risks", type="primary", use_container_width=True):
        with st.spinner("AI is analyzing your health profile..."):
            time.sleep(2)

        predictions = {
            'Diabetes':      47.5,
            'Hypertension':  25.7,
            'Heart Disease': 50.8,
            'Obesity':       15.2,
            'Anemia':         5.4,
            'Kidney Disease':13.1
        }

        st.subheader("Risk Assessment Results")
        g1, g2, g3 = st.columns(3)
        with g1: st.plotly_chart(create_risk_gauge(predictions['Diabetes'],      "Diabetes Risk"),      use_container_width=True)
        with g2: st.plotly_chart(create_risk_gauge(predictions['Hypertension'],  "Hypertension Risk"),  use_container_width=True)
        with g3: st.plotly_chart(create_risk_gauge(predictions['Heart Disease'], "Heart Disease Risk"), use_container_width=True)

        st.subheader("All Disease Risks")
        fig = create_risk_bar_chart(list(predictions.keys()), list(predictions.values()))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌿 Personalized Recommendations")
        if predictions['Diabetes'] > 40:
            st.markdown('<div class="risk-medium">⚠️ <strong>Diabetes Prevention:</strong> Reduce added sugar intake, increase fiber, and maintain regular physical activity</div>', unsafe_allow_html=True)
        if predictions['Heart Disease'] > 40:
            st.markdown('<div class="risk-medium">⚠️ <strong>Heart Health:</strong> Lower saturated fat, increase omega-3, and monitor sodium intake</div>', unsafe_allow_html=True)
        if predictions['Hypertension'] > 40:
            st.markdown('<div class="risk-medium">⚠️ <strong>Blood Pressure:</strong> Reduce sodium, increase potassium-rich foods, and stay hydrated</div>', unsafe_allow_html=True)

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
                'Amount':   [94, 245, 68, 28],
                'Goal':     [100, 275, 75, 35]
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
            'Nutrient':    ['Vitamin D', 'Vitamin B12', 'Iron', 'Calcium', 'Potassium'],
            'Intake':      [600, 2.4, 12, 800, 3200],
            'Recommended': [800, 3.0, 18, 1000, 4700]
        })
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Your Intake',
            y=micro_data['Nutrient'], x=micro_data['Intake'],
            orientation='h',
            marker_color=PASTEQUE,
            marker_line=dict(color=CARD_BG, width=2)
        ))
        fig.add_trace(go.Bar(
            name='Recommended',
            y=micro_data['Nutrient'], x=micro_data['Recommended'],
            orientation='h',
            marker_color=LAGOON,
            marker_line=dict(color=CARD_BG, width=2),
            opacity=0.75
        ))
        fig.update_layout(
            barmode='group', height=400,
            paper_bgcolor=CARD_BG, plot_bgcolor=PLOT_BG,
            font={'color': FONT_CLR, 'family': 'Nunito'},
            xaxis=dict(showgrid=True, gridcolor=GRID_CLR, tickfont=dict(color=TICK_CLR)),
            yaxis=dict(showgrid=False, tickfont=dict(color=FONT_CLR)),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5,
                        font=dict(color=FONT_CLR))
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("30-Day Nutrition Trends")
        dates = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(29)][::-1]
        tab3_1, tab3_2 = st.tabs(["🔥 Calories", "💪 Macros"])
        with tab3_1:
            fig = create_trend_chart(dates, np.random.randint(1800, 2500, 30).tolist(), "Daily Calories", PASTEQUE)
            st.plotly_chart(fig, use_container_width=True)
        with tab3_2:
            fig = create_trend_chart(dates, np.random.randint(70, 120, 30).tolist(), "Protein (g)", LAGOON)
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Nutrient Deficiency Alerts")
        st.markdown('<div class="risk-medium">⚠️ <strong>Vitamin D:</strong> Your intake (600 IU) is below recommended (800 IU). Consider sunlight exposure or supplementation</div>', unsafe_allow_html=True)
        st.markdown('<div class="risk-medium">⚠️ <strong>Iron:</strong> Your intake (12mg) is below recommended (18mg). Include more red meat, spinach, or fortified cereals</div>', unsafe_allow_html=True)
        st.markdown('<div class="risk-low">✅ <strong>Calcium:</strong> Good intake! Keep consuming dairy and leafy greens</div>', unsafe_allow_html=True)
        st.markdown('<div class="risk-low">✅ <strong>Potassium:</strong> Excellent! Your intake supports healthy blood pressure</div>', unsafe_allow_html=True)

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
        ("📈 Calorie Trend",  "Your average calorie intake increased by 8% over the past 2 weeks",  "positive"),
        ("💪 Protein Goal",   "You've met your protein target 18 out of 30 days",                    "positive"),
        ("⚠️ Sodium Alert",   "Sodium intake is 40% above recommended levels on weekends",           "warning"),
        ("💧 Hydration",      "Water intake consistency improved by 25% this month",                 "positive")
    ]
    for title, desc, status in insights:
        cls = "risk-low" if status == "positive" else "risk-medium"
        st.markdown(f'<div class="{cls}"><strong>{title}:</strong> {desc}</div>', unsafe_allow_html=True)

    st.subheader("🔗 Nutrient Correlation Analysis")
    corr_data = pd.DataFrame(
        np.random.rand(6, 6),
        columns=['Calories', 'Protein', 'Carbs', 'Fat', 'Sodium', 'Fiber'],
        index=['Calories', 'Protein', 'Carbs', 'Fat', 'Sodium', 'Fiber']
    )
    fig_corr = px.imshow(
        corr_data,
        color_continuous_scale=[[0, LAGOON], [0.5, ZESTE], [1, PASTEQUE]],
        aspect='auto',
        text_auto='.2f'
    )
    fig_corr.update_layout(
        height=500,
        paper_bgcolor=CARD_BG,
        font={'color': FONT_CLR, 'family': 'Nunito'}
    )
    fig_corr.update_traces(textfont=dict(color=FONT_CLR))
    st.plotly_chart(fig_corr, use_container_width=True)

elif page == "👤 Profile Settings":
    st.title("👤 Profile Settings")
    st.markdown("Manage your health profile and preferences")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Personal Information")
        st.text_input("Full Name", "Alex Rivers")
        st.number_input("Age",          min_value=18,  max_value=100, value=30)
        st.selectbox("Gender",           ["Male", "Female", "Other"])
        st.number_input("Weight (kg)",  min_value=40,  max_value=200, value=75)
        st.number_input("Height (cm)",  min_value=100, max_value=250, value=180)

    with col2:
        st.subheader("Health Goals")
        st.selectbox("Activity Level",  ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Athlete"])
        st.selectbox("Primary Goal",    ["Weight Loss", "Muscle Gain", "Maintenance", "Better Health"])
        st.multiselect("Dietary Preferences", ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", "Paleo"])
        st.number_input("Daily Calorie Goal", min_value=1000, max_value=5000, value=2200)

    st.markdown("---")
    st.subheader("Notification Preferences")
    c1, c2, c3 = st.columns(3)
    with c1: st.checkbox("Daily Reminders", value=True)
    with c2: st.checkbox("Weekly Reports",  value=True)
    with c3: st.checkbox("Risk Alerts",     value=True)
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