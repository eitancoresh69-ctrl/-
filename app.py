import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator

# חובה להיות השורה הראשונה
st.set_page_config(page_title="SportIQ ULTRA", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------
# הזרקת עיצוב (CSS) חזק שדורס את סטרימליט
# -----------------------------------------
st.markdown("""
    <style>
        /* איפוס מלא וימין-לשמאל */
        .stApp, .stAppHeader, [data-testid="stSidebar"] {
            direction: rtl !important;
            font-family: 'Heebo', 'Segoe UI', sans-serif !important;
        }
        
        /* צבעי רקע וטקסט כלליים */
        .stApp { background-color: #02040a !important; }
        [data-testid="stSidebar"] {
            background-color: #0c1220 !important;
            border-left: 1px solid rgba(0,240,255,0.08) !important;
        }
        
        /* הכרחת טקסטים להיות בהירים ומיושרים לימין */
        p, div, span, label, h1, h2, h3, h4, h5, h6, li {
            text-align: right !important;
            direction: rtl !important;
            color: #e8f4f8 !important;
        }
        
        /* כותרות ספציפיות */
        h1, h2 { color: #ffffff !important; font-weight: bold !important; }
        
        /* סידור רשימת המשחקים בסרגל הצד (Radio Buttons) */
        .stRadio > div { flex-direction: column !important; gap: 12px !important; }
        .stRadio label {
            background: rgba(255,255,255,0.02) !important;
            padding: 10px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
        }
        .stRadio label:hover { background: rgba(0,240,255,0.05) !important; border-color: rgba(0,240,255,0.3) !important; }
        
        /* עיצוב כפתור ה-AI */
        .stButton > button {
            background: linear-gradient(135deg, rgba(0,240,255,0.1), rgba(0,255,136,0.1)) !important;
            border: 1px solid rgba(0,240,255,0.3) !important;
            color: #00f0ff !important;
            border-radius: 8px !important;
            width: 100% !important;
            padding: 10px !important;
            font-weight: bold !important;
        }
        .stButton > button:hover {
            border-color: #00f0ff !important;
            box-shadow: 0 0 15px rgba(0,240,255,0.2) !important;
            color: #ffffff !important;
        }
        
        /* מספרי היחסים (Odds) */
        [data-testid="stMetricValue"] { color: #00f0ff !important; font-size: 2.2rem !important; font-family: monospace !important; }
        [data-testid="stMetricLabel"] { color: #8b9eb3 !important; font-size: 1rem !important; }
        
        hr { border-color: rgba(0,240,255,0.1) !important; margin: 20px 0 !important; }
        
        /* הסתרת המיתוג של סטרימליט */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# הגדרות API ומנועי AI/תרגום
# -----------------------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro') # תוקן לשם המודל העובד והיציב

translator = GoogleTranslator(source='en', target='he')

@st.cache_data(ttl=86400) # שומר תרגומים בזיכרון ל-24 שעות כדי למנוע עומס
def translate_team(team_name):
    try:
        translated = translator.translate(team_name)
        return translated if translated else team_name
    except:
        return team_name

TARGET_LEAGUES = [
    'Premier League', 'LaLiga', 'Ligue 1', 'Serie A',
    'Ligat HaAl', 'State Cup', 'Toto Cup',
    'NBA', 'Super League', 'National League'
]

SOFASCORE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/"
}

# -----------------------------------------
# משיכת נתונים מ-SofaScore
# -----------------------------------------
@st.cache_data(ttl=1800)
def get_sofascore_odds(game_id):
    url = f"https://api.sofascore.com/api/v1/event/{game_id}/odds/1/all"
    try:
        res = requests.get(url, headers=SOFASCORE_HEADERS, timeout=5)
        if res.status_code == 200:
            markets = res.json().get("markets", [])
            if markets:
                choices = markets[0].get("choices", [])
                return {c["name"]: c.get("fractionalValue", c.get("initialFractionalValue", "N/A")) for c in choices}
    except: pass
    return {"1": "חסר", "X": "חסר", "2": "חסר"}

@st.cache_data(ttl=3600)
def fetch_upcoming_games(sport, days=5):
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
                        
                        # תרגום שמות הקבוצות לעברית
                        home_en = event.get("homeTeam", {}).get("name", "Unknown")
                        away_en = event.get("awayTeam", {}).get("name", "Unknown")
                        home_he = translate_team(home_en)
                        away_he = translate_team(away_en)
                        
                        odds = get_sofascore_odds(game_id)
                        
                        games.append({
                            "id": game_id,
                            "date": target_date,
                            "league": league_name,
                            "home": home_he,
                            "away": away_he,
                            "odds_h": odds.get("1", "חסר"),
                            "odds_d": odds.get("X", "חסר"),
                            "odds_a": odds.get("2", "חסר")
                        })
        except: pass
    return games

@st.cache_data(ttl=3600)
def get_deep_stats(game_id, home_team, away_team):
    url = f"https://api.sofascore.com/api/v1/event/{game_id}/h2h/events"
    h2h_summary = "אין מספיק נתונים היסטוריים להשוואה."
    try:
        res = requests.get(url, headers=SOFASCORE_HEADERS, timeout=5)
        if res.status_code == 200:
            events = res.json().get("events", [])
            if events:
                # ה-API של SofaScore מחזיר שמות באנגלית, לכן לא נשתמש בשם המדויק להשוואה אלא במיקום
                h_wins = sum(1 for g in events[:10] if g.get("winnerCode") == 1)
                a_wins = sum(1 for g in events[:10] if g.get("winnerCode") == 2)
                draws = sum(1 for g in events[:10] if g.get("winnerCode") == 3)
                h2h_summary = f"ב-{min(len(events), 10)} המפגשים האחרונים ביניהן: {h_wins} ניצחונות ל{home_team}, {a_wins} ניצחונות ל{away_team}, ו-{draws} תוצאות תיקו."
    except: pass
    return {"h2h": h2h_summary}

# -----------------------------------------
# ממשק המשתמש (UI)
# -----------------------------------------
with st.sidebar:
    st.markdown("<h1 style='color:#00f0ff !important;'>⚡ SportIQ ULTRA</h1>", unsafe_allow_html=True)
    st.markdown("מערכת לאיתור Value Bets")
    st.divider()
    
    sport_choice = st.radio("בחר ענף ספורט:", ["כדורגל ⚽", "כדורסל 🏀"], horizontal=True)
    st.divider()
    
    st.write("📅 סורק משחקים (5 ימים)...")
    with st.spinner("מאתר ומתרגם משחקים..."):
        games = fetch_upcoming_games(sport_choice)
    
    selected_game = None
    if not games:
        st.info("לא נמצאו משחקים רלוונטיים.")
    else:
        # רשימת המשחקים בסרגל הצד - עכשיו בעברית!
        game_options = {f"{g['date']} | {g['home']} נגד {g['away']}": g for g in games}
        selected_game_str = st.radio("בחר משחק לניתוח:", list(game_options.keys()))
        selected_game = game_options[selected_game_str]

# אזור התצוגה המרכזי
if selected_game:
    st.markdown(f"<h1>{selected_game['home']} <span style='color:#00f0ff;'>VS</span> {selected_game['away']}</h1>", unsafe_allow_html=True)
    st.caption(f"ליגה: {selected_game['league']} | תאריך: {selected_game['date']}")
    st.divider()

    col_stats, col_ai = st.columns([1, 1.5], gap="large")

    with col_stats:
        st.subheader("📊 נתונים חיים (Live)")
        
        st.write("**יחסי זכייה (Odds):**")
        c1, c2, c3 = st.columns(3)
        if sport_choice == "כדורגל ⚽":
            c1.metric("1 (בית)", selected_game['odds_h'])
            c2.metric("X (תיקו)", selected_game['odds_d'])
            c3.metric("2 (חוץ)", selected_game['odds_a'])
        else:
            c1.metric("1 (בית)", selected_game['odds_h'])
            c3.metric("2 (חוץ)", selected_game['odds_a'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        stats = get_deep_stats(selected_game['id'], selected_game['home'], selected_game['away'])
        st.info(f"**היסטוריית H2H:**\n\n{stats['h2h']}")

    with col_ai:
        st.subheader("🧠 מנוע AI (Gemini 1.5 Pro)")
        st.markdown("ניתוח עומק ואיתור ערך להמר עליו.")
        
        if st.button("הפעל ניתוח AI עכשיו ⚡"):
            with st.spinner("מעבד נתונים ומחשב הסתברויות..."):
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
                    1. מי הפייבוריטית ולמה (לאור הנתונים).
                    2. האם היחסים המוצעים משקפים את המציאות ויש בהם ערך (Value).
                    3. המלצה חותכת מנומקת היטב.
                    """
                    response = model.generate_content(prompt)
                    st.success("ניתוח הושלם בהצלחה:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"שגיאת תקשורת עם גוגל. ודא שהמפתח תקין. פירוט השגיאה: {e}")
else:
    st.title("⚡ SportIQ ULTRA AI")
    st.write("אנא בחר משחק מסרגל הצד כדי להתחיל בניתוח.")
