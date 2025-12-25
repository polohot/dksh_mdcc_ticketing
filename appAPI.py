from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import glob

app = FastAPI()

def getLatestCsvFile():
    # Define the directory path
    folderPath = "ticketDatabase/ticketIndex"    
    # Get list of all csv files
    listOfTheFiles = glob.glob(os.path.join(folderPath, "*.csv"))    
    if not listOfTheFiles:
        return None    
    # Find the latest file based on filename (since your filenames are timestamps, max() works perfectly)
    latestFile = max(listOfTheFiles, key=os.path.getctime)    
    return latestFile

@app.get("/latest-ticket")
def readLatestTicket():
    latestFilePath = getLatestCsvFile()    
    if latestFilePath is None:
        raise HTTPException(status_code=404, detail="No CSV files found")        
    # Returns the file directly so you can download or view it
    return FileResponse(latestFilePath)