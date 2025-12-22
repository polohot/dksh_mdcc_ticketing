import datetime
import json
import os
import pandas as pd
import concurrent.futures
import streamlit as st
from h_auth import render_login_sidebar
from h_streamlit_custom_editor import custom_editor
from h_css import *

st.set_page_config(page_title="(2) Create Ticket", layout="wide")
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
if "ct_ticketType" not in st.session_state:
    st.session_state.ct_ticketType = 'SelType'
if "ct_activeDialog" not in st.session_state:
    st.session_state.ct_activeDialog = 0
if "ct_ticketData" not in st.session_state:
    st.session_state.ct_ticketData = {}
if "ct_showProgressBar" not in st.session_state:
    st.session_state.ct_showProgressBar = False

# INIT SESSION STATE - CUSTOM
if "vt_selTicketNumber" not in st.session_state:
    st.session_state["vt_selTicketNumber"] = None

# CSS SETTINGS
applyCompactStyle()

# CONSTANTS
lsCountry = ["","TH", "MM", "VM", "KH"]
lsBL = ["", "FBI", "PCI", "PHI", "SCI"]  
lsServiceType = ["Creation","CLPA","Extend","Update","Update Bank Details","Mark/Unmark for Deletion","Regulatory Review","Block/UnBlock"]
lsStatus = ['Open','Completed','Cancelled']

##################
# HELPER GENERIC #
##################

def ct_getTicketData():
    from datetime import datetime, timezone
    ct_ticketData = {
        "TICKET_NUMBER": None,
        "TICKET_CREATE_DTTM": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "TICKET_CREATED_BY": auth_user,
        "TICKET_TYPE": st.session_state.get("dialog_TICKET_TYPE"),
        "SAP_CODE": None,
        "SAP_NAME": st.session_state.get("dialog_SAP_NAME"),
        "REQUESTED_BY": st.session_state.get("dialog_REQUESTED_BY"),
        "COUNTRY": st.session_state.get("dialog_COUNTRY"),
        "BL_CD": st.session_state.get("dialog_BL_CD"),
        "SERVICE_TYPE": st.session_state.get("dialog_SERVICE_TYPE"),
        "SUBJECT": None,
        "CALLBACK_DATE": st.session_state.get("dialog_CALLBACK_DATE"),
        "CALLBACK_TIME": st.session_state.get("dialog_CALLBACK_TIME"),
        "REFERENCE_TICKET_NUMBER": None,
        "REQUEST_MISSING_DOC_DATE": None,
        "APPROVING_STATUS": None,
        "APPROVING_DATE": None,
        "SAP_CREATED_DATE": None,  
        "STAGE": None,
        "STATUS": st.session_state.get("dialog_STATUS"),
        "TICKET_CLOSED_BY": None,
        "TICKET_CLOSED_CODE": None,
        "TICKET_CLOSED_NOTE": None,
        "TICKET_CLOSED_DTTM": None}
    st.session_state.ct_ticketData = ct_ticketData

def ct_getTicketNaming(ct_folderPath, ct_prefix):
    from datetime import datetime
    # GET CURRENT YEAR
    current_year = str(datetime.now().year)
    # GET ALL FILES OF YEAR
    with os.scandir(ct_folderPath) as entries:
        filenames = [entry.name for entry in entries if entry.is_file()]
    filenames = [x for x in filenames if x.endswith('.json')]
    filenames = [x for x in filenames if x.split('---')[1] == current_year]
    # CASE1: FIRST FILE OF THE YEAR
    if len(filenames)==0:
        ct_ticketNumber = f"{ct_prefix}---{current_year}---000001"
        ct_ticketPath = f"{ct_folderPath}{ct_prefix}---{current_year}---000001.json"
    # CASE2: OTHER
    else:
        nnnnnn1 = [x.split('---')[2].split('.')[0] for x in filenames]
        nnnnnn1 = [int(x) for x in nnnnnn1]
        nnnnnn2 = max(nnnnnn1) + 1
        nnnnnn2 = str(nnnnnn2).zfill(6)
        ct_ticketNumber = f"{ct_prefix}---{current_year}---{nnnnnn2}"
        ct_ticketPath = f"{ct_folderPath}{ct_prefix}---{current_year}---{nnnnnn2}.json"
    return ct_ticketNumber, ct_ticketPath

