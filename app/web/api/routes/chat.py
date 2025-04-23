from http.client import HTTPException
import json
from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse

import os
from datetime import datetime

router = APIRouter()

@router.post("/chat")
def chat(message: str) -> List[str]:
    return JSONResponse(content={}) 

