import json
import os

def listAllJsonl(folderPath):
    if not os.path.exists(folderPath):
        return []
    with os.scandir(folderPath) as entries:
        filenames = [entry.name for entry in entries if entry.is_file()]
    filenames = [x for x in filenames if x.endswith('.jsonl')]
    return filenames

def getLastRecordOfJsonl(fullPath):
    try:
        last_line = None
        with open(fullPath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    last_line = line
        if last_line:
            return json.loads(last_line)
        return None 
    except Exception:
        return None    