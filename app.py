import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime

# 1. Page & Layout Config
st.set_page_config(page_title="AV Intel Pulse 2026", layout="wide", page_icon="📡")

# Professional Dashboard Styling - Removed potential stray brackets from CSS
st.html("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; border: 1px solid #e1e4e8; padding: 20px; }
    .report-card { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 5px solid #2e7d32;
        margin-top: 10px;
    }
    </style>
""")

# 2. Client Initialization
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception as e:
    st.error("API Keys missing in Secrets!")
    st.stop()

# 3. Persistent Data State
if "intel_data" not in st.session_state:
    st.session_state.intel_data = None
    st.session_state.active_co = ""

def clean_for_pdf(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# --- SIDEBAR: COMPETITIVE SELECTION ---
st.sidebar
