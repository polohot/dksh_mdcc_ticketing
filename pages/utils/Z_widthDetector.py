import streamlit as st
from streamlit_dimensions import st_dimensions

st.title("Real-Time Width Detector")

# This function listens to the resize event and triggers a rerun automatically
# returns a dictionary like {'width': 1200, 'height': 800}
dim = st_dimensions(key="main_container")

if dim:
    width = dim['width']
    st.metric("Browser Width", f"{width} px")
    