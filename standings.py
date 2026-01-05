import os
import time
import requests

# This will now raise an error immediately if you forgot to set it in Render
API_KEY = os.getenv("ALLSPORTS_API_KEY")
BASE_URL = "https://apiv2.allsportsapi.com/football"

CACHE = {}
CACHE_TTL = 300 

LEAGUES = {
    "england": {
        "country_id": 44,
        "league_name": "Premier League"
    },
    "spain": {
        "country_id": 6,
        "league_name": "La Liga"
    }
}

def get_league_id(country_id, league_name):
    if not API_KEY:
        raise ValueError("ALLSPORTS_API_KEY environment variable is not set.")

    params = {
        "met": "Leagues",
        "APIkey": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    
    data = response.json()
    
    # Check if API returned an error message instead of results
    if "error" in data:
        raise ValueError(f"API Error: {data.get('message', 'Unknown error')}")

    leagues = data.get("result", [])

    if not leagues:
        raise ValueError("No leagues returned. Check if your API Key is valid and has active permissions.")

    for league in leagues:
        if league.get("league_name", "").strip().lower() == league_name.lower():
            return league.get("league_key")

    available = [l.get("league_name") for l in leagues]
    raise ValueError(f"League '{league_name}' not found in your API plan. Available: {available}")

def get_standings(league_key, season=None):
    if league_key not in LEAGUES:
        raise ValueError(f"Unsupported league: {league_key}")

    season = season or "current"
    cache_key = f"{league_key}_{season}"
    now = time.time()

    if cache_key in CACHE and now - CACHE[cache_key]["time"] < CACHE_TTL:
        return CACHE[cache_key]["data"]

    league = LEAGUES[league_key]
    league_id = get_league_id(league["country_id"], league["league_name"])

    params = {
        "met": "Standings",
        "leagueId": league_id,
        "APIkey": API_KEY
    }

    if season != "current":
        params["season"] = season

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()

    payload = response.json()
    results = payload.get("result", [])

    if not results:
        raise ValueError(f"No standings returned for league ID {league_id}")

    # The API returns standings grouped by stage (e.g. Total, Home, Away)
    # We want the "Total" standings, which is usually the first block
    standings_block = results[0]
    teams = standings_block.get("standings", [])

    standings = []
    for team in teams:
        standings.append({
            "position": int(team.get("overall_league_position", 0)),
            "team": team.get("team_name", "Unknown"),
            "played": int(team.get("overall_league_payed", 0)),
            "wins": int(team.get("overall_league_W", 0)),
            "draws": int(team.get("overall_league_D", 0)),
            "losses": int(team.get("overall_league_L", 0)),
            "points": int(team.get("overall_league_PTS", 0))
        })

    data = {
        "league": league["league_name"],
        "season": season,
        "standings": standings
    }

    CACHE[cache_key] = {"time": now, "data": data}
    return data
