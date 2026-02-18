import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="AV Intel Pulse 2026", layout="wide", page_icon="📡")

# Professional Dashboard Styling
st.html("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; border: 1px solid #e1e4e8; padding: 20px; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 5px solid #2e7d32; }
    </style>
""")

# 2. Secure Client Initialization
try:
    # Citing usage of st.secrets for secure key management
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
# Ensure st.sidebar is used as an object, not called as a function
st.sidebar.title("AV Intelligence Hub")
st.sidebar.caption(f"Market Snapshot: {datetime.now().strftime('%B %d, %Y')}")
target = st.sidebar.selectbox("Select Target", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Pull {target} Intel"):
    with st.spinner(f"Accessing 2026 news wires for {target}..."):
        try:
            query = f"'{target}' L4 commercial deployment, fleet size, or production milestone February 2026 news"
            search = exa.search(
                query,
                num_results=3, 
                type="auto",
                start_published_date="2026-01-01",
                contents={"text": True}
            )
            
            context = "\n".join([f"URL: {r.url}\nCONTENT: {r.text[:2000]}" for r in search.results])
            
            prompt = f"""
            Act as a Senior Autonomous Vehicle Analyst. Using the 2026 data provided, 
            write a briefing for {target} that emphasizes HARD METRICS and RECENT EVENTS.
            
            Format the report with these headers:
            # {target} Status: February 2026
            ### 📍 Strategic Footprint
            ### ⚙️ Hardware & Tech Milestone
            ### 💰 Commercial & Partnership
            ### 📉 Safety & Regulatory
            
            DATA: {context}
            """
            
            res = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            # Sanitizing to remove stray brackets
            st.session_state.intel_data = res.text.lstrip(' ([{\n\r')
            st.session_state.active_co = target
            st.session_state.source_urls = [r.url for r in search.results]
            
        except Exception as e:
            st.error(f"Sync failed: {
