import json
import os
import streamlit as st
from auth import render_login_sidebar
st.set_page_config(page_title="(2) Create Ticket", layout="wide")
auth_logged_in, auth_user, auth_exp_dt = render_login_sidebar()

# INIT SESSION STATE - AUTH
if "auth_logged_in" not in st.session_state:
    st.session_state.auth_logged_in = auth_logged_in
if "auth_user" not in st.session_state:
    st.session_state.auth_user = auth_user
if "auth_exp_dt" not in st.session_state:
    st.session_state.auth_exp_dt = auth_exp_dt

# INIT SESSION STATE - CUSTOM
if "ct_current_step" not in st.session_state:
    st.session_state.ct_current_step = 'SelType'
if "ct_active_dialog" not in st.session_state:
    st.session_state.ct_active_dialog = False
if "ct_ticket_data" not in st.session_state:
    st.session_state.ct_ticket_data = {}
if "ct_file_path" not in st.session_state:
    st.session_state.ct_file_path = None


# CSS SETTINGS
st.markdown("""
    <style>
        /* Reduce the vertical padding of the dialog modal */
        div[data-testid="stDialog"] div[role="dialog"] {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        
        /* Reduce margin between widgets inside the form */
        div[data-testid="stForm"] .stElementContainer {
            margin-bottom: -15px; /* Pulls widgets closer together vertically */
        }
        
        /* Optional: Make the dialog even wider than 'large' to fit 4 columns */
        div[data-testid="stDialog"] > div > div {
            max-width: 1200px !important; 
        }

        /* Reduce font size of labels slightly to fit better */
        .stMarkdown label {
            font-size: 14px !important;
        }
    </style>
""", unsafe_allow_html=True)

# CONSTANTS
lsCountry = ["","TH", "MM", "VM", "KH"]
lsBL = ["", "FBI", "PCI", "PHI", "SCI"]  
lsServiceType = ["Creation","CLPA","Extend","Update","Update Bank Details","Mark/Unmark for Deletion","Regulatory Review","Block/UnBlock"]
lsStatus = ['Open','Completed','Cancelled']


##################
# HELPER GENERIC #
##################
def ct_reset_session():
    st.session_state.ct_current_step = 'SelType'
    st.session_state.ct_active_dialog = False
    st.rerun()

def ct_getTicketData():
    from datetime import datetime, timezone
    ct_ticket_data = {
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
    return ct_ticket_data

def ct_saveJson():
    from datetime import datetime
    # DETERMINE TICKET TYPE
    ct_ticket_data = st.session_state.ct_ticket_data
    t_type = ct_ticket_data.get('TICKET_TYPE')
    if t_type == "Material":
        folder_path = 'ticketHeader/Material/'
        prefix = "MATE"
    elif t_type == "Customer":
        folder_path = 'ticketHeader/Customer/'
        prefix = "CUST"
    elif t_type == "Vendor":
        folder_path = 'ticketHeader/Vendor/'
        prefix = "VEND"
    else:
        st.error(f"Unknown Ticket Type: {t_type}")
        return
    # ENSURE DIRECTORY EXISTS
    os.makedirs(folder_path, exist_ok=True)
    # GET CURRENT YEAR
    current_year = str(datetime.now().year)
    # GET ALL FILES OF YEAR
    with os.scandir(folder_path) as entries:
        filenames = [entry.name for entry in entries if entry.is_file()]
    filenames = [x for x in filenames if x.endswith('.json')]
    filenames = [x for x in filenames if x.split('---')[1] == current_year]
    # CASE1: FIRST FILE OF THE YEAR
    if len(filenames)==0:
        ct_ticket_number = f"{prefix}---{current_year}---000001"
        ct_file_path = f"{folder_path}{prefix}---{current_year}---000001.json"
    # CASE2: OTHER
    else:
        nnnnnn1 = [x.split('---')[2].split('.')[0] for x in filenames]
        nnnnnn1 = [int(x) for x in nnnnnn1]
        nnnnnn2 = max(nnnnnn1) + 1
        nnnnnn2 = str(nnnnnn2).zfill(6)
        ct_ticket_number = f"{prefix}---{current_year}---{nnnnnn2}"
        ct_file_path = f"{folder_path}{prefix}---{current_year}---{nnnnnn2}.json"
    st.session_state.ct_file_path = ct_file_path
    # UPDATE TICKET NUMBER
    st.session_state.ct_ticket_data['TICKET_NUMBER'] = ct_ticket_number
    ct_ticket_data['TICKET_NUMBER'] = ct_ticket_number
    # SAVE JSON
    with open(ct_file_path, 'w', encoding='utf-8') as f:
            json.dump(ct_ticket_data, f, indent=4, ensure_ascii=False)

########################
# HELPER - TICKET TYPE #
########################
@st.dialog('Create Material Ticket', width='large')
def ct_dialog_material():
    with st.form("Create Material Ticket", clear_on_submit=False):

        # FORM
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

        # BUTTONS
        st.text("---")
        but_save_draft = st.form_submit_button("Save Draft") 
        but_request_doc = st.form_submit_button("Request Document")
        but_submit = st.form_submit_button("Submit Ticket")
        st.text("---")

        # BUTTON - DRAFT
        if but_save_draft:
            chxerr = 0
            if fill_SAP_NAME == "":
                chxerr += 1
                st.error("Please enter a value for SAP Name. It cannot be empty.")
            if chxerr == 0:
                ct_ticket_data = ct_getTicketData()
                ct_ticket_data['STAGE'] = "S0_SAVE_DRAFT"
                st.session_state.ct_ticket_data = ct_ticket_data
                ct_saveJson()                
                ct_reset_session()
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
                ct_ticket_data = ct_getTicketData()
                ct_ticket_data['STAGE'] = "S1_REQUESTING_DOCUMENTS"
                st.session_state.ct_ticket_data = ct_ticket_data
                ct_saveJson()                
                ct_reset_session()

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
                ct_ticket_data = ct_getTicketData()
                ct_ticket_data['STAGE'] = "S2_SUBMITTED"
                st.session_state.ct_ticket_data = ct_ticket_data
                ct_saveJson()                
                ct_reset_session()


#############
# MAIN BODY #
#############

st.title("(2) Create Ticket")
if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:
    st.write(f"Welcome, **{auth_user}**.")

    # SELTYPE
    if st.session_state.ct_current_step == 'SelType':
        if st.button("Material"):
            st.session_state.ct_current_step = 'Material1'
            st.session_state.ct_active_dialog = True
            st.rerun()
        if st.button("Customer"):
            st.session_state.ct_current_step = 'Customer1'
            st.session_state.ct_active_dialog = True
            st.rerun()
        if st.button("Vendor"):
            st.session_state.ct_current_step = 'Vendor1'
            st.session_state.ct_active_dialog = True
            st.rerun()

    # DIALOG
    if st.session_state.ct_active_dialog and st.session_state.ct_current_step == 'Material1':
        ct_dialog_material()
    




    st.json(st.session_state)




