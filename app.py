import streamlit as st
import api_sofascore as api
import ai_analyzer as ai
import os
from datetime import datetime

st.set_page_config(page_title="SportIQ ULTRA v2", layout="wide", initial_sidebar_state="expanded")

if 'ai_results' not in st.session_state: st.session_state.ai_results = {}
if 'selected_sport' not in st.session_state: st.session_state.selected_sport = "כדורגל ⚽"

# CSS מתקדם לתיקון כל בעיות התצוגה
st.markdown("""
    <style>
        * { direction: rtl !important; font-family: 'Segoe UI', 'Heebo', sans-serif !important; }
        .stApp { background: linear-gradient(135deg, #02040a 0%, #0a1622 100%) !important; color: #e8f4f8 !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0c1220 0%, #131d2d 100%) !important; border-left: 2px solid rgba(0,240,255,0.15) !important; }
        
        /* תיקון טקסט כהה בסרגל הצד - הכל יהיה לבן וקריא */
        .stRadio > div[role="radiogroup"] > label > div > div > p { color: #ffffff !important; font-size: 15px !important; font-weight: 500 !important; }
        .stTextInput > div > div > input { color: #ffffff !important; }
        
        h1, h2, h3, h4 { color: #00f0ff !important; font-weight: 700 !important; }
        p, span, div, label { text-align: right !important; direction: rtl !important; }
        
        /* עיצוב כרטיסיות נתונים */
        .metric-card { background: rgba(0, 240, 255, 0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 240, 255, 0.2); text-align: center; }
        .metric-val { font-size: 1.8rem; font-weight: bold; color: #00ff88; }
        .metric-label { font-size: 0.9rem; color: #a8b2c1; }
        
        .data-box { background: rgba(17, 25, 39, 0.6); border: 1px solid rgba(0, 240, 255, 0.15); border-radius: 10px; padding: 18px; margin-bottom: 15px; }
        .form-badge { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 4px; font-weight: 900; font-size: 12px; margin: 0 3px; color: #111927; }
    </style>
""", unsafe_allow_html=True)

# אזור עליון: בחירת ספורט בשמאל, כותרת בימין
col_sport, col_title = st.columns([1, 3])
with col_title:
    st.markdown("<h1 style='text-align:right;'>⚡ SportIQ ULTRA v2</h1>", unsafe_allow_html=True)
with col_sport:
    # בחירת ענף בקופסאות נוחות בצד שמאל
    sport_choice = st.radio("בחר ענף:", ["כדורגל ⚽", "כדורסל 🏀"], horizontal=True, label_visibility="collapsed")
    st.session_state.selected_sport = sport_choice

st.divider()

# הבאת המשחקים
with st.spinner("🔄 מעדכן נתונים..."):
    games_by_date = api.fetch_games_for_dates(sport=sport_choice, days=5)

if not games_by_date:
    st.error("❌ לא נמצאו משחקים בימים הקרובים")
    st.stop()

