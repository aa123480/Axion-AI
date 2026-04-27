import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel


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


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


def get_openai_client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured on the server."
        )
    return OpenAI()


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "chat_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


@app.post("/api/stats")
def analyze_stats(stats: Stats):
    kills = stats.kills
    deaths = stats.deaths if stats.deaths > 0 else 1
    accuracy = stats.accuracy

    kd_ratio = kills / deaths
    score = (kd_ratio * 10) + (accuracy * 0.5)

    feedback = []

    if kd_ratio < 1:
        feedback.append("Your K/D is below 1. Focus on survival, spacing, and fewer isolated fights.")
    elif kd_ratio < 2:
        feedback.append("Your K/D is stable. Look for cleaner aggression when you have timing or utility advantage.")
    else:
        feedback.append("Your K/D is strong. Keep pressing advantages, but stay disciplined after opening picks.")

    if accuracy < 30:
        feedback.append("Accuracy is low. Prioritize crosshair placement, first-shot discipline, and short aim blocks.")
    elif accuracy < 60:
        feedback.append("Accuracy is serviceable. Consistency should improve with tighter pre-aiming and calmer engagements.")
    else:
        feedback.append("Accuracy is strong. Maintain that level and shift more attention to decision-making.")

    return {
        "kills": kills,
        "deaths": deaths,
        "accuracy": accuracy,
        "kd_ratio": round(kd_ratio, 2),
        "performance_score": round(score, 2),
        "coach_feedback": feedback,
    }


@app.post("/api/chat")
def game_chat(request: ChatRequest):
    cleaned_messages = [
        {
            "role": message.role,
            "content": [{"type": "input_text", "text": message.content.strip()}],
        }
        for message in request.messages
        if message.content.strip()
    ]

    if not cleaned_messages:
        raise HTTPException(status_code=400, detail="At least one non-empty message is required.")

    try:
        client = get_openai_client()
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=(
                "You are Axion AI, a precise and supportive game coach. "
                "Give practical advice for competitive games. Be concise, structured, and specific. "
                "When useful, break advice into immediate fixes, practice focus, and match habits. "
                "Do not mention being an AI unless directly asked."
            ),
            input=cleaned_messages,
            max_output_tokens=360,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Chat request failed: {exc}") from exc

    reply = (response.output_text or "").strip()
    if not reply:
        raise HTTPException(status_code=502, detail="The AI response was empty.")

    return {"reply": reply}
