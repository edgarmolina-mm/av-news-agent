import streamlit as st
from google import genai
from exa_py import Exa
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="AV Intel Pulse 2026", layout="wide", page_icon="📡")

# 2. Precision CSS for "Longest Name" Width
st.markdown("""
    <style>
    /* Force buttons to only be as wide as their text content */
    div.stButton > button {
        width: max-content !important;
        min-width: 0px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }
    
    .main { background-color: #f4f7f6; }
    .report-card { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 5px solid #2e7d32;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ... (Client initialization remains same) ...

# --- SIDEBAR: CONTROLS ---
st.sidebar.title("AV Intelligence Hub")
target_list = ["Waymo", "Tesla", "Zoox", "Motional", "May Mobility"]
target = st.sidebar.selectbox("Select Target", target_list)

# The button label now dynamically reflects the selected company
button_label = f"Pull {target} Intel"

if st.sidebar.button(button_label, width="content"): # Set width to content
    with st.spinner(f"Accessing 2026 news wires for {target}..."):
        # ... (Search and synthesis logic remains same) ...
        try:
            # (Fetching data and generating content as before)
            pass
        except Exception as e:
            st.error(f"Sync failed: {str(e)}")

# --- MAIN DASHBOARD DISPLAY ---
if st.session_state.get("intel_data"):
    # (Dashboard rendering logic remains same)
    st.title(f"Competitive Pulse: {st.session_state.active_co}")
    # ...
else:
    st.header("Autonomous Mobility Intelligence")
    st.info("Select a competitor to see the Feb 18, 2026 market update.")
