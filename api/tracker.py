#----------------------------------------------------------------------------------#
# Import Libraries 
#----------------------------------------------------------------------------------#
import os
import requests
from fastapi import APIRouter, HTTPException


router = APIRouter()

#----------------------------------------------------------------------------------#
# Tracker Function
#----------------------------------------------------------------------------------#

@router.get("/tracker/valorant/{username}/{tag}")
def valorant_account(username: str, tag: str):
    try:
        mmr_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/na/{username}/{tag}" 

        headers = {}
        key = os.getenv("HENRIK_API_KEY") # API key for valorant MMR tracking
        
        if key:
            headers["Authorization"] = key

        res = requests.get(mmr_url, headers=headers, timeout=10)

        if not res.ok:
            raise HTTPException(status_code=502, detail="API error")

        data = res.json().get("data", {})

        return {
            "username": username,
            "tag": tag,
            "rank": data.get("currenttierpatched", "Unranked"),
            "rr": data.get("ranking_in_tier", 0),
            "elo": data.get("elo", 0),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))