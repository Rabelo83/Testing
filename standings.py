import os
import requests
import time

API_KEY = os.getenv("ALLSPORTS_API_KEY")

BASE_URL = "https://allsportsapi.com/api/football"

# Simple in-memory cache
CACHE = {}
CACHE_TTL = 300  # 5 minutes

LEAGUES = {
    "england": {
        "league_id": 152,
        "name": "Premier League"
    },
    "spain": {
        "league_id": 302,
        "name": "La Liga"
    }
}

def get_standings(league_key):
    if league_key not in LEAGUES:
        raise ValueError("Unsupported league")

    now = time.time()
    cache_key = f"standings_{league_key}"

    # Return cached data if valid
    if cache_key in CACHE:
        cached = CACHE[cache_key]
        if now - cached["timestamp"] < CACHE_TTL:
            return cached["data"]

    league = LEAGUES[league_key]

    params = {
        "met": "Standings",
        "leagueId": league["league_id"],
        "APIkey": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()

    raw = response.json()

    standings = []

    for team in raw["result"]:
        standings.append({
            "position": team["overall_league_position"],
            "team": team["team_name"],
            "played": team["overall_league_payed"],
            "wins": team["overall_league_W"],
            "draws": team["overall_league_D"],
            "losses": team["overall_league_L"],
            "goals_for": team["overall_league_GF"],
            "goals_against": team["overall_league_GA"],
            "goal_diff": team["overall_league_GF"] - team["overall_league_GA"],
            "points": team["overall_league_PTS"]
        })

    data = {
        "league": league["name"],
        "teams": standings
    }

    CACHE[cache_key] = {
        "timestamp": now,
        "data": data
    }

    return data
