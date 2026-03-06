import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime, timedelta

# חובה להיות השורה הראשונה: הגדרת הדף לפריסה רחבה וסרגל צד פתוח
st.set_page_config(page_title="SportIQ ULTRA", layout="wide", initial_sidebar_state="expanded")

# הזרקת CSS מתקדם ליצירת ה-Dark Mode והעיצוב המקורי שלך (ניאון) בתוך Streamlit
st.markdown("""
    <style>
        /* הגדרות כלליות וימין-לשמאל */
        body, .stApp { 
            direction: rtl; 
            text-align: right; 
            font-family: 'Heebo', 'Segoe UI', sans-serif;
            background-color: #02040a;
            color: #e8f4f8;
        }
        
        /* כיווניות של טקסטים */
        p, div, span, label, h1, h2, h3, h4, h5, h6 { text-align: right; direction: rtl; }
        
        /* עיצוב סרגל הצד (Sidebar) */
        [data-testid="stSidebar"] {
            background-color: #0c1220 !important;
            border-left: 1px solid rgba(0,240,255,0.08);
        }
        
        /* צבעוניות ניאון לכפתורים */
        .stButton > button {
            background: linear-gradient(135deg, rgba(0,240,255,0.1), rgba(0,255,136,0.1));
            border: 1px solid rgba(0,240,255,0.3);
            color: #00f0ff;
            border-radius: 8px;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton > button:hover {
            border-color: #00f0ff;
            box-shadow: 0 0 15px rgba(0,240,255,0.2);
            color: #ffffff;
        }
        
        /* עיצוב כרטיסיות הנתונים היבשים */
        div[data-testid="stMetricValue"] { color: #00f0ff; }
        hr { border-color: rgba(0,240,255,0.1); }
        
        /* רדיו באטנס (רשימת המשחקים) בסרגל הצד */
        div.row-widget.stRadio > div { flex-direction: column; gap: 10px; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# הגדרות מערכת ו-API
# -----------------------------------------
# משיכת מפתח מ-Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# התיקון לשגיאת ה-404: שימוש במודל המעודכן
model = genai.GenerativeModel('gemini-1.5-pro-latest') 

TARGET_LEAGUES = [
    'Premier League', 'LaLiga', 'Ligue 1', 'Serie A',
    'Ligat HaAl', 'State Cup', 'Toto Cup',
    'NBA', 'Super League', 'National League'
]

SOFASCORE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/"
}

# -----------------------------------------
# פונקציות שליפת נתונים (עם שמירה בזיכרון)
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
                home_wins = sum(1 for g in events[:10] if (g.get("homeScore",{}).get("current",0) > g.get("awayScore",{}).get("current",0) and g.get("homeTeam",{}).get("name") == home_team) or (g.get("awayScore",{}).get("current",0) > g.get("homeScore",{}).get("current",0) and g.get("awayTeam",{}).get("name") == home_team))
                away_wins = sum(1 for g in events[:10] if (g.get("homeScore",{}).get("current",0) > g.get("awayScore",{}).get("current",0) and g.get("homeTeam",{}).get("name") == away_team) or (g.get("awayScore",{}).get("current",0) > g.get("homeScore",{}).get("current",0) and g.get("awayTeam",{}).get("name") == away_team))
                draws = sum(1 for g in events[:10] if g.get("homeScore",{}).get("current",0) == g.get("awayScore",{}).get("current",0))
                h2h_summary = f"ב-{len(events[:10])} המפגשים האחרונים: {home_wins} ניצחונות ל{home_team}, {away_wins} ל{away_team}, ו-{draws} תוצאות תיקו."
    except: pass
    return {"h2h": h2h_summary}


# -----------------------------------------
# ממשק המשתמש (UI)
# -----------------------------------------

# סרגל הצד (Sidebar) - לסינון ובחירת משחקים
with st.sidebar:
    st.title("⚡ SportIQ ULTRA")
    st.markdown("מערכת לאיתור Value Bets")
    st.divider()
    
    sport_choice = st.radio("בחר ענף ספורט:", ["כדורגל ⚽", "כדורסל 🏀"], horizontal=True)
    st.divider()
    
    st.write("📅 סורק משחקים (5 ימים)...")
    with st.spinner("מחפש..."):
        games = fetch_upcoming_games(sport_choice)
    
    selected_game = None
    if not games:
        st.info("לא נמצאו משחקים רלוונטיים.")
    else:
        # רשימת המשחקים מוצגת בסרגל הצד בפריסה נוחה
        game_options = {f"{g['date']} | {g['home']} - {g['away']}": g for g in games}
        selected_game_str = st.radio("בחר משחק לניתוח:", list(game_options.keys()))
        selected_game = game_options[selected_game_str]

# אזור התצוגה המרכזי
if selected_game:
    st.markdown(f"<h2>{selected_game['home']} <span style='color:#00f0ff'>VS</span> {selected_game['away']}</h2>", unsafe_allow_html=True)
    st.caption(f"ליגה: {selected_game['league']} | תאריך: {selected_game['date']}")
    st.divider()

    col_stats, col_ai = st.columns([1, 1.5])

    with col_stats:
        st.subheader("📊 נתונים חיים (Live)")
        
        # תצוגת יחסים
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
        st.info(f"**היסטוריית H2H:**\n{stats['h2h']}")

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
