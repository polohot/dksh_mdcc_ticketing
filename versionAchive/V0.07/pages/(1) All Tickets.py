import datetime
import json
import os
import pandas as pd
import concurrent.futures
import streamlit as st
from h_auth import render_login_sidebar
from h_streamlit_custom_editor import custom_editor
from h_css import *

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
    allCSV = at_listAllCsv('ticketIndex/')
    latestCSV = max(allCSV)
    df = pd.read_csv('ticketIndex/' + latestCSV)
    df = df.rename(columns={'TICKET_NUMBER':'TicketNumber',
                            'TICKET_CREATE_DTTM':'CreatedOn',
                            'TICKET_CREATED_BY':'CreatedBy',
                            'TICKET_TYPE':'Type',
                            'SAP_CODE':'SAPCode',
                            'SAP_NAME':'SAPName',
                            'REQUESTED_BY':'RequestedBy',
                            'COUNTRY':'Country',
                            'BL_CD':'BLCD',
                            'SERVICE_TYPE':'ServiceType',
                            'SUBJECT':'Subject',
                            'CALLBACK_DATE':'CallbackDate',
                            'CALLBACK_TIME':'CallbackTime',
                            'REFERENCE_TICKET_NUMBER':'ReferenceTicketNumber',
                            'REQUEST_MISSING_DOC_DATE':'RequestMissingDocDate',
                            'APPROVING_STATUS':'ApprovingStatus',
                            'APPROVING_DATE':'ApprovingDate',
                            'SAP_CREATED_DATE':'SAPCreatedDate',
                            'STAGE':'Stage',
                            'STATUS':'Status',
                            'TICKET_CLOSED_BY':'TicketClosedBy',
                            'TICKET_CLOSED_CODE':'TicketClosedCode',
                            'TICKET_CLOSED_NOTE':'TicketClosedNote',
                            'TICKET_CLOSED_DTTM':'TicketClosedDttm'                            
                            })
    return df

#############
# MAIN BODY #
#############

st.title("(1) All Tickets")
st.markdown("---")

if not auth_logged_in:
    st.info("Please login using the left tab (sidebar).")
else:
    # LOAD DATA
    df_tickets = at_getTicketsDataFrame()

    if not df_tickets.empty:

        # ROW 1: TICKET TYPES
        r1_col1, r1_col2, r1_col3, r1_col4 = st.columns(4)
        with r1_col1:
            st.write("Ticket Types")
        with r1_col2:
            filter_material = st.checkbox("Material", value=True)
        with r1_col3:
            filter_customer = st.checkbox("Customer", value=True)
        with r1_col4:
            filter_vendor = st.checkbox("Vendor", value=True)        
        # ROW 2: FILTER NAME
        r2_col1, r2_col2, r2_col3, r2_col4 = st.columns(4)
        with r2_col1:
            st.write("Filter Name")
        with r2_col2:
            filter_created_by_me = st.checkbox("Created by Me", value=False) 
        
        # APPLY LOGIC     
        df_display = df_tickets.copy()
        # ROW1: TICKET TYPES
        selected_types1 = []
        if filter_material: selected_types1.append("Material")
        if filter_customer: selected_types1.append("Customer")
        if filter_vendor: selected_types1.append("Vendor")
        df_display = df_tickets[df_tickets["Type"].isin(selected_types1)]
        # ROW2: CREATED BY
        if filter_created_by_me: df_display = df_display[df_display["CreatedBy"] == st.session_state.auth_user]

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
                st.session_state["vt_selTicketHeaderPath"] = f"ticketHeader/{selected_ticket['Type']}/{selected_ticket['TicketNumber']}.json"
                st.session_state["vt_selTicketThreadPath"] = f"ticketThread/{selected_ticket['Type']}/{selected_ticket['TicketNumber']}.jsonl"
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