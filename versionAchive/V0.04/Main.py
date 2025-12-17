import json
import streamlit as st
from auth import render_login_sidebar
st.set_page_config(page_title="Main", layout="wide")
auth_logged_in, auth_user, auth_exp_dt = render_login_sidebar()

# INIT SESSION STATE - AUTH
if "auth_logged_in" not in st.session_state:
    st.session_state.auth_logged_in = auth_logged_in
if "auth_user" not in st.session_state:
    st.session_state.auth_user = auth_user
if "auth_exp_dt" not in st.session_state:
    st.session_state.auth_exp_dt = auth_exp_dt

# BODY
st.title("Main")
if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:
    st.write(f"Welcome, **{auth_user}**.")
    if st.button("(1) All Tickets"):
        st.switch_page("pages/(1) All Tickets.py")
    if st.button("(2) Create Ticket"):
        st.switch_page("pages/(2) Create Ticket.py")
    if st.button("(3) View Ticket"):
        st.switch_page("pages/(3) View Ticket.py")

        

st.code("""
[V0.04 - alpha] - 2025-12-17
- Found way to use tiny editor free version
        
[V0.03 - alpha] - 2025-12-16
- Checkpoint end of day
- Material Ticket Creation - In Progress        

[V0.02 - alpha] - 2025-12-16
- More refined and understandable auth code
        
[V0.01 - alpha] - 2025-12-16
- Initial login and page skeleton
""")
