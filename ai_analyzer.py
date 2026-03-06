import google.generativeai as genai

def analyze_match(sport, game_info, deep_data, api_key):
    genai.configure(api_key=api_key)
    # שימוש ב- gemini-pro פותר את שגיאת 404 ומבטיח יציבות בכל מפתח
    model = genai.GenerativeModel('gemini-pro')
    
    h2h_text = "\n".join(deep_data['h2h_matches']) if deep_data['h2h_matches'] else "אין מפגשים היסטוריים מתועדים לאחרונה."
    
    home_form = [x[0] for x in deep_data['home_form']]
    away_form = [x[0] for x in deep_data['away_form']]
    home_home_form = [x[0] for x in deep_data['home_home_form']]
    away_away_form = [x[0] for x in deep_data['away_away_form']]
    
    prompt = f"""
    אתה אנליסט ספורט ומומחה באיתור Value Bets. נתח את המשחק הבא:
    ספורט: {sport}
    משחק: {game_info['home']} נגד {game_info['away']} (ליגה: {game_info['league']})
    יחסים (Odds): {deep_data['odds']}
    
    נתוני כושר (נ=ניצחון, ת=תיקו, ה=הפסד):
    כושר כללי קבוצת בית ({game_info['home']}): {home_form}
    כושר בית בלבד: {home_home_form}
    כושר כללי קבוצת חוץ ({game_info['away']}): {away_form}
    כושר חוץ בלבד: {away_away_form}
    
    היסטוריית מפגשים (H2H):
    {h2h_text}
    
    פצועים ונעדרים (עם עמדות):
    שחקנים חסרים ב-{game_info['home']}: {deep_data['missing_home']}
    שחקנים חסרים ב-{game_info['away']}: {deep_data['missing_away']}
    
    אנא ספק בעברית:
    1. ניתוח יחסי הכוחות על בסיס הכושר הנוכחי, מפגשי העבר, והשפעת החיסורים הספציפיים (לפי העמדות שצוינו).
    2. ניתוח הערך (Value) ביחסים המוצעים.
    3. שורת מחץ: המלצת הימור פרקטית המבוססת על הנתונים.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה בהפקת ניתוח ה-AI. ודא שהמפתח תקין. פרטים: {e}"
