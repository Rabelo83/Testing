import os
import time
import requests

# This matches the variable name you set on Render
API_KEY = os.getenv("FOOTBALL_API_KEY")
# Base URL for API-Sports
BASE_URL = "https://v3.football.api-sports.io/standings"

CACHE = {}
CACHE_TTL = 600  # 10 minutes cache to save your 100 daily requests

# Official IDs for API-Football
LEAGUE_MAPPING = {
    "england": {"id": 39, "name": "Premier League"},
    "spain": {"id": 140, "name": "La Liga"}
}

def get_standings(league_key, season=None):
    if league_key not in LEAGUE_MAPPING:
        raise ValueError(f"League '{league_key}' not supported. Use 'england' or 'spain'.")

    # API-Football requires a 4-digit year (e.g., 2024)
    # If no season is provided, we default to the current year
    if not season:
        season = time.strftime("%Y")
    
    cache_key = f"{league_key}_{season}"
    now = time.time()

    if cache_key in CACHE and now - CACHE[cache_key]["time"] < CACHE_TTL:
        return CACHE[cache_key]["data"]

    league_id = LEAGUE_MAPPING[league_key]["id"]
    
    headers = {
        'x-apisports-key': API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    params = {
        'league': league_id,
        'season': season
    }

    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        # Check if the API returned errors (like invalid key)
        if data.get("errors"):
            raise ValueError(f"API Error: {data['errors']}")

        results = data.get("response", [])
        if not results:
            raise ValueError(f"No standings found for {league_key} in season {season}")

        # Extracting the standings list
        league_data = results[0].get("league", {})
        # The API returns a list of lists for standings
        standings_list = league_data.get("standings", [[]])[0]

        formatted_standings = []
        for row in standings_list:
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
            "country": league_data.get("country"),
            "season": league_data.get("season"),
            "standings": formatted_standings
        }

        CACHE[cache_key] = {"time": now, "data": result}
        return result

    except Exception as e:
        raise Exception(f"Failed to process API-Football data: {str(e)}")
