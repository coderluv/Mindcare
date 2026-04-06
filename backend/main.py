from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from database import init_db, get_db
from auth import hash_password, verify_password, create_token, get_current_user
from chat import chat_with_guardian, create_session, get_session_history, get_user_sessions
from journal import create_journal_entry, get_journal_entries, get_journal_entry, delete_journal_entry
from reports import generate_weekly_report, get_all_reports, get_mood_calendar

app = FastAPI(title="Guardian API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.on_event("startup")
def startup():
    init_db()

# ─── Pydantic Models ───────────────────────────────────────────────────────────

class RegisterInput(BaseModel):
    username: str
    password: str
    age_group: str = "adult"
    gender: str = ""
    country: str = ""
    language: str = "en"
    voice_preference: str = "female"

class LoginInput(BaseModel):
    username: str
    password: str

class ChatInput(BaseModel):
    message: str
    session_id: Optional[int] = None

class JournalInput(BaseModel):
    title: str = ""
    content: str

class ProfileUpdate(BaseModel):
    age_group: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    voice_preference: Optional[str] = None

# ─── Frontend Routes ───────────────────────────────────────────────────────────

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/login")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/register")
def serve_register():
    return FileResponse(os.path.join(FRONTEND_DIR, "register.html"))

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

@app.get("/chat")
def serve_chat():
    return FileResponse(os.path.join(FRONTEND_DIR, "chat.html"))

@app.get("/mood")
def serve_mood():
    return FileResponse(os.path.join(FRONTEND_DIR, "mood.html"))

@app.get("/journal")
def serve_journal():
    return FileResponse(os.path.join(FRONTEND_DIR, "journal.html"))

@app.get("/reports")
def serve_reports():
    return FileResponse(os.path.join(FRONTEND_DIR, "reports.html"))

@app.get("/crisis")
def serve_crisis():
    return FileResponse(os.path.join(FRONTEND_DIR, "crisis.html"))

@app.get("/profile")
def serve_profile():
    return FileResponse(os.path.join(FRONTEND_DIR, "profile.html"))

# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.post("/auth/register")
def register(data: RegisterInput):
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (data.username,)).fetchone()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Username already taken")
    db.execute(
        "INSERT INTO users (username, password_hash, age_group, gender, country, language, voice_preference) VALUES (?,?,?,?,?,?,?)",
        (data.username, hash_password(data.password), data.age_group, data.gender, data.country, data.language, data.voice_preference)
    )
    db.commit()
    user = db.execute("SELECT * FROM users WHERE username = ?", (data.username,)).fetchone()
    db.close()
    token = create_token(user["id"], user["username"])
    return {"token": token, "username": user["username"], "user_id": user["id"]}

@app.post("/auth/login")
def login(data: LoginInput):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (data.username,)).fetchone()
    db.close()
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(user["id"], user["username"])
    return {"token": token, "username": user["username"], "user_id": user["id"]}

@app.get("/auth/me")
def me(user=Depends(get_current_user)):
    return {k: v for k, v in user.items() if k != "password_hash"}

# ─── Chat Routes ──────────────────────────────────────────────────────────────

@app.post("/chat/message")
async def send_message(data: ChatInput, user=Depends(get_current_user)):
    session_id = data.session_id
    if not session_id:
        session_id = create_session(user["id"])
    history = get_session_history(session_id)
    result = await chat_with_guardian(user["id"], session_id, data.message, history, user)
    result["session_id"] = session_id
    return result

@app.post("/chat/session")
def new_session(user=Depends(get_current_user)):
    sid = create_session(user["id"])
    return {"session_id": sid}

@app.get("/chat/sessions")
def sessions(user=Depends(get_current_user)):
    return get_user_sessions(user["id"])

@app.get("/chat/history/{session_id}")
def history(session_id: int, user=Depends(get_current_user)):
    return get_session_history(session_id)

# ─── Journal Routes ───────────────────────────────────────────────────────────

@app.post("/journal/entry")
async def add_entry(data: JournalInput, user=Depends(get_current_user)):
    return await create_journal_entry(user["id"], data.title, data.content, user)

