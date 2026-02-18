import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re

# 1. Setup
st.set_page_config(page_title="AV Intel 2026", layout="wide", page_icon="🚗")
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
exa = Exa(api_key=st.secrets["EXA_API_KEY"])

if "intel_report" not in st.session_state:
    st.session_state.intel_report = None
    st.session_state.current_co = ""

def clean_txt(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# --- UI Sidebar ---
st.sidebar.header("Intelligence Control")
target = st.sidebar.selectbox("Competitor", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Analyze {target}"):
    with st.spinner(f"Synthesizing {target} signals..."):
        # Fetching top 3 results from last 90 days
        search = exa.search(
            f"latest {target} L4 autonomous driving metrics city launches Feb 2026",
            num_results=3, type="auto", start_published_date="2025-11-20", contents={"summary": True}
        )
        
        context = "\n".join([f"Source: {r.url}\nSummary: {r.summary}" for r in search.results])
        
        # STRUCTURED PROMPT
        prompt = f"""
        Act as a Lead AV Industry Analyst. Based on the 2026 news for {target}, 
        create a brief Intelligence Report. Use these EXACT headers:
        
        ## 1. Strategic Positioning
        (Partnerships, funding, and 2026 commercial goals)
        
        ## 2. Operational Footprint
        (Active cities, fleet size, and new launch zones)
        
        ## 3. Tech & Product Stack
        (Hardware/software updates, sensors, or AI models)
        
        ## 4. Key Performance Indicators (KPIs)
        (Miles driven, intervention rates, or safety milestones)
        
        ## 5. Market Sentiment & Regulatory
        (Public trust and government investigations)
        
        DATA:
        {context}
        """
        
        res = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
        st.session_state.intel_report = res.text
        st.session_state.current_co = target
        st.session_state.sources = [r.url for r in search.results]

# --- Main Dashboard ---
if st.session_state.intel_report:
    st.title(f"🚀 {st.session_state.current_co} Analyst Brief")
    st.caption("Standardized Competitive Intelligence Format • Feb 18, 2026")
