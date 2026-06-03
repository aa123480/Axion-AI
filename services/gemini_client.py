#----------------------------------------------------------------------------------#
# Import Libraries 
#----------------------------------------------------------------------------------#

import os 
from google import genai # gemini API
from fastapi import HTTPException

#----------------------------------------------------------------------------------#
# Gemini AI Setup 
#----------------------------------------------------------------------------------#

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



def generate_chat_reply(message):
    cleaned_message = [
        {"role": message.role, "content": message.content.strip()}
        for message in message
        if message.content.strip()
    ]

    if not cleaned_message:
        raise HTTPException(
            status_code=400, 
            detail="At least one non-empty message is required."
        )
    
    try:
        cilent = get_gemini_client()

        coversation = "\n\n".join(
            f"{message['role'].title()}: {message['content']}"
            for message in cleaned_message
        )
    
        response = cilent.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=(
                f"{SYSTEM_PROMPT}\n\n"
                f"{coversation}\n\nAssistant:"
            ),
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502, 
                            detail=f"Chat request failed: {exc}"
        ) from exc

    reply = normalize_chat_reply((response.text or "").strip())
    if not reply:
        raise HTTPException(status_code=502, detail="The Gemini response was empty.")

    return {"reply": reply}