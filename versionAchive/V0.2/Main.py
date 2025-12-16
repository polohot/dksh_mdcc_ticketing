from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from auth import render_login_sidebar

st.set_page_config(page_title="Main", layout="wide")

auth_logged_in, auth_user, auth_exp_dt = render_login_sidebar()

st.title("Main")

if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:
    st.write(f"Welcome, **{auth_user}**.")
    if st.button("Go to Landing"):
        st.switch_page("pages/(1) Landing.py")

st.code("""
[V0.2 - alpha] - 2025-12-16
- More refined and understandable auth code
        
[V0.1 - alpha] - 2025-12-16
- Initial login and page skeleton
""")