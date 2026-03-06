import requests
from datetime import datetime, timedelta
import streamlit as st
import time
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
    "Cache-Control": "no-cache"
}

TARGET_LEAGUES = [
    'UEFA Champions League', 'NBA', 'Super League', 'CBA', 
    'Ligat HaAl', 'LaLiga', 'Copa del Rey', 'Supercopa',
    'Premier League', 'FA Cup', 'EFL Cup', 'Ligue 1',
    'Serie A', 'Bundesliga', 'MLS'
]

POS_MAP = {"G": "GK", "D": "CB", "M": "CM", "F": "ST"}

def get_israel_time(utc_timestamp):
    """המרת UTC לשעון ישראל (UTC+2/+3 בהתאם לשעון קיץ)"""
    try:
        utc_time = datetime.utcfromtimestamp(utc_timestamp)
        # בדוק אם בשעון קיץ בישראל (מרץ-אוקטובר בערך)
        israel_offset = 3 if (utc_time.month in [3,4,5,6,7,8,9]) and utc_time.day > 20 else 2
        israel_time = utc_time + timedelta(hours=israel_offset)
        return israel_time
    except:
        return datetime.utcfromtimestamp(utc_timestamp)

@st.cache_data(ttl=1800)
def fetch_games_for_dates(sport="soccer", days=7):
    """מושך משחקים לימים הקרובים עם פילטור ליגות"""
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
                            "league": league,
                            "home": event.get("homeTeam", {}).get("name", "Unknown"),
                            "home_id": event.get("homeTeam", {}).get("id"),
                            "away": event.get("awayTeam", {}).get("name", "Unknown"),
                            "away_id": event.get("awayTeam", {}).get("id"),
                        })
                games_by_date[target_date].sort(key=lambda x: x['time'])
        except Exception as e: 
            pass
    
    return {k: v for k, v in games_by_date.items() if v}

def get_team_stats(team_id, include_home_away=False):
    """מושך סטטיסטיקות מלאות של קבוצה"""
    stats = {
        "form": [],
        "goals_scored": 0,
        "goals_conceded": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "total_games": 0,
        "win_rate": 0,
        "avg_goals_for": 0,
        "avg_goals_against": 0,
        "home_form": [],
        "away_form": []
    }
    
    url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/0"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            events = res.json().get("events", [])[:15]  # 15 משחקים אחרונים
            
            for e in events:
                h_score = e.get("homeScore", {}).get("current", 0)
                a_score = e.get("awayScore", {}).get("current", 0)
                is_h = e.get("homeTeam", {}).get("id") == team_id
                
                # סטטיסטיקות כללי
                stats["goals_scored"] += h_score if is_h else a_score
                stats["goals_conceded"] += a_score if is_h else h_score
                stats["total_games"] += 1
                
                # תוצאה
                if h_score == a_score:
                    stats["form"].append(("ת", "#4a6070"))
                    stats["draws"] += 1
                elif (is_h and h_score > a_score) or (not is_h and a_score > h_score):
                    stats["form"].append(("נ", "#00ff88"))
                    stats["wins"] += 1
                else:
                    stats["form"].append(("ה", "#ff3b5c"))
                    stats["losses"] += 1
                
                # פרדות בית/חוץ
                if include_home_away:
                    if is_h:
                        if h_score == a_score:
                            stats["home_form"].append(("ת", "#4a6070"))
                        elif h_score > a_score:
                            stats["home_form"].append(("נ", "#00ff88"))
                        else:
                            stats["home_form"].append(("ה", "#ff3b5c"))
                    else:
                        if h_score == a_score:
                            stats["away_form"].append(("ת", "#4a6070"))
                        elif a_score > h_score:
                            stats["away_form"].append(("נ", "#00ff88"))
                        else:
                            stats["away_form"].append(("ה", "#ff3b5c"))
            
            # חישובים
            if stats["total_games"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["total_games"]) * 100
                stats["avg_goals_for"] = stats["goals_scored"] / stats["total_games"]
                stats["avg_goals_against"] = stats["goals_conceded"] / stats["total_games"]
    
    except Exception as e:
        pass
    
    return stats

