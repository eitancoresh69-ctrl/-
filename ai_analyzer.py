import google.generativeai as genai

def analyze_match(sport, game_info, deep_data, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    h2h_text = ", ".join(deep_data['h2h_matches']) if deep_data['h2h_matches'] else "אין מפגשים היסטוריים מתועדים לאחרונה."
    
    home_form = [x[0] for x in deep_data['home_form']]
    away_form = [x[0] for x in deep_data['away_form']]
    home_home_form = [x[0] for x in deep_data['home_home_form']]
    away_away_form = [x[0] for x in deep_data['away_away_form']]
    
    prompt = f"""
    אתה אנליסט ספורט ומומחה באיתור Value Bets. נתח את המשחק הבא:
    ספורט: {sport}
    משחק: {game_info['home']} נגד {game_info['away']} (ליגה: {game_info['league']})
    יחסים (Odds): {deep_data['odds']}
    
    נתוני כושר נוכחי מ-5 המשחקים האחרונים (נ=ניצחון, ת=תיקו, ה=הפסד):
    כושר כללי קבוצת בית ({game_info['home']}): {home_form}
    כושר בבית בלבד קבוצת בית: {home_home_form}
    כושר כללי קבוצת חוץ ({game_info['away']}): {away_form}
    כושר בחוץ בלבד קבוצת חוץ: {away_away_form}
    
    היסטוריית מפגשים ישירים (H2H):
    {h2h_text}
    
    פצועים/חסרים: {deep_data['missing_players']}
    
    אנא ספק בעברית:
    1. ניתוח יחסי הכוחות על בסיס הכושר הנוכחי ומפגשי העבר.
    2. ניתוח הערך (Value) ביחסים המוצעים.
    3. שורת מחץ: המלצת הימור פרקטית המבוססת על הנתונים.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה בהפקת ניתוח ה-AI: {e}"
