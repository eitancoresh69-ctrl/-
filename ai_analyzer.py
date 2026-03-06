import google.generativeai as genai

def format_form_string(form_list):
    if not form_list:
        return "אין נתונים"
    return "".join([item[0] for item in form_list[:10]])

def analyze_match(sport, game_info, deep_data, GEMINI_API_KEY):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # תיקון: שימוש במודל החדש והנתמך של גוגל
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        h2h_text = ""
        if deep_data.get('h2h_matches'):
            h2h_text = "\n".join([
                f"📅 {m['date']}: {m['home']} {m['home_score']}-{m['away_score']} {m['away']} ({m['result']})"
                for m in deep_data['h2h_matches'][:5]
            ])
        else:
            h2h_text = "אין מפגשים קודמים מתועדים"
        
        h2h_summary = deep_data.get('h2h_summary', {})
        h2h_stats = f"""
        סה"כ משחקים: {h2h_summary.get('total', 0)}
        ניצחונות בית: {h2h_summary.get('home_wins', 0)} | תיקו: {h2h_summary.get('draws', 0)} | ניצחונות חוץ: {h2h_summary.get('away_wins', 0)}
        שערים (בית/חוץ): {h2h_summary.get('home_goals', 0)}/{h2h_summary.get('away_goals', 0)}
        """ if h2h_summary.get('total', 0) > 0 else "אין מפגשים קודמים"
        
        home_stats = deep_data.get('home_stats', {})
        away_stats = deep_data.get('away_stats', {})
        
        home_form_str = format_form_string(home_stats.get('form', []))
        away_form_str = format_form_string(away_stats.get('form', []))
        home_home_form = format_form_string(home_stats.get('home_form', []))
        away_away_form = format_form_string(away_stats.get('away_form', []))
        
        missing_home = ", ".join(deep_data.get('missing_home', ['סגל מלא'])) if deep_data.get('missing_home') else "סגל מלא"
        missing_away = ", ".join(deep_data.get('missing_away', ['סגל מלא'])) if deep_data.get('missing_away') else "סגל מלא"
        
        odds = deep_data.get('odds', {})
        
        prompt = f"""
אתה אנליסט ספורט מנוסה. נתח את המשחק בעברית:
ספורט: {sport}
משחק: {game_info['home']} נגד {game_info['away']} (ליגה: {game_info['league']})

יחסים (Odds):
1: {odds.get('1', 'N/A')} | X: {odds.get('X', 'N/A')} | 2: {odds.get('2', 'N/A')}
Over 2.5: {odds.get('over_2_5', 'N/A')} | Under 2.5: {odds.get('under_2_5', 'N/A')}

סטטיסטיקת בית ({game_info['home']}):
כושר: {home_form_str} | Win Rate: {home_stats.get('win_rate', 0):.1f}%

סטטיסטיקת חוץ ({game_info['away']}):
כושר: {away_form_str} | Win Rate: {away_stats.get('win_rate', 0):.1f}%

H2H:
{h2h_stats}

חסרים:
בית: {missing_home}
חוץ: {missing_away}

תן סיכום קצר, ניתוח יחסי כוחות, 2 המלצות להימור עם ערך (Value Bets), ורמת ביטחון.
"""
        response = model.generate_content(prompt, stream=False)
        return response.text
    
    except Exception as e:
        return f"❌ שגיאה בעיבוד ה-AI: {str(e)}"
