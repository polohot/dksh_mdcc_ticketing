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
    st.session_state.vt_selTicketNumber = None
if "vt_ticketHeader" not in st.session_state:
    st.session_state.vt_ticketHeader = []
if "vt_ticketThread" not in st.session_state:
    st.session_state.vt_ticketThread = []
if "vt_editorKey" not in st.session_state:
    st.session_state.vt_editorKey = 0
if "vt_diffHeader" not in st.session_state:
    st.session_state.vt_diffHeader = {}

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

def getDictDiff(oldData, newData):
    diff = {}    
    # Get all unique keys from both dictionaries
    allKeys = set(oldData.keys()) | set(newData.keys())    
    for key in allKeys:
        oldVal = oldData.get(key)
        newVal = newData.get(key)        
        # If the values are different, record the change
        if oldVal != newVal:
            diff[key] = [oldVal, newVal]            
    return diff

def saveWhenHeaderChanges(currentTicket, newTicketDict):
    # LOG DIFF IN THREAD
    st.session_state["vt_diffHeader"] = getDictDiff(currentTicket, newTicketDict)
    st.session_state["vt_diffHeader"].pop('LAST_MODIFIED_DTTM', None)
    st.session_state["vt_diffHeader"].pop('LAST_MODIFIED_BY', None)
    # ONLY SAVE CHANGED IF THERE IS CHANGE IN THE HEADER
    if st.session_state["vt_diffHeader"] != {}:       

        ### HEADER 
        # SAVE JSONL
        with open(st.session_state["vt_selTicketHeaderPath"], 'a', encoding='utf-8') as f:
            jsonLine = json.dumps(newTicketDict)
            f.write(jsonLine + "\n")
        # RELOAD
        st.session_state["vt_ticketHeader"] = vt_getFullJsonl(st.session_state["vt_selTicketHeaderPath"])    

        ### THREAD - SAVE JSONL
        vt_content = f'<p>'
        for key, value in st.session_state["vt_diffHeader"].items():
            # We use 'display: inline-block' on spans to give them padding/backgrounds nicely
            vt_content += f"""
            <span style="color: #444; font-weight: bold;">{key}:</span> 
            <span style="background-color: #f0f0f0; color: #888; text-decoration: line-through;">{value[0]}</span>
            <span style="color: #ccc;">&rarr;</span>
            <span style="background-color: #e3f2fd; color: #0056b3; font-weight: bold;">{value[1]}</span>
            <br>
            """
        vt_content += "</p>"
        # BUILD COMMENT LOG
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
        # RELOAD
        st.session_state["vt_ticketThread"] = vt_getFullJsonl(st.session_state["vt_selTicketThreadPath"])
    
        ### REGENERATE TICKET INDEX
        stBar = st.progress(0, text="Syncing")
        lsFullPath = listAllJsonl3cat()
        rowList = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(getLastRecordOfJsonl, fullPath) for fullPath in lsFullPath]            
            total_files = len(futures)
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                if result:
                    rowList.append(result)                
                if i % 10 == 0 or i == total_files - 1:
                    percent_complete = int((i + 1) / total_files * 100)
                    stBar.progress(percent_complete, text=f"Syncing: {percent_complete}%")
        df = pd.DataFrame(rowList)
        stBar.empty()
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        df.to_csv(f"ticketDatabase/ticketIndex/{timestamp}.csv", index=False)
        # KEEP ONLY THE LATEST 10 CSV - DELETE ALL OTHER CSV
        lscsv = os.listdir(f"ticketDatabase/ticketIndex/")
        lscsv = [x for x in lscsv if x.endswith('.csv')]
        lscsv.sort(reverse=True)
        if len(lscsv) > 10:
            for csv in lscsv[10:]:
                os.remove(f"ticketDatabase/ticketIndex/{csv}")

