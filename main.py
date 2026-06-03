# Aarav Dhamija 
# Axion AI - Competitive Gaming Coach API

#----------------------------------------------------------------------------------#
# Import Libraries and Initialize FastAPI App
#----------------------------------------------------------------------------------#

import os 
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI() # create FastAPI instance

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#----------------------------------------------------------------------------------#
# Recall files for Gemini client, data models and routes
#----------------------------------------------------------------------------------#

from services.gemini_client import generate_chat_reply
from services.stats_service import analyze_stats
from models.schemas import Stats, ChatMessage, ChatRequest # Data models

from api.chat import router as chat_router
from api.stats import router as stats_router
from api.tracker import router as tracker_router

app.include_router(chat_router)
app.include_router(stats_router)
app.include_router(tracker_router)

