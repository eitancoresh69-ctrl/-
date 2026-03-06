from groq import Groq

def analyze_match(game_info, game_data, api_key):
    try:
        client = Groq(api_key=api_key)
        
        prompt = f"""
ניתוח משחק כדורגל:
{game_info.get('home', '')} vs {game_info.get('away', '')}

יחסים: 1={game_data['odds'].get('1', '-')}, X={game_data['odds'].get('X', '-')}, 2={game_data['odds'].get('2', '-')}

בצע ניתוח קצר וממוקד בעברית.
"""
        
        message = client.messages.create(
            model="mixtral-8x7b-32768",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    except Exception as e:
        return f"שגיאה בניתוח: {str(e)}"
