import os
from groq import Groq

def format_form_string(form_list):
    if not form_list: return "אין נתונים"
    return "".join([item[0] for item in form_list[:10]])

def analyze_match(sport, game_info, deep_data, api_key, ai_provider):
    h2h_summary = deep_data.get('h2h_summary', {})
    h2h_stats = f"סה״כ: {h2h_summary.get('total',0)} | נצ׳ בית: {h2h_summary.get('home_wins',0)} | נצ׳ חוץ: {h2h_summary.get('away_wins',0)} | תיקו: {h2h_summary.get('draws',0)}"
    
    home_stats, away_stats = deep_data.get('home_stats', {}), deep_data.get('away_stats', {})
    home_form = format_form_string(home_stats.get('form', []))
    away_form = format_form_string(away_stats.get('form', []))
    odds = deep_data.get('odds', {})
    
    missing_h = ", ".join(deep_data.get('missing_home', ['לא ידוע']))
    missing_a = ", ".join(deep_data.get('missing_away', ['לא ידוע']))
    
    prompt = f"""
אתה אנליסט ספורט מנוסה. נתח בעברית:
{game_info['home']} נגד {game_info['away']} ({game_info['league']})

יחסים: 1: {odds.get('1')} | X: {odds.get('X')} | 2: {odds.get('2')}
בית ({game_info['home']}): כושר: {home_form} | Win Rate: {home_stats.get('win_rate', 0):.1f}% | פצועים: {missing_h}
חוץ ({game_info['away']}): כושר: {away_form} | Win Rate: {away_stats.get('win_rate', 0):.1f}% | פצועים: {missing_a}
H2H: {h2h_stats}

תן סיכום קצר, השפעת הפצועים, והמלצת Value Bet ברורה עם רמת ביטחון.
"""

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
            
    except Exception as e:
        return f"Error in Groq AI: {str(e)}\n\nMake sure you added GROQ_API_KEY in Secrets."