# ניווט תאריכים בחלק העליון המרכזי (במקום בסרגל)
st.markdown("### 📅 בחר תאריך למשחקים:")
dates_list = sorted(list(games_by_date.keys()))
# הפיכת תאריכים לפורמט קריא יותר
formatted_dates = [datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m") for d in dates_list]

selected_date_index = st.radio("תאריך:", range(len(dates_list)), format_func=lambda x: formatted_dates[x], horizontal=True, label_visibility="collapsed")
selected_date = dates_list[selected_date_index]
daily_games = games_by_date[selected_date]

# סרגל צד: חיפוש ובחירת משחק ספציפי
with st.sidebar:
    st.markdown("### 🔍 סינון משחקים להיום")
    search_query = st.text_input("חפש שם קבוצה...", placeholder="לדוגמה: מכבי...")
    st.divider()
    
    # סינון המשחקים לפי החיפוש
    if search_query:
        daily_games = [g for g in daily_games if search_query.lower() in g['home'].lower() or search_query.lower() in g['away'].lower()]
    
    if not daily_games:
        st.warning("לא נמצאו משחקים לחיפוש זה.")
        st.stop()
        
    game_options = {f"{g['time']} | {g['home']} - {g['away']}": g for g in daily_games}
    st.markdown("**👇 בחר משחק לניתוח:**")
    selected_game_str = st.radio("רשימת משחקים", options=list(game_options.keys()), label_visibility="collapsed")
    selected_game = game_options[selected_game_str]

# טעינת נתונים למשחק הנבחר
with st.spinner("📊 מנתח יחסי הימורים וסטטיסטיקות..."):
    deep_data = api.get_game_deep_data(selected_game['id'], selected_game['home_id'], selected_game['away_id'], selected_game['home'], selected_game['away'])

st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin: 20px 0; background: rgba(0,240,255,0.1); padding: 20px; border-radius: 15px;'>
        <h2 style='margin: 0; flex: 1; text-align: right;'>{selected_game['home']}</h2>
        <span style='color: #00f0ff; font-size: 1.2rem; font-weight: bold; background: #0c1220; padding: 5px 15px; border-radius: 20px;'>{selected_game['time']} | {selected_game['league']}</span>
        <h2 style='margin: 0; flex: 1; text-align: left;'>{selected_game['away']}</h2>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💰 נתונים ויחסים", "⚔️ היסטוריה וסטטיסטיקה", "🧠 ניתוח AI"])

with tab1:
    st.markdown("#### 🎲 יחסי הימורים (Match Odds)")
    odds = deep_data['odds']
    
    # הצגת יחסים בצורה בולטת באמצעות HTML אישי
    st.markdown(f"""
        <div style="display:flex; gap:15px; margin-bottom:20px;">
            <div class="metric-card" style="flex:1;"><div class="metric-label">ניצחון בית (1)</div><div class="metric-val">{odds.get('1', '-')}</div></div>
            <div class="metric-card" style="flex:1;"><div class="metric-label">תיקו (X)</div><div class="metric-val" style="color:#ffd94a;">{odds.get('X', '-')}</div></div>
            <div class="metric-card" style="flex:1;"><div class="metric-label">ניצחון חוץ (2)</div><div class="metric-val" style="color:#ff3b5c;">{odds.get('2', '-')}</div></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📋 כושר נוכחי (5 אחרונים)")
    def render_form(team, form_data):
        html = f"<div style='margin-bottom:10px;'><b style='color:#00f0ff;'>{team}</b><div style='display:flex; gap:4px; margin-top:5px;'>"
        for res, color in form_data: html += f"<span class='form-badge' style='background-color:{color};'>{res}</span>"
        return html + "</div></div>"
    
    st.markdown(f"<div class='data-box'>{render_form(selected_game['home'], deep_data['home_stats'].get('form', []))}{render_form(selected_game['away'], deep_data['away_stats'].get('form', []))}</div>", unsafe_allow_html=True)

with tab2:
    if deep_data['h2h_summary'].get('total', 0) > 0:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('סה"כ משחקים', deep_data['h2h_summary'].get('total', 0))
        c2.metric("ניצחונות בית", deep_data['h2h_summary'].get('home_wins', 0))
        c3.metric("תיקו", deep_data['h2h_summary'].get('draws', 0))
        c4.metric("ניצחונות חוץ", deep_data['h2h_summary'].get('away_wins', 0))
        st.divider()
        for match in deep_data['h2h_matches']:
            st.markdown(f"<div class='data-box' style='text-align:center;'><b>{match['home']}</b> {match['home_score']}-{match['away_score']} <b>{match['away']}</b><br><small>{match['date']} | {match['result']}</small></div>", unsafe_allow_html=True)
    else:
        st.info("אין מפגשים קודמים מתועדים בין הקבוצות.")

with tab3:
    st.markdown("#### 🧠 מנוע ניתוח AI (Google Gemini)")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
        
    if not GEMINI_API_KEY:
        st.error("❌ חסר מפתח API של Gemini ב-Secrets")
    else:
        game_id_str = str(selected_game['id'])
        if game_id_str in st.session_state.ai_results:
            st.success("✅ ניתוח הושלם")
            st.markdown(st.session_state.ai_results[game_id_str])
        else:
            if st.button("🚀 הפעל ניתוח AI", use_container_width=True):
                with st.spinner("🤖 מנתח את כל הנתונים..."):
                    st.session_state.ai_results[game_id_str] = ai.analyze_match(st.session_state.selected_sport, selected_game, deep_data, GEMINI_API_KEY)
                    st.rerun()
