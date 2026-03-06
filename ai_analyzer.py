import google.generativeai as genai

def analyze_match(sport, game_info, deep_data, api_key):
    genai.configure(api_key=api_key)
    # שימוש במודל החדש והיציב שפותר את השגיאה
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    h2h_text = "\n".join(deep_data['h2h_matches']) if deep_data['h2h_matches'] else "אין מפגשים היסטוריים מתועדים לאחרונה ב-SofaScore."
    
    home_form = [x[0] for x in deep_data['home_form']]
    away_form = [x[0] for x in deep_data['away_form']]
    
    prompt = f"""
    אתה אנליסט ספורט ומומחה באיתור Value Bets. נתח את המשחק הבא:
    ספורט: {sport}
    משחק: {game_info['home']} נגד {game_info['away']} (ליגה: {game_info['league']})
    יחסים (Odds): {deep_data['odds']}
    
    נתוני כושר (נ=ניצחון, ת=תיקו, ה=הפסד):
    כושר {game_info['home']}: {home_form} | שערי זכות: {deep_data['home_goals'][0]}, שערי חובה: {deep_data['home_goals'][1]}
    כושר {game_info['away']}: {away_form} | שערי זכות: {deep_data['away_goals'][0]}, שערי חובה: {deep_data['away_goals'][1]}
    
    היסטוריית מפגשים (H2H):
    {h2h_text}
    
    פצועים ונעדרים (עם עמדות):
    שחקנים חסרים ב-{game_info['home']}: {deep_data['missing_home']}
    שחקנים חסרים ב-{game_info['away']}: {deep_data['missing_away']}
    
    אנא ספק בעברית:
    1. ניתוח יחסי הכוחות על בסיס הכושר, מפגשי העבר, ומאזן השערים.
    2. השפעת הפצועים והעמדות החסרות על המשחק.
    3. ניתוח הערך (Value) ביחסים המוצעים (למשל האם היחס על הבית משתלם).
    4. המלצת הימור פרקטית וחותכת (מי תנצח או Over/Under שערים).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה בהפקת ניתוח ה-AI. ודא שהמפתח תקין. פרטים: {e}"
