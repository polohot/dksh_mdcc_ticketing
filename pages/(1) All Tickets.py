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

st.set_page_config(page_title="(1) All Tickets", layout="wide")
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
if "vt_selTicketType" not in st.session_state:
    st.session_state["vt_selTicketType"] = None
if "vt_selTicketNumber" not in st.session_state:
    st.session_state["vt_selTicketNumber"] = None
if "vt_selTicketHeaderPath" not in st.session_state:
    st.session_state["vt_selTicketHeaderPath"] = None
if "vt_selTicketThreadPath" not in st.session_state:
    st.session_state["vt_selTicketThreadPath"] = None

# CSS SETTINGS
applyCompactStyle()

##################
# HELPER GENERIC #
##################

def at_listAllCsv(folderPath):
    if not os.path.exists(folderPath):
        return []
    with os.scandir(folderPath) as entries:
        filenames = [entry.name for entry in entries if entry.is_file()]
    filenames = [x for x in filenames if x.endswith('.csv')]
    return filenames


def at_getTicketsDataFrame():
    allCSV = at_listAllCsv('ticketDatabase/ticketIndex/')
    latestCSV = max(allCSV)
    df = pd.read_csv('ticketDatabase/ticketIndex/' + latestCSV)
    df = df.rename(columns={'TICKET_NUMBER':'TicketNumber',
                            'TICKET_CREATE_DTTM':'CreatedOn',
                            'TICKET_CREATED_BY':'CreatedBy',
                            'TICKET_TYPE':'Type',
                            'SAP_CODE':'SAPCode',
                            'SAP_NAME':'SAPName',
                            'REQUEST_INQUIRY_DATE':'RequestInquiryDate',
                            'REQUESTED_BY':'RequestedBy',
                            'COUNTRY':'Country',
                            'BL_CD':'Business Line',
                            'SERVICE_TYPE':'ServiceType',
                            'SUBJECT':'Subject',
                            'CALLBACK_DATE':'CallbackDate',
                            'CALLBACK_TIME':'CallbackTime',
                            'REFERENCE_TICKET_NUMBER':'ReferenceTicketNumber',
                            'REQUEST_MISSING_DOC_DATE':'RequestMissingDocDate',
                            'APPROVING_STATUS':'ApprovingStatus',
                            'APPROVING_DATE':'ApprovingDate',
                            "REJECTION_DATE": "RejectionDate",
                            'SAP_CREATED_DATE':'SAPCreatedDate',
                            'STAGE':'Stage',
                            'STATUS':'Status',
                            'TICKET_CLOSED_BY':'TicketClosedBy',
                            'TICKET_CLOSED_CODE':'TicketClosedCode',
                            'TICKET_CLOSED_NOTE':'TicketClosedNote',
                            'TICKET_CLOSED_DTTM':'TicketClosedDttm',
                            'LAST_MODIFIED_BY':'LastModifiedBy',
                            'LAST_MODIFIED_DTTM':'LastModifiedDttm',                      
                            })
    return df

#############
# MAIN BODY #
#############

titlec1, titlec2 = st.columns([1,2], vertical_alignment="center")
with titlec1:
    st.title("(1) All Tickets")
with titlec2:
    renderNavigationButtons()

