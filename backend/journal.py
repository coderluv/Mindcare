import httpx, os
from database import get_db
from chat import call_groq, score_mood

async def create_journal_entry(user_id: int, title: str, content: str, user_profile: dict) -> dict:
    mood = score_mood(content)
    reflection_prompt = [{"role": "user", "content": f"I wrote this in my journal: {content}\n\nPlease give me a short, warm, insightful reflection (2-3 sentences) on what I shared."}]
    reflection = await call_groq(reflection_prompt, user_profile)

    db = get_db()
    cur = db.execute(
        "INSERT INTO journal_entries (user_id, title, content, ai_reflection, mood_score) VALUES (?,?,?,?,?)",
        (user_id, title, content, reflection, mood)
    )
    db.commit()
    entry_id = cur.lastrowid
    row = db.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,)).fetchone()
    db.close()
    return dict(row)

def get_journal_entries(user_id: int) -> list:
    db = get_db()
    rows = db.execute("SELECT * FROM journal_entries WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

def get_journal_entry(entry_id: int, user_id: int) -> dict:
    db = get_db()
    row = db.execute("SELECT * FROM journal_entries WHERE id = ? AND user_id = ?", (entry_id, user_id)).fetchone()
    db.close()
    return dict(row) if row else None

def delete_journal_entry(entry_id: int, user_id: int) -> bool:
    db = get_db()
    db.execute("DELETE FROM journal_entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
    db.commit()
    db.close()
    return True
