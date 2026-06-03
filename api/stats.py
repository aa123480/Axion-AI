#----------------------------------------------------------------------------------#
# Import Libraries 
#----------------------------------------------------------------------------------#

from fastapi import APIRouter
from models.schemas import Stats
from services.gemini_client import analyze_stats

router = APIRouter()

@router.post("/stats")
def stats_route(stats: Stats):
    return analyze_stats(stats)