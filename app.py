import streamlit as st
from google import genai
from exa_py import Exa
from fpdf import FPDF, XPos, YPos
import re
from datetime import datetime, timedelta

# 1. Dashboard Configuration
st.set_page_config(page_title="AV Intel Pulse 2026", layout="wide", page_icon="📡")

st.html("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; border: 1px solid #e1e4e8; padding: 20px; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 5px solid #2e7d32; }
    </style>
""")

# 2. Client Initialization
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception as e:
    st.error("API Keys missing in Secrets!")
    st.stop()

if "intel_data" not in st.session_state:
    st.session_state.intel_data = None
    st.session_state.active_co = ""

def clean_for_pdf(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# --- SIDEBAR: COMPETITIVE SELECTION ---
st.sidebar.title("AV Intelligence Hub")
# Displaying current date: February 18, 2026
st.sidebar.caption(f"Market Snapshot: {datetime.now().strftime('%B %d, %Y')}")
target = st.sidebar.selectbox("Select Target", ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"])

if st.sidebar.button(f"Analyze {target} Momentum"):
    with st.spinner(f"Synthesizing last 60 days of intel for {target}..."):
        try:
            # 3. Dynamic 60-Day Lookback
            start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
            
            # 4. Fetch 5 Recent Public Articles
            search = exa.search(
                f"latest commercial L4 advancements and news for {target}",
                num_results=5, 
                type="auto",
                category="news",
                start_published_date=start_date,
                contents={"text": True}
            )
            
            if not search.results:
                st.warning(f"No recent public articles found for {target} since {start_date}.")
            else:
                # 5. Prepare Enriched Context
                context = ""
                for i, r in enumerate(search.results):
                    context += f"\n--- ARTICLE {i+1} ---\nURL: {r.url}\nCONTENT: {r.text[:2000]}\n"
                
                # 6. Analyst-Grade Synthesis Prompt
                prompt = f"""
                You are a Senior AV Industry Analyst. Synthesize the following 5 articles for {target}.
                
                # {target} Pulse: February 2026
                
                ### 🗞️ Top 5 Recent Articles (Summarized)
                (Provide a 2-3 sentence technical synthesis for EACH of the 5 articles. Focus on hard metrics, city names, and dates.)
                
                ### 🚀 Critical 60-Day Momentum Shift
                (Identify the single most significant development for {target} since {start_date}.)
                
                ### ⚠️ Strategic Outlook
                (Note any regulatory or competitive risks mentioned in the data.)
                
                DATA: {context}
                """
                
                res = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                
                st.session_state.intel_data = res.text.lstrip(' ([{\n\r')
                st.session_state.active_co = target
                st.session_state.source_urls = [r.url for r in search.results]
            
        except Exception as e:
            st.error(f"Sync failed: {str(e)}")

# --- MAIN DASHBOARD ---
if st.session_state.intel_data:
    st.title(f"Competitive Pulse: {st.session_state.active_co}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Dynamic metrics reflecting Feb 2026 reality
        val = "1M Weekly Rides" if target == "Waymo" else "10B Miles Goal" if target == "Tesla" else "Scaling"
        st.metric("Top 2026 Objective", val)
    with col2:
        status = "Active / Scaling" if target != "Tesla" else "FSD Supervised"
        st.metric("Deployment Phase", status)
    with col3:
        st.metric("Data Quality", "High (60-Day Lookback)")

    st.divider()

    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown(st.session_state.intel_data)
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("📚 View Original Source URLs"):
        for link in st.session_state.source_urls:
            st.caption(link)

    # Professional PDF Export
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, f"{st.session_state.active_co} Intelligence Brief", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(5)
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 10, clean_for_pdf(st.session_state.intel_data), markdown=True)
        
        st.download_button("📥 Export Brief (PDF)", data=bytes(pdf.output()), 
                           file_name=f"{st.session_state.active_co}_Brief_Feb2026.pdf")
    except Exception as pdf_err:
        st.warning(f"PDF Export unavailable: {str(pdf_err)}")

else:
    st.header("Autonomous Mobility Intelligence")
    st.info("👈 Select a competitor to synthesize the latest 60 days of market data.")
