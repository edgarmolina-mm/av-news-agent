import streamlit as st
from google import genai
from exa_py import Exa
from datetime import datetime, timedelta

# 1. Page & Layout Configuration
st.set_page_config(page_title="AV Intel Pulse 2026", layout="wide", page_icon="📡")

# Professional Styling for rapid scanning
st.html("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; border: 1px solid #e1e4e8; padding: 20px; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 5px solid #2e7d32; }
    </style>
""")

# 2. Secure Client Initialization
try:
    # Always use st.secrets for production security
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception:
    st.error("⚠️ API Keys missing! Add them in Settings > Secrets.")
    st.stop()

# Persistent State Management
if "intel_data" not in st.session_state:
    st.session_state.intel_data = None
    st.session_state.active_co = ""
    st.session_state.source_urls = []

# --- SIDEBAR: CONTROLS ---
st.sidebar.title("AV Intelligence Hub")
st.sidebar.caption(f"Market Snapshot: {datetime.now().strftime('%B %d, %Y')}")
target = st.sidebar.selectbox("Select Target", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Scan {target} Momentum"):
    with st.spinner(f"Synthesizing 60 days of {target} data..."):
        try:
            # Dynamic 60-day lookback for fresh 2026 data
            lookback = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
            
            # Precision query to isolate target specific news
            query = f"latest commercial L4 advancements, fleet metrics, and news for {target} 2026"
            
            search = exa.search(
                query,
                num_results=5, 
                type="auto",
                category="news",
                start_published_date=lookback,
                contents={"text": True}
            )
            
            if not search.results:
                st.warning(f"No recent news found for {target} since {lookback}.")
