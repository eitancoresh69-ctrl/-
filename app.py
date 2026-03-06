import streamlit as st
import api_sofascore as api
import ai_analyzer as ai

# הגדרת הדף
st.set_page_config(page_title="SportIQ ULTRA", layout="wide", initial_sidebar_state="expanded")

# --- זיכרון פנימי לניתוחי AI ---
if 'ai_results' not in st.session_state:
    st.session_state.ai_results = {}

# --- CSS מעודכן (עיצוב מדויק לסגנון שלך וסידור סרגל הצד) ---
st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { direction: rtl !important; font-family: 'Heebo', sans-serif; }
        .stApp { background-color: #02040a !important; color: #e8f4f8 !important; }
        [data-testid="stSidebar"] { background-color: #0c1220 !important; border-left: 1px solid rgba(0,240,255,0.08) !important; }
        p, div, span, label, h1, h2, h3 { text-align: right !important; direction: rtl !important; }
        
        /* כרטיסיות מידע ומשחקים בסרגל הצד */
        .stRadio > div { gap: 8px !important; }
        .stRadio label { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: 8px !important; padding: 10px !important; }
        .stRadio label:hover { border-color: #00f0ff !important; background: rgba(0,240,255,0.05) !important; }
        
        /* 🔥 תיקון הצבע של המשחקים בסרגל הצד 🔥 */
        [data-testid="stSidebar"] .stRadio label p, 
        [data-testid="stSidebar"] .stRadio label span {
            color: #ffffff !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }
        
        /* קופסאות נתונים */
        .data-box { background: #111927; border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; margin-bottom: 15px; }
        .data-box h4 { color: #00f0ff; margin-top: 0; font-size: 0.9rem; margin-bottom: 10px;}
        
        /* כפתור AI */
        .stButton > button { background: linear-gradient(135deg, rgba(0,240,255,0.1), rgba(0,255,136,0.1)) !important; border: 1px solid rgba(0,240,255,0.3) !important; color: #00f0ff !important; width: 100%; font-weight: bold;}
        .stButton > button:hover { border-color: #00f0ff !important; box-shadow: 0 0 15px rgba(0,240,255,0.2) !important; color: white !important;}
        
        /* הסתרת מיתוג */
        #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- סרגל צד (Sidebar) ---
with st.sidebar:
    st.markdown("<h1 style='color:#00f0ff;'>⚡ SportIQ ULTRA</h1>", unsafe_allow_html=True)
    st.divider()
    
    sport_choice = st.radio("ענף:", ["כדורגל ⚽", "כדורסל 🏀"], horizontal=True)
    st.divider()
    
    with st.spinner("סורק משחקים מ-SofaScore..."):
        games_by_date = api.fetch_games_for_dates(sport=sport_choice, days=7)
    
    if not games_by_date:
        st.warning("לא נמצאו משחקים בליגות המטרה בימים הקרובים.")
        st.stop()
    
    # סינון חכם לפי תאריך
    selected_date = st.selectbox("📅 בחר תאריך למשחקים:", list(games_by_date.keys()))
    
    st.markdown(f"**משחקים ל-{selected_date}:**")
    daily_games = games_by_date[selected_date]
    
    # בניית אפשרויות למשחקים באותו תאריך בלבד
    game_options = {f"{g['time']} | {g['home']} - {g['away']}": g for g in daily_games}
    selected_game_str = st.radio("בחר משחק:", list(game_options.keys()), label_visibility="collapsed")
    selected_game = game_options[selected_game_str]

# --- מסך מרכזי (Main Content) ---
st.markdown(f"<h2>{selected_game['home']} <span style='color:#00f0ff'>VS</span> {selected_game['away']}</h2>", unsafe_allow_html=True)
st.caption(f"ליגה: {selected_game['league']} | שעה: {selected_game['time']} | תאריך: {selected_date}")

with st.spinner("מושך נתוני עומק, פצועים וסטטיסטיקות..."):
    deep_data = api.get_game_deep_data(selected_game['id'], selected_game['home'], selected_game['away'])

col_data, col_ai = st.columns([1, 1.5], gap="large")

with col_data:
    st.markdown("### 📊 לוח נתונים (Live)")
    
    st.markdown(f"""
        <div class='data-box'>
            <h4>יחסי זכייה (Odds)</h4>
            <b>1:</b> {deep_data['odds'].get('1', '-')} &nbsp;|&nbsp; 
            <b>X:</b> {deep_data['odds'].get('X', '-')} &nbsp;|&nbsp; 
            <b>2:</b> {deep_data['odds'].get('2', '-')}
        </div>
        
        <div class='data-box'>
            <h4>ראש בראש (H2H)</h4>
            {deep_data['h2h']}
        </div>
        
        <div class='data-box'>
            <h4>🚑 פצועים / הרכבים חסרים</h4>
            <span style="color:#ff3b5c; font-size:0.9rem;">{deep_data['missing_players']}</span>
        </div>
        
        <div class='data-box'>
            <h4>📈 סטטיסטיקות משחק (קרנות/כרטיסים)</h4>
            <span style="color:#e8f4f8; font-size:0.9rem;">{deep_data['stats']}</span>
        </div>
    """, unsafe_allow_html=True)

with col_ai:
    st.markdown("### 🧠 מנוע AI (Gemini)")
    
    game_id_str = str(selected_game['id'])
    
    if game_id_str in st.session_state.ai_results:
        st.success("ניתוח מהזיכרון:")
        st.write(st.session_state.ai_results[game_id_str])
        if st.button("🔄 רענן ניתוח AI מחדש"):
            del st.session_state.ai_results[game_id_str]
            st.rerun()
    else:
        st.info("ה-AI ממתין לפקודה. הניתוח ישמר אוטומטית למעבר מהיר בין משחקים.")
        if st.button("הפעל ניתוח AI עמוק ⚡"):
            with st.spinner("מעבד נתונים, שוקל פצועים ומחשב הסתברויות..."):
                result = ai.analyze_match(sport_choice, selected_game, deep_data, GEMINI_API_KEY)
                st.session_state.ai_results[game_id_str] = result
                st.rerun()
