# ⚡ Quick Start - SportIQ ULTRA

**Get started in 5 minutes!**

## 1. Clone Repository
```bash
git clone https://github.com/yourusername/SportIQ-ULTRA.git
cd SportIQ-ULTRA
```

## 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. Configure API Key
```bash
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "your-api-key"' > .streamlit/secrets.toml
```

Get free API key: https://makersuite.google.com/app/apikey

## 4. Run Application
```bash
streamlit run app.py
```

## 5. Open Browser
Visit: `http://localhost:8501`

## That's It! 🎉

You now have:
- 📊 Live sports odds
- 🧠 AI-powered analysis
- ⚔️ Head-to-head history
- 📈 Team statistics
- 🚑 Injury reports

## Features by Tab

**📊 Data Tab**
- Real-time odds (1x2, Over/Under)
- Team form (last 5 games)
- Goal statistics

**⚔️ H2H Tab**
- Last 10 head-to-head matches
- Win/Draw/Loss summary
- Score comparisons

**🧠 AI Tab**
- Gemini-powered analysis
- Value betting detection
- Confidence levels

**📈 Stats Tab**
- Detailed team metrics
- Home/Away splits
- Win rate analysis

## Support
See README.md for full documentation
See INSTALLATION.md for detailed setup

## Tips
- Change date range in sidebar to find games
- AI analysis takes 2-3 seconds
- Data updates every 30 minutes (cache)
- Works best with Chrome or Firefox

Enjoy! 🚀
