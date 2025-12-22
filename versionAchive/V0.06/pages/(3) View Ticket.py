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

#############
# MAIN BODY #
#############

st.title("(3) View Ticket")
st.markdown("---")

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
                f.write("")
            st.session_state["vt_ticketThread"] = []
        else:
            if st.session_state["vt_ticketThread"] == []:
                with open(st.session_state["vt_selTicketThreadPath"], 'r') as f:
                    for line in f:
                        if line.strip():
                            st.session_state["vt_ticketThread"].append(json.loads(line))

        # DISPLAY - HEADER
        # st.json(vt_ticketHeader)

        # DISPLAY - THREAD
        if st.session_state["vt_ticketThread"] != []:
            for vt_comment in st.session_state["vt_ticketThread"]:
                with st.chat_message(vt_comment["author"]):
                    # COMMENT HEADER
                    st.write(f"**{vt_comment['author']}** · *{vt_comment['time']}*")
                    # ALLOW OVERFLOW FOR HORIZONTAL SCROLL
                    wrapped_content = f"""
                    <div style="overflow-x: auto; padding-bottom: 10px;">
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