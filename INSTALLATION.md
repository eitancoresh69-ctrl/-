# 🚀 Installation Guide - SportIQ ULTRA

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection
- Google Gemini API key (free)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/SportIQ-ULTRA.git
cd SportIQ-ULTRA
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed streamlit google-generativeai requests pandas python-dateutil
```

### 4. Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the generated key

### 5. Configure Secrets

Create directory and file:

```bash
mkdir -p .streamlit
```

Create file: `.streamlit/secrets.toml`

Add this line:
```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
```

Replace `your-gemini-api-key-here` with your actual key.

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open at: `http://localhost:8501`

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'streamlit'"

Solution:
```bash
pip install -r requirements.txt --upgrade
```

### Error: "Gemini API Error"

Check:
1. API key is correct in `.streamlit/secrets.toml`
2. You have API credits available
3. Internet connection is working

### Error: "No games found"

Check:
1. Internet connection
2. SofaScore API is working
3. Try different date range

## Uninstallation

To remove the virtual environment:

```bash
# Deactivate first
deactivate

# Remove venv folder
rm -rf venv  # Linux/macOS
rmdir venv   # Windows
```

## Next Steps

See README.md for feature documentation and usage instructions.
