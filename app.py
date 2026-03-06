import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta
import pandas as pd

# הגדרת הדף (חייב להיות הראשון)
st.set_page_config(page_title="SportIQ ULTRA", layout="wide")

# הזרקת CSS כדי להפוך את הממשק לימין-לשמאל (RTL) בסגנון שאהבת
st.markdown("""
    <style>
        body, .stApp { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .stMarkdown p { text-align: right; }
        .stSelectbox label { text-align: right; }
        div[data-testid="stSidebar"] { border-left: 1px solid #30363d; background-color: #0d1117;}
    </style>
""", unsafe_allow_html=True)

# --- הגדרת ה-AI (Gemini) ---
# עליך להוציא מפתח API חינמי מ: https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSyAxVxrUdjzVmdyGrTsCe6zkYIuAE1RG0Wc"
genai.configure(api_key=GEMINI_API_KEY)
# שימוש במודל מתקדם של Gemini לטקסט
model = genai.GenerativeModel('gemini-1.5-pro') 

# --- נתוני תשתית ---
TARGET_LEAGUES = [
    'Premier League', 'LaLiga', 'Ligue 1', 'Serie A',
    'Ligat HaAl', 'State Cup', 'Toto Cup',
    'NBA', 'Super League', 'National League'
]

# --- פונקציות דמי (עד שתחבר את ה-API של הספורט שאתה עובד איתו) ---
def fetch_upcoming_games(sport, days=5):
    # כאן תבצע את קריאות ה-GET ל-SofaScore או RapidAPI על פני 5 ימים
    # כרגע נחזיר נתוני דמי לבדיקה
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    
    if sport == "כדורגל ⚽":
        return [
            {"id": "1", "date": dates[0], "league": "Premier League", "home": "ארסנל", "away": "צ'לסי", "odds_h": 2.10, "odds_d": 3.40, "odds_a": 3.50},
            {"id": "2", "date": dates[1], "league": "Ligat HaAl", "home": "מכבי תל אביב", "away": "מכבי חיפה", "odds_h": 2.50, "odds_d": 3.10, "odds_a": 2.80},
        ]
    else:
        return [
            {"id": "3", "date": dates[0], "league": "NBA", "home": "לייקרס", "away": "בוסטון", "odds_h": 1.90, "odds_d": 0, "odds_a": 1.90},
        ]

def get_deep_stats(game_id):
    # כאן תביא נתוני H2H, פצועים, קרנות וכו'
    return {
        "h2h": "ב-5 המפגשים האחרונים: 3 ניצחונות לבית, 1 לחוץ, 1 תיקו.",
        "missing_players": "קבוצת בית: שחקן מפתח א' (פצוע). קבוצת חוץ: סגל מלא.",
        "momentum": "קבוצת הבית במומנטום חיובי עם 4 ניצחונות רצופים."
    }

# --- ממשק המשתמש (Streamlit UI) ---
st.title("⚡ SportIQ ULTRA AI")
st.markdown("מערכת ניתוח ספורט ואיתור Value Bets")

# בחירת ספורט
sport_choice = st.radio("בחר ענף ספורט:", ["כדורגל ⚽", "כדורסל 🏀"], horizontal=True)

# הבאת המשחקים ל-5 הימים הקרובים
st.subheader("📅 משחקים קרובים (5 ימים)")
games = fetch_upcoming_games(sport_choice)

if not games:
    st.info("לא נמצאו משחקים בליגות המטרה בימים הקרובים.")
else:
    # יצירת טבלה יפה של המשחקים
    df = pd.DataFrame(games)
    # בחירת משחק לניתוח מהרשימה
    game_options = {f"{g['date']} | {g['league']} | {g['home']} נגד {g['away']}": g for g in games}
    selected_game_str = st.selectbox("🎯 בחר משחק לניתוח AI מעמיק:", list(game_options.keys()))
    selected_game = game_options[selected_game_str]

    st.divider()

    # --- אזור ניתוח AI ---
    col1, col2 = st.columns([2, 1])

    with col2:
        st.write("### נתונים יבשים")
        stats = get_deep_stats(selected_game['id'])
        st.write(f"**היסטוריית H2H:** {stats['h2h']}")
        st.write(f"**חיסורים בסגל:** {stats['missing_players']}")
        st.write(f"**מומנטום:** {stats['momentum']}")
        
        if sport_choice == "כדורגל ⚽":
            st.write(f"**יחסי זכייה (Odds):** 1({selected_game['odds_h']}) | X({selected_game['odds_d']}) | 2({selected_game['odds_a']})")
        else:
             st.write(f"**יחסי זכייה (Odds):** 1({selected_game['odds_h']}) | 2({selected_game['odds_a']})")

    with col1:
        st.write("### 🧠 ניתוח מנוע AI")
        if st.button("הפעל ניתוח Gemini"):
            with st.spinner("ה-AI מנתח את הנתונים, מחשב הסתברויות ומחפש Value..."):
                try:
                    # בניית הפרומפט שיישלח אלי (Gemini)
                    prompt = f"""
                    אתה מומחה לאנליטיקס של ספורט וחישוב Value Bets. 
                    אנא נתח את המשחק הבא והמלץ האם יש כאן הימור ערך.
                    
                    ספורט: {sport_choice}
                    משחק: {selected_game['home']} נגד {selected_game['away']}
                    ליגה: {selected_game['league']}
                    יחסים: בית ({selected_game['odds_h']}), תיקו ({selected_game.get('odds_d', 'אין')}), חוץ ({selected_game['odds_a']})
                    סטטיסטיקה: {stats['h2h']}, {stats['missing_players']}, {stats['momentum']}
                    
                    ספק ניתוח קצר בעברית הכולל:
                    1. מי הפייבוריטית האמיתית ולמה.
                    2. האם היחסים המוצעים משקפים את המציאות (איפה ה-Value).
                    3. המלצה סופית חותכת (למשל: "הימור על קבוצת בית", "הימנעות", "אובר/אנדר מומלץ").
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("הניתוח הושלם:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"שגיאה בהתחברות ל-API של Gemini. ודא שהכנסת מפתח תקין. פירוט: {e}")
