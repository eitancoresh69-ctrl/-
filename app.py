import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta
import pandas as pd

# הגדרת הדף (חייב להיות הראשון)
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

# משיכת מפתחות אבטחה מ-Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro') 

# הגדרות APIs
TARGET_LEAGUES = [
    'Premier League', 'LaLiga', 'Ligue 1', 'Serie A',
    'Ligat HaAl', 'State Cup', 'Toto Cup',
    'NBA', 'Super League', 'National League'
]

SOFASCORE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/"
}

# --- פונקציות משיכת נתונים (עם Caching לחסכון בבקשות API) ---

@st.cache_data(ttl=1800) # שומר נתונים לחצי שעה
def get_sofascore_odds(game_id):
    """מושך יחסי זכייה ישירות מ-SofaScore"""
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
    except Exception as e:
        print(f"Error fetching odds: {e}")
    return {"1": "חסר", "X": "חסר", "2": "חסר"}

@st.cache_data(ttl=3600) # שומר נתונים לשעה
def fetch_upcoming_games(sport, days=5):
    """מושך משחקים מ-SportAPI7 ומשלב יחסים מ-SofaScore"""
    api_sport = "football" if sport == "כדורגל ⚽" else "basketball"
    games = []
    today = datetime.now()
    
    headers = {
        "x-rapidapi-host": "sportapi7.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }

    # סריקת ימים
    for i in range(days):
        target_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/{api_sport}/scheduled-events/{target_date}"
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                events = res.json().get("events", [])
                
                # סינון לפי ליגות המטרה שלנו
                for event in events:
                    league_name = event.get("tournament", {}).get("name", "")
                    if any(target in league_name for target in TARGET_LEAGUES):
                        game_id = event.get("id")
                        home_team = event.get("homeTeam", {}).get("name", "Unknown")
                        away_team = event.get("awayTeam", {}).get("name", "Unknown")
                        
                        # משיכת Odds מ-SofaScore
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
            st.error(f"שגיאה במשיכת נתונים לתאריך {target_date}: {e}")
            
    return games

@st.cache_data(ttl=3600)
def get_deep_stats(game_id):
    """תשתית למשיכת סטטיסטיקות עומק ו-H2H מ-SofaScore"""
    # כרגע נשאיר מוקאפ חכם, בשלב הבא נחבר גם את זה ל-API הסטטיסטיקות
    return {
        "h2h": "מערכת אוספת נתונים היסטוריים...",
        "missing_players": "ממתין לפרסום סגלים סופיים...",
        "momentum": "מבוסס על 5 משחקים אחרונים."
    }

# --- ממשק המשתמש (Streamlit UI) ---
st.title("⚡ SportIQ ULTRA AI")
st.markdown("מערכת ניתוח ספורט ואיתור Value Bets")

sport_choice = st.radio("בחר ענף ספורט:", ["כדורגל ⚽", "כדורסל 🏀"], horizontal=True)

st.subheader("📅 משחקים קרובים ב-5 הימים הבאים (מבוסס נתוני אמת)")
with st.spinner("מושך נתוני לייב מ-RapidAPI ו-SofaScore... זה עשוי לקחת כמה שניות בפעם הראשונה."):
    games = fetch_upcoming_games(sport_choice)

if not games:
    st.info("לא נמצאו משחקים בליגות המטרה בימים הקרובים, או שהמכסה של ה-API הסתיימה.")
else:
    df = pd.DataFrame(games)
    game_options = {f"{g['date']} | {g['league']} | {g['home']} נגד {g['away']}": g for g in games}
    selected_game_str = st.selectbox("🎯 בחר משחק לניתוח AI מעמיק:", list(game_options.keys()))
    selected_game = game_options[selected_game_str]

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col2:
        st.write("### נתונים חיים (Live)")
        stats = get_deep_stats(selected_game['id'])
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
                    
                    ספק ניתוח קצר בעברית הכולל:
                    1. ניתוח יחסי הכוחות בין שתי הקבוצות הללו בדרך כלל.
                    2. האם היחסים המוצעים משקפים את המציאות ויש בהם ערך (Value).
                    3. המלצה חותכת מנומקת.
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("הניתוח הושלם:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"שגיאת AI. בדוק את מפתח ה-Gemini. שגיאה: {e}")
