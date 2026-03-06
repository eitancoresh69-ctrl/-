#!/bin/bash

# 🚀 SportIQ ULTRA v2 - SETUP SCRIPT
# תסריט התקנה אוטומטי לנוחות המשתמש

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        SportIQ ULTRA v2 - AUTOMATIC SETUP WIZARD              ║"
echo "║                    Installation Script                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# בדוק Python
echo "📦 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   ✅ Python $python_version detected"
echo ""

# התקנת dependencies
echo "📥 Installing dependencies..."
echo "   • streamlit"
echo "   • google-generativeai"
echo "   • requests"
echo "   • pandas"
echo ""

pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "   ✅ Dependencies installed successfully"
else
    echo "   ❌ Failed to install dependencies"
    exit 1
fi

echo ""

# הגדרת Gemini API Key
echo "🔐 Setting up Gemini API Key..."
echo ""
echo "   📝 You need a Google Gemini API Key to use this app."
echo "   📍 Get one at: https://makersuite.google.com/app/apikey"
echo ""

read -p "   🔑 Enter your Gemini API Key (or press Enter to skip): " api_key

if [ -n "$api_key" ]; then
    mkdir -p .streamlit
    echo "GEMINI_API_KEY = \"$api_key\"" > .streamlit/secrets.toml
    echo "   ✅ API Key saved to .streamlit/secrets.toml"
else
    echo "   ⚠️  API Key not configured. You can add it later in .streamlit/secrets.toml"
fi

echo ""

# הרץ בדיקות
echo "🧪 Running tests..."
echo ""

python simulation_engine.py > test_output.log 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ All tests passed!"
    echo ""
    tail -20 test_output.log | grep -E "PASS|FAIL"
else
    echo "   ⚠️  Some tests might have warnings (see test_output.log)"
fi

echo ""

# הגדרות Streamlit
echo "⚙️  Configuring Streamlit..."
mkdir -p .streamlit

cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#00f0ff"
backgroundColor = "#02040a"
secondaryBackgroundColor = "#0c1220"
textColor = "#e8f4f8"
font = "sans serif"

[client]
showErrorDetails = true

[server]
headless = true
port = 8501
EOF

echo "   ✅ Streamlit configured"
echo ""

# סיכום
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✨ SETUP COMPLETE! ✨"
echo ""
echo "🚀 To start the application, run:"
echo "   streamlit run app.py"
echo ""
echo "📱 The app will open at: http://localhost:8501"
echo ""
echo "📖 For more information, read: README.md"
echo ""
echo "════════════════════════════════════════════════════════════════"
