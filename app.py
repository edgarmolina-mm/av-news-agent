import streamlit as st
from google import genai
from exa_py import Exa
import time
from fpdf import FPDF, XPos, YPos

# 1. Page & Client Setup
st.set_page_config(page_title="AV Intel Tracker", layout="wide")
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
exa = Exa(api_key=st.secrets["EXA_API_KEY"])

# 2. Initialize Session State (This is your "Session Memory")
if "last_report" not in st.session_state:
    st.session_state.last_report = None

# 3. Cached Report Generation (This is your "Disk Memory")
@st.cache_data(persist="disk", show_spinner=False)
def generate_cached_report(company):
    # Fetch data
    search = exa.search(
        f"latest {company} L4 autonomous driving advancements Feb 2026",
        num_results=2,
        type="auto",
        contents={"summary": True}
    )
    
    # Process with Gemini
    context = "\n".join([f"Source: {r.url}\nSummary: {r.summary}" for r in search.results])
    prompt = f"Provide a high-level 2026 update for {company} based on: {context}. Use no emojis."
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    return {"text": response.text, "sources": [r.url for r in search.results]}

# --- UI LAYOUT ---
st.title("🚦 L4 Competitor Intelligence")

company = st.selectbox("Select Competitor", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.button(f"Generate New {company} Report"):
    with st.spinner("Analyzing market data..."):
        report_data = generate_cached_report(company)
        st.session_state.last_report = report_data
        st.session_state.current_company = company

# --- DISPLAY LAST REPORT ---
if st.session_state.last_report:
    st.divider()
    st.subheader(f"Latest Intelligence: {st.session_state.get('current_company', '')}")
    st.markdown(st.session_state.last_report["text"])
    
    with st.expander("View Sources"):
        for url in st.session_state.last_report["sources"]:
            st.write(url)

    # 4. PDF Export Logic (In-memory for download)
    def create_pdf(text):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        pdf.multi_cell(0, 10, text)
        return pdf
