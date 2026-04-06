# 🧠 Calvira — AI Mental Health Companion

> A Caring Voice Chatbot for Private Mental Health Support and Medical Guidance  
> Built by **Lakshya Lathi** | Engineering College Ajmer

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9 or higher
- A free **Groq API key** → https://console.groq.com

### 2. Install & Run

```bash
# Clone / extract the project folder, then:
cd guardian

# Set your Groq API key
export GROQ_API_KEY=your_groq_api_key_here

# Run the start script
bash start.sh
```

Or manually:
```bash
cd guardian
pip install fastapi uvicorn "python-jose[cryptography]" "passlib[bcrypt]" python-multipart httpx
cd backend
export GROQ_API_KEY=your_key_here
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open in Browser
Visit: **http://localhost:8000**

---

## 📁 Project Structure

```
guardian/
├── backend/
│   ├── main.py          ← FastAPI app (all routes)
│   ├── database.py      ← SQLite setup (5 tables)
│   ├── auth.py          ← JWT login / bcrypt passwords
│   ├── chat.py          ← Groq AI + mood scoring + crisis detection
│   ├── journal.py       ← Journal CRUD + AI reflection
│   ├── reports.py       ← Weekly wellness report generation
│   └── guardian.db      ← Auto-created SQLite database
│
├── frontend/
│   ├── index.html       ← Landing page
│   ├── login.html       ← Sign in
│   ├── register.html    ← Create account (2 steps)
│   ├── dashboard.html   ← Home stats + recent sessions
│   ├── chat.html        ← Voice AI chatbot
│   ├── mood.html        ← Mood calendar + heatmap + chart
│   ├── journal.html     ← Private journal + AI reflection
│   ├── reports.html     ← Weekly wellness reports
│   ├── crisis.html      ← Crisis helplines + coping tips
│   ├── profile.html     ← Settings & preferences
│   ├── css/
│   │   └── base.css     ← Glassmorphism dark theme
│   └── js/
│       └── api.js       ← API client + utilities
│
├── start.sh             ← One-command launcher
├── requirements.txt     ← Python dependencies
└── README.md
```

---

## 🔑 API Keys Needed

| Service | Purpose | Cost | Link |
|---------|---------|------|------|
| **Groq** | AI chatbot brain (LLaMA 3) | **Free** | https://console.groq.com |
| Web Speech API | Voice input/output | **Free** (browser built-in) | — |

> **No ElevenLabs key needed** — the app uses the browser's built-in Web Speech API for voice by default.  
> You can add ElevenLabs later for premium voice quality.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Voice Chatbot** | Talk or type — AI responds with voice using Web Speech API |
| 🧠 **Crisis Detection** | Auto-detects distress keywords → shows emergency helplines |
| 📅 **Mood Calendar** | 90-day heatmap of your emotional journey |
| 📈 **Mood Charts** | Line chart of daily mood scores |
| 📓 **Private Journal** | Write entries, get AI reflections |
| 📊 **Weekly Reports** | AI-generated wellness digest every week |
| 🚨 **Crisis Helplines** | India, USA, UK, Australia helplines |
| 🔒 **Secure Auth** | JWT tokens + bcrypt password hashing |
| ⚙️ **Preferences** | Voice gender, language, age group, country |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python + FastAPI |
| **Database** | SQLite (file-based, zero config) |
| **Auth** | JWT via `python-jose` + `passlib[bcrypt]` |
| **AI** | Groq Cloud API (LLaMA 3 70B) |
| **Voice In** | Web Speech API (browser native) |
| **Voice Out** | SpeechSynthesis API (browser native) |
| **Charts** | Chart.js 4 (CDN) |
| **Frontend** | Vanilla HTML + CSS + JS (Glassmorphism UI) |

---

## 🔗 API Endpoints

```
POST /auth/register        Create account
POST /auth/login           Sign in → JWT token
GET  /auth/me              Get current user

POST /chat/message         Send message → AI reply + mood score
POST /chat/session         Create new chat session
GET  /chat/sessions        List all sessions
GET  /chat/history/{id}    Load session messages

POST /journal/entry        Save journal entry + AI reflection
GET  /journal/entries      List all entries
GET  /journal/entry/{id}   Get single entry
DELETE /journal/entry/{id} Delete entry

GET  /mood/calendar        Daily mood scores (90 days)
GET  /reports/weekly       Generate/get this week's report
GET  /reports/all          All past reports

GET  /crisis/resources     Helpline numbers by country
PUT  /profile/update       Update user preferences
GET  /dashboard/stats      Stats summary
```

---

## 🌍 Crisis Helplines Included

- 🇮🇳 **iCall India** — 9152987821
- 🇮🇳 **Vandrevala Foundation** — 1860-2662-345
- 🇮🇳 **NIMHANS Helpline** — 080-46110007
- 🇮🇳 **Befrienders India** — 044-24640050
- 🇺🇸 **988 Suicide & Crisis Lifeline**
- 🇺🇸 **Crisis Text Line** — Text HOME to 741741
- 🇬🇧 **Samaritans** — 116 123
- 🇦🇺 **Lifeline Australia** — 13 11 14

---

## 📝 Notes

- The database (`calvira.db`) is created automatically on first run
- All passwords are hashed with bcrypt — never stored in plain text
- JWT tokens expire after 7 days
- Crisis detection uses keyword matching on user messages
- Mood scoring uses a simple sentiment keyword algorithm (0–10 scale)

---

*Built with ❤️ for mental wellness accessibility*
