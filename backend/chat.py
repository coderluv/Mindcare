import httpx, os, json

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die", "harm myself",
    "self harm", "cutting myself", "no reason to live", "better off dead",
    "can't go on", "giving up", "overdose", "jump off", "hang myself"
]

SYSTEM_PROMPT = """You are Calvira, a warm and empathetic mental health support companion.
You listen deeply, respond with compassion, and help users explore their feelings safely.
You speak like a caring friend who also has professional insight.
Always validate feelings before offering advice.
If someone seems in crisis, gently encourage professional help and provide hope.
Keep responses conversational, warm, and under 150 words unless more detail is truly needed.
Never diagnose. Never be dismissive. Always be present."""

def detect_crisis(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in CRISIS_KEYWORDS)

def score_mood(text: str) -> float:
    positive = ["happy","great","good","better","hopeful","excited","grateful","calm","peaceful","joy","love","wonderful","amazing","fantastic","relieved","motivated"]
    negative = ["sad","depressed","anxious","scared","hopeless","worthless","empty","alone","tired","angry","frustrated","overwhelmed","crying","pain","hurt","terrible","awful","bad"]
    t = text.lower()
    pos = sum(1 for w in positive if w in t)
    neg = sum(1 for w in negative if w in t)
    score = 5.0 + (pos * 0.5) - (neg * 0.5)
    return round(max(0.0, min(10.0, score)), 1)

async def call_groq(messages: list, user_profile: dict) -> str:
    profile_context = f"The user is {user_profile.get('age_group','an adult')}."
    system = SYSTEM_PROMPT + "\n" + profile_context

    # Build clean messages list - only role and content
    clean_messages = []
    for m in messages:
        if isinstance(m, dict) and "role" in m and "content" in m:
            clean_messages.append({
                "role": str(m["role"]),
                "content": str(m["content"])
            })

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system}] + clean_messages,
        "max_tokens": 512,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(GROQ_URL, json=payload, headers=headers)

            # Print full error details to terminal for debugging
            if r.status_code != 200:
                print(f"\n❌ GROQ ERROR {r.status_code}:")
                print(f"   URL: {GROQ_URL}")
                print(f"   Model: {GROQ_MODEL}")
                print(f"   Key starts with: {GROQ_API_KEY[:8]}...")
                print(f"   Response: {r.text}\n")
                return f"Guardian is having trouble connecting. Error {r.status_code}: {r.text[:200]}"

            data = r.json()
            return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"\n❌ EXCEPTION in call_groq: {str(e)}\n")
        return f"Connection error: {str(e)[:100]}"

async def chat_with_guardian(user_id: int, session_id: int, user_message: str, history: list, user_profile: dict) -> dict:
    from database import get_db
    crisis = detect_crisis(user_message)
    mood = score_mood(user_message)

    messages = history + [{"role": "user", "content": user_message}]
    reply = await call_groq(messages, user_profile)

    db = get_db()
    db.execute("INSERT INTO messages (session_id, role, content, mood_score, crisis_flag) VALUES (?,?,?,?,?)",
               (session_id, "user", user_message, mood, int(crisis)))
    db.execute("INSERT INTO messages (session_id, role, content, mood_score, crisis_flag) VALUES (?,?,?,?,?)",
               (session_id, "assistant", reply, mood, 0))
    db.commit()
    db.close()

    return {"reply": reply, "mood_score": mood, "crisis": crisis}

def get_session_history(session_id: int) -> list:
    from database import get_db
    db = get_db()
    rows = db.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at", (session_id,)).fetchall()
    db.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]

def create_session(user_id: int) -> int:
    from database import get_db
    db = get_db()
    cur = db.execute("INSERT INTO chat_sessions (user_id) VALUES (?)", (user_id,))
    db.commit()
    sid = cur.lastrowid
    db.close()
    return sid

def get_user_sessions(user_id: int) -> list:
    from database import get_db
    db = get_db()
    rows = db.execute("""
        SELECT cs.id, cs.started_at,
               COUNT(m.id) as message_count,
               AVG(CASE WHEN m.role='user' THEN m.mood_score END) as avg_mood
        FROM chat_sessions cs
        LEFT JOIN messages m ON m.session_id = cs.id
        WHERE cs.user_id = ?
        GROUP BY cs.id ORDER BY cs.started_at DESC LIMIT 20
    """, (user_id,)).fetchall()
    db.close()
    return [dict(r) for r in rows]
