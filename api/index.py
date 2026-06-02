import os
import requests
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ──────────────────────────────────────────────────────────────────

class Stats(BaseModel):
    kills : int
    deaths: int
    accuracy: float

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured on the server."
        )
    return genai.Client(api_key=api_key)

def normalize_chat_reply(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            cleaned.append(stripped.strip("*"))
            continue
        if stripped.startswith("* "):
            cleaned.append("- " + stripped[2:])
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()

SYSTEM_PROMPT = """
You are Axion AI, an elite competitive gaming coach specializing in Valorant, Fortnite, and CS2.

Valorant knowledge:
- All agents, their abilities, roles (duelist, initiator, controller, sentinel)
- Map callouts, site execution, post-plant positioning
- Economy management, weapon tiers, buy rounds vs save rounds
- Rank-specific mistakes from Iron to Radiant

CS2 knowledge:
- All maps in active duty pool, common smokes, flashes, molotovs
- Economy rounds, force buys, eco rounds
- Spray patterns, movement accuracy, counter-strafing
- Role-specific play: entry fragger, AWPer, support, lurker

Fortnite knowledge:
- Building mechanics, edit courses, box fighting
- Zone strategy, storm pathing, rotations
- Loadout optimization, weapon tiers per season
- Ranked vs pubs strategy differences

When coaching:
- Always ask for rank and skill level if not provided
- Give immediate fixes, medium-term habits, and long-term goals
- Be direct and specific, never vague
- Reference real in-game scenarios
- Do not use markdown, bold markers, or asterisk bullets
- Use plain text with short paragraphs or simple dash bullets only when needed
- Do not mention being an AI unless directly asked
"""

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "chat_configured": bool(os.getenv("GEMINI_API_KEY"))
    }

@app.post("/api/stats")
def analyze_stats(stats: Stats):
    kills = stats.kills
    deaths = stats.deaths if stats.deaths > 0 else 1
    accuracy = stats.accuracy

    if kills < 0 or deaths < 0 or accuracy < 0 or accuracy > 100:
        raise HTTPException(status_code=400, detail="Invalid stats. Kills and deaths must be 0 or above. Accuracy must be between 0 and 100.")

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
        {"role": message.role, "content": message.content.strip()}
        for message in request.messages
        if message.content.strip()
    ]

    if not cleaned_messages:
        raise HTTPException(status_code=400, detail="At least one non-empty message is required.")

    try:
        client = get_gemini_client()
        conversation = "\n\n".join(
            f"{message['role'].title()}: {message['content']}"
            for message in cleaned_messages
        )
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=(
                f"{SYSTEM_PROMPT}\n\n"
                f"{conversation}\n\nAssistant:"
            ),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Chat request failed: {exc}") from exc

    reply = normalize_chat_reply((response.text or "").strip())
    if not reply:
        raise HTTPException(status_code=502, detail="The Gemini response was empty.")

    return {"reply": reply}

# ── Valorant Tracker ─────────────────────────────────────────────────────────

@app.get("/api/tracker/valorant/{username}/{tag}")
async def valorant_account(username: str, tag: str):
    """Get basic account info and current rank."""
    try:
        mmr_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/na/{username}/{tag}"
        headers = {}
        henrik_key = os.getenv("HENRIK_API_KEY")
        if henrik_key:
            headers["Authorization"] = henrik_key

        mmr_response = requests.get(mmr_url, headers=headers, timeout=10)

        if mmr_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Player not found. Check your username and tag.")
        if mmr_response.status_code == 429:
            raise HTTPException(status_code=429, detail="Rate limit hit. Try again in a moment.")
        if not mmr_response.ok:
            raise HTTPException(status_code=502, detail="Could not reach Valorant API.")

        mmr_data = mmr_response.json().get("data", {})

        return {
            "username": username,
            "tag": tag,
            "rank": mmr_data.get("currenttierpatched", "Unranked"),
            "rr": mmr_data.get("ranking_in_tier", 0),
            "elo": mmr_data.get("elo", 0),
            "peak_rank": mmr_data.get("highest_rank", {}).get("patched_tier", "N/A"),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Tracker error: {exc}")

@app.get("/api/tracker/valorant/{username}/{tag}/matches")
async def valorant_matches(username: str, tag: str):
    """Get last 5 matches with K/D, result, and agent."""
    try:
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/na/{username}/{tag}?mode=competitive&size=5"
        headers = {}
        henrik_key = os.getenv("HENRIK_API_KEY")
        if henrik_key:
            headers["Authorization"] = henrik_key

        response = requests.get(url, headers=headers, timeout=10)

        if not response.ok:
            raise HTTPException(status_code=502, detail="Could not fetch match history.")

        matches = response.json().get("data", [])
        results = []

        for match in matches:
            players = match.get("players", {}).get("all_players", [])
            player = next(
                (p for p in players if p["name"].lower() == username.lower() and p["tag"].lower() == tag.lower()),
                None
            )

            if not player:
                continue

            stats = player.get("stats", {})
            teams = match.get("teams", {})
            player_team = player.get("team", "").lower()
            won = teams.get(player_team, {}).get("has_won", False)

            results.append({
                "agent": player.get("character", "Unknown"),
                "kills": stats.get("kills", 0),
                "deaths": stats.get("deaths", 0),
                "assists": stats.get("assists", 0),
                "kd": round(stats.get("kills", 0) / max(stats.get("deaths", 1), 1), 2),
                "score": stats.get("score", 0),
                "headshots": stats.get("headshots", 0),
                "map": match.get("metadata", {}).get("map", "Unknown"),
                "result": "Win" if won else "Loss",
            })

        return {"matches": results}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Match history error: {exc}")
