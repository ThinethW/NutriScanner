import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
PARENT_DIR = Path(__file__).resolve().parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from nutritional_analysis.main import NutriScanner

# Page config
st.set_page_config(
    page_title="NutriScanner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background-color: #FAFAF9;
}

h1 {
    color: #1D5A10 !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #4CAF50 !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B3B18 0%, #2D5A27 100%) !important;
}

[data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
    color: #F0F4F0 !important;
}

.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    width: 100%;
}

.stButton>button:hover {
    background-color: #2D5A27;
}
</style>
""", unsafe_allow_html=True)

# Initialize NutriScanner once
@st.cache_resource
def load_scanner():
    """Load NutriScanner (cached)"""
    return NutriScanner()

scanner = load_scanner()

# Sidebar
with st.sidebar:
    st.markdown('<p style="font-size: 30px; font-weight: 800; text-align: center; color: #D4E157;">🥗 NutriScanner</p>', unsafe_allow_html=True)
    st.write("")
    page = st.radio(
        "NAVIGATION",
        ["🏠 Dashboard", "📷 Label Scanner", "🍽️ Meal Analyzer", "👤 Profile"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("v1.0 - AI Powered")

# Route to pages
if page == "🏠 Dashboard":
    import pages.home as home
    home.show()

elif page == "📷 Label Scanner":
    import pages.scanner as scanner_page
    scanner_page.show(scanner)

elif page == "🍽️ Meal Analyzer":
    import pages.analyzer as analyzer_page
    analyzer_page.show(scanner)

elif page == "👤 Profile":
    import pages.profile as profile
    profile.show()