def ct_saveJson():
    # DETERMINE TICKET TYPE
    if st.session_state.ct_ticketType == "Material":
        ct_folderPath = 'ticketHeader/Material/'
        ct_prefix = "MATE"
    elif st.session_state.ct_ticketType == "Customer":
        ct_folderPath = 'ticketHeader/Customer/'
        ct_prefix = "CUST"
    elif st.session_state.ct_ticketType == "Vendor":
        ct_folderPath = 'ticketHeader/Vendor/'
        ct_prefix = "VEND"    
    # ENSURE DIRECTORY EXISTS
    os.makedirs(ct_folderPath, exist_ok=True)
    # GET TICKET PATH TO SAVE
    ct_ticketNumber, ct_ticketPath = ct_getTicketNaming(ct_folderPath, ct_prefix)
    # UPDATE TICKET NUMBER
    st.session_state.ct_ticketData['TICKET_NUMBER'] = ct_ticketNumber
    # SAVE JSON
    tdict = st.session_state.ct_ticketData
    with open(ct_ticketPath, 'w', encoding='utf-8') as f:
        json.dump(tdict, f, indent=4, ensure_ascii=False)

def ct_listAllJson(ct_folderPath):
    if not os.path.exists(ct_folderPath):
        return []
    with os.scandir(ct_folderPath) as entries:
        filenames = [entry.name for entry in entries if entry.is_file()]
    filenames = [x for x in filenames if x.endswith('.json')]
    return filenames

