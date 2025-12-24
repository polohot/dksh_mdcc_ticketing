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