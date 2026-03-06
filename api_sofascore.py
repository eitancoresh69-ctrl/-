import requests
from datetime import datetime, timedelta
import streamlit as st
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
    "Cache-Control": "no-cache"
}

TARGET_LEAGUES = [
    'UEFA Champions League', 'NBA', 'Super League', 'CBA', 
    'Ligat HaAl', 'LaLiga', 'Copa del Rey', 'Supercopa',
    'Premier League', 'FA Cup', 'EFL Cup', 'Ligue 1'
]

POS_MAP = {"G": "GK", "D": "CB", "M": "CM", "F": "ST"}

@st.cache_data(ttl=1800)
def fetch_games_for_dates(sport="soccer", days=5):
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
                        # תיקון שעון ישראל (UTC + 2)
                        utc_time = datetime.utcfromtimestamp(event.get("startTimestamp", 0))
                        israel_time = utc_time + timedelta(hours=2)
                        
                        games_by_date[target_date].append({
                            "id": event.get("id"),
                            "time": israel_time.strftime("%H:%M"),
                            "league": league,
                            "home": event.get("homeTeam", {}).get("name", "Unknown"),
                            "home_id": event.get("homeTeam", {}).get("id"),
                            "away": event.get("awayTeam", {}).get("name", "Unknown"),
                            "away_id": event.get("awayTeam", {}).get("id"),
                        })
        except: pass
    
    return {k: v for k, v in games_by_date.items() if v}

def get_form_and_goals(team_id, is_home=None):
    """מושך כושר + מחשב שערי זכות וחובה מ-5 משחקים אחרונים"""
    url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/0"
    form = []
    goals_scored = 0
    goals_conceded = 0
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            events = res.json().get("events", [])
            if is_home is True:
                events = [e for e in events if e.get("homeTeam", {}).get("id") == team_id]
            elif is_home is False:
                events = [e for e in events if e.get("awayTeam", {}).get("id") == team_id]
            
            for e in events[:5]:
                h_score = e.get("homeScore", {}).get("current", 0)
                a_score = e.get("awayScore", {}).get("current", 0)
                is_h = e.get("homeTeam", {}).get("id") == team_id
                
                # חישוב שערים
                goals_scored += h_score if is_h else a_score
                goals_conceded += a_score if is_h else h_score
                
                # חישוב תוצאה
                if h_score == a_score:
                    form.append(("ת", "#4a6070"))
                elif (is_h and h_score > a_score) or (not is_h and a_score > h_score):
                    form.append(("נ", "#00ff88"))
                else:
                    form.append(("ה", "#ff3b5c"))
    except: pass
    return form, goals_scored, goals_conceded

@st.cache_data(ttl=1800)
def get_game_deep_data(game_id, home_id, away_id):
    data = {
        "odds": {"1": "-", "X": "-", "2": "-"},
        "h2h_matches": [],
        "home_form": [], "home_goals": (0,0),
        "away_form": [], "away_goals": (0,0),
        "home_home_form": [],
        "away_away_form": [],
        "missing_home": "סגל מלא או נתונים חסרים",
        "missing_away": "סגל מלא או נתונים חסרים",
        "stats": "המשחק טרם החל או שאין נתונים חיים."
    }
    
    # 1. יחסים
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/odds/1/all", headers=HEADERS, timeout=5).json()
        data["odds"] = {c["name"]: c.get("fractionalValue") for c in res.get("markets", [])[0].get("choices", [])}
    except: pass

    time.sleep(0.5) # השהיה קצרה למניעת חסימה של SofaScore

    # 2. H2H חזק יותר
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/h2h/events", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            events = res.json().get("events", [])[:5]
            for e in events:
                h_team = e.get("homeTeam", {}).get("name", "")
                a_team = e.get("awayTeam", {}).get("name", "")
                h_score = e.get("homeScore", {}).get("current", 0)
                a_score = e.get("awayScore", {}).get("current", 0)
                date_str = datetime.utcfromtimestamp(e.get("startTimestamp", 0)).strftime("%d/%m/%Y")
                data["h2h_matches"].append(f"📅 {date_str} | {h_team} {h_score} - {a_score} {a_team}")
    except: pass

    # 3. כושר ושערים
    data["home_form"], scored_h, conc_h = get_form_and_goals(home_id)
    data["home_goals"] = (scored_h, conc_h)
    
    data["away_form"], scored_a, conc_a = get_form_and_goals(away_id)
    data["away_goals"] = (scored_a, conc_a)
    
    data["home_home_form"], _, _ = get_form_and_goals(home_id, is_home=True)
    data["away_away_form"], _, _ = get_form_and_goals(away_id, is_home=False)

    time.sleep(0.5)

    # 4. פצועים
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/lineups", headers=HEADERS, timeout=8).json()
        
        home_missing = [f"{p.get('player', {}).get('name', '')} ({POS_MAP.get(p.get('player', {}).get('position', ''), '')})" for p in res.get("home", {}).get("missingPlayers", [])]
        away_missing = [f"{p.get('player', {}).get('name', '')} ({POS_MAP.get(p.get('player', {}).get('position', ''), '')})" for p in res.get("away", {}).get("missingPlayers", [])]
            
        if home_missing: data["missing_home"] = ", ".join(home_missing)
        if away_missing: data["missing_away"] = ", ".join(away_missing)
    except: pass

    return data