########################
# HELPER - TICKET TYPE #
########################
@st.dialog('Create New Ticket', width='large', dismissible=False)
def ct_dialogAddInfo():

    with st.form(f"Create Ticket", clear_on_submit=False):
        st.subheader(f"{st.session_state.ct_ticketType} Ticket")
        st.markdown("<br>", unsafe_allow_html=True)   
        # FORM - MATERIAL
        if st.session_state.ct_ticketType == 'Material':
            col1form, col2form = st.columns(2)
            with col1form:
                fill_SAP_NAME = st.text_input("SAP Name *", key="dialog_SAP_NAME")
                fill_COUNTRY = st.selectbox("Country *", options=lsCountry, index=0, key="dialog_COUNTRY")
                fill_TICKET_TYPE = st.text_input("Ticket Type", value="Material", disabled=True, key="dialog_TICKET_TYPE")  
                fill_TICKET_CREATED_BY = st.text_input("Ticket Created By", value=auth_user, disabled=True, key="dialog_TICKET_CREATED_BY")  
                fill_STATUS = st.selectbox("Status", options=lsStatus, index=0, disabled=True, key="dialog_STATUS")
            with col2form:
                fill_REQUESTED_BY = st.text_input("Requested By *", key="dialog_REQUESTED_BY")
                fill_BL_CD = st.selectbox("Business Line (Optional)", options=lsBL, index=0, key="dialog_BL_CD")           
                fill_SERVICE_TYPE = st.selectbox("Service Type *", options=lsServiceType, index=0, key="dialog_SERVICE_TYPE")   
                fill_CALLBACK_DATE = st.date_input("Callback Date (Optional)", key="dialog_CALLBACK_DATE", value=None)
                fill_CALLBACK_TIME = st.time_input("Callback Time (Optional)", key="dialog_CALLBACK_TIME", value=None)
        # FORM - CUSTOMER
        elif st.session_state.ct_ticketType == 'Customer':
            col1form, col2form = st.columns(2)
            with col1form:
                fill_SAP_NAME = st.text_input("SAP Name *", key="dialog_SAP_NAME")
                fill_COUNTRY = st.selectbox("Country *", options=lsCountry, index=0, key="dialog_COUNTRY")
                fill_TICKET_TYPE = st.text_input("Ticket Type", value="Customer", disabled=True, key="dialog_TICKET_TYPE")  
                fill_TICKET_CREATED_BY = st.text_input("Ticket Created By", value=auth_user, disabled=True, key="dialog_TICKET_CREATED_BY")  
                fill_STATUS = st.selectbox("Status", options=lsStatus, index=0, disabled=True, key="dialog_STATUS")
            with col2form:
                fill_REQUESTED_BY = st.text_input("Requested By *", key="dialog_REQUESTED_BY")
                fill_BL_CD = st.selectbox("Business Line (Optional)", options=lsBL, index=0, key="dialog_BL_CD")           
                fill_SERVICE_TYPE = st.selectbox("Service Type *", options=lsServiceType, index=0, key="dialog_SERVICE_TYPE")   
                fill_CALLBACK_DATE = st.date_input("Callback Date (Optional)", key="dialog_CALLBACK_DATE", value=None)
                fill_CALLBACK_TIME = st.time_input("Callback Time (Optional)", key="dialog_CALLBACK_TIME", value=None)
        # FORM - VENDOR
        elif st.session_state.ct_ticketType == 'Vendor':
            col1form, col2form = st.columns(2)
            with col1form:
                fill_SAP_NAME = st.text_input("SAP Name *", key="dialog_SAP_NAME")
                fill_COUNTRY = st.selectbox("Country *", options=lsCountry, index=0, key="dialog_COUNTRY")
                fill_TICKET_TYPE = st.text_input("Ticket Type", value="Vendor", disabled=True, key="dialog_TICKET_TYPE")  
                fill_TICKET_CREATED_BY = st.text_input("Ticket Created By", value=auth_user, disabled=True, key="dialog_TICKET_CREATED_BY")  
                fill_STATUS = st.selectbox("Status", options=lsStatus, index=0, disabled=True, key="dialog_STATUS")
            with col2form:
                fill_REQUESTED_BY = st.text_input("Requested By *", key="dialog_REQUESTED_BY")
                fill_BL_CD = st.selectbox("Business Line (Optional)", options=lsBL, index=0, key="dialog_BL_CD")           
                fill_SERVICE_TYPE = st.selectbox("Service Type *", options=lsServiceType, index=0, key="dialog_SERVICE_TYPE")   
                fill_CALLBACK_DATE = st.date_input("Callback Date (Optional)", key="dialog_CALLBACK_DATE", value=None)
                fill_CALLBACK_TIME = st.time_input("Callback Time (Optional)", key="dialog_CALLBACK_TIME", value=None)

        # BUTTONS
        st.markdown("<br>", unsafe_allow_html=True)   
        but_save_draft = st.form_submit_button("Save Draft") 
        but_request_doc = st.form_submit_button("Request Document")
        but_submit = st.form_submit_button("Submit Ticket")
        st.markdown("<br>", unsafe_allow_html=True)   
        # BUTTON - DRAFT
        if but_save_draft:
            chxerr = 0
            if fill_SAP_NAME == "":
                chxerr += 1
                st.error("Please enter a value for SAP Name. It cannot be empty.")
            if chxerr == 0:
                ct_getTicketData()
                st.session_state.ct_ticketData['STAGE'] = "0 SaveDraft"
                ct_saveJson()     
                st.session_state.ct_showProgressBar = True
                st.session_state.ct_activeDialog = 2   
                st.rerun()           
        # BUTTON - REQUEST DOC
        if but_request_doc:
            chxerr = 0
            if fill_SAP_NAME == "":
                chxerr += 1
                st.error("Please enter a value for SAP Name. It cannot be empty.")
            if fill_REQUESTED_BY == "":
                chxerr += 1
                st.error("Please enter a value for Requested By. It cannot be empty.")
            if fill_COUNTRY == "":
                chxerr += 1
                st.error("Please select a value for Country. It cannot be empty.")
            if chxerr == 0:
                ct_getTicketData()
                st.session_state.ct_ticketData['STAGE'] = "1 RequestingDocuments"
                ct_saveJson()    
                st.session_state.ct_showProgressBar = True
                st.session_state.ct_activeDialog = 2   
                st.rerun()            
        # BUTTON - SUBMIT 
        if but_submit:
            chxerr = 0
            if fill_SAP_NAME == "":
                chxerr += 1
                st.error("Please enter a value for SAP Name. It cannot be empty.")
            if fill_REQUESTED_BY == "":
                chxerr += 1
                st.error("Please enter a value for Requested By. It cannot be empty.")
            if fill_COUNTRY == "":
                chxerr += 1
                st.error("Please select a value for Country. It cannot be empty.")
            if chxerr == 0:
                ct_getTicketData()
                st.session_state.ct_ticketData['STAGE'] = "2 Submitted"
                ct_saveJson()      
                st.session_state.ct_showProgressBar = True
                st.session_state.ct_activeDialog = 2          
                st.rerun()

