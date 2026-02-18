import streamlit as st
from google import genai
from exa_py import Exa
import pandas as pd

# 1. Page Config & Theme
st.set_page_config(page_title="AV Intel 2026", layout="wide", page_icon="🚗")

# 2. Initialize Clients (Using Streamlit Secrets)
# When deploying, you'll add these to the Streamlit Cloud dashboard
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
EXA_KEY = st.secrets["EXA_API_KEY"]

client = genai.Client(api_key=GEMINI_KEY)
exa = Exa(api_key=EXA_KEY)

# 3. Sidebar Setup
st.sidebar.title("Competitor Intel")
st.sidebar.info("Real-time L4 advancements for Feb 2026.")
competitor = st.sidebar.selectbox(
    "Select Company", 
    ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"]
)

# 4. Main Dashboard Logic
st.title(f"🚀 {competitor} Intelligence Brief")
st.caption(f"Last updated: February 18, 2026")

if st.button("Generate Latest Report"):
    with st.spinner(f"Scanning 90-day data for {competitor}..."):
        try:
            # Neural Search via Exa
            search = exa.search(
                f"latest {competitor} L4 autonomous driving city launch partnership Feb 2026",
                num_results=3,
                type="auto",
                start_published_date="2025-11-20",
                contents={"summary": True}
            )

            # Summarization via Gemini
            raw_data = "\n".join([f"Source: {r.url}\nSummary: {r.summary}" for r in search.results])
            prompt = f"Analyze these news summaries for {competitor}. Extract a 'Bottom Line' and any specific 2026 metrics.\n\n{raw_data}"
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt
            )

            # Display Layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Executive Summary")
                st.markdown(response.text)
                
                st.subheader("Top Recent Sources")
                for r in search.results:
                    st.markdown(f"- [{r.url}]({r.url})")

            with col2:
                st.subheader("Key 2026 Indicators")
                # Example hardcoded context for 2026 (or you can ask Gemini to extract these)
                st.info("Market Sentiment: **Bullish**")
                st.warning("Regulatory Status: **Active Inquiry**")

        except Exception as e:
            st.error(f"Error fetching data: {e}")
