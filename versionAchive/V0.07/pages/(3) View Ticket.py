import datetime
import json
import os
import pandas as pd
import concurrent.futures
import streamlit as st
from h_auth import render_login_sidebar
from h_streamlit_custom_editor import custom_editor
from h_css import *

st.set_page_config(page_title="(3) View Ticket", layout="wide")
st.logo("logo.png", size='large')
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
if "vt_ticketThread" not in st.session_state:
    st.session_state["vt_ticketThread"] = []
if "vt_editorKey" not in st.session_state:
    st.session_state["vt_editorKey"] = 0

# CSS SETTINGS
applyCompactStyle()

##########
# HELPER #
##########
def renderTicketHeader(headerData):
    """
    Render Ticket Header V2
    - Top Row: Key Identity (Number + Status)
    - Body: 4 Columns of logically grouped data (Scope, Object, Context, Audit)
    """
    if not headerData:
        return
    
    st.markdown("""
        <style>
        div[data-testid="stLayoutWrapper"]:has(.st-key-ticketHeaderContainer) {
            background-color: #eef6ff !important; 
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container(border=True, key="ticketHeaderContainer"):
        # --- SECTION 1: HEADER (Identity) ---
        cRow1_1, cRow1_2, cRow1_3, cRow1_4 = st.columns(4)
        
        with cRow1_1:
            st.caption("Ticket Number")
            st.markdown(f"### {headerData.get('TICKET_NUMBER', '-')}")
        
        with cRow1_2:
            st.caption("Status")
            status = headerData.get('STATUS')
            if status == "Completed":
                st.success(f"**{status}**", icon="🟢")
            elif status == "Cancelled":
                st.error(f"**{status}**", icon="🔴")
            else:
                st.info(f"**{status}**", icon="🔵")

        with cRow1_3:
            st.caption("Stage")
            st.markdown(f"**{headerData.get('STAGE', '-')}**")

        with cRow1_4:
            st.caption("Creation")
            st.markdown(f"**Created By:** {headerData.get('TICKET_CREATED_BY', '-')}")
            st.markdown(f"**Created On:** {headerData.get('TICKET_CREATE_DTTM', '-')}")

        # --- SECTION 2: DETAILS GRID (4 Columns) ---
        cRow2_1, cRow2_2, cRow2_3, cRow2_4 = st.columns(4)

        # COLUMN 1: CLASSIFICATION (What is this?)
        with cRow2_1:
            st.caption("Classification")
            st.markdown(f"**Type:** {headerData.get('TICKET_TYPE', '-')}")
            st.markdown(f"**Service:** {headerData.get('SERVICE_TYPE', '-')}")

        # COLUMN 2: SAP / OBJECT DETAILS (What is it touching?)
        with cRow2_2:
            st.caption("SAP Details")
            st.markdown(f"**SAP Name:** {headerData.get('SAP_NAME', '-') or '-'}")
            st.markdown(f"**SAP Code:** {headerData.get('SAP_CODE', '-') or '-'}")

        # COLUMN 3: CONTEXT (Where is it?)
        with cRow2_3:
            st.caption("Context")
            st.markdown(f"**Country:** {headerData.get('COUNTRY') or '-'}")
            st.markdown(f"**Ref Ticket:** {headerData.get('REFERENCE_TICKET_NUMBER') or '-'}")

        # COLUMN 4: AUDIT (Who & When?) - Merged display
        with cRow2_4:
            st.caption("Approval")
            st.markdown(f"**Approving Status:** {headerData.get('APPROVING_STATUS', '-')}")
            st.markdown(f"**Approving Date:** {headerData.get('APPROVING_DATE', '-')}")
            
        
        cRow3_1, cRow3_2, cRow3_3, cRow3_4 = st.columns(4)
        with cRow3_1:
            with st.expander('Closing Details'):
                st.markdown(f"**Closed By:** {headerData.get('TICKET_CLOSED_BY', '-')}")
                st.markdown(f"**Closed Date:** {headerData.get('TICKET_CLOSED_DTTM', '-')}")
                st.markdown(f"**Closed Code:** {headerData.get('TICKET_CLOSED_CODE', '-')}")
                st.markdown(f"**Callback Date:** {headerData.get('CALLBACK_DATE', '-')}")
        
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
        # GET HEADER
        with open(st.session_state["vt_selTicketHeaderPath"], 'r') as f:
            vt_ticketHeader = json.load(f)

        # GET THREAD - CREATE JSONL IF NOT EXISTS
        if not os.path.exists(st.session_state["vt_selTicketThreadPath"]):
            with open(st.session_state["vt_selTicketThreadPath"], 'w') as f:
                f.write("")
            st.session_state["vt_ticketThread"] = []
        else:
            if st.session_state["vt_ticketThread"] == []:
                with open(st.session_state["vt_selTicketThreadPath"], 'r') as f:
                    for line in f:
                        if line.strip():
                            st.session_state["vt_ticketThread"].append(json.loads(line))

        # DISPLAY - HEADER
        renderTicketHeader(vt_ticketHeader)
        #st.json(vt_ticketHeader)

        # DISPLAY - THREAD
        if st.session_state["vt_ticketThread"] != []:
            for vt_comment in st.session_state["vt_ticketThread"]:
                with st.container(border=True):

                    with st.chat_message(vt_comment["author"]):
                        # COMMENT HEADER
                        st.write(f"**{vt_comment['author']}** · *{vt_comment['time']}*")
                        # ALLOW OVERFLOW FOR HORIZONTAL SCROLL
                        wrapped_content = f"""
                        <div style="overflow-x: auto; padding-bottom: 0px;">
                            {vt_comment["content"]}
                        </div>
                        """
                        st.markdown(wrapped_content, unsafe_allow_html=True)

        # DISPLAY - EDITOR
        vt_editorKey = f"content_custom_editor_{st.session_state.vt_editorKey}"
        vt_content = custom_editor(
            height=300, 
            initialValue="", 
            key=vt_editorKey,
            toolbar="undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image | align lineheight | numlist bullist indent outdent", 
            plugins=["image", "link", "lists", "table"]
        )

        # DISPLAY - EDITOR - POST ACTION
        if st.button("Post Comment", type="primary"):
            if vt_content and len(vt_content) > 10:
                vt_new_comment = {
                    "author": st.session_state.auth_user,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "content": vt_content}
                st.session_state["vt_ticketThread"].append(vt_new_comment)
                # SAVE JSONL
                with open(st.session_state["vt_selTicketThreadPath"], 'a', encoding='utf-8') as f:
                    jsonLine = json.dumps(vt_new_comment)
                    f.write(jsonLine + "\n")


                st.session_state.vt_editorKey += 1
                st.rerun()
            else:
                st.warning("Please enter some text or add an image before posting.")
            
        st.markdown("---")
    # DEBUG
    with st.expander('DEBUG', expanded=False):
        st.json(st.session_state)