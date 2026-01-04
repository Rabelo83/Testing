import os
import time
import requests

API_KEY = os.getenv("ALLSPORTS_API_KEY")
BASE_URL = "https://apiv2.allsportsapi.com/football"

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

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()

    leagues = response.json().get("result", [])

    for league in leagues:
        if league.get("league_name", "").strip().lower() == league_name.lower():
            return league.get("league_key")

    available = [l.get("league_name") for l in leagues]
    raise ValueError(f"Exact league not found. Available: {available}")


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

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()

    payload = response.json()
    results = payload.get("result", [])

    if not results:
        raise ValueError("No standings returned by API")

    standings_block = results[0]
    teams = standings_block.get("standings", [])

    if not teams:
        raise ValueError("Standings list is empty")

    standings = []

    for team in teams:
        standings.append({
            "position": int(team["overall_league_position"]),
            "team": team["team_name"],
            "played": int(team["overall_league_payed"]),
            "wins": int(team["overall_league_W"]),
            "draws": int(team["overall_league_D"]),
            "losses": int(team["overall_league_L"]),
            "goals_for": int(team["overall_league_GF"]),
            "goals_against": int(team["overall_league_GA"]),
            "goal_diff": int(team["overall_league_GF"]) - int(team["overall_league_GA"]),
            "points": int(team["overall_league_PTS"])
        })

    data = {
        "league": league["league_name"],
        "season": season,
        "standings": standings
    }

    CACHE[cache_key] = {
        "time": now,
        "data": data
    }

    return data
