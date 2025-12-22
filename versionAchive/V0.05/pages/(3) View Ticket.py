import datetime
import json
import os
import pandas as pd
import streamlit as st
from h_auth import render_login_sidebar

st.set_page_config(page_title="(3) View Ticket", layout="wide")
auth_logged_in, auth_user, auth_exp_dt = render_login_sidebar()

# INIT SESSION STATE - AUTH
if "auth_logged_in" not in st.session_state:
    st.session_state.auth_logged_in = auth_logged_in
if "auth_user" not in st.session_state:
    st.session_state.auth_user = auth_user
if "auth_exp_dt" not in st.session_state:
    st.session_state.auth_exp_dt = auth_exp_dt

# INIT SESSION STATE - CUSTOM
if "vt_selTicketNumber" not in st.session_state:
    st.session_state["vt_selTicketNumber"] = None

#############
# MAIN BODY #
#############

st.title("(3) View Ticket")

if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:
    # CHECK IF WE HAVE TICKET DATA IN SESSION STATE
    if st.session_state["vt_selTicketNumber"] is None:
        st.warning("No ticket selected. Please go back to the 'All Tickets' page.")
        if st.button("Go to All Tickets"):
             st.switch_page("pages/(1) All Tickets.py")
    else:
        # SHOW TICKET HEADER
        st.subheader(f"Ticket: {st.session_state["vt_selTicketNumber"]} ({st.session_state["vt_selTicketType"]})")

        # GET HEADER
        with open(st.session_state["vt_selTicketHeaderPath"], 'r') as f:
            vt_ticketHeader = json.load(f)
        # GET THREAD - CREATE JSONL IF NOT EXISTS
        if not os.path.exists(st.session_state["vt_selTicketThreadPath"]):
            with open(st.session_state["vt_selTicketThreadPath"], 'w') as f:
                f.write("[]")
        with open(st.session_state["vt_selTicketThreadPath"], 'r') as f:
            vt_ticketThread = json.load(f)

        # DISPLAY - HEADER
        st.json(vt_ticketHeader)

        # DISPLAY - THREAD
        # st.json(vt_ticketThread)
        # Load "jsonl" from path st.session_state["vt_selTicketThreadPath"]


        # DEBUG
        st.json(st.session_state)
            
        # Optional: Back Button
        st.markdown("---")
        if st.button("← Back to List"):
            st.switch_page("pages/(1) All Tickets.py")