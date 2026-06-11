#----------------------------------------------------------------------------------#
# Import Libraries 
#----------------------------------------------------------------------------------#

import os
import requests
from fastapi import APIRouter, HTTPException

router = APIRouter()

HENRIK_BASE_URL = "https://api.henrikdev.xyz/valorant"


def henrik_headers():
    key = os.getenv("HENRIK_API_KEY") or os.getenv("HENRIKDEV_API_KEY")
    headers = {"Accept": "application/json"}

    if key:
        headers["Authorization"] = key.strip().strip("\"'")

    return headers


def henrik_get(url: str, params=None):
    try:
        res = requests.get(url, headers=henrik_headers(), params=params, timeout=10)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Henrik API: {exc}")

    if res.ok:
        return res.json()

    detail = "Henrik API error"
    try:
        body = res.json()
        detail = body.get("message") or body.get("error") or body.get("detail") or detail
    except ValueError:
        if res.text:
            detail = res.text[:200]

    if res.status_code in {401, 403}:
        detail = (
            f"{detail}. Check that HENRIK_API_KEY is set to your Henrik API key "
            "without extra spaces or quotes."
        )

    raise HTTPException(status_code=res.status_code, detail=detail)

#----------------------------------------------------------------------------------#
# Tracker Functions
#----------------------------------------------------------------------------------#

@router.get("/tracker/valorant/{username}/{tag}") 
def valorant_account(username: str, tag: str): # Get Valorant account details using Henrik API
    mmr_url = f"{HENRIK_BASE_URL}/v2/mmr/na/{username}/{tag}"
    payload = henrik_get(mmr_url)
    data = payload.get("data", {})
    peak_rank = data.get("highest_rank", {})

    return {
        "username": username,
        "tag": tag,
        "rank": data.get("currenttierpatched", "Unranked"),
        "rr": data.get("ranking_in_tier", 0),
        "elo": data.get("elo", 0),
        "peak_rank": peak_rank.get("patched_tier") or peak_rank.get("tier") or "N/A",
    }

@router.get("/tracker/valorant/{username}/{tag}/matches")
def valorant_matches(username: str, tag: str): # Get recent Valorant matches using Henrik API
    matches_url = f"{HENRIK_BASE_URL}/v3/matches/na/{username}/{tag}"
    payload = henrik_get(matches_url, params={"filter": "competitive", "size": 5})
    matches = payload.get("data", [])

    return {
        "matches": [format_match(match, username, tag) for match in matches],
    }


def format_match(match, username, tag): # Extract and format relevant match details for the specified player
    metadata = match.get("metadata", {})
    all_players = match.get("players", {}).get("all_players", [])
    player = find_player(all_players, username, tag)
    stats = player.get("stats", {})
    teams = match.get("teams", {})
    player_team = player.get("team", "")
    team_data = teams.get(player_team.lower(), {})

    kills = stats.get("kills", 0)
    deaths = stats.get("deaths", 0)
    assists = stats.get("assists", 0)
    headshots = stats.get("headshots", 0)
    kd = round(kills / max(deaths, 1), 2)

    return {
        "agent": player.get("character", "Unknown"),
        "map": metadata.get("map", "Unknown map"),
        "result": "Win" if team_data.get("has_won") else "Loss",
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kd": kd,
        "headshots": headshots,
    }


def find_player(players, username, tag): # Find the player in the match data that matches the given username and tag, or return the first player if not found
    for player in players:
        if (
            player.get("name", "").lower() == username.lower()
            and player.get("tag", "").lower() == tag.lower()
        ):
            return player

    return players[0] if players else {}
