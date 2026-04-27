from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Stats(BaseModel):
    kills: int
    deaths: int
    accuracy: float

# Path to public folder
public_path = os.path.join(os.path.dirname(__file__), '..', 'public')

@app.get("/")
async def root():
    """Serve index.html"""
    index_path = os.path.join(public_path, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return {"message": "AI Game Coach is running"}

@app.get("/{path:path}")
async def serve_file(path: str):
    """Serve any file as fallback, otherwise return index.html"""
    file_path = os.path.join(public_path, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA routing
    index_path = os.path.join(public_path, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    
    return {"error": "Not found"}

@app.post("/api/stats")
def analyze_stats(stats: Stats):
    kills = stats.kills
    deaths = stats.deaths if stats.deaths > 0 else 1
    accuracy = stats.accuracy

    kd_ratio = kills / deaths
    score = (kd_ratio * 10) + (accuracy * 0.5)

    feedback = []

    if kd_ratio < 1:
        feedback.append("Your K/D is below 1 — focus on survival and positioning.")
    elif kd_ratio < 2:
        feedback.append("Decent K/D — try to play more aggressively.")
    else:
        feedback.append("Strong K/D — you're winning fights consistently.")

    if accuracy < 30:
        feedback.append("Low accuracy — practice aim training.")
    elif accuracy < 60:
        feedback.append("Average accuracy — keep improving consistency.")
    else:
        feedback.append("Good accuracy — solid aim.")

    return {
        "kills": kills,
        "deaths": deaths,
        "accuracy": accuracy,
        "kd_ratio": round(kd_ratio, 2),
        "performance_score": round(score, 2),
        "coach_feedback": feedback
    }
