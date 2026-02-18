import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime

# 1. Page & Client Configuration
st.set_page_config(page_title="AV Pulse 2026", layout="wide", page_icon="📈")

# Standard styling for better readability
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_name_with_html=True)

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception as e:
    st.error("Missing API Keys in Settings > Secrets!")
    st.stop()

# Persistent session state
if "raw_report" not in st.session_state:
    st.session_state.raw_report = None
    st.session_state.active_co = ""
    st.session_state.source_list = []

def pdf_clean(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# --- SIDEBAR CONTROL ---
st.sidebar.title("Intelligence Hub")
st.sidebar.markdown("Get a real-time pulse on the AV market.")
target = st.sidebar.selectbox("Choose Competitor", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Scan {target} Momentum"):
    with st.spinner(f"Reading latest {target} signals..."):
        try:
            # 2. Precision Search: Filters out general industry noise
            query = f"site:maymobility.com OR '{target}' commercial driverless operations city expansion Feb 2026" if target == "May Mobility" else f"latest {target} L4 autonomous driving metrics Feb 2026"
            
            search = exa.search(
                query,
                num_results=3, 
                type="auto", 
                category="news",
                start_published_date="2025-12-01",
                contents={"summary": True}
            )
            
            # 3. User-Friendly Prompt: Executive Summary + Key Wins
            prompt = f"""
            Act as a Competitive Intelligence Specialist. Summarize the status of {target} for a new user.
            
            Structure your response as follows:
            ### 🏁 The Bottom Line
            (A 2-sentence summary of where they stand right now)
            
            ### 🚀 Recent Wins & Milestones
            (Bullet points of the most important news from the data)
            
            ### 📍 Where they are driving
            (Specific cities or launch zones mentioned)
            
            ### ⚠️ Current Challenges
            (Any regulatory issues, competition, or technical hurdles)
            
            DATA SOURCES:
            {chr(10).join([f"Source: {r.url} Summary: {r.summary}" for r in search.results])}
            """
            
            res = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            st.session_state.raw_report = res.text
            st.session_state.active_co = target
            st.session_state.source_list = [r.url for r in search.results]
                
        except Exception as e:
            st.error(f"Search failed: {e}")

# --- MAIN DASHBOARD ---
if st.session_state.raw_report:
    st.title(f"Competitive Pulse: {st.session_state.active_co}")
    
    # 4. Impact Metrics (Simplified for new users)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Primary Focus", "Mass-Market" if target == "Tesla" else "Ride-Hail")
    with m2:
        st.metric("2026 Momentum", "Expanding" if target in ["Waymo", "Zoox", "May Mobility"] else "Consolidating")
    with m3:
        # Dynamic Risk Assessment based on recent headlines
        st.metric("Risk Level", "Medium" if "investigation" in st.session_state.raw_report.lower() else "Low")
    
    st.divider()

    # 5. Display the Digestible Report
    st.markdown(st.session_state.raw_report)
    
    # Research Expander
    with st.expander("🔗 View Original Sources"):
        for link in st.session_state.source_list:
            st.write(f"- {link}")

    # Simplified PDF Export
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, f"{st.session_state.active_co} Intel - Feb 2026", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(5)
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 10, pdf_clean(st.session_state.raw_report), markdown=True)
        
        st.download_button("📥 Save this Brief as PDF", data=bytes(pdf.output()), 
                           file_name=f"{st.session_state.active_co}_Pulse.pdf")
    except Exception as pdf_err:
        st.error(f"PDF Error: {pdf_err}")
else:
    st.header("Welcome to the 2026 AV Tracker")
    st.write("👈 Select a company from the sidebar to get a 2-minute intelligence briefing.")
    
    # Educational Tip for New Users
    st.info("""
    **Did you know?** In early 2026, the AV market has split into two lanes:
    - **Waymo & Zoox:** Scaling 'Driverless Pods' in major urban hubs.
    - **Tesla:** Focusing on the 'Cybercab' for personal ownership and fleet use.
    """)
