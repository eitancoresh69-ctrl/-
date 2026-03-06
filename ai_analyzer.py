import google.generativeai as genai
import streamlit as st

def analyze_match(sport, game_info, deep_data, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    אתה אנליסט ספורט ומומחה באיתור Value Bets. נתח את המשחק הבא:
    ספורט: {sport}
    משחק: {game_info['home']} נגד {game_info['away']} (ליגה: {game_info['league']})
    יחסים (Odds): {deep_data['odds']}
    היסטוריית H2H: {deep_data['h2h']}
    פצועים/חסרים: {deep_data['missing_players']}
    סטטיסטיקות (אם קיימות): {deep_data['stats']}
    
    אנא ספק בעברית:
    1. ניתוח מצב הקבוצות (הפתעות אפשריות, השפעת הפצועים).
    2. ניתוח היחסים (האם יש כאן Value?).
    3. שורת מחץ: המלצת הימור פרקטית (או המלצה להתרחק).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה בהפקת ניתוח ה-AI: {e}"
