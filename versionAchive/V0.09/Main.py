import datetime
import json
import os
import pandas as pd
import concurrent.futures
import streamlit as st
from h_auth import render_login_sidebar
from h_streamlit_custom_editor import custom_editor
from h_css import *
from h_json import *
from h_selectList import *

st.set_page_config(page_title="Main", layout="wide")
st.logo("logo.png", size='large')
auth_logged_in, auth_user, auth_exp_dt = render_login_sidebar()

# INIT SESSION STATE - AUTH
if "auth_logged_in" not in st.session_state:
    st.session_state.auth_logged_in = auth_logged_in
if "auth_user" not in st.session_state:
    st.session_state.auth_user = auth_user
if "auth_exp_dt" not in st.session_state:
    st.session_state.auth_exp_dt = auth_exp_dt

# CSS SETTINGS
applyCompactStyle()

# BODY
st.title("Main")
st.markdown("---")

if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:   
    
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
[V0.09-alpha] - 2025-12-24
- Check point

[V0.08-alpha] - 2025-12-23
- Revamp "View Ticket" split columns
        
[V0.07-alpha] - 2025-12-22
- Added "Super Nova" Logo
- Update View ticket to show more compact ticket detail
- Add some styling to View ticket - header section

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
