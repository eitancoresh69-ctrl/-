import streamlit as st
import api_sofascore as api
import ai_analyzer as ai

st.set_page_config(page_title="SportIQ ULTRA", layout="wide", initial_sidebar_state="expanded")

if 'ai_results' not in st.session_state:
    st.session_state.ai_results = {}

st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { direction: rtl !important; font-family: 'Heebo', sans-serif; }
        .stApp { background-color: #02040a !important; color: #e8f4f8 !important; }
        [data-testid="stSidebar"] { background-color: #0c1220 !important; border-left: 1px solid rgba(0,240,255,0.08) !important; }
        p, div, span, label, h1, h2, h3 { text-align: right !important; direction: rtl !important; }
        
        .stRadio > div { gap: 8px !important; }
        .stRadio label { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: 8px !important; padding: 10px !important; }
        .stRadio label:hover { border-color: #00f0ff !important; background: rgba(0,240,255,0.05) !important; }
        [data-testid="stSidebar"] .stRadio label p, [data-testid="stSidebar"] .stRadio label span { color: #ffffff !important; font-size: 0.9rem !important; }
        
        .data-box { background: #111927; border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; margin-bottom: 15px; }
        .data-box h4 { color: #00f0ff; margin-top: 0; font-size: 0.9rem; margin-bottom: 15px;}
        
        .stButton > button { background: linear-gradient(135deg, rgba(0,240,255,0.1), rgba(0,255,136,0.1)) !important; border: 1px solid rgba(0,240,255,0.3) !important; color: #00f0ff !important; width: 100%; font-weight: bold;}
        .stButton > button:hover { border-color: #00f0ff !important; box-shadow: 0 0 15px rgba(0,240,255,0.2) !important; color: white !important;}
        #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

def render_form_badges(form_data):
    if not form_data: return "<span style='color:gray;'>אין נתונים</span>"
    html = "<div style='display:flex; gap: 5px; direction:ltr;'>"
    for res, color in form_data:
        html += f"<span style='background-color:{color}; color:#111927; font-weight:900; width:22px; height:22px; display:flex; align-items:center; justify-content:center; border-radius:4px; font-size:11px;'>{res}</span>"
    html += "</div>"
    return html

def parse_odds_to_decimal(odd_str):
    try:
        if '/' in str(odd_str):
            n, d = str(odd_str).split('/')
            return (float(n) / float(d)) + 1
        return float(odd_str)
    except:
        return 0

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
    
    selected_date = st.selectbox("📅 בחר תאריך למשחקים:", list(games_by_date.keys()))
    st.markdown(f"**משחקים ל-{selected_date}:**")
    daily_games = games_by_date[selected_date]
    
    game_options = {f"{g['time']} | {g['home']} - {g['away']}": g for g in daily_games}
    selected_game_str = st.radio("בחר משחק:", list(game_options.keys()), label_visibility="collapsed")
    selected_game = game_options[selected_game_str]

st.markdown(f"<h2>{selected_game['home']} <span style='color:#00f0ff'>VS</span> {selected_game['away']}</h2>", unsafe_allow_html=True)
st.caption(f"ליגה: {selected_game['league']} | שעה (שעון ישראל): {selected_game['time']} | תאריך: {selected_date}")

with st.spinner("מושך נתוני עומק..."):
    deep_data = api.get_game_deep_data(selected_game['id'], selected_game['home_id'], selected_game['away_id'])

col_data, col_ai = st.columns([1.3, 1.2], gap="large")

with col_data:
    st.markdown("### 📊 לוח נתונים (Live)")
    
    h_odd = parse_odds_to_decimal(deep_data['odds'].get('1', '0'))
    d_odd = parse_odds_to_decimal(deep_data['odds'].get('X', '0'))
    a_odd = parse_odds_to_decimal(deep_data['odds'].get('2', '0'))
    
    h_prob = 100 / h_odd if h_odd > 0 else 0
    d_prob = 100 / d_odd if d_odd > 0 else 0
    a_prob = 100 / a_odd if a_odd > 0 else 0
    total_prob = h_prob + d_prob + a_prob
    
    prob_html = ""
    if total_prob > 0:
        h_norm = (h_prob / total_prob) * 100
        d_norm = (d_prob / total_prob) * 100
        a_norm = (a_prob / total_prob) * 100
        fav_text = f"פייבוריטית: {selected_game['home']}" if h_norm > a_norm and h_norm > d_norm else (f"פייבוריטית: {selected_game['away']}" if a_norm > h_norm and a_norm > d_norm else "משחק שקול")
            
        prob_html = f"""
        <div style='margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 12px;'>
            <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:5px;'>📊 מדד עוצמה ({fav_text})</div>
            <div style='display:flex; width:100%; height:8px; border-radius:4px; overflow:hidden;'>
                <div style='width:{h_norm}%; background-color:#00ff88;'></div>
                <div style='width:{d_norm}%; background-color:#ffd94a;'></div>
                <div style='width:{a_norm}%; background-color:#ff3b5c;'></div>
            </div>
            <div style='display:flex; justify-content:space-between; font-size:0.65rem; color:gray; margin-top:4px;'>
                <span>בית ({int(h_norm)}%)</span>
                <span>תיקו ({int(d_norm)}%)</span>
                <span>חוץ ({int(a_norm)}%)</span>
            </div>
        </div>
        """

    h2h_html = "".join([f"<div style='font-size: 0.85rem; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); color:#e8f4f8;'>{m}</div>" for m in deep_data["h2h_matches"]])
    if not h2h_html: h2h_html = "<span style='color:gray;'>אין מפגשים קודמים קרובים.</span>"
    
    st.markdown(f"""
        <div class='data-box'>
            <h4>יחסי זכייה (Odds)</h4>
            <b>1:</b> {deep_data['odds'].get('1', '-')} &nbsp;|&nbsp; 
            <b>X:</b> {deep_data['odds'].get('X', '-')} &nbsp;|&nbsp; 
            <b>2:</b> {deep_data['odds'].get('2', '-')}
            {prob_html}
        </div>
        
        <div class='data-box'>
            <h4>כושר נוכחי ומאזן שערים (5 משחקים אחרונים)</h4>
            <div style='display:flex; justify-content:space-between; margin-bottom:12px; background:rgba(0,0,0,0.2); padding:10px; border-radius:6px;'>
                <div style='text-align:right;'>
                    <div style='font-size:0.75rem; color:gray; margin-bottom:4px;'>{selected_game['home']} (כללי)</div>
                    {render_form_badges(deep_data['home_form'])}
                    <div style='font-size:0.7rem; color:#00f0ff; margin-top:6px;'>⚽ זכות: {deep_data['home_goals'][0]} | 🥅 חובה: {deep_data['home_goals'][1]}</div>
                </div>
                <div style='text-align:left;'>
                    <div style='font-size:0.75rem; color:gray; margin-bottom:4px;'>{selected_game['away']} (כללי)</div>
                    {render_form_badges(deep_data['away_form'])}
                    <div style='font-size:0.7rem; color:#00f0ff; margin-top:6px;'>⚽ זכות: {deep_data['away_goals'][0]} | 🥅 חובה: {deep_data['away_goals'][1]}</div>
                </div>
            </div>
            <div style='display:flex; justify-content:space-between; padding:0 10px;'>
                <div style='text-align:right;'>
                    <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:4px;'>{selected_game['home']} (בבית)</div>
                    {render_form_badges(deep_data['home_home_form'])}
                </div>
                <div style='text-align:left;'>
                    <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:4px;'>{selected_game['away']} (בחוץ)</div>
                    {render_form_badges(deep_data['away_away_form'])}
                </div>
            </div>
        </div>

        <div class='data-box'>
            <h4>⚔️ היסטוריית מפגשים (H2H - אחרונים)</h4>
            {h2h_html}
        </div>
        
        <div class='data-box'>
            <h4>🚑 פצועים / הרכבים חסרים</h4>
            <div style='display:flex; justify-content:space-between; gap: 15px;'>
                <div style='text-align:right; flex:1;'>
                    <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:4px; font-weight:bold;'>{selected_game['home']}</div>
                    <span style='color:#ff3b5c; font-size:0.8rem; line-height:1.4;'>{deep_data['missing_home']}</span>
                </div>
                <div style='text-align:left; flex:1;'>
                    <div style='font-size:0.75rem; color:#00f0ff; margin-bottom:4px; font-weight:bold;'>{selected_game['away']}</div>
                    <span style='color:#ff3b5c; font-size:0.8rem; line-height:1.4;'>{deep_data['missing_away']}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_ai:
    st.markdown("### 🧠 מנוע AI (Gemini 1.5 Flash)")
    game_id_str = str(selected_game['id'])
    
    if game_id_str in st.session_state.ai_results:
        st.success("ניתוח מהזיכרון:")
        st.write(st.session_state.ai_results[game_id_str])
        if st.button("🔄 רענן ניתוח AI מחדש"):
            del st.session_state.ai_results[game_id_str]
            st.rerun()
    else:
        st.info("ה-AI ממתין לפקודה לניתוח הנתונים המלאים.")
        if st.button("הפעל ניתוח AI עמוק ⚡"):
            with st.spinner("מעבד היסטוריה, שערי זכות/חובה, ופצועים..."):
                result = ai.analyze_match(sport_choice, selected_game, deep_data, GEMINI_API_KEY)
                st.session_state.ai_results[game_id_str] = result
                st.rerun()
