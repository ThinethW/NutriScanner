import streamlit as st

# ---------- 1. PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="NutriScanner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------- 2. FULL MODERN CSS ----------
def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    /* Global Typography & Background */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #FAFAF9;
    }

    /* --- TITLES & HEADERS --- */
    h1 {
        color: #1D5A10 !important; /* Deep Forest Green */
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    h2, h3 {
        color: #4CAF50 !important; /* Leaf Green */
        font-weight: 700 !important;
    }

    /* Sidebar Title Customization */
    .sidebar-brand {
        color: #D4E157 !important; /* Lime Accent */
        font-size: 30px;
        font-weight: 800;
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    /* --- SIDEBAR (NAVIGATION BAR) --- */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, #1B3B18 0%, #2D5A27 100%) !important;
        min-width: 300px;
    }

    /* Sidebar Labels & Icons */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stRadio span {
        color: #F0F4F0 !important;
        font-weight: 500;
    }

    /* Customizing the Radio Button Selection */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.05);
        margin: 5px 0px;
        padding: 12px 20px;
        border-radius: 12px;
        transition: 0.3s ease;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(212, 225, 87, 0.2);
    }

    /* --- DASHBOARD COMPONENTS --- */

    /* Hero Banner */
    .hero-container {
        background:linear-gradient(135deg, #2D6A4F 0%, #74C69D 100%);
        padding: 60px;
        border-radius: 35px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 20px 40px rgba(45, 90, 39, 0.15);
    }

    .hero-container h1 {
        color: white !important; /* Override white for banner title */
        font-size: 3.5rem !important;
        margin-bottom: 10px;
    }

    /* Modern Cards */
    .feature-card {
        background: white;
        padding: 35px;
        border-radius: 25px;
        border: 8px solid #E5E7EB;
        text-align: center;
        transition: all 0.4s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 25px rgba(0,0,0,0.05);
        border-color: #D4E157;
    }

    .icon-box {
        font-size: 45px;
        margin-bottom: 15px;
        display: block;
    }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #2D5A27 !important;
        font-weight: 800;
    }

    /* Custom Button */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        font-weight: 600;
        width: 100%;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #2D5A27;
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


# Helper to render cards
def draw_card(icon, title, text):
    st.markdown(f"""
        <div class="feature-card">
            <span class="icon-box">{icon}</span>
            <h3>{title}</h3>
            <p style="color: #6B7280; font-size: 0.95rem;">{text}</p>
        </div>
    """, unsafe_allow_html=True)


# ---------- 3. LOGIC & ROUTING ----------

apply_styles()

# Sidebar Setup
with st.sidebar:
    st.markdown('<p class="sidebar-brand">🥗 NutriScanner</p>', unsafe_allow_html=True)
    st.write("")  # Spacer
    page = st.radio("NAVIGATION", ["🏠 Dashboard", "📷 AI Food Scanner", "📊 Nutrition Analysis", "👤 Profile"])
    st.markdown("---")
    st.caption("v3.0.1 Premium AI Active")

# --- HOME / DASHBOARD ---
if page == "🏠 Dashboard":
    st.markdown("""
        <div class="hero-container">
            <h1>Intelligence on your plate.</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">Analyze macros, track health risks, and optimize your lifestyle.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        draw_card("🔬", "Scan & Analyze", "Upload meal photos for instant calorie and macro breakdown.")
    with col2:
        draw_card("📈", "Health Trends", "Visualize your nutrient intake over weeks and months.")
    with col3:
        draw_card("🛡️", "Risk Predictor", "AI-based insights to lower health risks based on diet.")

    st.write("---")
    st.subheader("Your Daily Snapshot")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Calories", "1,840 kcal", "85%")
    m2.metric("Protein", "92g", "+12g")
    m3.metric("Carbs", "210g", "-5g")
    m4.metric("Fat", "54g", "Normal")

# --- AI SCANNER ---
elif page == "📷 AI Food Scanner":
    st.title("Smart Food Recognition")
    st.write("Our vision model identifies ingredients and calculates nutritional density automatically.")

    col_up, col_res = st.columns([1, 1])
    with col_up:
        uploaded_file = st.file_uploader("Upload meal image", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, caption="Processing Input...", use_container_width=True)

    with col_res:
        if uploaded_file:
            with st.spinner("AI is analyzing composition..."):
                import time

                time.sleep(1.5)  # Simulating AI work
                st.success("Analysis Complete!")
                st.markdown("### **Detected: Roasted Salmon & Asparagus**")
                st.info("**AI Insight:** Excellent source of Omega-3 and Vitamin K.")
                st.progress(0.85, text="Protein Density")
        else:
            st.warning("Please upload a clear photo of your food.")

# --- ANALYSIS ---
elif page == "📊 Nutrition Analysis":
    st.title("Nutrition Dashboard")
    st.write("Historical data visualization.")

    # Placeholder data for the chart
    import pandas as pd
    import numpy as np
    import plotly.express as px  # <--- NEEDED FOR PIE CHART

    # Generating random data for the pie chart
    chart_data = pd.DataFrame({
        'Nutrient': ['Protein', 'Carbs', 'Fats'],
        'Amount': [92, 210, 54]
    })

    # --- NEW PIE CHART LOGIC ---
    fig = px.pie(
        chart_data,
        values='Amount',
        names='Nutrient',
        title='Macronutrient Distribution',
        color='Nutrient',
        color_discrete_map={
            'Protein': '#4CAF50',  # Leaf Green
            'Carbs': '#D4E157',  # Lime Accent
            'Fats': '#1B3B18'  # Deep Forest Green
        }
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Show the raw data
    with st.expander("View Raw Data"):
        st.dataframe(chart_data)
# --- PROFILE ---
elif page == "👤 Profile":
    st.title("User Intelligence Profile")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Full Name", "Alex Rivers")
            st.slider("Age", 18, 95, 30)
            st.selectbox("Activity Level", ["Sedentary", "Moderate", "High Athlete"])
        with c2:
            st.number_input("Weight (kpython -m streamlit run nutri_scanner_app.pyg)", 40, 200, 75)
            st.number_input("Height (cm)", 100, 250, 180)
            st.multiselect("Dietary Restrictions", ["None", "Vegan", "Gluten-Free", "Nut-Allergy"])

        if st.button("Save & Update Profile"):
            st.balloons()
            st.toast("Profile successfully updated and encrypted.")