import requests
from datetime import datetime, timedelta
import streamlit as st
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
    "Cache-Control": "no-cache"
}

TARGET_LEAGUES = [
    'UEFA Champions League', 'NBA', 'Super League', 'CBA', 
    'Ligat HaAl', 'LaLiga', 'Copa del Rey', 'Supercopa',
    'Premier League', 'FA Cup', 'EFL Cup', 'Ligue 1',
    'Serie A', 'Bundesliga', 'MLS', 'Euroleague'
]

def get_israel_time(utc_timestamp):
    try:
        utc_time = datetime.utcfromtimestamp(utc_timestamp)
        israel_offset = 3 if (utc_time.month in [3,4,5,6,7,8,9]) and utc_time.day > 20 else 2
        return utc_time + timedelta(hours=israel_offset)
    except:
        return datetime.utcfromtimestamp(utc_timestamp)

@st.cache_data(ttl=1800)
def fetch_games_for_dates(sport="soccer", days=7):
    api_sport = "football" if sport == "כדורגל ⚽" else "basketball"
    today = datetime.now()
    games_by_date = {}

    for i in range(days):
        target_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"https://api.sofascore.com/api/v1/sport/{api_sport}/scheduled-events/{target_date}"
        games_by_date[target_date] = []
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                for event in res.json().get("events", []):
                    league = event.get("tournament", {}).get("name", "")
                    if any(target in league for target in TARGET_LEAGUES):
                        israel_time = get_israel_time(event.get("startTimestamp", 0))
                        games_by_date[target_date].append({
                            "id": event.get("id"),
                            "time": israel_time.strftime("%H:%M"),
                            "datetime": israel_time.strftime("%Y-%m-%d %H:%M"),
                            "date": target_date,
                            "league": league,
                            "home": event.get("homeTeam", {}).get("name", "Unknown"),
                            "home_id": event.get("homeTeam", {}).get("id"),
                            "away": event.get("awayTeam", {}).get("name", "Unknown"),
                            "away_id": event.get("awayTeam", {}).get("id"),
                        })
                games_by_date[target_date].sort(key=lambda x: x['time'])
        except Exception: 
            pass
    
    return {k: v for k, v in games_by_date.items() if v}

def get_team_stats(team_id, include_home_away=False):
    stats = {"form": [], "goals_scored": 0, "goals_conceded": 0, "wins": 0, "draws": 0, "losses": 0, "total_games": 0, "win_rate": 0, "avg_goals_for": 0, "avg_goals_against": 0, "home_form": [], "away_form": []}
    url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/0"
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            events = res.json().get("events", [])[:15]
            for e in events:
                if e.get("status", {}).get("type") != "finished": continue
                h_score, a_score = e.get("homeScore", {}).get("current", 0), e.get("awayScore", {}).get("current", 0)
                is_h = e.get("homeTeam", {}).get("id") == team_id
                
                stats["goals_scored"] += h_score if is_h else a_score
                stats["goals_conceded"] += a_score if is_h else h_score
                stats["total_games"] += 1
                
                if h_score == a_score:
                    stats["form"].append(("ת", "#4a6070")); stats["draws"] += 1
                elif (is_h and h_score > a_score) or (not is_h and a_score > h_score):
                    stats["form"].append(("נ", "#00ff88")); stats["wins"] += 1
                else:
                    stats["form"].append(("ה", "#ff3b5c")); stats["losses"] += 1
            
            if stats["total_games"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["total_games"]) * 100
                stats["avg_goals_for"] = stats["goals_scored"] / stats["total_games"]
                stats["avg_goals_against"] = stats["goals_conceded"] / stats["total_games"]
    except Exception: pass
    return stats

