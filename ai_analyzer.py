import google.generativeai as genai

def format_form_string(form_list):
    if not form_list: return "אין נתונים"
    return "".join([item[0] for item in form_list[:10]])

def analyze_match(sport, game_info, deep_data, GEMINI_API_KEY):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        h2h_summary = deep_data.get('h2h_summary', {})
        h2h_stats = f"סה'כ: {h2h_summary.get('total',0)} | נצ' בית: {h2h_summary.get('home_wins',0)} | נצ' חוץ: {h2h_summary.get('away_wins',0)} | תיקו: {h2h_summary.get('draws',0)}"
        
        home_stats, away_stats = deep_data.get('home_stats', {}), deep_data.get('away_stats', {})
        home_form = format_form_string(home_stats.get('form', []))
        away_form = format_form_string(away_stats.get('form', []))
        odds = deep_data.get('odds', {})
        
        prompt = f"""
אתה אנליסט ספורט מנוסה. נתח בעברית:
{game_info['home']} נגד {game_info['away']} ({game_info['league']})

יחסים: 1: {odds.get('1')} | X: {odds.get('X')} | 2: {odds.get('2')}
בית ({game_info['home']}): כושר: {home_form} | Win Rate: {home_stats.get('win_rate', 0):.1f}%
חוץ ({game_info['away']}): כושר: {away_form} | Win Rate: {away_stats.get('win_rate', 0):.1f}%
H2H: {h2h_stats}

תן סיכום קצר, ניתוח כוחות, והמלצת Value Bet ברורה עם רמת ביטחון.
"""
        response = model.generate_content(prompt, stream=False)
        return response.text
    except Exception as e:
        return f"❌ שגיאה ב-AI: {str(e)}"
