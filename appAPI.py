from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import glob
import json
import requests
import pandas as pd
import io


# distinct_path prefix is crucial so the docs work at /api/docs
app = FastAPI(root_path="/api") 

##########
# HELPER #
##########

def getLatestCsvFile():
    folderPath = "ticketDatabase/ticketIndex"
    listOfTheFiles = glob.glob(os.path.join(folderPath, "*.csv"))    
    if not listOfTheFiles:
        return None    
    latestFile = max(listOfTheFiles, key=os.path.getctime)
    return latestFile

##########
# METHOD #
##########

@app.get("/")
def readRoot():
    return {"message": "API is running. Go to /api/docs for documentation."}

### TICKET ###

@app.get("/V01/ticketGetLatestCsv")
def ticketGetLatestCsv():
    latestFilePath = getLatestCsvFile()    
    if latestFilePath is None:
        raise HTTPException(status_code=404, detail="No CSV files found")        
    return FileResponse(latestFilePath)

### USER ###

@app.get("/V01/userGetAll")
def userGetAll():
    folderPath = "sysDatabase"
    fileName = "login.jsonl"
    fullPath = os.path.join(folderPath, fileName)
    if not os.path.exists(fullPath):
        return []
    userList = []
    with open(fullPath, "r") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                userList.append(data)    
    return userList

@app.post("/V01/userAdd")
def userAdd(user, password):
    folderPath = "sysDatabase"
    fileName = "login.jsonl"
    fullPath = os.path.join(folderPath, fileName)    
    targetUser = str(user).upper()
    if os.path.exists(fullPath):
        with open(fullPath, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("user") == targetUser:
                            raise HTTPException(status_code=400, detail="User already exists")
                    except json.JSONDecodeError:
                        continue
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    userData = {"password": str(password), "user": targetUser}
    with open(fullPath, "a") as f:
        f.write(json.dumps(userData) + "\n")        
    return {"message": "User added", "user": targetUser}

@app.post("/V01/userDelete")
def userDelete(user):
    folderPath = "sysDatabase"
    fileName = "login.jsonl"
    fullPath = os.path.join(folderPath, fileName)
    if not os.path.exists(fullPath):
         raise HTTPException(status_code=404, detail="Database not found")
    linesToKeep = []
    targetUser = str(user).upper()
    userFound = False
    with open(fullPath, "r") as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    if data.get("user") == targetUser:
                        userFound = True
                    else:
                        linesToKeep.append(line)
                except json.JSONDecodeError:
                    continue
    if not userFound:
         raise HTTPException(status_code=404, detail="User not found")
    with open(fullPath, "w") as f:
        f.writelines(linesToKeep)
    return {"message": "User deleted", "user": targetUser}


### REQUESTED BY ###

@app.post("/V01/requestedByRefreshList")
def requestedByRefreshList():
    folder = "sysDatabase"
    os.makedirs(folder, exist_ok=True)    
    url = "https://dksh.freshservice.com/api/v2/analytics/export?id=d4361d53-ea36-4d28-a6d5-edf786432721"
    r = requests.get(url, auth=("9yYknDv2bBTP0RKVdcV", "*"), verify=False)    
    if r.status_code == 200:
        # Load, unique, sort, and prepend empty string
        df = pd.read_csv(io.StringIO(r.text))
        emails = [""] + sorted(df["Requester Primary Email"].dropna().unique().tolist())        
        # Save directly to JSONL format {"email": "xxx"}
        pd.DataFrame(emails, columns=["email"]).to_json(
            f"{folder}/requestedBy.jsonl", orient="records", lines=True
        )
        return {"status": "success", "count": len(emails)}        
    return {"status": "error", "code": r.status_code}

### COUNTRY ###

@app.get("/V01/countryGetAll")
def countryGetAll():
    folderPath = "sysDatabase"
    fileName = "country.jsonl"
    fullPath = os.path.join(folderPath, fileName)    
    if not os.path.exists(fullPath):
        return []        
    countryList = []
    with open(fullPath, "r") as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    countryList.append(data)
                except json.JSONDecodeError:
                    continue
    return countryList

@app.post("/V01/countryAdd")
def countryAdd(country):
    folderPath = "sysDatabase"
    fileName = "country.jsonl"
    fullPath = os.path.join(folderPath, fileName)    
    targetCountry = str(country).upper()
    if os.path.exists(fullPath):
        with open(fullPath, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("country") == targetCountry:
                            raise HTTPException(status_code=400, detail="Country already exists")
                    except json.JSONDecodeError:
                        continue
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    countryData = {"country": targetCountry}
    with open(fullPath, "a") as f:
        f.write(json.dumps(countryData) + "\n")        
    return {"message": "Country added", "country": targetCountry}

@app.post("/V01/countryDelete")
def countryDelete(country):
    folderPath = "sysDatabase"
    fileName = "country.jsonl"
    fullPath = os.path.join(folderPath, fileName)
    if not os.path.exists(fullPath):
         raise HTTPException(status_code=404, detail="Database not found")
    linesToKeep = []
    targetCountry = str(country).upper()
    countryFound = False
    with open(fullPath, "r") as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    if data.get("country") == targetCountry:
                        countryFound = True
                    else:
                        linesToKeep.append(line)
                except json.JSONDecodeError:
                    continue
    if not countryFound:
         raise HTTPException(status_code=404, detail="Country not found")
    with open(fullPath, "w") as f:
        f.writelines(linesToKeep)
    return {"message": "Country deleted", "country": targetCountry}