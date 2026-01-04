import os
import time
import requests

API_KEY = os.getenv("ALLSPORTS_API_KEY")
BASE_URL = "https://apiv2.allsportsapi.com/football"

# Cache (league + season)
CACHE = {}
CACHE_TTL = 300  # 5 minutes

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
    params = {
        "met": "Leagues",
        "countryId": country_id,
        "APIkey": API_KEY
    }

    res = requests.get(BASE_URL, params=params, timeout=20)
    res.raise_for_status()

    leagues = res.json()["result"]

    for league in leagues:
        if league_name.lower() in league["league_name"].lower():
            return league["league_key"]

    raise ValueError("League not found")

def get_standings(league_key, season=None):
    if league_key not in LEAGUES:
        raise ValueError("Unsupported league")

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

    res = requests.get(BASE_URL, params=params, timeout=20)
    res.raise_for_status()

    raw = res.json()["result"]

    standings = []
    for team in raw:
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
        "league": league["league_name"],
        "season": season,
        "standings": standings
    }

    CACHE[cache_key] = {"time": now, "data": data}
    return data
