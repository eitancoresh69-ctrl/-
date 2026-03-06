# SportIQ ULTRA v2

Advanced Sports Analytics with AI Analysis

## Features

- Live betting odds
- Head-to-head history
- Team statistics
- AI analysis with Groq
- Missing players/injuries

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Create `.streamlit/secrets.toml`:

```toml
RAPID_API_KEY = "your_key"
GROQ_API_KEY = "your_groq_key"
```

## Requirements

- Python 3.8+
- Streamlit
- Groq API key (free)
- RapidAPI key (free)
