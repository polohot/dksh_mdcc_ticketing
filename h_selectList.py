import json
import requests
import pandas as pd
import io

def get_lsCountry():
    filePath = "sysDatabase/country.jsonl"
    lsCountry = []
    # Open the file and read it line by line
    with open(filePath, 'r', encoding='utf-8') as file:
        for line in file:
            # Strip whitespace and convert JSON string to dictionary
            data = json.loads(line.strip())
            # Add the country code to our list
            lsCountry.append(data['country'])
    # INSERT BLANK ELEMENT
    if "" not in lsCountry:
        lsCountry.insert(0, "")
    return lsCountry

def get_lsRequestedBy():
    filePath = "sysDatabase/requestedBy.jsonl"
    lsRequestedBy = []
    # Open the file and read it line by line
    with open(filePath, 'r', encoding='utf-8') as file:
        for line in file:
            # Strip whitespace and convert JSON string to dictionary
            data = json.loads(line.strip())
            # Add the email to our list
            lsRequestedBy.append(data['email'])
    # INSERT BLANK ELEMENT
    if "" not in lsRequestedBy:
        lsRequestedBy.insert(0, "")
    return lsRequestedBy

def get_lsBL():
    lsBL = ["", "FBI", "PCI", "PHI", "SCI"]
    return lsBL

def get_lsServiceType(ttype):
    if ttype == 'Material': 
        lsServiceType = ["Creation","Extend","Regulatory Review","Block/UnBlock"]
    elif ttype == 'Customer':
        lsServiceType = ["Creation","CLPA","Extend","Update","Mark/Unmark for Deletion","Block/UnBlock"]
    elif ttype == 'Vendor':
        lsServiceType = ["Creation","Extend","Update","Update Bank Details","Block/UnBlock"]
    else:
        lsServiceType = ["Creation","CLPA","Extend","Update","Update Bank Details","Mark/Unmark for Deletion","Regulatory Review","Block/UnBlock"]
    return lsServiceType

def get_lsStatus():
    lsStatus = ['Open','Completed','Cancelled']
    return lsStatus

def get_lsStage(currStage):
    if currStage == '0 SaveDraft':
        lsStage = ['1 Requesting Documents', '2 Submitted', '99C Cancelled']
    elif currStage == '1 Requesting Documents':
        lsStage = ['2 Submitted', '99C Cancelled']
    elif currStage == '2 Submitted':
        lsStage = ['3A Approved', '3B Rejected', '99C Cancelled']
    elif currStage == '3A Approved':
        lsStage = ['99A Sap Created', '99C Cancelled']
    elif currStage == '3B Rejected':
        lsStage = ['4 Resubmitting', '99C Cancelled']
    elif currStage == '4 Resubmitting':
        lsStage = ['1 Requesting Documents', '99C Cancelled']
    else: # SHOW ALL STAGE
        lsStage = ['0 SaveDraft', '1 Requesting Documents', '2 Submitted', '3A Approved', '3B Rejected', '4 Resubmitting', '99A Sap Created', '99C Cancelled']
    return lsStage

def get_lsClosureCode():
    lsClosureCode = ["","Cancelled","Master Data Management", "Enquiry", "Project Approved", "Rejected", "Project Cancelled", "Optimization/fine-tuning", "Change - Completed"]
    return lsClosureCode


