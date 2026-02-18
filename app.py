import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="AV Pulse 2026", layout="wide", page_icon="📈")

# 2. Modern CSS (Updated for Streamlit 1.54+)
st.html("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { 
        background-color: #ffffff; 
        border: 1px solid #eee;
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); 
    }
    h1, h2, h3 { color: #1e1e1e; }
    </style>
    """)

# 3. Secure API Initialization
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception as e:
    st.error("⚠️ API Keys missing! Add them in Settings > Secrets.")
    st.stop()

# Persistent State
if "raw_report" not in st.session_state:
    st.session_state.raw_report = None
    st.session_state.active_co = ""
    st.session_state.source_list = []

def pdf_clean(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# --- SIDEBAR CONTROL ---
st.sidebar.title("Market Pulse")
st.sidebar.caption("L4 Intelligence • Feb 18, 2026")
target = st.sidebar.selectbox("Select Competitor", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Generate {target} Briefing"):
    with st.spinner(f"Scanning market for {target}..."):
        try:
            # 4. Precision Search Query
            # Using site: and quotes to ensure target exclusivity
            search_query = f"'{target}' autonomous driving latest commercial updates metrics February 2026"
            if target == "May Mobility":
                search_query = "site:maymobility.com OR 'May Mobility' driverless Peachtree Corners news 2026"
            
            search = exa.search(
                search_query,
                num_results=3, 
                type="auto", 
                category="news",
                start_published_date="2025-12-01",
                contents={"summary": True}
            )
            
            # 5. User-Friendly AI Prompt
            prompt = f"""
            Act as a Lead AV Analyst. Summarize the status of {target} for a new user based ONLY on the provided data.
            DO NOT mention Waymo or Tesla unless the data is explicitly about a partnership with them.
            
            Format as:
            ### 🏁 The Bottom Line
            (Short summary of today's status)
            
            ### 🚀 Recent Milestones
            (Key news from 2026)
            
            ### 📍 Active Footprint
            (Cities or zones mentioned)
            
            ### ⚠️ Market Context
            (Risks or competition focus)
            
            DATA:
            {chr(10).join([f"Source: {r.url} Summary: {r.summary}" for r in search.results])}
            """
            
            res = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            st.session_state.raw_report = res.text
            st.session_state.active_co = target
            st.session_state.source_list = [r.url for r in search.results]
                
        except Exception as e:
            st.error(f"Scan failed: {e}")

# --- MAIN DASHBOARD ---
if st.session_state.raw_report:
    st.title(f"{st.session_state.active_co} Status Report")
    
    # 6. Strategic Metrics Row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Primary Lane", "Robotaxi" if target != "Tesla" else "Personal FSD")
    with m2:
        st.metric("2026 Trajectory", "Scaling" if target in ["Waymo", "Zoox"] else "Deploying")
    with m3:
        risk = "Moderate" if "regulation" in st.session_state.raw_report.lower() else "Low"
        st.metric("Risk Profile", risk)
    
    st.divider()

    st.markdown(st.session_state.raw_report)
    
    # Research Sources (No Variable Shadowing Fix)
    with st.expander("🔗 View Evidence Base"):
        for url_link in st.session_state.source_list:
            st.write(url_link)

    # Professional PDF Export
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, f"{st.session_state.active_co} Intelligence Brief", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(5)
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 10, pdf_clean(st.session_state.raw_report), markdown=True)
        
        st.download_button("📥 Save Report as PDF", data=bytes(pdf.output()), 
                           file_name=f"{st.session_state.active_co}_Brief_Feb2026.pdf")
    except Exception as pdf_err:
        st.warning(f"PDF unavailable: {pdf_err}")
else:
    st.header("AV Market Intelligence")
    st.info("Select a competitor to see their 2026 progress.")