@st.cache_data(ttl=1800)
def get_h2h_data(game_id, home_id, away_id):
    """מושך H2H נתונים מלאים"""
    h2h_data = {
        "matches": [],
        "head_to_head": {
            "home_wins": 0,
            "away_wins": 0,
            "draws": 0,
            "total": 0,
            "home_goals": 0,
            "away_goals": 0
        }
    }
    
    try:
        # H2H אירועים
        res = requests.get(
            f"https://api.sofascore.com/api/v1/event/{game_id}/h2h/events", 
            headers=HEADERS, 
            timeout=10
        )
        
        if res.status_code == 200:
            events = res.json().get("events", [])[:10]  # 10 משחקים אחרונים
            
            for e in events:
                h_team = e.get("homeTeam", {}).get("name", "")
                a_team = e.get("awayTeam", {}).get("name", "")
                h_score = e.get("homeScore", {}).get("current", 0)
                a_score = e.get("awayScore", {}).get("current", 0)
                date_str = get_israel_time(e.get("startTimestamp", 0)).strftime("%d/%m/%Y")
                
                h2h_data["matches"].append({
                    "date": date_str,
                    "home": h_team,
                    "away": a_team,
                    "home_score": h_score,
                    "away_score": a_score,
                    "result": "ניצחון בית" if h_score > a_score else ("ניצחון חוץ" if a_score > h_score else "תיקו")
                })
                
                # עדכון סטטיסטיקה H2H
                h2h_data["head_to_head"]["total"] += 1
                h2h_data["head_to_head"]["home_goals"] += h_score
                h2h_data["head_to_head"]["away_goals"] += a_score
                
                if h_score > a_score:
                    h2h_data["head_to_head"]["home_wins"] += 1
                elif a_score > h_score:
                    h2h_data["head_to_head"]["away_wins"] += 1
                else:
                    h2h_data["head_to_head"]["draws"] += 1
    
    except Exception as e:
        pass
    
    return h2h_data

@st.cache_data(ttl=1800)
def get_odds_from_multiple_sources(game_id):
    """מושך יחסים מכמה מקורות (סופא סקור עיקרי)"""
    odds_data = {
        "1": "-",
        "X": "-", 
        "2": "-",
        "over_2_5": "-",
        "under_2_5": "-"
    }
    
    try:
        res = requests.get(
            f"https://api.sofascore.com/api/v1/event/{game_id}/odds/1/all",
            headers=HEADERS,
            timeout=5
        ).json()
        
        if res.get("markets"):
            for market in res.get("markets", []):
                if market.get("marketName") in ["1x2", "Moneyline"]:
                    for choice in market.get("choices", []):
                        odds_data[choice.get("name")] = choice.get("fractionalValue", "-")
                elif "Over/Under" in market.get("marketName", ""):
                    for choice in market.get("choices", []):
                        if "2.5" in str(choice.get("name", "")):
                            if "Over" in str(choice.get("name", "")):
                                odds_data["over_2_5"] = choice.get("fractionalValue", "-")
                            else:
                                odds_data["under_2_5"] = choice.get("fractionalValue", "-")
    except:
        pass
    
    return odds_data

def get_team_standings(team_id, league_name):
    """מושך עמדה בטבלה"""
    standings = {
        "position": "-",
        "points": 0,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "gf": 0,
        "ga": 0
    }
    
    try:
        # ספסריום: צריך למצוא את Tournament ID תחילה
        pass  # צריך מיזום נוסף
    except:
        pass
    
    return standings

def get_missing_players(game_id):
    """מושך שחקנים חסרים"""
    missing = {
        "home": [],
        "away": []
    }
    
    try:
        res = requests.get(
            f"https://api.sofascore.com/api/v1/event/{game_id}/lineups",
            headers=HEADERS,
            timeout=8
        ).json()
        
        home_missing = [
            f"{p.get('player', {}).get('name', '')} ({POS_MAP.get(p.get('player', {}).get('position', ''), 'N/A')})"
            for p in res.get("home", {}).get("missingPlayers", [])
        ]
        away_missing = [
            f"{p.get('player', {}).get('name', '')} ({POS_MAP.get(p.get('player', {}).get('position', ''), 'N/A')})"
            for p in res.get("away", {}).get("missingPlayers", [])
        ]
        
        missing["home"] = home_missing if home_missing else ["סגל מלא"]
        missing["away"] = away_missing if away_missing else ["סגל מלא"]
    except:
        missing["home"] = ["נתונים לא זמינים"]
        missing["away"] = ["נתונים לא זמינים"]
    
    return missing

@st.cache_data(ttl=1800)
def get_game_deep_data(game_id, home_id, away_id):
    """מושך כל הנתונים העמוקים למשחק - גרסה משופרת"""
    data = {
        "odds": {"1": "-", "X": "-", "2": "-", "over_2_5": "-", "under_2_5": "-"},
        "h2h_matches": [],
        "h2h_summary": {},
        "home_stats": {},
        "away_stats": {},
        "missing_home": ["נתונים לא זמינים"],
        "missing_away": ["נתונים לא זמינים"],
        "team_standings": {
            "home": {},
            "away": {}
        }
    }
    
    # 1. יחסים
    data["odds"] = get_odds_from_multiple_sources(game_id)
    time.sleep(0.3)
    
    # 2. H2H מלא
    h2h = get_h2h_data(game_id, home_id, away_id)
    data["h2h_matches"] = h2h["matches"]
    data["h2h_summary"] = h2h["head_to_head"]
    time.sleep(0.3)
    
    # 3. סטטיסטיקות קבוצות
    data["home_stats"] = get_team_stats(home_id, include_home_away=True)
    data["away_stats"] = get_team_stats(away_id, include_home_away=True)
    time.sleep(0.3)
    
    # 4. שחקנים חסרים
    missing = get_missing_players(game_id)
    data["missing_home"] = missing["home"]
    data["missing_away"] = missing["away"]
    
    return data
