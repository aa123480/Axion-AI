from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

# Load HTML at startup
html_content = None

def load_html():
    global html_content
    try:
        # Try multiple possible paths
        paths = [
            os.path.join(os.path.dirname(__file__), '..', 'public', 'index.html'),
            os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html'),
            '/var/task/public/index.html',
            '/var/task/frontend/index.html',
        ]
        
        for path in paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    print(f"Loaded HTML from {path}")
                    return html_content
        
        print("Warning: HTML file not found in any expected location")
    except Exception as e:
        print(f"Error loading HTML: {e}")
    
    return None

@app.on_event("startup")
async def startup_event():
    load_html()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve index.html"""
    if html_content:
        return html_content
    return "<h1>Axion AI - Game Coach</h1><p>Loading...</p>"

@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_file(path: str):
    """Fallback to index.html for SPA routing"""
    # If requesting a path like /api/stats, let it be handled by the API route
    if path.startswith("api/"):
        return {"error": "Not found"}
    
    # Otherwise return index.html for client-side routing
    if html_content:
        return html_content
    return "<h1>Axion AI - Game Coach</h1>"

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
