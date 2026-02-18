import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime, timedelta

# 1. Page & Layout Configuration
st.set_page_config(page_title="AV Intel Pulse 2026", layout="wide", page_icon="📡")

# Professional Dashboard Styling
st.html("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; border: 1px solid #e1e4e8; padding: 20px; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 5px solid #2e7d32; }
    /* Dynamic Button Width Hack */
    div.stButton > button { width: max-content !important; min-width: 0px !important; padding: 0 20px !important; }
    </style>
""")

# 2. Secure Client Initialization
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception:
    st.error("⚠️ API Keys missing in Secrets!")
    st.stop()

# Persistent State Management
if "intel_data" not in st.session_state:
    st.session_state.intel_data = None
    st.session_state.active_co = ""
    st.session_state.source_urls = []

# --- HELPER FUNCTIONS ---
def clean_for_pdf(text):
    """Removes non-ASCII characters that standard PDF fonts can't render."""
    return re.sub(r'[^\x00-\x7F]+', '', text)

def create_pdf(report_text, company):
    """Generates a binary PDF file from the report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, f"{company} Market Intelligence - Feb 2026", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    pdf.set_font("helvetica", size=12)
    # multi_cell handles text wrapping automatically
    pdf.multi_cell(0, 10, clean_for_pdf(report_text))
    return bytes(pdf.output()) # Return binary bytes

# --- SIDEBAR: CONTROLS ---
st.sidebar.title("AV Intelligence Hub")
st.sidebar.caption(f"Snapshot: {datetime.now().strftime('%B %d, %Y')}")
target = st.sidebar.selectbox("Select Target", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Scan {target} Momentum"):
    with st.spinner(f"Synthesizing 60 days of {target} data..."):
        try:
            lookback = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
            search = exa.search(
                f"latest commercial L4 advancements and metrics for {target} 2026",
                num_results=5, 
                type="auto",
                category="news",
                start_published_date=lookback,
                contents={"text": True}
            )
            
            if not search.results:
                st.warning(f"No recent news found for {target} since {lookback}.")
            else:
                context = "\n".join([f"Source: {r.url}\nContent: {r.text[:1500]}" for r in search.results])
                prompt = f"""
                Act as a Senior Analyst. Synthesize the last 60 days for {target} into a speed-reading digest.
                - Headline News (1 sentence)
                - 3 Bulleted Metrics (cities, production, or miles)
                - 1 Strategic Risk/Outlook
                DATA: {context}
                """
                res = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                
                st.session_state.intel_data = res.text.lstrip(' ([{\n\r')
                st.session_state.active_co = target
                st.session_state.source_urls = [r.url for r in search.results]
                
        except Exception as e:
            st.error(f"Failed to fetch data: {str(e)}")

# --- MAIN DASHBOARD DISPLAY ---
if st.session_state.intel_data:
    st.header(f"Pulse: {st.session_state.active_co}")
    
    # KPI Row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Primary Goal", "Scaling Operations" if target != "Tesla" else "Volume Production")
    with c2:
        st.metric("News Density", "High (60-Day Window)")
    with c3:
        st.metric("Deployment", "Level 4 Active" if target != "Tesla" else "L2/L3 Hybrid")

    st.divider()

    # The Report Digest
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown(st.session_state.intel_data)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()

    # PDF Download Section
    pdf_bytes = create_pdf(st.session_state.intel_data, st.session_state.active_co)
    st.download_button(
        label=f"📥 Download {st.session_state.active_co} Report (PDF)",
        data=pdf_bytes,
        file_name=f"{st.session_state.active_co}_Briefing_Feb2026.pdf",
        mime="application/pdf"
    )

    with st.expander("📚 Explore Original Sources"):
        for link in st.session_state.source_urls:
            st.caption(link)
else:
    st.title("Autonomous Mobility Intelligence")
    st.info("👈 Select a competitor to begin your market analysis.")
