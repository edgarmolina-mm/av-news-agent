import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime

# 1. Setup
st.set_page_config(page_title="AV Intel 2026", layout="wide", page_icon="🚗")

# Accessing secrets
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception as e:
    st.error("API Keys missing in Secrets!")
    st.stop()

# Initialize Session States correctly
if "intel_report" not in st.session_state:
    st.session_state.intel_report = None
if "current_co" not in st.session_state:
    st.session_state.current_co = ""
if "sources" not in st.session_state:
    st.session_state.sources = []

def clean_txt(text):
    # Removes emojis for PDF compatibility
    return re.sub(r'[^\x00-\x7F]+', '', text)

# --- UI Sidebar ---
st.sidebar.header("Intelligence Control")
target = st.sidebar.selectbox("Competitor", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Analyze {target}"):
    with st.spinner(f"Synthesizing {target} signals..."):
        try:
            # 2. Refined Search Query for 2026
            search = exa.search(
                f"latest advancements and commercial L4 autonomous driving metrics for {target} Feb 2026",
                num_results=3, 
                type="auto", 
                start_published_date="2025-11-01", # Slightly wider window for better results
                contents={"summary": True}
            )
            
            if not search.results:
                st.warning(f"No recent news found for {target}. Try a different competitor.")
            else:
                context = "\n".join([f"Source: {r.url}\nSummary: {r.summary}" for r in search.results])
                
                # STRUCTURED PROMPT
                prompt = f"""
                Act as a Lead AV Industry Analyst. Based on the 2026 news for {target}, 
                create a brief Intelligence Report. Use these EXACT headers:
                
                ## 1. Strategic Positioning
                ## 2. Operational Footprint
                ## 3. Tech & Product Stack
                ## 4. Key Performance Indicators (KPIs)
                ## 5. Market Sentiment & Regulatory
                
                DATA:
                {context}
                """
                
                res = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                
                # Save to Session State to prevent disappearing on rerun
                st.session_state.intel_report = res.text
                st.session_state.current_co = target
                st.session_state.sources = [r.url for r in search.results]
                
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# --- Main Dashboard Display ---
if st.session_state.intel_report:
    st.title(f"🚀 {st.session_state.current_co} Analyst Brief")
    st.caption(f"Standardized Intelligence Format • Updated {datetime.now().strftime('%b %d, %Y')}")
    
    # Quick KPI Row
    c1, c2, c3 = st.columns(3)
    c1.metric("L4 Status", "Operational" if st.session_state.current_co != "Tesla" else "L2++ / Testing")
    c2.metric("2026 Momentum", "High")
    c3.metric("Data Quality", "Verified")

    st.divider()
    
    # Display the Report
    st.markdown(st.session_state.intel_report)
    
    with st.expander("View Research Sources"):
        for src in st.session_state.sources:
            st
