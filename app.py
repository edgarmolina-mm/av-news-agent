import streamlit as st
from google import genai
from exa_py import Exa
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="AV Intel Pulse 2026", layout="wide", page_icon="📡")

# 2. Secure Client Initialization
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    exa = Exa(api_key=st.secrets["EXA_API_KEY"])
except Exception:
    st.error("⚠️ API Keys missing! Add them in Settings > Secrets.")
    st.stop()

# Persistent State
if "intel_data" not in st.session_state:
    st.session_state.intel_data = None
    st.session_state.active_co = ""

# --- SIDEBAR: CONTROLS ---
st.sidebar.title("AV Intelligence Hub")
target = st.sidebar.selectbox("Select Target", ["Waymo", "Tesla", "Zoox", "May Mobility"])

if st.sidebar.button(f"Scan {target} Momentum"):
    with st.spinner(f"Synthesizing 60 days of {target} data..."):
        try: # Pair this try with the except below
            lookback = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
            query = f"latest commercial L4 advancements for {target} 2026"
            
            search = exa.search(
                query,
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
                prompt = f"Synthesize these articles for {target}. Headline News (1 sentence), Metrics, and Risk. DATA: {context}"
                res = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
                
                st.session_state.intel_data = res.text.lstrip(' ([{\n\r')
                st.session_state.active_co = target
        
        # REQUIRED: Handles the SyntaxError by closing the try block
        except Exception as e:
            st.error(f"Failed to fetch data: {str(e)}")

# --- MAIN DASHBOARD ---
if st.session_state.intel_data:
    st.header(f"Pulse: {st.session_state.active_co}")
    st.info(st.session_state.intel_data)
else:
    st.title("Autonomous Mobility Intelligence")
    st.info("👈 Select a competitor to synthesize the latest market data.")
