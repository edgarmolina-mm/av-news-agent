import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime

# 1. Setup
st.set_page_config(page_title="AV Intel 2026", layout="wide", page_icon="🚗")

# API Initialization
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception as e:
    st.error("Missing API Keys in Settings > Secrets!")
    st.stop()

# Initialize Session State
if "intel_report" not in st.session_state:
    st.session_state.intel_report = None
if "current_co" not in st.session_state:
    st.session_state.current_co = ""
if "sources" not in st.session_state:
    st.session_state.sources = []

def clean_txt(text):
    # Essential for PDF compatibility
    return re.sub(r'[^\x00-\x7F]+', '', text)

# --- UI Sidebar ---
st.sidebar.header("Intelligence Control")
target = st.sidebar.selectbox("Competitor", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Analyze {target}"):
    with st.spinner(f"Synthesizing {target} signals..."):
        try:
            # 2. Search Logic
            search = exa.search(
                f"latest L4 autonomous driving advancements and commercial metrics for {target} Feb 2026",
                num_results=3, 
                type="auto", 
                start_published_date="2025-11-01",
                contents={"summary": True}
            )
            
            if not search.results:
                st.warning("No recent news found. Try a different date range or competitor.")
            else:
                context = "\n".join([f"Source: {r.url}\nSummary: {r.summary}" for r in search.results])
                
                # 3. Standardized Prompt
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
                
                # Update Session State
                st.session_state.intel_report = res.text
                st.session_state.current_co = target
                st.session_state.sources = [r.url for r in search.results]
                
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# --- Main Dashboard ---
if st.session_state.intel_report:
    st.title(f"🚀 {st.session_state.current_co} Analyst Brief")
    st.caption(f"Standardized Format • Updated {datetime.now().strftime('%b %d, %Y')}")
    
    st.divider()
    
    # Display the structured report
    st.markdown(st.session_state.intel_report)
    
    # Corrected Research Sources (Fixes the 'module' error)
    with st.expander("View Research Sources"):
        for src in st.session_state.sources:
            st.write(src)

    # PDF Export
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, f"{st.session_state.current_co} Intel 2026", 
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(5)
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 10, clean_txt(st.session_state.intel_report), markdown=True)
        
        st.download_button(
            label="📥 Download PDF Report", 
            data=bytes(pdf.output()), 
            file_name=f"{st.session_state.current_co}_Report.pdf",
            mime="application/pdf"
        )
    except Exception as pdf_err:
        st.error(f"PDF Error: {pdf_err}")
else:
    st.info("👈 Select a competitor and click 'Analyze' to begin.")
