from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import glob

# distinct_path prefix is crucial so the docs work at /api/docs
app = FastAPI(root_path="/api") 

def getLatestCsvFile():
    folderPath = "ticketDatabase/ticketIndex"
    listOfTheFiles = glob.glob(os.path.join(folderPath, "*.csv"))
    
    if not listOfTheFiles:
        return None
    
    latestFile = max(listOfTheFiles, key=os.path.getctime)
    return latestFile

@app.get("/latest-ticket")
def readLatestTicket():
    latestFilePath = getLatestCsvFile()
    
    if latestFilePath is None:
        raise HTTPException(status_code=404, detail="No CSV files found")
        
    return FileResponse(latestFilePath)

@app.get("/")
def readRoot():
    return {"message": "API is running. Go to /api/docs for documentation."}