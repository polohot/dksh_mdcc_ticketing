import json
import streamlit as st
from auth import render_login_sidebar
st.set_page_config(page_title="(3) View Ticket", layout="wide")
auth_logged_in, auth_user, auth_exp_dt = render_login_sidebar()

# INIT SESSION STATE - AUTH
if "auth_logged_in" not in st.session_state:
    st.session_state.auth_logged_in = auth_logged_in
if "auth_user" not in st.session_state:
    st.session_state.auth_user = auth_user
if "auth_exp_dt" not in st.session_state:
    st.session_state.auth_exp_dt = auth_exp_dt

# HELPER





# BODY
st.title("(3) View Ticket")
if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:
    st.write(f"Welcome, **{auth_user}**.")




