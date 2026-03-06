import streamlit as st
import api_sofascore as api
import ai_analyzer as ai
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="SportIQ ULTRA v2", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

if 'ai_results' not in st.session_state:
    st.session_state.ai_results = {}
if 'selected_sport' not in st.session_state:
    st.session_state.selected_sport = "כדורגל ⚽"

st.markdown("""
    <style>
        * { direction: rtl !important; font-family: 'Segoe UI', 'Heebo', sans-serif !important; }
        .stApp { background: linear-gradient(135deg, #02040a 0%, #0a1622 100%) !important; color: #e8f4f8 !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0c1220 0%, #131d2d 100%) !important; border-left: 2px solid rgba(0,240,255,0.15) !important; }
        h1, h2, h3, h4 { color: #00f0ff !important; font-weight: 700 !important; }
        p, span, div, label { text-align: right !important; direction: rtl !important; }
        .stMetric { background: rgba(0, 240, 255, 0.05) !important; padding: 15px !important; border-radius: 10px !important; border: 1px solid rgba(0, 240, 255, 0.15) !important; }
        .data-box { background: rgba(17, 25, 39, 0.6) !important; border: 1px solid rgba(0, 240, 255, 0.15) !important; border-radius: 10px !important; padding: 18px !important; margin-bottom: 15px !important; }
        .form-badge { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 4px; font-weight: 900; font-size: 12px; margin: 0 3px; color: #111927; }
        .stat-item { background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 8px; padding: 12px 15px; flex: 1; min-width: 150px; text-align: center; }
        .stat-value { font-size: 1.3rem; font-weight: 700; color: #00ff88; }
        .stat-label { font-size: 0.75rem; color: #a8b2c1; margin-top: 4px; }
        .stats-row { display: flex; gap: 15px; margin: 15px 0; flex-wrap: wrap; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>⚡ SportIQ ULTRA v2</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#a8b2c1;'>מערכת ניתוח ספורט מתקדמת עם AI</p>", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🎯 בחירות</h2>", unsafe_allow_html=True)
    sport_choice = st.radio("🏅 ענף ספורט:", ["כדורגל ⚽", "כדורסל 🏀"], key="sport_choice")
    st.session_state.selected_sport = sport_choice
    st.divider()
    
    with st.spinner("🔄 טוען משחקים..."):
        games_by_date = api.fetch_games_for_dates(sport=sport_choice, days=7)
    
    if not games_by_date:
        st.error("❌ לא נמצאו משחקים בליגות המטרה")
        st.stop()
        
    dates_list = sorted(list(games_by_date.keys()))
    col_start, col_end = st.columns(2)
    with col_start: start_date = st.selectbox("מתאריך:", dates_list, index=0)
    with col_end: end_date = st.selectbox("עד תאריך:", dates_list, index=min(2, len(dates_list)-1))
    
    filtered_games = []
    for date_str in dates_list:
        if start_date <= date_str <= end_date:
            filtered_games.extend(games_by_date[date_str])
            
    if not filtered_games:
        st.warning("⚠️ אין משחקים בטווח התאריכים שנבחר")
        st.stop()
        
    game_options = {f"{g['time']} | {g['home']} - {g['away']} ({g['league'][:15]})": g for g in filtered_games}
    st.markdown("**🎯 כל המשחקים להיום:**")
    selected_game_str = st.radio("בחר משחק:", options=list(game_options.keys()), label_visibility="collapsed")
    selected_game = game_options[selected_game_str]
    st.divider()

st.markdown("### 🔄 טוען נתוני עומק...")
with st.spinner("📊 מושך נתונים מכמה מקורות..."):
    deep_data = api.get_game_deep_data(
        selected_game['id'], selected_game['home_id'], selected_game['away_id'],
        selected_game['home'], selected_game['away']
    )

st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; margin: 20px 0;'>
        <h2 style='margin: 0;'>{selected_game['home']}</h2>
        <span style='color: #00f0ff; font-size: 1.5rem; font-weight: bold;'>VS</span>
        <h2 style='margin: 0;'>{selected_game['away']}</h2>
    </div>
    <p style='text-align: center; color: #a8b2c1; margin: 0;'>⏰ {selected_game['time']} | 📍 {selected_game['league']}</p>
""", unsafe_allow_html=True)
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📊 נתונים", "⚔️ H2H", "🧠 ניתוח AI", "📈 סטטיסטיקות"])

