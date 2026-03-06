import requests
from datetime import datetime, timedelta
import streamlit as st

def get_israel_time(timestamp):
    utc = datetime.utcfromtimestamp(timestamp)
    israel_offset = 3 if (utc.month in [3,4,5,6,7,8,9]) else 2
    return utc + timedelta(hours=israel_offset)

@st.cache_data(ttl=1800)
def fetch_games(days=5):
    games = {}
    today = datetime.now()
    
    for i in range(days):
        date_str = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        games[date_str] = []
        
        try:
            url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}"
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                for event in resp.json().get("events", []):
                    league = event.get("tournament", {}).get("name", "")
                    time = get_israel_time(event.get("startTimestamp", 0))
                    games[date_str].append({
                        "id": event.get("id"),
                        "time": time.strftime("%H:%M"),
                        "home": event.get("homeTeam", {}).get("name", ""),
                        "away": event.get("awayTeam", {}).get("name", ""),
                        "home_id": event.get("homeTeam", {}).get("id"),
                        "away_id": event.get("awayTeam", {}).get("id"),
                        "league": league
                    })
                games[date_str].sort(key=lambda x: x['time'])
        except:
            pass
    
    return {k: v for k, v in games.items() if v}

def get_team_stats(team_id):
    stats = {"form": [], "wins": 0, "draws": 0, "losses": 0}
    
    try:
        url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/0"
        resp = requests.get(url, timeout=8)
        
        if resp.status_code == 200:
            for event in resp.json().get("events", [])[:5]:
                h_score = event.get("homeScore", {}).get("current")
                a_score = event.get("awayScore", {}).get("current")
                
                if h_score is None or a_score is None:
                    continue
                
                is_home = event.get("homeTeam", {}).get("id") == team_id
                
                if h_score == a_score:
                    stats["form"].append(("ת", "#4a6070"))
                    stats["draws"] += 1
                elif (is_home and h_score > a_score) or (not is_home and a_score > h_score):
                    stats["form"].append(("נ", "#00ff88"))
                    stats["wins"] += 1
                else:
                    stats["form"].append(("ה", "#ff3b5c"))
                    stats["losses"] += 1
    except:
        pass
    
    return stats

def get_h2h(game_id):
    h2h = {"matches": [], "summary": {"total": 0, "home_wins": 0, "away_wins": 0, "draws": 0}}
    
    try:
        url = f"https://api.sofascore.com/api/v1/event/{game_id}/h2h/events"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            for event in resp.json().get("events", [])[:10]:
                h_score = event.get("homeScore", {}).get("current")
                a_score = event.get("awayScore", {}).get("current")
                
                if h_score is None or a_score is None:
                    continue
                
                date = get_israel_time(event.get("startTimestamp", 0)).strftime("%d/%m/%Y")
                h2h["matches"].append({
                    "date": date,
                    "home": event.get("homeTeam", {}).get("name", ""),
                    "away": event.get("awayTeam", {}).get("name", ""),
                    "home_score": h_score,
                    "away_score": a_score,
                    "result": "בית" if h_score > a_score else ("חוץ" if a_score > h_score else "תיקו")
                })
                
                h2h["summary"]["total"] += 1
                if h_score > a_score:
                    h2h["summary"]["home_wins"] += 1
                elif a_score > h_score:
                    h2h["summary"]["away_wins"] += 1
                else:
                    h2h["summary"]["draws"] += 1
    except:
        pass
    
    return h2h

def get_odds(game_id):
    odds = {"1": "-", "X": "-", "2": "-"}
    
    try:
        url = f"https://api.sofascore.com/api/v1/event/{game_id}/odds/1/all"
        resp = requests.get(url, timeout=5)
        
        if resp.status_code == 200:
            for market in resp.json().get("markets", []):
                if market.get("marketName") in ["1x2", "Moneyline"]:
                    for choice in market.get("choices", []):
                        odds[choice.get("name")] = choice.get("fractionalValue", "-")
    except:
        pass
    
    return odds

def get_missing_players(game_id):
    missing = {"home": [], "away": []}
    
    try:
        url = f"https://api.sofascore.com/api/v1/event/{game_id}/lineups"
        resp = requests.get(url, timeout=8)
        
        if resp.status_code == 200:
            data = resp.json()
            home_missing = [p.get("player", {}).get("name", "") for p in data.get("home", {}).get("missingPlayers", [])]
            away_missing = [p.get("player", {}).get("name", "") for p in data.get("away", {}).get("missingPlayers", [])]
            
            missing["home"] = home_missing if home_missing else ["סגל מלא"]
            missing["away"] = away_missing if away_missing else ["סגל מלא"]
    except:
        missing["home"] = ["אין נתונים"]
        missing["away"] = ["אין נתונים"]
    
    return missing

def get_game_data(game_id, home_id, away_id):
    return {
        "odds": get_odds(game_id),
        "home_stats": get_team_stats(home_id),
        "away_stats": get_team_stats(away_id),
        "h2h": get_h2h(game_id),
        "missing": get_missing_players(game_id)
    }
