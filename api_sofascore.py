import requests
from datetime import datetime, timedelta
import streamlit as st

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/"
}

TARGET_LEAGUES = [
    'UEFA Champions League', 'NBA', 'Super League', 'CBA', 
    'Ligat HaAl', 'LaLiga', 'Copa del Rey', 'Supercopa',
    'Premier League', 'FA Cup', 'EFL Cup', 'Ligue 1'
]

# מילון המרת עמדות מ-SofaScore לסגנון EA FC
POS_MAP = {
    "G": "GK",
    "D": "CB",
    "M": "CM",
    "F": "ST"
}

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
                        games_by_date[target_date].append({
                            "id": event.get("id"),
                            "time": datetime.fromtimestamp(event.get("startTimestamp", 0)).strftime("%H:%M"),
                            "league": league,
                            "home": event.get("homeTeam", {}).get("name", "Unknown"),
                            "home_id": event.get("homeTeam", {}).get("id"),
                            "away": event.get("awayTeam", {}).get("name", "Unknown"),
                            "away_id": event.get("awayTeam", {}).get("id"),
                        })
        except: pass
    
    return {k: v for k, v in games_by_date.items() if v}

def get_form(team_id, is_home=None):
    url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/0"
    form = []
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
                
                if h_score == a_score:
                    form.append(("ת", "#4a6070"))
                elif (is_h and h_score > a_score) or (not is_h and a_score > h_score):
                    form.append(("נ", "#00ff88"))
                else:
                    form.append(("ה", "#ff3b5c"))
    except: pass
    return form

@st.cache_data(ttl=1800)
def get_game_deep_data(game_id, home_id, away_id):
    data = {
        "odds": {"1": "-", "X": "-", "2": "-"},
        "h2h_matches": [],
        "home_form": get_form(home_id),
        "away_form": get_form(away_id),
        "home_home_form": get_form(home_id, is_home=True),
        "away_away_form": get_form(away_id, is_home=False),
        "missing_home": "סגל מלא",
        "missing_away": "סגל מלא",
        "stats": "המשחק טרם החל או שאין נתונים חיים."
    }
    
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/odds/1/all", headers=HEADERS, timeout=5).json()
        choices = res.get("markets", [])[0].get("choices", [])
        data["odds"] = {c["name"]: c.get("fractionalValue") for c in choices}
    except: pass

    # הוגדל זמן ההמתנה ל-15 שניות כדי לוודא ש-H2H נטען בהצלחה
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/h2h/events", headers=HEADERS, timeout=15).json()
        events = res.get("events", [])[:5]
        for e in events:
            h_team = e.get("homeTeam", {}).get("name", "")
            a_team = e.get("awayTeam", {}).get("name", "")
            h_score = e.get("homeScore", {}).get("current", 0)
            a_score = e.get("awayScore", {}).get("current", 0)
            date_str = datetime.fromtimestamp(e.get("startTimestamp", 0)).strftime("%d/%m/%Y")
            data["h2h_matches"].append(f"📅 {date_str} | {h_team} {h_score} - {a_score} {a_team}")
    except: pass

    # משיכת פצועים עם חלוקה לקבוצות ועמדות FC
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/lineups", headers=HEADERS, timeout=8).json()
        
        home_missing = []
        for p in res.get("home", {}).get("missingPlayers", []):
            pos_code = p.get("player", {}).get("position", "")
            fc_pos = POS_MAP.get(pos_code, pos_code)
            name = p.get("player", {}).get("name", "Unknown")
            home_missing.append(f"{name} ({fc_pos})")
            
        away_missing = []
        for p in res.get("away", {}).get("missingPlayers", []):
            pos_code = p.get("player", {}).get("position", "")
            fc_pos = POS_MAP.get(pos_code, pos_code)
            name = p.get("player", {}).get("name", "Unknown")
            away_missing.append(f"{name} ({fc_pos})")
            
        if home_missing: data["missing_home"] = ", ".join(home_missing)
        if away_missing: data["missing_away"] = ", ".join(away_missing)
    except: pass

    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/statistics", headers=HEADERS, timeout=8)
        if res.status_code == 200:
            stats_list = res.json().get("statistics", [])[0].get("groups", [])
            extracted = []
            for group in stats_list:
                for item in group.get("statisticsItems", []):
                    if item["name"] in ["Corner kicks", "Red cards", "Yellow cards", "Ball possession"]:
                        extracted.append(f"{item['name']}: {item['home']} - {item['away']}")
            if extracted:
                data["stats"] = " | ".join(extracted)
    except: pass

    return data
