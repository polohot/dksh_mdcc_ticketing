import json
import streamlit as st
from h_auth import render_login_sidebar
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
    # st.write(f"Welcome, **{auth_user}**.")
    # if st.button("(1) All Tickets"):
    #     st.switch_page("pages/(1) All Tickets.py")
    # if st.button("(2) Create Ticket"):
    #     st.switch_page("pages/(2) Create Ticket.py")
    # if st.button("(3) View Ticket"):
    #     st.switch_page("pages/(3) View Ticket.py")

    st.markdown("---")
    
    # DASHBOARD LAYOUT
    dashCol1, dashCol2, dashCol3 = st.columns(3)

    # COLUMN 1: ALL TICKETS
    with dashCol1:
        with st.container(border=True):
            st.markdown("## 📂")
            st.subheader("All Tickets")
            st.write("Browse, search, and filter through the complete history of tickets.")
            st.markdown("<br>", unsafe_allow_html=True) # Spacing
            if st.button("View List", use_container_width=True):
                st.switch_page("pages/(1) All Tickets.py")

    # COLUMN 2: CREATE TICKET
    with dashCol2:
        with st.container(border=True):
            st.markdown("## 🆕")
            st.subheader("Create Ticket")
            st.write("Initiate a new request for Material, Customer, or Vendor setup.")
            st.markdown("<br>", unsafe_allow_html=True) # Spacing
            if st.button("Create New", use_container_width=True):
                st.switch_page("pages/(2) Create Ticket.py")

    # COLUMN 3: VIEW TICKET
    with dashCol3:
        with st.container(border=True):
            st.markdown("## 🎫")
            st.subheader("View Ticket")
            st.write("Return to the details and discussion thread of your selected ticket.")
            st.markdown("<br>", unsafe_allow_html=True) # Spacing
            if st.button("Go to View Ticket", use_container_width=True):
                st.switch_page("pages/(3) View Ticket.py")

    st.markdown("---")

st.caption("Changelog")

st.code("""
[V0.06-alpha] - 2025-12-22
- Enable Thread in "View Ticket"
- Enhance Visual in "Main" and "Create Ticket"
        
[V0.05-alpha] - 2025-12-22
- Basic Create and view ticket

[V0.04-alpha] - 2025-12-17
- Found way to use tiny editor free version
        
[V0.03-alpha] - 2025-12-16
- Checkpoint end of day
- Material Ticket Creation - In Progress

[V0.02-alpha] - 2025-12-16
- More refined and understandable auth code
        
[V0.01-alpha] - 2025-12-16
- Initial login and page skeleton
""")
