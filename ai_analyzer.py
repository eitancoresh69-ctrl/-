import google.generativeai as genai
import json

def format_form_string(form_list):
    """המרת form list לstring קריא"""
    if not form_list:
        return "אין נתונים"
    return "".join([item[0] for item in form_list[:10]])

def analyze_match(sport, game_info, deep_data, GEMINI_API_KEY):
    """
    ניתוח מתקדם של משחק עם Gemini AI
    """
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # עיצוב נתוני H2H
        h2h_text = ""
        if deep_data.get('h2h_matches'):
            h2h_text = "\n".join([
                f"📅 {m['date']}: {m['home']} {m['home_score']}-{m['away_score']} {m['away']} ({m['result']})"
                for m in deep_data['h2h_matches'][:5]
            ])
        else:
            h2h_text = "אין מפגשים קודמים מתועדים"
        
        # עיצוב סטטיסטיקה H2H
        h2h_summary = deep_data.get('h2h_summary', {})
        h2h_stats = f"""
        סה"כ משחקים: {h2h_summary.get('total', 0)}
        ניצחונות בית: {h2h_summary.get('home_wins', 0)} | תיקו: {h2h_summary.get('draws', 0)} | ניצחונות חוץ: {h2h_summary.get('away_wins', 0)}
        שערים (בית/חוץ): {h2h_summary.get('home_goals', 0)}/{h2h_summary.get('away_goals', 0)}
        """ if h2h_summary.get('total', 0) > 0 else "אין מפגשים קודמים"
        
        # סטטיסטיקות בית
        home_stats = deep_data.get('home_stats', {})
        away_stats = deep_data.get('away_stats', {})
        
        home_form_str = format_form_string(home_stats.get('form', []))
        away_form_str = format_form_string(away_stats.get('form', []))
        
        home_home_form = format_form_string(home_stats.get('home_form', []))
        away_away_form = format_form_string(away_stats.get('away_form', []))
        
        # עיצוב נתוני פצועים
        missing_home = ", ".join(deep_data.get('missing_home', ['סגל מלא'])) if deep_data.get('missing_home') else "סגל מלא"
        missing_away = ", ".join(deep_data.get('missing_away', ['סגל מלא'])) if deep_data.get('missing_away') else "סגל מלא"
        
        # יחסים
        odds = deep_data.get('odds', {})
        
        # בניית prompt מפורט
        prompt = f"""
אתה אנליסט ספורט מנוסה, מומחה Value Betting, ו-DFS Strategy. 
נתח את המשחק הבא בעברית עם ממוקד על:
1. ניתוח סטטיסטי מעמיק
2. איתור Value Bets
3. הערכת סיכון

═══════════════════════════════════════════════════════════════════

📊 פרטי המשחק:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ספורט: {sport}
קבוצה בית: {game_info['home']} | קבוצה חוץ: {game_info['away']}
ליגה: {game_info['league']}

═══════════════════════════════════════════════════════════════════

💰 יחסים (Odds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1 (בית): {odds.get('1', 'N/A')}
X (תיקו): {odds.get('X', 'N/A')}
2 (חוץ): {odds.get('2', 'N/A')}
Over 2.5: {odds.get('over_2_5', 'N/A')}
Under 2.5: {odds.get('under_2_5', 'N/A')}

═══════════════════════════════════════════════════════════════════

📈 סטטיסטיקות {game_info['home']} (בית):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
כושר (אחרונים): {home_form_str}
ניצחונות: {home_stats.get('wins', 0)} | תיקו: {home_stats.get('draws', 0)} | הפסדים: {home_stats.get('losses', 0)}
שערים: {home_stats.get('goals_scored', 0)} הבקיע / {home_stats.get('goals_conceded', 0)} קיבל
ממוצע שערים: {home_stats.get('avg_goals_for', 0):.2f} ± {home_stats.get('avg_goals_against', 0):.2f}
Win Rate: {home_stats.get('win_rate', 0):.1f}%
בבית (כושר): {home_home_form}

═══════════════════════════════════════════════════════════════════

📈 סטטיסטיקות {game_info['away']} (חוץ):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
כושר (אחרונים): {away_form_str}
ניצחונות: {away_stats.get('wins', 0)} | תיקו: {away_stats.get('draws', 0)} | הפסדים: {away_stats.get('losses', 0)}
שערים: {away_stats.get('goals_scored', 0)} הבקיע / {away_stats.get('goals_conceded', 0)} קיבל
ממוצע שערים: {away_stats.get('avg_goals_for', 0):.2f} ± {away_stats.get('avg_goals_against', 0):.2f}
Win Rate: {away_stats.get('win_rate', 0):.1f}%
בחוץ (כושר): {away_away_form}

═══════════════════════════════════════════════════════════════════

⚔️ היסטוריית מפגשים (H2H):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{h2h_text}

סטטיסטיקה H2H:
{h2h_stats}

═══════════════════════════════════════════════════════════════════

🚑 שחקנים חסרים / פצועים:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{game_info['home']}: {missing_home}
{game_info['away']}: {missing_away}

═══════════════════════════════════════════════════════════════════

📋 דרישות הניתוח:
1️⃣ ניתוח יחסי הכוחות בהתאם לסטטיסטיקה, כושר נוכחי, ו-H2H
2️⃣ הערכת השפעת הפצועים על כל קבוצה
3️⃣ חישוב הסתברות אפקטיבית לכל תוצאה
4️⃣ זיהוי Value Bets (יחסים שלא משקפים את ההסתברות האמיתית)
5️⃣ ניתוח Over/Under שערים
6️⃣ המלצות הימור אופרטיביות עם Risk/Reward
7️⃣ Confidence Level לכל המלצה (גבוה/בינוני/נמוך)

📌 תן תשובה מובנית בעברית עם:
   • סיכום קצר של הניתוח
   • יחסי הכוחות המדויקים
   • 2-3 Value Bets מומלצות
   • הערות על סיכונים
   • ROI משוער במונחי Staking
"""
        
        # שליחה ל-Gemini
        response = model.generate_content(prompt, stream=False)
        return response.text
    
    except Exception as e:
        return f"❌ שגיאה בעיבוד ה-AI: {str(e)}\n\n💡 טיפ: ודא שה-Gemini API Key תקין ויש לך credits זמינים."

def simulate_predictions(game_data_list, deep_data_list):
    """
    הרץ סימולציות על סדרת משחקים
    """
    results = {
        "total_games": len(game_data_list),
        "simulations": [],
        "accuracy": 0,
        "roi": 0,
        "avg_confidence": 0
    }
    
    try:
        # כאן יכול להיות logic סימולציה יותר מעמיק
        pass
    except:
        pass
    
    return results
