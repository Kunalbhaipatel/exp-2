
import streamlit as st

st.set_page_config(page_title="Home - Rig Dashboard", layout="wide")
st.title("🏠 Welcome to the Rig Analysis Dashboard")

st.markdown("""
This multipage dashboard includes:
- Well Overview
- Summary Charts
- Derrick vs Non-Derrick Cost Comparison
- 🔍 Advanced Shaker Scenario Simulator (see sidebar)

Use the navigation on the left to explore each feature.
""")

st.info("Select a page from the sidebar to begin.")
