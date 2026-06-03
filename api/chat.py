#----------------------------------------------------------------------------------#
# Import Libraries 
#----------------------------------------------------------------------------------#

from fastapi import APIRouter
from models.schemas import ChatRequest
from services.gemini_client import generate_chat_reply

router = APIRouter()

@router.post("/chat")
def game_chat(request: ChatRequest):
    return {
        "reply": generate_chat_reply(request.messages)
    }