@st.dialog('Change Ticket Stage')
def vt_dialogChangeStage():
    # GET LATEST HEADER
    currentTicket = st.session_state["vt_ticketHeader"][-1]
    # LIST OPTIONS
    lsStage = get_lsStage(currentTicket["STAGE"])
    vt_newStage = st.selectbox("**Update Stage** *", options=lsStage, key="vt_newStage")
    # CONDITION FOR CLOSURE
    if vt_newStage == "99C Cancelled":
        st.warning("You are cancelling this ticket. Please provide closure details.")
        vt_closureCode = st.text_input("Closure Code *", key="vt_closureCode")
        vt_closureNote = st.text_area("Closure Note *", key="vt_closureNote")
    # BUTTON
    if st.button("Save Changes"):
        newTicketDict = currentTicket.copy()
        # VALIDATION - 99C Cancelled - ERROR - CLOSURE CODE NOT FILLED
        if vt_newStage == "99C Cancelled" and vt_closureCode == "":
            st.error("Please fill in Closure Code.")
        # VALIDATION - 99C Cancelled - PASS
        elif vt_newStage == "99C Cancelled" and vt_closureNote != "":
            newTicketDict['STAGE'] = vt_newStage
            newTicketDict['STATUS'] = "Cancelled"
            newTicketDict['TICKET_CLOSED_BY'] = st.session_state.auth_user
            newTicketDict['TICKET_CLOSED_CODE'] = vt_closureCode
            newTicketDict['TICKET_CLOSED_NOTE'] = vt_closureNote
            newTicketDict['TICKET_CLOSED_DTTM'] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            newTicketDict["LAST_MODIFIED_BY"] = st.session_state.auth_user
            newTicketDict["LAST_MODIFIED_DTTM"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            saveWhenHeaderChanges(currentTicket, newTicketDict)
            st.rerun()
        # VALIDATION - 99A Sap Created - PASS
        elif vt_newStage == "99A Sap Created":
            newTicketDict['STAGE'] = vt_newStage
            newTicketDict['STATUS'] = "Completed"
            newTicketDict["LAST_MODIFIED_BY"] = st.session_state.auth_user
            newTicketDict["LAST_MODIFIED_DTTM"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            saveWhenHeaderChanges(currentTicket, newTicketDict)
            st.rerun()
        # VALIDATION - OTHER
        else:
            newTicketDict['STAGE'] = vt_newStage
            newTicketDict["LAST_MODIFIED_BY"] = st.session_state.auth_user
            newTicketDict["LAST_MODIFIED_DTTM"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            saveWhenHeaderChanges(currentTicket, newTicketDict)
            st.rerun()

@st.dialog('Edit Ticket Info', width='large')
def vt_dialogEditTicketInfo():
    # CLEAN
    st.session_state["vt_diffHeader"] = {}
    # GET LATEST HEADER
    currentTicket = st.session_state["vt_ticketHeader"][-1]
    with st.form("frm_edit_ticket"):     
        # ORGANIZE SIMILAR TO VIEW TICKET
        col1, col2, col3 = st.columns(3)
        with col1:            
            # ROW 1            
            st.subheader("Request Info")
            # SPECIAL FIX TO NOT MAKE FIELD "vt_newRequestInquiryDate" POP UP DATE SELECTION BOX IN THE BEGINNING
            reqDateVal = None
            if currentTicket.get('REQUEST_INQUIRY_DATE'):
                try: reqDateVal = datetime.datetime.strptime(currentTicket['REQUEST_INQUIRY_DATE'], "%Y-%m-%d").date()
                except: pass
            vt_newRequestInquiryDate = st.date_input("Request Inquiry Date", value=reqDateVal, format="YYYY-MM-DD", key="vt_newRequestInquiryDate")
            st.markdown(f"Country: {currentTicket['COUNTRY'] or '-'}")
            st.markdown(f"Business Line: {currentTicket['BL_CD'] or '-'}")
            # ROW 2 
            st.subheader("Classification")
            st.markdown(f"Type: {currentTicket['TICKET_TYPE'] or '-'}")
            st.markdown(f"Service Type: {currentTicket['SERVICE_TYPE'] or '-'}")
            # ROW 3
            st.subheader("SAP Details")
            vt_newSapName = st.text_input("SAP Name", value=currentTicket['SAP_NAME'])
            vt_newSapCode = st.text_input("SAP Code", value=currentTicket['SAP_CODE'])
        with col2:
            # ROW 1
            st.subheader("Ref Ticket")
            vt_newRefTicket = st.text_input("Ref Ticket", value=currentTicket['REFERENCE_TICKET_NUMBER'], key="vt_newRefTicket")
            # ROW 2
            st.subheader("Approval")
            vt_newAppStatus = st.text_input("Approving Status", value=currentTicket['APPROVING_STATUS'], key="vt_newAppStatus")
            try: vt_currentAppDate = datetime.datetime.strptime(currentTicket['APPROVING_DATE'], "%Y-%m-%d")
            except: vt_currentAppDate = None
            vt_newAppDate = st.date_input("Approving Date", value=vt_currentAppDate, format="YYYY-MM-DD", key="vt_newAppDate")
            # ROW 3
            st.subheader("Callback")
            try: vt_currentCallbackDate = datetime.datetime.strptime(currentTicket['CALLBACK_DATE'], "%Y-%m-%d")
            except: vt_currentCallbackDate = None
            vt_newCallbackDate = st.date_input("Callback Date", value=vt_currentCallbackDate, format="YYYY-MM-DD", key="vt_newCallbackDate")
            try: vt_currentCallbackTime = datetime.datetime.strptime(currentTicket['CALLBACK_TIME'], "%H:%M:%S")
            except: vt_currentCallbackTime = None
            vt_newCallbackTime = st.time_input("Callback Time", value=vt_currentCallbackTime, key="vt_newCallbackTime")  
        with col3:
            # ROW 1
            st.subheader("Request Missing Document Date")
            try: vt_currentRequestMissingDocDate = datetime.datetime.strptime(currentTicket['REQUEST_MISSING_DOC_DATE'], "%Y-%m-%d")
            except: vt_currentRequestMissingDocDate = None
            vt_newRequestMissingDocDate = st.date_input("Date", value=vt_currentRequestMissingDocDate, format="YYYY-MM-DD", key="vt_newRequestMissingDocDate")
            # ROW 2
            st.subheader("Save Changes")
            if st.form_submit_button("Save Changes"):
                newTicketDict = currentTicket.copy()
                newTicketDict["REQUEST_INQUIRY_DATE"] = str(vt_newRequestInquiryDate) if str(vt_newRequestInquiryDate) != "None" else None
                newTicketDict["SAP_NAME"] = vt_newSapName
                newTicketDict["SAP_CODE"] = vt_newSapCode
                newTicketDict["REFERENCE_TICKET_NUMBER"] = vt_newRefTicket
                newTicketDict["APPROVING_STATUS"] = vt_newAppStatus
                newTicketDict["APPROVING_DATE"] = str(vt_newAppDate) if str(vt_newAppDate) != "None" else None
                newTicketDict["CALLBACK_DATE"] = str(vt_newCallbackDate) if str(vt_newCallbackDate) != "None" else None
                newTicketDict["CALLBACK_TIME"] = str(vt_newCallbackTime) if str(vt_newCallbackTime) != "None" else None
                newTicketDict["REQUEST_MISSING_DOC_DATE"] = str(vt_newRequestMissingDocDate) if str(vt_newRequestMissingDocDate) != "None" else None
                newTicketDict["LAST_MODIFIED_BY"] = st.session_state.auth_user
                newTicketDict["LAST_MODIFIED_DTTM"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                saveWhenHeaderChanges(currentTicket, newTicketDict)
                st.rerun()



def renderTicketHeader():
    """
    Render Ticket Header V2
    - Top Row: Key Identity (Number + Status)
    - Body: 4 Columns of logically grouped data (Scope, Object, Context, Audit)
    """

    headerData = st.session_state["vt_ticketHeader"][-1]

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
            st.markdown(f"### {headerData['TICKET_NUMBER']}")       
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
            st.info(f"**{headerData.get('STAGE', '-')}**", icon="📌")
            if headerData.get('STAGE') not in ["99A Sap Created", "99C Cancelled"]:    
                if st.button("Change Stage", use_container_width=True, key="vt_stageEditButton"):
                    vt_dialogChangeStage()
            # ROW 4
            st.markdown(f"**Created:** {headerData.get('TICKET_CREATED_BY', '-')} ({headerData.get('TICKET_CREATE_DTTM', '-')})")

    with c2:
        with st.container(border=True, key="ticketHeaderContainerR"):
            c2c1, c2c2, c2c3 = st.columns(3)
            # COL 1
            with c2c1:
                # ROW 1
                st.caption("Request Info")
                st.markdown(f"**Requested By:** {headerData.get('REQUESTED_BY', '-') or '-'}")
                st.markdown(f"**Request Inquiry Date:** {headerData['REQUEST_INQUIRY_DATE'] or '-'}")                
                st.markdown(f"**Country:** {headerData.get('COUNTRY', '-') or '-'}")
                st.markdown(f"**Business Line:** {headerData.get('BL_CD', '-') or '-'}")
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
                st.caption("Ref Ticket")
                st.markdown(f"**Ref Ticket:** {headerData.get('REFERENCE_TICKET_NUMBER') or '-'}")
                # ROW 2
                st.caption("Approval")
                st.markdown(f"**Approving Status:** {headerData.get('APPROVING_STATUS', '-') or '-'}")
                st.markdown(f"**Approving Date:** {headerData.get('APPROVING_DATE', '-') or '-'}")
                # ROW 3
                st.caption("Callback")
                st.markdown(f"**Callback Date:** {headerData.get('CALLBACK_DATE', '-') or '-'}")
                st.markdown(f"**Callback Time:** {headerData.get('CALLBACK_TIME', '-') or '-'}")
                # ROW 4
                st.caption("Request Missing Document Date")
                st.markdown(f"**Date:** {headerData.get('REQUEST_MISSING_DOC_DATE', '-') or '-'}")

            # COL 3
            with c2c3:
                # ROW 1
                st.caption("Closing Details")
                with st.expander('Closing Details'):
                    st.markdown(f"**Closed By:** {headerData.get('TICKET_CLOSED_BY', '-') or '-'}")
                    st.markdown(f"**Closed Date:** {headerData.get('TICKET_CLOSED_DTTM', '-') or '-'}")
                    st.markdown(f"**Closed Code:** {headerData.get('TICKET_CLOSED_CODE', '-') or '-'}")
                    st.markdown(f"**Closed Note:** {headerData.get('TICKET_CLOSED_NOTE', '-') or '-'}")
                # ROW 2
                if headerData.get('STAGE') not in ["99A Sap Created", "99C Cancelled"]: 
                    st.caption("Edit Info")
                    if st.button("Edit Info", use_container_width=True, key="vt_EditInfoButton"):
                        vt_dialogEditTicketInfo()
                # ROW 3
                st.caption("Last Modified")
                st.markdown(f"{headerData.get('LAST_MODIFIED_BY', '-') or '-'} ({headerData.get('LAST_MODIFIED_DTTM', '-') or '-'})")

#############
# MAIN BODY #
#############

titlec1, titlec2 = st.columns([1,2], vertical_alignment="center")
with titlec1:
    st.title("(3) View Ticket")
with titlec2:
    renderNavigationButtons()

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
        renderTicketHeader()
        st.markdown("<br>", unsafe_allow_html=True)

        # DISPLAY - THREAD
        if st.session_state["vt_ticketThread"] != []:
            for vt_comment in st.session_state["vt_ticketThread"]:
                with st.container(border=True):

                    with st.chat_message(vt_comment["author"]):
                        # COMMENT HEADER
                        st.write(f"**{vt_comment['author']}** · *{vt_comment['time']}*")
                        st.markdown("<br>", unsafe_allow_html=True)
                        # ALLOW OVERFLOW FOR HORIZONTAL SCROLL
                        wrapped_content = f"""
                        <div style="overflow-x: auto; padding-bottom: 0px;">
                            {vt_comment["content"]}
                        </div>
                        """
                        st.markdown(wrapped_content, unsafe_allow_html=True)

        # ONLY ALLOW ADD THREAD IF TICKER NOT CLOSED
        if st.session_state["vt_ticketHeader"][-1]['STAGE'] not in ["99A Sap Created", "99C Cancelled"]:
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