@st.cache_data(ttl=1800)
def get_h2h_data(game_id, home_id, away_id):
    h2h_data = {"matches": [], "head_to_head": {"home_wins": 0, "away_wins": 0, "draws": 0, "total": 0, "home_goals": 0, "away_goals": 0}}
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/h2h/events", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            for e in res.json().get("events", []):
                if e.get("status", {}).get("type") != "finished": continue
                h_score, a_score = e.get("homeScore", {}).get("current"), e.get("awayScore", {}).get("current")
                if h_score is None or a_score is None: continue
                
                h2h_data["matches"].append({
                    "date": get_israel_time(e.get("startTimestamp", 0)).strftime("%d/%m/%Y"),
                    "home": e.get("homeTeam", {}).get("name", ""), "away": e.get("awayTeam", {}).get("name", ""),
                    "home_score": h_score, "away_score": a_score,
                    "result": "ניצחון בית" if h_score > a_score else ("ניצחון חוץ" if a_score > h_score else "תיקו")
                })
                h2h_data["head_to_head"]["total"] += 1
                h2h_data["head_to_head"]["home_goals"] += h_score; h2h_data["head_to_head"]["away_goals"] += a_score
                if h_score > a_score: h2h_data["head_to_head"]["home_wins"] += 1
                elif a_score > h_score: h2h_data["head_to_head"]["away_wins"] += 1
                else: h2h_data["head_to_head"]["draws"] += 1
                
                if len(h2h_data["matches"]) >= 10: break
    except Exception: pass
    return h2h_data

def get_odds_from_the_odds_api(home_team, away_team):
    odds_data = {"1": "לא זמין", "X": "לא זמין", "2": "לא זמין", "over_2_5": "-", "under_2_5": "-"}
    api_key = os.environ.get("ODDS_API_KEY") or st.secrets.get("ODDS_API_KEY", "")
    if not api_key: return odds_data
        
    try:
        url = "https://api.the-odds-api.com/v4/sports/upcoming/odds/"
        params = {"apiKey": api_key, "regions": "eu", "markets": "h2h,totals", "oddsFormat": "decimal"}
        res = requests.get(url, params=params, timeout=5)
        
        if res.status_code == 200:
            for game in res.json():
                # אלגוריתם חכם יותר לחיפוש שמות קבוצות
                api_home = game['home_team'].lower()
                api_away = game['away_team'].lower()
                
                if (home_team[:4].lower() in api_home) or (away_team[:4].lower() in api_away):
                    bookmaker = game['bookmakers'][0] 
                    h2h_market = next((m for m in bookmaker['markets'] if m['key'] == 'h2h'), None)
                    if h2h_market:
                        for outcome in h2h_market['outcomes']:
                            if outcome['name'] == game['home_team']: odds_data["1"] = outcome['price']
                            elif outcome['name'] == game['away_team']: odds_data["2"] = outcome['price']
                            elif outcome['name'] == 'Draw': odds_data["X"] = outcome['price']
                    break
    except: pass
    return odds_data

@st.cache_data(ttl=1800)
def get_game_deep_data(game_id, home_id, away_id, home_team="", away_team=""):
    data = {"odds": {"1": "לא זמין", "X": "לא זמין", "2": "לא זמין", "over_2_5": "-", "under_2_5": "-"},
            "h2h_matches": [], "h2h_summary": {}, "home_stats": {}, "away_stats": {}, "missing_home": [], "missing_away": []}
    
    # הבאת יחסים
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/odds/1/all", headers=HEADERS, timeout=5).json()
        if res.get("markets"):
            for market in res.get("markets", []):
                if market.get("marketName") in ["1x2", "Moneyline"]:
                    for choice in market.get("choices", []): data["odds"][choice.get("name")] = choice.get("fractionalValue", "לא זמין")
    except: pass
    
    # הפעלת הגיבוי רק אם אין נתונים
    if data["odds"]["1"] == "לא זמין":
        fallback = get_odds_from_the_odds_api(home_team, away_team)
        if fallback["1"] != "לא זמין": data["odds"] = fallback

    h2h = get_h2h_data(game_id, home_id, away_id)
    data["h2h_matches"] = h2h["matches"]
    data["h2h_summary"] = h2h["head_to_head"]
    
    data["home_stats"] = get_team_stats(home_id)
    data["away_stats"] = get_team_stats(away_id)
    
    return data
