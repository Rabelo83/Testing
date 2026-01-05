import os
import time
import requests

# Use 'x-apisports-key' for direct signups or 'x-rapidapi-key' for RapidAPI
API_KEY = os.getenv("FOOTBALL_API_KEY") 
BASE_URL = "https://v3.football.api-sports.io/standings"

CACHE = {}
CACHE_TTL = 300 

# Direct IDs for API-Football V3
LEAGUE_MAPPING = {
    "england": {"id": 39, "name": "Premier League"},
    "spain": {"id": 140, "name": "La Liga"}
}

def get_standings(league_key, season=None):
    if league_key not in LEAGUE_MAPPING:
        raise ValueError(f"League '{league_key}' not supported.")

    # API-Football requires a specific year for the season (e.g., 2023)
    # If not provided, we default to the current year
    current_year = time.strftime("%Y")
    season = season or current_year
    
    cache_key = f"{league_key}_{season}"
    now = time.time()

    if cache_key in CACHE and now - CACHE[cache_key]["time"] < CACHE_TTL:
        return CACHE[cache_key]["data"]

    league_id = LEAGUE_MAPPING[league_key]["id"]
    
    headers = {
        'x-apisports-key': API_KEY, # Change to 'x-rapidapi-key' if using RapidAPI
    }
    
    params = {
        'league': league_id,
        'season': season
    }

    response = requests.get(BASE_URL, headers=headers, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    # Check for API-specific errors in the response body
    if data.get("errors"):
        error_msg = str(data["errors"])
        raise ValueError(f"API Error: {error_msg}")

    results = data.get("response", [])
    if not results:
        raise ValueError(f"No standings found for {league_key} in season {season}.")

    # API-Football nests standings inside: response -> league -> standings (list of groups)
    league_data = results[0].get("league", {})
    standings_groups = league_data.get("standings", [])
    
    if not standings_groups:
        raise ValueError("Standings data structure is empty.")

    # We take the first group (Total standings)
    raw_rows = standings_groups[0]
    
    formatted_standings = []
    for row in raw_rows:
        formatted_standings.append({
            "position": row.get("rank"),
            "team": row.get("team", {}).get("name"),
            "played": row.get("all", {}).get("played"),
            "wins": row.get("all", {}).get("win"),
            "draws": row.get("all", {}).get("draw"),
            "losses": row.get("all", {}).get("lose"),
            "points": row.get("points"),
            "goal_diff": row.get("goalsDiff"),
            "form": row.get("form")
        })

    result = {
        "league": league_data.get("name"),
        "season": league_data.get("season"),
        "standings": formatted_standings
    }

    CACHE[cache_key] = {"time": now, "data": result}
    return result