with tab1:
    col_odds, col_form = st.columns([1.2, 1], gap="large")
    with col_odds:
        st.markdown("#### 💰 יחסי זכייה (Odds)")
        odds = deep_data['odds']
        c1, c2, c3 = st.columns(3)
        c1.metric("1️⃣ בית", odds.get('1', '-'))
        c2.metric("🤝 תיקו", odds.get('X', '-'))
        c3.metric("2️⃣ חוץ", odds.get('2', '-'))
        c4, c5 = st.columns(2)
        c4.metric("⬆️ Over 2.5", odds.get('over_2_5', '-'))
        c5.metric("⬇️ Under 2.5", odds.get('under_2_5', '-'))
        
    with col_form:
        st.markdown("#### 📋 כושר נוכחי")
        def render_form(team_name, form_data):
            html = f"<div style='margin-bottom:10px;'><div style='color:#00f0ff; font-weight:bold;'>{team_name}</div><div style='display:flex; gap:4px;'>"
            for res, color in form_data: html += f"<span class='form-badge' style='background-color:{color};'>{res}</span>"
            return html + "</div></div>"
        
        st.markdown(f"<div class='data-box'>{render_form(selected_game['home'], deep_data['home_stats'].get('form', []))}{render_form(selected_game['away'], deep_data['away_stats'].get('form', []))}</div>", unsafe_allow_html=True)
        
    st.divider()
    col_h, col_a = st.columns(2, gap="large")
    with col_h:
        stats = deep_data['home_stats']
        st.markdown(f"#### ⚽ {selected_game['home']} (בית)")
        st.markdown(f"<div class='data-box'><div class='stats-row'><div class='stat-item'><div class='stat-value'>{stats.get('wins',0)}</div><div class='stat-label'>ניצחונות</div></div><div class='stat-item'><div class='stat-value'>{stats.get('goals_scored',0)}</div><div class='stat-label'>הבקיע</div></div><div class='stat-item'><div class='stat-value'>{stats.get('goals_conceded',0)}</div><div class='stat-label'>ספג</div></div></div></div>", unsafe_allow_html=True)
    with col_a:
        stats = deep_data['away_stats']
        st.markdown(f"#### ⚽ {selected_game['away']} (חוץ)")
        st.markdown(f"<div class='data-box'><div class='stats-row'><div class='stat-item'><div class='stat-value'>{stats.get('wins',0)}</div><div class='stat-label'>ניצחונות</div></div><div class='stat-item'><div class='stat-value'>{stats.get('goals_scored',0)}</div><div class='stat-label'>הבקיע</div></div><div class='stat-item'><div class='stat-value'>{stats.get('goals_conceded',0)}</div><div class='stat-label'>ספג</div></div></div></div>", unsafe_allow_html=True)
        
    st.divider()
    c_inj_h, c_inj_a = st.columns(2)
    with c_inj_h:
        st.markdown(f"**{selected_game['home']}:**")
        missing = [p for p in deep_data.get('missing_home', []) if p and p.strip() and p != "סגל מלא"]
        if missing:
            for p in missing: st.error(f"🚑 {p}")
        else: st.success("✅ סגל מלא")
    with c_inj_a:
        st.markdown(f"**{selected_game['away']}:**")
        missing = [p for p in deep_data.get('missing_away', []) if p and p.strip() and p != "סגל מלא"]
        if missing:
            for p in missing: st.error(f"🚑 {p}")
        else: st.success("✅ סגל מלא")

with tab2:
    if deep_data['h2h_summary'].get('total', 0) > 0:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('סה"כ משחקים', deep_data['h2h_summary'].get('total', 0))
        c2.metric("ניצחונות בית", deep_data['h2h_summary'].get('home_wins', 0))
        c3.metric("תיקו", deep_data['h2h_summary'].get('draws', 0))
        c4.metric("ניצחונות חוץ", deep_data['h2h_summary'].get('away_wins', 0))
        for match in deep_data['h2h_matches']:
            st.markdown(f"<div class='data-box' style='text-align:center;'><b>{match['home']}</b> {match['home_score']}-{match['away_score']} <b>{match['away']}</b><br><small>{match['date']} | {match['result']}</small></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ אין מפגשים קודמים מתועדים")

with tab3:
    st.markdown("#### 🧠 מנוע ניתוח AI (Google Gemini)")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        try: GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        except: GEMINI_API_KEY = ""
        
    if not GEMINI_API_KEY:
        st.error("❌ חסר מפתח API של Gemini ב-Secrets")
    else:
        game_id_str = str(selected_game['id'])
        if game_id_str in st.session_state.ai_results:
            st.success("✅ ניתוח זמין")
            st.markdown(st.session_state.ai_results[game_id_str])
            if st.button("🔄 רענן ניתוח מחדש"):
                del st.session_state.ai_results[game_id_str]
                st.rerun()
        else:
            if st.button("🚀 הפעל ניתוח AI עמוק", use_container_width=True):
                with st.spinner("🤖 מנתח..."):
                    st.session_state.ai_results[game_id_str] = ai.analyze_match(st.session_state.selected_sport, selected_game, deep_data, GEMINI_API_KEY)
                    st.rerun()

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🏠 {selected_game['home']}**")
        st.json(deep_data['home_stats'])
    with col2:
        st.markdown(f"**🚗 {selected_game['away']}**")
        st.json(deep_data['away_stats'])
