# Version History

## v3.0.0 - Production Release (March 6, 2026)

### Features
✅ Real-time odds from SofaScore API
✅ AI analysis with Google Gemini
✅ Head-to-head history (last 10 matches)
✅ Team statistics and form analysis
✅ Injury/missing players reports
✅ Hebrew RTL support
✅ Israel timezone support (UTC+2/+3)
✅ 4 interactive tabs (Data, H2H, AI, Stats)

### Fixes in v3.0.0
✅ Fixed Gemini model (changed from gemini-1.5-flash to gemini-pro)
✅ Fixed Odds display (changed from HTML to Streamlit components)
✅ Fixed missing players display (added color indicators)
✅ Fixed game list clarity (improved formatting)
✅ Fixed file naming (renamed simulation engine.py)

### Testing
✅ 11/11 simulation tests passing
✅ All syntax validation passing
✅ UI tested on multiple screens
✅ API integration verified

### Known Limitations
- Games limited to major leagues
- Cache duration: 30 minutes
- SofaScore rate limit: 30 req/min
- Gemini rate limit: 60 req/min

## Future Roadmap

### v3.1 (Planned)
- Betfair API integration
- Multiple odds sources
- Historical data tracking
- Performance analytics

### v4.0 (Future)
- Mobile app
- Machine learning predictions
- Telegram bot
- Email alerts
- Docker support
