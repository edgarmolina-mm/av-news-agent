import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime

# 1. Setup & Secrets
st.set_page_config(page_title="AV Intel 2026", layout="wide", page_icon="🚗")

# Use st.secrets for permanent deployment; otherwise, hardcode for local testing
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_KEY_HERE")
EXA_KEY = st.secrets.get("EXA_API_KEY", "YOUR_KEY_HERE")

client = genai.Client(api_key=GEMINI_KEY)
exa = Exa(api_key=EXA_KEY)

# 2. Session State to save the last report
if "report" not in st.session_state:
    st.session_state.report = None
    st.session_state.company = ""

# 3. Helper: Clean text for PDF (Remove Emojis)
def clean_for_pdf(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# 4. Helper: Create PDF
def create_pdf(content, company):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, f"{company} Intelligence Brief - 2026", 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(5)
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 10, clean_for_pdf(content), markdown=True)
    return pdf.output()

# --- UI Sidebar ---
st.sidebar.title("Competitor Intel")
target = st.sidebar.selectbox("Choose Competitor", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Generate {target} Report"):
    with st.spinner(f"Analyzing {target} market signals..."):
        try:
            # Search last 90 days
            search = exa.search(
                f"latest {target} L4 autonomous driving advancement Feb 2026",
                num_results=3,
                type="auto",
                start_published_date="2025-11-20",
                contents={"summary": True}
            )
            
            # Synthesize with Gemini
            context = "\n".join([f"Source: {r.url}\nSummary: {r.summary}" for r in search.results])
            prompt = f"Analyze these news items for {target}. Extract key 2026 milestones. Be concise.\n\n{context}"
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt
            )
            
            # Save to Session State
            st.session_state.report = response.text
            st.session_state.company = target
            st.session_state.sources = [r.url for r in search.results]
        except Exception as e:
            st.error(f"Limit reached or API Error: {e}")

# --- Main Dashboard Display ---
if st.session_state.report:
    st.title(f"🚀 {st.session_state.company} Status")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(st.session_state.report)
        
    with col2:
        st.subheader("Reference Links")
        for url in st.session_state.sources:
            st.caption(url)
        
        # Download Section
        pdf_data = create_pdf(st.session_state.report, st.session_state.company)
        st.download_button(
            label="📄 Export as PDF",
            data=bytes(pdf_data),
            file_name=f"{st.session_state.company}_Intel_2026.pdf",
            mime="application/pdf"
        )
else:
    st.header("Select a competitor to begin.")
    st.info("The dashboard will persist your last generated report in this session.")
