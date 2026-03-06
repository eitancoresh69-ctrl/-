import requests
from datetime import datetime, timedelta
import streamlit as st

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/"
}

TARGET_LEAGUES = [
    'Premier League', 'LaLiga', 'Ligue 1', 'Serie A',
    'Ligat HaAl', 'State Cup', 'Toto Cup',
    'NBA', 'Super League', 'National League'
]

@st.cache_data(ttl=1800)
def fetch_games_for_dates(sport="soccer", days=5):
    """מושך משחקים ומסדר אותם לפי תאריכים"""
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
                            "away": event.get("awayTeam", {}).get("name", "Unknown"),
                        })
        except: pass
    
    # מנקה תאריכים שאין בהם משחקים
    return {k: v for k, v in games_by_date.items() if v}

@st.cache_data(ttl=1800)
def get_game_deep_data(game_id, home_name, away_name):
    """מושך סטטיסטיקות עומק, H2H, פצועים ויחסים"""
    data = {
        "odds": {"1": "N/A", "X": "N/A", "2": "N/A"},
        "h2h": "אין מספיק נתונים היסטוריים.",
        "missing_players": "אין מידע זמין כרגע על חיסורים.",
        "stats": "ממתין לנתוני משחק..."
    }
    
    # משיכת Odds
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/odds/1/all", headers=HEADERS).json()
        choices = res.get("markets", [])[0].get("choices", [])
        data["odds"] = {c["name"]: c.get("fractionalValue") for c in choices}
    except: pass

    # משיכת H2H (מפגשים קודמים)
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/h2h/events", headers=HEADERS).json()
        events = res.get("events", [])[:10]
        if events:
            h_wins = sum(1 for g in events if g.get("winnerCode") == 1)
            a_wins = sum(1 for g in events if g.get("winnerCode") == 2)
            draws = sum(1 for g in events if g.get("winnerCode") == 3)
            data["h2h"] = f"ב-{len(events)} המפגשים האחרונים: {h_wins} נצחונות לבית, {a_wins} לחוץ, {draws} תיקו."
    except: pass

    # משיכת פצועים/מושעים מתוך ההרכבים
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/lineups", headers=HEADERS).json()
        missing = []
        for team in ["home", "away"]:
            for player in res.get(team, {}).get("missingPlayers", []):
                missing.append(f"{player.get('player', {}).get('name')} ({player.get('reason', 'Missing')})")
        if missing:
            data["missing_players"] = " | ".join(missing)
    except: pass

    # סטטיסטיקות כלליות (אם המשחק התחיל או הסתיים)
    try:
        res = requests.get(f"https://api.sofascore.com/api/v1/event/{game_id}/statistics", headers=HEADERS).json()
        stats_list = res.get("statistics", [])[0].get("groups", [])
        extracted_stats = []
        for group in stats_list:
            for item in group.get("statisticsItems", []):
                if item["name"] in ["Corner kicks", "Red cards", "Yellow cards"]:
                    extracted_stats.append(f"{item['name']}: {item['home']} - {item['away']}")
        if extracted_stats:
            data["stats"] = " | ".join(extracted_stats)
    except: pass

    return data
