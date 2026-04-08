#!/bin/bash
echo ""
echo "Starting Mindcare — Mental Health Companion"
echo "================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install fastapi uvicorn "python-jose[cryptography]" "passlib[bcrypt]" python-multipart httpx --quiet

echo ""
echo "✅ Dependencies installed."
echo ""
echo "🔑 IMPORTANT: Set your Groq API key!"
echo "   Get a free key at: https://console.groq.com"
echo "   Then run: export GROQ_API_KEY=your_key_here"
echo ""
echo "🌐 Starting server at: http://localhost:8000"
echo "   Press Ctrl+C to stop."
echo ""

cd "$(dirname "$0")/backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