def loadSingleJson(fullPath):
    """Helper to load a single JSON file safely."""
    try:
        with open(fullPath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None # Handle corrupt files gracefully
    
@st.dialog('Syncing Ticket', dismissible=False)
def ct_dialogConfirm():
    # GET ALL FILES
    lsFullPath = []
    for ttype in ['Material','Customer','Vendor']:
        lsFile = ct_listAllJson(f'ticketHeader/{ttype}/')
        lsFullPathtype = ['ticketHeader/'+ttype+'/'+x for x in lsFile]
        lsFullPath += lsFullPathtype
    # PARSE ALL FILES INTO DF
    if st.session_state.ct_showProgressBar == True:
        stBar = st.progress(0, text="Syncing")

        # WARMUP
        rowList = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all file load tasks immediately
            futures = [executor.submit(loadSingleJson, fullPath) for fullPath in lsFullPath[:100]]            
            # Process them as they finish (as_completed) to update the bar fluidly
            total_files = len(futures)
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                if result:
                    rowList.append(result)                

        # ACTUAL
        rowList = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all file load tasks immediately
            futures = [executor.submit(loadSingleJson, fullPath) for fullPath in lsFullPath]            
            # Process them as they finish (as_completed) to update the bar fluidly
            total_files = len(futures)
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                if result:
                    rowList.append(result)                
                # Update progress bar every 5% or every 10 files to reduce UI redraw overhead
                if i % 10 == 0 or i == total_files - 1:
                    percent_complete = int((i + 1) / total_files * 100)
                    stBar.progress(percent_complete, text=f"Syncing: {percent_complete}%")

        stBar.empty()
        st.session_state.ct_showProgressBar = False
        df = pd.DataFrame(rowList)

        # SAVE
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        df.to_csv(f"ticketIndex/{timestamp}.csv", index=False)

    # GET TICKET NUMBER
    ticket_num = st.session_state.ct_ticketData['TICKET_NUMBER'] 
    ticket_type = st.session_state.ct_ticketData['TICKET_TYPE']
    st.success("Ticket has been successfully created!")
    st.caption('Ticket Type')
    st.code(ticket_type, language=None)
    st.caption("Ticket Number (Click icon to copy)")
    st.code(ticket_num, language=None)

    # ROW 2: GO TO TICKET BUTTON
    st.markdown("<br>", unsafe_allow_html=True) 
    if st.button("Go to Ticket", use_container_width=True):
        # RESET STATE
        st.session_state.ct_showProgressBar = False
        st.session_state.ct_ticketType = 'SelType'
        st.session_state.ct_activeDialog = 0
        st.session_state.ct_ticketData = {}
        # FILL TICKET FOR VIEW
        st.session_state["vt_selTicketType"] = ticket_type
        st.session_state["vt_selTicketNumber"] = ticket_num
        st.session_state["vt_selTicketHeaderPath"] = f"ticketHeader/{ticket_type}/{ticket_num}.json"
        st.session_state["vt_selTicketThreadPath"] = f"ticketThread/{ticket_type}/{ticket_num}.jsonl"
        st.session_state["vt_ticketThread"] = []
        st.session_state["vt_editorKey"] = 0
        st.switch_page("pages/(3) View Ticket.py")
        st.rerun()


#############
# MAIN BODY #
#############

st.title("(2) Create Ticket")
st.markdown("---")

if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:

    # SELTYPE
    if st.session_state.ct_ticketType == 'SelType':
        
        c1, c2, c3 = st.columns(3)
        
        # CARD 1: MATERIAL
        with c1:
            with st.container(border=True):
                st.markdown("## 📦")
                st.subheader("Material")
                st.write("SOME NOTE HERE")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Create Material Ticket", type="secondary", use_container_width=True):
                    st.session_state.ct_ticketType = 'Material'
                    st.session_state.ct_activeDialog = 1
                    st.rerun()

        # CARD 2: CUSTOMER
        with c2:
            with st.container(border=True):
                st.markdown("## 👤")
                st.subheader("Customer")
                st.write("SOME NOTE HERE")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Create Customer Ticket", type="secondary", use_container_width=True):
                    st.session_state.ct_ticketType = 'Customer'
                    st.session_state.ct_activeDialog = 1
                    st.rerun()

        # CARD 3: VENDOR
        with c3:
            with st.container(border=True):
                st.markdown("## 🏢")
                st.subheader("Vendor")
                st.write("SOME NOTE HERE")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Create Vendor Ticket", type="secondary", use_container_width=True):
                    st.session_state.ct_ticketType = 'Vendor'
                    st.session_state.ct_activeDialog = 1
                    st.rerun()

    # DIALOG1
    if st.session_state.ct_activeDialog == 1:
        ct_dialogAddInfo()

    # DIALOG2
    if st.session_state.ct_activeDialog == 2:
        ct_dialogConfirm()

    st.markdown("---")

    # DEBUG
    with st.expander('DEBUG', expanded=False):
        st.json(st.session_state)



