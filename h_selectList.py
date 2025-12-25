def get_lsCountry():
    lsCountry = ["","TH", "MM", "VN", "KH"]
    return lsCountry

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

def get_lsRequestedBy():
    lsRequestedBy = ['','polohot@gmail.com','aaa@bbb.com','cccc@dddd.com']
    return lsRequestedBy

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
