import streamlit as st
import api_sofascore as sofascore
import ai_analyzer
import os
from datetime import datetime

st.set_page_config(page_title="SportIQ ULTRA v2", layout="wide")

if 'ai_results' not in st.session_state:
    st.session_state.ai_results = {}

st.title("SportIQ ULTRA v2")
st.write("Advanced Sports Analytics")
st.divider()

rapid_api_key = os.environ.get("RAPID_API_KEY") or st.secrets.get("RAPID_API_KEY", "")

with st.spinner("Loading games..."):
    games_dict = sofascore.fetch_games(days=5)

if not games_dict:
    st.error("No games found")
    st.stop()

dates = sorted(list(games_dict.keys()))
date_display = {datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m"): d for d in dates}

selected_date = st.selectbox("Select date:", options=list(date_display.keys()))
selected_date_str = date_display[selected_date]
daily_games = games_dict[selected_date_str]

with st.sidebar:
    st.header("Select Game")
    
    search = st.text_input("Search team...")
    if search:
        daily_games = [g for g in daily_games if search.lower() in g['home'].lower() or search.lower() in g['away'].lower()]
    
    if not daily_games:
        st.warning("No games found")
        st.stop()
    
    game_labels = [f"{g['time']} | {g['home']} vs {g['away']}" for g in daily_games]
    selected_idx = st.radio("Games:", range(len(game_labels)), format_func=lambda x: game_labels[x], label_visibility="collapsed")
    selected_game = daily_games[selected_idx]

with st.spinner("Loading data..."):
    game_data = sofascore.get_game_data(
        selected_game['id'],
        selected_game['home_id'],
        selected_game['away_id']
    )

st.markdown(f"### {selected_game['home']} vs {selected_game['away']}")
st.write(f"{selected_game['time']} | {selected_game['league']}")
st.divider()

tab1, tab2, tab3 = st.tabs(["Data", "H2H", "AI Analysis"])

with tab1:
    st.subheader("Betting Odds")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Home (1)", game_data['odds'].get('1', '-'))
    col2.metric("Draw (X)", game_data['odds'].get('X', '-'))
    col3.metric("Away (2)", game_data['odds'].get('2', '-'))
    
    st.divider()
    
    st.subheader("Recent Form")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{selected_game['home']}**")
        form_home = game_data['home_stats']['form']
        if form_home:
            form_text = " ".join([res for res, _ in form_home])
            st.write(form_text)
    
    with col2:
        st.write(f"**{selected_game['away']}**")
        form_away = game_data['away_stats']['form']
        if form_away:
            form_text = " ".join([res for res, _ in form_away])
            st.write(form_text)
    
    st.divider()
    
    st.subheader("Missing Players")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**{selected_game['home']}**")
        for p in game_data['missing'].get('home', []):
            if p == "סגל מלא":
                st.success(p)
            else:
                st.warning(f"Injured: {p}")
    
    with col2:
        st.write(f"**{selected_game['away']}**")
        for p in game_data['missing'].get('away', []):
            if p == "סגל מלא":
                st.success(p)
            else:
                st.warning(f"Injured: {p}")

with tab2:
    st.subheader("Head-to-Head")
    h2h = game_data['h2h']['summary']
    
    if h2h.get('total', 0) > 0:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", h2h['total'])
        col2.metric("Home Wins", h2h['home_wins'])
        col3.metric("Draws", h2h['draws'])
        col4.metric("Away Wins", h2h['away_wins'])
        
        st.divider()
        
        for match in game_data['h2h']['matches']:
            st.info(f"{match['date']}: {match['home']} {match['home_score']}-{match['away_score']} {match['away']}")
    else:
        st.info("No head-to-head data available")

with tab3:
    st.subheader("AI Analysis")
    
    groq_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    
    if not groq_key:
        st.error("GROQ_API_KEY not configured")
    else:
        game_id = str(selected_game['id'])
        
        if game_id in st.session_state.ai_results:
            st.success("Analysis completed")
            st.write(st.session_state.ai_results[game_id])
            
            if st.button("New Analysis"):
                del st.session_state.ai_results[game_id]
                st.rerun()
        else:
            if st.button("Run AI Analysis", use_container_width=True):
                with st.spinner("Analyzing..."):
                    result = ai_analyzer.analyze_match(selected_game, game_data, groq_key)
                    st.session_state.ai_results[game_id] = result
                    st.rerun()

st.divider()
st.caption("SportIQ ULTRA v2 | Data from SofaScore")
