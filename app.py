import streamlit as st
from google import genai
from exa_py import Exa
from datetime import datetime, timedelta

# 1. Clean Layout Setup
st.set_page_config(page_title="AV Intel 2026", layout="wide", page_icon="📡")

# Professional Dashboard Styling
st.html("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; border: 1px solid #e1e4e8; padding: 20px; }
    </style>
""")

# Secure Client Initialization
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception as e:
    st.error("API Keys missing in Secrets!")
    st.stop()

# 2. Sidebar - Essential Controls
st.sidebar.title("AV Intelligence Hub")
st.sidebar.caption(f"Market Snapshot: {datetime.now().strftime('%B %d, %Y')}")
target = st.sidebar.selectbox("Select Target", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])
run_btn = st.sidebar.button(f"Scan {target} Momentum")

if run_btn:
    with st.spinner(f"Synthesizing latest news for {target}..."):
        try:
            # 3. Dynamic 60-Day Lookback
            look
