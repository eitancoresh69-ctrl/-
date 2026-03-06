# 🚀 SportIQ ULTRA v3.0.0

**Advanced Sports Analytics & AI-Powered Betting Analysis**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)

---

## ✨ Features

### 📊 Data Analysis
- **Live Odds** - Real-time betting odds from SofaScore
- **Team Statistics** - Win rates, goal averages, form analysis
- **Head-to-Head** - Historical matchups (last 10 games)
- **Injury Reports** - Missing players and unavailable squads

### 🧠 AI Analysis
- **Gemini Integration** - Google's advanced AI model
- **Value Betting** - Identify profitable betting opportunities
- **Probability Analysis** - Accurate match probability calculations
- **Kelly Criterion** - Optimal staking recommendations

### 🎯 User Interface
- **4 Interactive Tabs** - Data, H2H, AI, Statistics
- **Hebrew RTL Support** - Full right-to-left language support
- **Dark Theme** - Modern design with cyan/green/red accents
- **Date Range Picker** - Easy game filtering

### 🇮🇱 Israel-Specific
- **Correct Timezone** - UTC+2/+3 with DST detection
- **Hebrew Labels** - All UI in Hebrew
- **Israel Leagues** - Support for local football leagues

---

## 🚀 Quick Start

### Requirements
- Python 3.8 or higher
- pip package manager
- Internet connection
- Free Gemini API key

### Installation

```bash
# 1. Clone or download the repository
git clone https://github.com/yourusername/SportIQ-ULTRA.git
cd SportIQ-ULTRA

# 2. Install dependencies
pip install -r requirements.txt

# 3. Get Gemini API key
# Visit: https://makersuite.google.com/app/apikey

# 4. Create configuration
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "your-api-key-here"' > .streamlit/secrets.toml

# 5. Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📋 Files Overview

### Core Application
- **app.py** - Main Streamlit interface with 4 tabs
- **api_sofascore.py** - SofaScore API integration
- **ai_analyzer.py** - Gemini AI analysis engine
- **simulation_engine.py** - Test suite (11/11 tests passing)

### Configuration
- **requirements.txt** - Python dependencies
- **.streamlit/secrets.toml** - API credentials (create manually)

---

## 🔧 Configuration

### Gemini API Setup

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the generated key
4. Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key-here"
```

---

## 🎓 Features Detail

### Tab 1: 📊 Data
- Live betting odds (1x2, Over/Under 2.5)
- Recent form badges (W/D/L)
- Goal statistics
- Team-specific metrics

### Tab 2: ⚔️ H2H
- Last 10 head-to-head matches
- Historical results
- Win/Draw/Loss summary
- Trend analysis

### Tab 3: 🧠 AI Analysis
- Detailed Gemini-powered insights
- Value betting opportunities
- Confidence levels
- Risk assessment

### Tab 4: 📈 Statistics
- Team performance metrics
- Home/Away split statistics
- Win rate calculations
- Goal averages

---

## 🧪 Testing

Run the simulation engine to validate all components:

```bash
python simulation_engine.py
```

Expected output: **11/11 tests PASS ✅**

---

## 🌍 Supported Leagues

- **Football**: Premier League, LaLiga, Serie A, Bundesliga, Ligue 1, Champions League
- **Basketball**: NBA, EuroLeague, Israeli leagues
- **Local**: Israeli Ligat HaAl

---

## ⚠️ Important Notes

1. **API Rate Limiting**: 30 requests/minute on SofaScore, 60/minute on Gemini
2. **First Load**: May take 2-3 seconds for data fetching
3. **Timezone**: Automatically detects Israel DST
4. **Hebrew Support**: Full RTL support for all text

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "No games found"
- Check internet connection
- Verify date range selection
- Ensure selected sport has games

### "Gemini API Error"
- Verify API key in `.streamlit/secrets.toml`
- Check if API is enabled in Google Cloud Console
- Confirm you have API credits

### "Wrong timezone"
- System automatically detects Israel timezone (UTC+2/+3)
- DST handled automatically March-October

---

## 📊 Recent Updates (v3.0.0)

✅ **Fixed Issues:**
- Gemini model updated to `gemini-pro` (was invalid `gemini-1.5-flash`)
- Game list display improved with better spacing
- Injury report display enhanced (red for injuries, green for full squad)
- File naming corrected (simulation_engine.py)

✅ **Testing:**
- All 11 simulation tests passing
- Syntax validation complete
- Production-ready

---

## 📈 Performance

- **Load Time**: 2-3 seconds (first load with API calls)
- **Cache Duration**: 30 minutes
- **Model Size**: ~26 KB (app.py) + supporting modules
- **Memory**: ~150-200 MB when running

---

## 🔐 Security

- All API calls encrypted (HTTPS)
- No personal data stored
- API keys stored locally only
- Cache cleared every 30 minutes

---

## 📞 Support & Contributing

- Report issues on GitHub Issues
- Contribute via Pull Requests
- Check existing issues first

---

## 📄 License

MIT License - Feel free to use and modify

---

## 🎉 Credits

- **SofaScore API** - Sports data
- **Google Gemini** - AI analysis
- **Streamlit** - Web framework
- **Community** - Testing and feedback

---

**Made with ❤️ for Sports Analytics**

v3.0.0 | March 6, 2026 | Production Ready ✅