@app.get("/journal/entries")
def list_entries(user=Depends(get_current_user)):
    return get_journal_entries(user["id"])

@app.get("/journal/entry/{entry_id}")
def get_entry(entry_id: int, user=Depends(get_current_user)):
    e = get_journal_entry(entry_id, user["id"])
    if not e:
        raise HTTPException(404, "Entry not found")
    return e

@app.delete("/journal/entry/{entry_id}")
def del_entry(entry_id: int, user=Depends(get_current_user)):
    delete_journal_entry(entry_id, user["id"])
    return {"deleted": True}

# ─── Mood & Reports Routes ────────────────────────────────────────────────────

@app.get("/mood/calendar")
def mood_calendar(user=Depends(get_current_user)):
    return get_mood_calendar(user["id"])

@app.get("/reports/weekly")
async def weekly_report(user=Depends(get_current_user)):
    return await generate_weekly_report(user["id"], user)

@app.get("/reports/all")
def all_reports(user=Depends(get_current_user)):
    return get_all_reports(user["id"])

# ─── Crisis Resources ─────────────────────────────────────────────────────────

@app.get("/crisis/resources")
def crisis_resources():
    return {
        "resources": [
            {"name": "iCall (India)", "number": "9152987821", "desc": "Mon–Sat, 10am–8pm", "country": "India"},
            {"name": "Vandrevala Foundation", "number": "1860-2662-345", "desc": "24/7 India", "country": "India"},
            {"name": "NIMHANS Helpline", "number": "080-46110007", "desc": "Mental health, India", "country": "India"},
            {"name": "Befrienders India", "number": "044-24640050", "desc": "Suicide prevention", "country": "India"},
            {"name": "National Suicide Prevention (US)", "number": "988", "desc": "24/7 US", "country": "USA"},
            {"name": "Crisis Text Line (US)", "number": "Text HOME to 741741", "desc": "24/7 Text-based", "country": "USA"},
            {"name": "Samaritans (UK)", "number": "116 123", "desc": "24/7 UK", "country": "UK"},
            {"name": "Lifeline (Australia)", "number": "13 11 14", "desc": "24/7 Australia", "country": "Australia"},
        ]
    }

# ─── Profile Routes ───────────────────────────────────────────────────────────

@app.put("/profile/update")
def update_profile(data: ProfileUpdate, user=Depends(get_current_user)):
    db = get_db()
    fields = {k: v for k, v in data.dict().items() if v is not None}
    if fields:
        sets = ", ".join(f"{k} = ?" for k in fields)
        db.execute(f"UPDATE users SET {sets} WHERE id = ?", list(fields.values()) + [user["id"]])
        db.commit()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
    db.close()
    return {k: v for k, v in dict(row).items() if k != "password_hash"}

@app.get("/dashboard/stats")
def dashboard_stats(user=Depends(get_current_user)):
    db = get_db()
    uid = user["id"]
    total_sessions = db.execute("SELECT COUNT(*) as c FROM chat_sessions WHERE user_id = ?", (uid,)).fetchone()["c"]
    total_messages = db.execute("""
        SELECT COUNT(*) as c FROM messages m JOIN chat_sessions cs ON cs.id = m.session_id
        WHERE cs.user_id = ? AND m.role = 'user'
    """, (uid,)).fetchone()["c"]
    avg_mood = db.execute("""
        SELECT AVG(m.mood_score) as a FROM messages m JOIN chat_sessions cs ON cs.id = m.session_id
        WHERE cs.user_id = ? AND m.role = 'user'
    """, (uid,)).fetchone()["a"]
    journal_count = db.execute("SELECT COUNT(*) as c FROM journal_entries WHERE user_id = ?", (uid,)).fetchone()["c"]
    crisis_count = db.execute("""
        SELECT COUNT(*) as c FROM messages m JOIN chat_sessions cs ON cs.id = m.session_id
        WHERE cs.user_id = ? AND m.crisis_flag = 1
    """, (uid,)).fetchone()["c"]
    db.close()
    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "avg_mood": round(avg_mood, 1) if avg_mood else 5.0,
        "journal_count": journal_count,
        "crisis_alerts": crisis_count
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
