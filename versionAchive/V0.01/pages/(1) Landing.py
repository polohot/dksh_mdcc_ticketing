from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from auth import render_login_sidebar

st.set_page_config(page_title="Landing", layout="wide")

logged_in, user, exp_dt, days_left = render_login_sidebar()

st.title("Landing")

if not logged_in:
    st.info("Please login using the left tab (sidebar).")
else:
    st.write(f"Hello **{user}** 👋")
    if st.button("Go to Main page"):
        st.switch_page("Main.py")