if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:
    # LOAD DATA
    df_tickets = at_getTicketsDataFrame()

    if not df_tickets.empty:

        # FILTER SET 1: TICKET TYPES
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            # FILTER SET 1: TICKET TYPES
            st.write("Ticket Types")
            at_filterMaterial = st.checkbox("Material", value=True, key="at_filterMaterial")
            at_filterCustomer = st.checkbox("Customer", value=True, key="at_filterCustomer")
            at_filterVendor = st.checkbox("Vendor", value=True, key="at_filterVendor")
        with c2:
            # FILTER SET 2: CNTY + BL
            lsCountry = ['--ALL--'] + [x for x in df_tickets['Country'].sort_values().unique() if pd.notna(x)] + ['--NONE--']
            at_filterCountry = st.selectbox("Country", options=lsCountry, index=0, key="at_filterCountry")
        with c3:
            # FILTER SET3: STATUS + STAGE
            lsStatus = ['--ALL--'] + [x for x in df_tickets['Status'].sort_values().unique() if pd.notna(x)]
            at_filterStatus = st.selectbox("Status", options=lsStatus, index=0, key="at_filterStatus")
            lsStage = ['--ALL--'] + [x for x in df_tickets['Stage'].sort_values().unique() if pd.notna(x)]
            at_filterStage = st.selectbox("Stage", options=lsStage, index=0, key="at_filterStage")
        with c4:
            # FILTER SET 4: FILTER NAME
            lsCreator = ['--ALL--'] + [x for x in df_tickets['CreatedBy'].sort_values().unique() if pd.notna(x)]
            at_filterCreatedBy = st.selectbox("CreatedBy", options=lsCreator, index=0, key="at_filterCreatedBy")

        # APPLY LOGIC     
        df_display = df_tickets.copy()
        # FILTER SET 1: TICKET TYPES
        at_selectFilterSet1 = []
        if at_filterMaterial: at_selectFilterSet1.append("Material")
        if at_filterCustomer: at_selectFilterSet1.append("Customer")
        if at_filterVendor: at_selectFilterSet1.append("Vendor")
        df_display = df_tickets[df_tickets["Type"].isin(at_selectFilterSet1)]
        # FILTER SET 2: CNTY + BL
        if at_filterCountry == '--ALL--': pass
        elif at_filterCountry == '--NONE--': df_display = df_tickets[df_tickets["Country"].isnull()]
        else: df_display = df_tickets[df_tickets["Country"] == at_filterCountry]
        # FILTER SET3: STATUS + STAGE
        if at_filterStatus == '--ALL--': pass
        elif at_filterStatus == '--NONE--': df_display = df_tickets[df_tickets["Status"].isnull()]
        else: df_display = df_tickets[df_tickets["Status"] == at_filterStatus]
        if at_filterStage == '--ALL--': pass
        elif at_filterStage == '--NONE--': df_display = df_tickets[df_tickets["Stage"].isnull()]
        else: df_display = df_tickets[df_tickets["Stage"] == at_filterStage]
        # FILTER SET 4: FILTER NAME
        if at_filterCreatedBy == '--ALL--': pass   
        else: df_display = df_tickets[df_tickets["CreatedBy"] == at_filterCreatedBy]

        # --- SHOW DATAFRAME ---
        st.markdown("---")
        st.write(f"Showing **{len(df_display)}** tickets:")
        
        event = st.dataframe(
            df_display,
            width="stretch",
            hide_index=True,
            on_select="rerun", 
            selection_mode="single-row",
            #column_order=("TicketNumber", "Type", "Status", "Stage", "CreatedBy", "CreatedOn") 
        )

        st.markdown("<br>", unsafe_allow_html=True)        
        
        if st.button("SEE TICKET", type="primary"):
            if len(event.selection.rows) > 0:
                # GET INDEX OF SELECTED ROW
                selected_index = event.selection.rows[0]
                
                # GET ACTUAL DATA
                selected_ticket = df_display.iloc[selected_index]
                
                # SAVE TO SESSION STATE
                st.session_state["vt_selTicketType"] = selected_ticket["Type"]
                st.session_state["vt_selTicketNumber"] = selected_ticket["TicketNumber"]
                st.session_state["vt_selTicketHeaderPath"] = f"ticketDatabase/ticketHeader/{selected_ticket['TicketNumber']}.jsonl"
                st.session_state["vt_selTicketThreadPath"] = f"ticketDatabase/ticketThread/{selected_ticket['TicketNumber']}.jsonl"
                st.session_state["vt_ticketHeader"] = []
                st.session_state["vt_ticketThread"] = []
                st.session_state["vt_editorKey"] = 0
                # SWITCH PAGE
                st.switch_page("pages/(3) View Ticket.py")
            else:
                st.warning("Please select a ticket from the table above first.")

    else:
        st.warning("No ticket data found in the directories.")
    
    st.markdown("---")

    # DEBUG
    with st.expander('DEBUG', expanded=False):
        st.json(st.session_state)