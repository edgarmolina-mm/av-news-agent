import streamlit as st
from google import genai
from exa_py import Exa

# Page Config
st.set_page_config(page_title="AV Intel Tracker", layout="wide")

# Initialize Clients
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
exa = Exa(api_key=st.secrets["EXA_API_KEY"])

st.title("🚦 AV Competitor Intelligence Dashboard")

# Competitor Selection
company = st.selectbox("Select Target Company", ["May Mobility", "Motional", "Tesla", "Waymo", "Zoox"])

if st.button(f"Generate {company} Report"):
    with st.spinner("Searching for latest AV news and metrics..."):
        # 1. Search for News and Metrics via Exa
        search_result = exa.search(
            f"Latest L4 autonomous driving updates for {company} including city launches, fleet size, and funding as of Feb 2026",
            num_results=3,
            type="auto",
            contents={"summary": True} # Getting summaries directly from Exa
        )

        # 2. Synthesize with Gemini
        context = "\n".join([f"Source: {r.url}\nSummary: {r.summary}" for r in search_result.results])
        prompt = f"Using this data: {context}, provide a technical summary of {company}'s current L4 status. Include a bulleted list of city launches and key metrics (fleet size, capital)."
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite", # High-speed model for 2026
            contents=prompt
        )

        # 3. Display Results
        st.subheader(f"Current Status: {company}")
        st.markdown(response.text)
        
        with st.expander("View Source Links"):
            for res in search_result.results:
                st.write(res.url)
