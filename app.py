import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta
import pandas as pd

# הגדרת הדף
st.set_page_config(page_title="SportIQ ULTRA", layout="wide")

# הזרקת CSS לימין-לשמאל
st.markdown("""
    <style>
        body, .stApp { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .stMarkdown p { text-align: right; }
        .stSelectbox label { text-align: right; }
        div[data-testid="stSidebar"] { border-left: 1px solid #30363d; background-color: #0d1117;}
    </style>
""", unsafe_allow_html=True)

# משיכת מפתח אבטחה של AI (אין צורך יותר ב-RapidAPI!)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro') 

# הגדרות ליגות למעקב
TARGET_LEAGUES = [
    'Premier League', 'LaLiga', 'Ligue 1', 'Serie A',
    'Ligat HaAl', 'State Cup', 'Toto Cup',
    'NBA', 'Super League', 'National League'
]

# כותרות התחזות לדפדפן כדי ש-SofaScore לא יחסמו אותנו
SOFASCORE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/"
}

# --- פונקציות משיכת נתונים ישירות מ-SofaScore ---

@st.cache_data(ttl=1800) # שומר בזיכרון לחצי שעה כדי לא להיחסם
def get_sofascore_odds(game_id):
    """מושך יחסי זכייה מ-SofaScore"""
    url = f"https://api.sofascore.com/api/v1/event/{game_id}/odds/1/all"
    try:
        res = requests.get(url, headers=SOFASCORE_HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            markets = data.get("markets", [])
            if markets:
                choices = markets[0].get("choices", [])
                odds = {}
                for choice in choices:
                    odds[choice["name"]] = choice.get("fractionalValue", choice.get("initialFractionalValue", "N/A"))
                return odds
    except:
        pass
    return {"1": "חסר", "X": "חסר", "2": "חסר"}

@st.cache_data(ttl=3600) # שומר לשעה
def fetch_upcoming_games(sport, days=5):
    """מושך משחקים מהדלת האחורית של SofaScore"""
    api_sport = "football" if sport == "כדורגל ⚽" else "basketball"
    games = []
    today = datetime.now()
    
    for i in range(days):
        target_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"https://api.sofascore.com/api/v1/sport/{api_sport}/scheduled-events/{target_date}"
        
        try:
            res = requests.get(url, headers=SOFASCORE_HEADERS, timeout=10)
            if res.status_code == 200:
                events = res.json().get("events", [])
                
                for event in events:
                    league_name = event.get("tournament", {}).get("name", "")
                    if any(target in league_name for target in TARGET_LEAGUES):
                        game_id = event.get("id")
                        home_team = event.get("homeTeam", {}).get("name", "Unknown")
                        away_team = event.get("awayTeam", {}).get("name", "Unknown")
                        
                        odds = get_sofascore_odds(game_id)
                        
                        games.append({
                            "id": game_id,
                            "date": target_date,
                            "league": league_name,
                            "home": home_team,
                            "away": away_team,
                            "odds_h": odds.get("1", "חסר"),
                            "odds_d": odds.get("X", "חסר"),
                            "odds_a": odds.get("2", "חסר")
                        })
        except Exception as e:
            print(f"Error on {target_date}: {e}")
            
    return games

@st.cache_data(ttl=3600)
def get_deep_stats(game_id, home_team, away_team):
    """מושך נתוני H2H (ראש בראש) היסטוריים מ-SofaScore"""
    url = f"https://api.sofascore.com/api/v1/event/{game_id}/h2h/events"
    h2h_summary = "אין מספיק נתונים היסטוריים."
    
    try:
        res = requests.get(url, headers=SOFASCORE_HEADERS, timeout=5)
        if res.status_code == 200:
            events = res.json().get("events", [])
            if events:
                home_wins = 0
                away_wins = 0
                draws = 0
                
                # מנתח את 10 המפגשים האחרונים ביניהן
                for past_game in events[:10]:
                    winner_code = past_game.get("winnerCode")
                    # SofaScore winnerCode: 1 = הבית של המשחק ההוא ניצח, 2 = החוץ, 3 = תיקו
                    # כדי לא להסתבך עם מי אירח אז, נסתכל על תוצאת הסיום
                    home_score = past_game.get("homeScore", {}).get("current", 0)
                    away_score = past_game.get("awayScore", {}).get("current", 0)
                    past_home_name = past_game.get("homeTeam", {}).get("name", "")
                    
                    if home_score == away_score:
                        draws += 1
                    elif (home_score > away_score and past_home_name == home_team) or \
                         (away_score > home_score and past_home_name != home_team):
                        home_wins += 1
                    else:
                        away_wins += 1
                        
                h2h_summary = f"ב-{len(events[:10])} המפגשים האחרונים: {home_wins} ניצחונות ל{home_team}, {away_wins} ל{away_team}, ו-{draws} תוצאות תיקו."
    except Exception as e:
        print(f"Error fetching H2H: {e}")

    return {
        "h2h": h2h_summary,
        "missing_players": "נתוני פצועים דורשים סריקה מורכבת מ-Rotowire/SofaScore (יצורף בעתיד)",
    }

# --- ממשק המשתמש (Streamlit UI) ---
st.title("⚡ SportIQ ULTRA AI")
st.markdown("מערכת ניתוח ספורט ואיתור Value Bets")

sport_choice = st.radio("בחר ענף ספורט:", ["כדורגל ⚽", "כדורסל 🏀"], horizontal=True)

st.subheader("📅 משחקים קרובים ב-5 הימים הבאים (ישירות מ-SofaScore)")
with st.spinner("מושך נתוני לייב... (מתחזה לדפדפן כדי לא להיחסם)"):
    games = fetch_upcoming_games(sport_choice)

if not games:
    st.info("לא נמצאו משחקים בליגות המטרה בימים הקרובים.")
else:
    df = pd.DataFrame(games)
    game_options = {f"{g['date']} | {g['league']} | {g['home']} נגד {g['away']}": g for g in games}
    selected_game_str = st.selectbox("🎯 בחר משחק לניתוח AI מעמיק:", list(game_options.keys()))
    selected_game = game_options[selected_game_str]

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col2:
        st.write("### נתונים חיים (Live)")
        stats = get_deep_stats(selected_game['id'], selected_game['home'], selected_game['away'])
        st.write(f"**היסטוריית H2H:** {stats['h2h']}")
        st.write(f"**חיסורים בסגל:** {stats['missing_players']}")
        
        if sport_choice == "כדורגל ⚽":
            st.write(f"**יחסי SofaScore:** 1({selected_game['odds_h']}) | X({selected_game['odds_d']}) | 2({selected_game['odds_a']})")
        else:
             st.write(f"**יחסי SofaScore:** 1({selected_game['odds_h']}) | 2({selected_game['odds_a']})")

    with col1:
        st.write("### 🧠 ניתוח מנוע AI")
        if st.button("הפעל ניתוח Gemini"):
            with st.spinner("ה-AI מנתח את הנתונים ומחפש Value..."):
                try:
                    prompt = f"""
                    אתה מומחה לאנליטיקס של ספורט וחישוב Value Bets. 
                    אנא נתח את המשחק הבא והמלץ האם יש כאן הימור ערך.
                    
                    ספורט: {sport_choice}
                    משחק: {selected_game['home']} נגד {selected_game['away']}
                    ליגה: {selected_game['league']}
                    יחסים: בית ({selected_game['odds_h']}), תיקו ({selected_game.get('odds_d', 'אין')}), חוץ ({selected_game['odds_a']})
                    סטטיסטיקה: {stats['h2h']}
                    
                    ספק ניתוח קצר בעברית הכולל:
                    1. ניתוח יחסי הכוחות לאור נתוני ה-H2H.
                    2. האם היחסים המוצעים משקפים את המציאות ויש בהם ערך (Value).
                    3. המלצה חותכת מנומקת.
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("הניתוח הושלם:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"שגיאת AI. בדוק את מפתח ה-Gemini. שגיאה: {e}")
