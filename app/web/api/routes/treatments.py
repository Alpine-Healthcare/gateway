from http.client import HTTPException
import json
from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse

import os
from datetime import datetime

router = APIRouter()

TREATMENTS_FOLDER = "./treatments/"

@router.get("/therapies")
def available_therapies() -> List[str]:
    available_treatments = []
    
    try:
        # List all files in the JSON_FOLDER
        for filename in os.listdir(TREATMENTS_FOLDER):
            if filename.endswith(".json"):
                file_path = os.path.join(TREATMENTS_FOLDER, filename)
                
                # Read the content of each JSON file
                with open(file_path, 'r') as file:
                    json_content = json.load(file)
                    available_treatments.append(json_content)
    except Exception as e:
        print("e: ", e)
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content=available_treatments) 
