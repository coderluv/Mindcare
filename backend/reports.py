from datetime import date, timedelta
from database import get_db
from chat import call_groq

def get_week_start(d: date = None) -> date:
    d = d or date.today()
    return d - timedelta(days=d.weekday())

async def generate_weekly_report(user_id: int, user_profile: dict) -> dict:
    week_start = get_week_start()
    week_end = week_start + timedelta(days=6)
    db = get_db()

    existing = db.execute(
        "SELECT * FROM weekly_reports WHERE user_id = ? AND week_start = ?",
        (user_id, week_start.isoformat())
    ).fetchone()
    if existing:
        db.close()
        return dict(existing)

    messages = db.execute("""
        SELECT m.content, m.mood_score, m.created_at FROM messages m
        JOIN chat_sessions cs ON cs.id = m.session_id
        WHERE cs.user_id = ? AND m.role = 'user'
        AND date(m.created_at) BETWEEN ? AND ?
    """, (user_id, week_start.isoformat(), week_end.isoformat())).fetchall()

    journals = db.execute(
        "SELECT content, mood_score FROM journal_entries WHERE user_id = ? AND date(created_at) BETWEEN ? AND ?",
        (user_id, week_start.isoformat(), week_end.isoformat())
    ).fetchall()

    sessions_count = db.execute("""
        SELECT COUNT(*) as c FROM chat_sessions WHERE user_id = ?
        AND date(started_at) BETWEEN ? AND ?
    """, (user_id, week_start.isoformat(), week_end.isoformat())).fetchone()["c"]

    all_moods = [r["mood_score"] for r in messages] + [r["mood_score"] for r in journals]
    avg_mood = round(sum(all_moods) / len(all_moods), 1) if all_moods else 5.0

    combined_text = " ".join([r["content"][:100] for r in messages[:10]])
    if combined_text:
        prompt = [{"role": "user", "content": f"Based on this week's mental health conversations: '{combined_text[:500]}'\n\nWrite a warm, encouraging weekly wellness summary (3-4 sentences). Mention mood trends, highlight positives, and give one gentle suggestion."}]
        summary = await call_groq(prompt, user_profile)
    else:
        summary = "You haven't had any sessions this week. Remember, talking about your feelings — even a little — can make a big difference. Guardian is here whenever you're ready."

    cur = db.execute(
        "INSERT INTO weekly_reports (user_id, week_start, avg_mood, total_sessions, summary) VALUES (?,?,?,?,?)",
        (user_id, week_start.isoformat(), avg_mood, sessions_count, summary)
    )
    db.commit()
    row = db.execute("SELECT * FROM weekly_reports WHERE id = ?", (cur.lastrowid,)).fetchone()
    db.close()
    return dict(row)

def get_all_reports(user_id: int) -> list:
    db = get_db()
    rows = db.execute("SELECT * FROM weekly_reports WHERE user_id = ? ORDER BY week_start DESC", (user_id,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

def get_mood_calendar(user_id: int) -> list:
    db = get_db()
    rows = db.execute("""
        SELECT date(m.created_at) as day, AVG(m.mood_score) as avg_mood, COUNT(*) as count
        FROM messages m JOIN chat_sessions cs ON cs.id = m.session_id
        WHERE cs.user_id = ? AND m.role = 'user'
        GROUP BY date(m.created_at) ORDER BY day DESC LIMIT 90
    """, (user_id,)).fetchall()
    db.close()
    return [dict(r) for r in rows]
