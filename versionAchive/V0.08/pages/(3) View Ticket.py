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
if "vt_ticketHeader" not in st.session_state:
    st.session_state["vt_ticketHeader"] = []
if "vt_ticketThread" not in st.session_state:
    st.session_state["vt_ticketThread"] = []
if "vt_editorKey" not in st.session_state:
    st.session_state["vt_editorKey"] = 0

# CSS SETTINGS
applyCompactStyle()

##########
# HELPER #
##########

def vt_getFullJsonl(fullPath):
    lsJsonl = []
    if not os.path.exists(fullPath):
        with open(fullPath, 'w') as f:
            f.write("")
    else:
        with open(fullPath, 'r') as f:
            for line in f:
                if line.strip():
                    lsJsonl.append(json.loads(line))
    return lsJsonl

@st.dialog('Change Ticket Stage')
def vt_dialogChangeStage():
    st.write('HEHE')

def renderTicketHeader(headerData):
    """
    Render Ticket Header V2
    - Top Row: Key Identity (Number + Status)
    - Body: 4 Columns of logically grouped data (Scope, Object, Context, Audit)
    """
    if not headerData:
        return
    
    # HEADER BOX COLOR
    st.markdown("""
        <style>
        div.st-key-ticketHeaderContainerL {
            background-color: #e2e8f0 !important; 
        }             

        div.st-key-ticketHeaderContainerR {
            background-color: #e2e8f0 !important; 
        }   
        </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1,3])
    with c1:
        with st.container(border=True, key="ticketHeaderContainerL"):
            # ROW 1
            st.caption("Ticket Number")
            st.markdown(f"### {headerData.get('TICKET_NUMBER', '-')}")            
            # ROW 2
            st.caption("Status")
            if headerData.get('STATUS') == "Completed":
                st.success(f"**{headerData.get('STATUS')}**", icon="🟢")
            elif headerData.get('STATUS') == "Cancelled":
                st.error(f"**{headerData.get('STATUS')}**", icon="🔴")
            else:
                st.info(f"**{headerData.get('STATUS')}**", icon="🔵")    
            # ROW 3
            st.caption("Stage")
            c1r2c1, c1r2c2 = st.columns([2,1])
            with c1r2c1:                
                st.info(f"**{headerData.get('STAGE', '-')}**", icon="📌")
            with c1r2c2:
                if st.button("Edit", use_container_width=True, key="vt_stageEditButton"):
                    vt_dialogChangeStage()
    with c2:
        with st.container(border=True, key="ticketHeaderContainerR"):
            c2c1, c2c2, c2c3 = st.columns(3)
            # COL 1
            with c2c1:
                # ROW 1
                st.caption("Creation")
                st.markdown(f"**Created By:** {headerData.get('TICKET_CREATED_BY', '-')}")
                st.markdown(f"**Created On:** {headerData.get('TICKET_CREATE_DTTM', '-')}")
                # ROW 2
                st.caption("Classification")
                st.markdown(f"**Type:** {headerData.get('TICKET_TYPE', '-')}")
                st.markdown(f"**Service:** {headerData.get('SERVICE_TYPE', '-')}")
                # ROW 3
                st.caption("SAP Details")
                st.markdown(f"**SAP Name:** {headerData.get('SAP_NAME', '-') or '-'}")
                st.markdown(f"**SAP Code:** {headerData.get('SAP_CODE', '-') or '-'}")
            # COL 2
            with c2c2:
                # ROW 1
                st.caption("Context")
                st.markdown(f"**Country:** {headerData.get('COUNTRY') or '-'}")
                st.markdown(f"**Ref Ticket:** {headerData.get('REFERENCE_TICKET_NUMBER') or '-'}")
                # ROW 2
                st.caption("Approval")
                st.markdown(f"**Approving Status:** {headerData.get('APPROVING_STATUS', '-') or '-'}")
                st.markdown(f"**Approving Date:** {headerData.get('APPROVING_DATE', '-') or '-'}")
                # ROW 3
                st.caption("Modified")
                st.markdown(f"**Modified By:** {headerData.get('LAST_MODIFIED_BY', '-') or '-'}")
                st.markdown(f"**Modified On:** {headerData.get('LAST_MODIFIED_DTTM', '-') or '-'}")
            # COL 3
            with c2c3:
                # ROW 1
                st.caption("Closing Details")
                st.markdown(f"**Closed By:** {headerData.get('TICKET_CLOSED_BY', '-') or '-'}")
                st.markdown(f"**Closed Date:** {headerData.get('TICKET_CLOSED_DTTM', '-') or '-'}")
                st.markdown(f"**Closed Code:** {headerData.get('TICKET_CLOSED_CODE', '-') or '-'}")
                st.markdown(f"**Callback Date:** {headerData.get('CALLBACK_DATE', '-') or '-'}")

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
        if st.session_state["vt_ticketHeader"]==[]:
            st.session_state["vt_ticketHeader"] = vt_getFullJsonl(st.session_state["vt_selTicketHeaderPath"])
        # GET THREAD
        if st.session_state["vt_ticketThread"]==[]:
            st.session_state["vt_ticketThread"] = vt_getFullJsonl(st.session_state["vt_selTicketThreadPath"])

        # DISPLAY - HEADER
        renderTicketHeader(st.session_state["vt_ticketHeader"][-1])
        st.markdown("&nbsp;", unsafe_allow_html=True)

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