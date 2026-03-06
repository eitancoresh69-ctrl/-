import requests
import streamlit as st
import os

# RapidAPI Endpoints
RAPIDAPI_HOST = "free-api-live-football-data.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"

def get_rapidapi_headers(api_key):
    """Get RapidAPI headers with your API key"""
    return {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

@st.cache_data(ttl=3600)
def get_league_standings(league_name, api_key):
    """Get league standings from RapidAPI"""
    try:
        url = f"{RAPIDAPI_BASE_URL}/standings"
        params = {"league": league_name}
        headers = get_rapidapi_headers(api_key)
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            standings = []
            
            # Parse standings data
            if 'response' in data:
                for item in data['response']:
                    if 'league' in item and 'standings' in item:
                        for table in item['standings']:
                            for team in table:
                                standings.append({
                                    'position': team.get('rank'),
                                    'team': team.get('team', {}).get('name'),
                                    'played': team.get('all', {}).get('played', 0),
                                    'won': team.get('all', {}).get('win', 0),
                                    'draw': team.get('all', {}).get('draw', 0),
                                    'lost': team.get('all', {}).get('lose', 0),
                                    'points': team.get('points', 0),
                                    'goals_for': team.get('all', {}).get('goals', {}).get('for', 0),
                                    'goals_against': team.get('all', {}).get('goals', {}).get('against', 0),
                                    'goal_diff': team.get('goalsDiff', 0)
                                })
            
            return standings
        else:
            st.warning(f"❌ API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching standings: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_h2h_matches(home_team, away_team, api_key):
    """Get head-to-head history from RapidAPI"""
    try:
        url = f"{RAPIDAPI_BASE_URL}/fixtures"
        params = {
            "h2h": f"{home_team}-{away_team}",
            "last": "10"
        }
        headers = get_rapidapi_headers(api_key)
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            matches = []
            
            # Parse H2H matches
            if 'response' in data:
                for match in data['response'][:10]:  # Last 10 matches
                    home = match.get('teams', {}).get('home', {}).get('name', '')
                    away = match.get('teams', {}).get('away', {}).get('name', '')
                    home_score = match.get('goals', {}).get('home')
                    away_score = match.get('goals', {}).get('away')
                    date = match.get('fixture', {}).get('date', '')
                    
                    # Determine result
                    if home_score is not None and away_score is not None:
                        if home_score > away_score:
                            result = f"ניצחון {home}"
                        elif away_score > home_score:
                            result = f"ניצחון {away}"
                        else:
                            result = "תיקו"
                        
                        matches.append({
                            'date': date.split('T')[0] if 'T' in date else date,
                            'home': home,
                            'away': away,
                            'home_score': home_score,
                            'away_score': away_score,
                            'result': result
                        })
            
            return matches
        else:
            st.warning(f"❌ API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching H2H: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_game_odds(home_team, away_team, api_key):
    """Get odds for a specific match from RapidAPI"""
    try:
        url = f"{RAPIDAPI_BASE_URL}/odds"
        params = {
            "league": "premier_league",
            "season": "2024"
        }
        headers = get_rapidapi_headers(api_key)
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            odds_data = {
                '1': 'לא זמין',
                'X': 'לא זמין',
                '2': 'לא זמין',
                'over_2_5': '-',
                'under_2_5': '-'
            }
            
            # Parse odds data
            if 'response' in data:
                for item in data['response']:
                    h = item.get('teams', {}).get('home', {}).get('name', '').lower()
                    a = item.get('teams', {}).get('away', {}).get('name', '').lower()
                    
                    if home_team.lower() in h and away_team.lower() in a:
                        # Extract odds if available
                        odds = item.get('odds')
                        if odds:
                            odds_data['1'] = odds.get('1x2', {}).get('home', 'לא זמין')
                            odds_data['X'] = odds.get('1x2', {}).get('draw', 'לא זמין')
                            odds_data['2'] = odds.get('1x2', {}).get('away', 'לא זמין')
                        break
            
            return odds_data
        else:
            return {
                '1': 'לא זמין',
                'X': 'לא זמין',
                '2': 'לא זמין',
                'over_2_5': '-',
                'under_2_5': '-'
            }
    except Exception as e:
        st.error(f"Error fetching odds: {str(e)}")
        return {
            '1': 'לא זמין',
            'X': 'לא זמין',
            '2': 'לא זמין',
            'over_2_5': '-',
            'under_2_5': '-'
        }

def get_team_league_position(team_name, league_standings):
    """Find team position in league standings"""
    if not league_standings:
        return None
    
    for team in league_standings:
        if team_name.lower() in team.get('team', '').lower():
            return team
    
    return None
