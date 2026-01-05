import os
import time
import requests

# Set this to FOOTBALL_DATA_API_KEY in your Render environment variables
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4/competitions"

CACHE = {}
CACHE_TTL = 900  # 15 minutes (Free tier is 10 requests/min, so cache is important)

# Football-Data.org specific league codes
LEAGUE_CODES = {
    "england": "PL",   # Premier League
    "spain": "PD"      # Primera Division (La Liga)
}

def get_standings(league_key, season=None):
    if league_key not in LEAGUE_CODES:
        raise ValueError(f"League '{league_key}' not supported. Use 'england' or 'spain'.")

    # If no season is provided, football-data.org defaults to the current one
    cache_key = f"{league_key}_{season or 'current'}"
    now = time.time()

    if cache_key in CACHE and now - CACHE[cache_key]["time"] < CACHE_TTL:
        return CACHE[cache_key]["data"]

    league_code = LEAGUE_CODES[league_key]
    url = f"{BASE_URL}/{league_code}/standings"
    
    headers = { 'X-Auth-Token': API_KEY }
    params = {}
    if season:
        params['season'] = season

    response = requests.get(url, headers=headers, params=params, timeout=20)
    
    if response.status_code == 403:
        raise Exception("Access Denied: Your API key doesn't have access to this league or season.")
    
    response.raise_for_status()
    data = response.json()

    # Football-Data.org structure: data['standings'] is a list of tables (TOTAL, HOME, AWAY)
    standings_list = data.get("standings", [])
    if not standings_list:
        raise ValueError("No standings data found in the response.")

    # We want the 'TOTAL' table
    total_table = next((s for s in standings_list if s['type'] == 'TOTAL'), standings_list[0])
    rows = total_table.get("table", [])

    formatted_standings = []
    for row in rows:
        formatted_standings.append({
            "position": row.get("position"),
            "team": row.get("team", {}).get("name"),
            "played": row.get("playedGames"),
            "wins": row.get("won"),
            "draws": row.get("draw"),
            "losses": row.get("lost"),
            "points": row.get("points"),
            "goal_diff": row.get("goalDifference"),
            "goals_for": row.get("goalsFor"),
            "goals_against": row.get("goalsAgainst")
        })

    result = {
        "league": data.get("competition", {}).get("name"),
        "season": data.get("filters", {}).get("season"),
        "standings": formatted_standings
    }

    CACHE[cache_key] = {"time": now, "data": result}
    return result
