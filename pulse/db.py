"""SQLite layer for Pulse. No external dependencies."""
import sqlite3
import time
import os
from datetime import datetime, date

DB_PATH = os.path.expanduser("~/.pulse/pulse.db")


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                started_at INTEGER,
                ended_at INTEGER,
                duration_seconds INTEGER,
                cwd TEXT,
                session_id TEXT UNIQUE
            );
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)


def log_session_start(cwd: str, session_id: str):
    init_db()
    now = int(time.time())
    with _conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO sessions (started_at, cwd, session_id) VALUES (?, ?, ?)",
            (now, cwd, session_id),
        )


def log_session_end(session_id: str, duration_seconds: int):
    now = int(time.time())
    with _conn() as c:
        c.execute(
            "UPDATE sessions SET ended_at=?, duration_seconds=? WHERE session_id=?",
            (now, duration_seconds, session_id),
        )
        # Update total_seconds
        total = c.execute("SELECT COALESCE(SUM(duration_seconds),0) FROM sessions").fetchone()[0]
        c.execute("INSERT OR REPLACE INTO state VALUES ('total_seconds', ?)", (str(total),))
        # Update total_sessions
        count = c.execute("SELECT COUNT(*) FROM sessions WHERE ended_at IS NOT NULL").fetchone()[0]
        c.execute("INSERT OR REPLACE INTO state VALUES ('total_sessions', ?)", (str(count),))


def get_state(key: str, default: str = "") -> str:
    init_db()
    with _conn() as c:
        row = c.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return row[0] if row else default


def set_state(key: str, value: str):
    init_db()
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO state VALUES (?, ?)", (key, value))


def get_context(session_id: str = None, duration_seconds: int = 0) -> dict:
    """Build the full context dict for message generation."""
    init_db()
    today = date.today().isoformat()
    now = datetime.now()

    with _conn() as c:
        # Sessions today (ended)
        today_start = int(datetime.combine(date.today(), datetime.min.time()).timestamp())
        sessions_today = c.execute(
            "SELECT COUNT(*) FROM sessions WHERE ended_at >= ? AND ended_at IS NOT NULL",
            (today_start,),
        ).fetchone()[0]

        total_time_today_seconds = c.execute(
            "SELECT COALESCE(SUM(duration_seconds),0) FROM sessions WHERE ended_at >= ?",
            (today_start,),
        ).fetchone()[0]

    total_sessions = int(get_state("total_sessions", "0"))
    # Level progression based on total sessions
    # Egg: 1-10, Hatchling: 11-30, Companion: 31-75, Veteran: 76-150, Legend: 151+
    if total_sessions <= 10:
        level = total_sessions if total_sessions > 0 else 1
    elif total_sessions <= 30:
        level = 10 + (total_sessions - 10)
    elif total_sessions <= 75:
        level = 30 + (total_sessions - 30)
    elif total_sessions <= 150:
        level = 75 + (total_sessions - 75)
    else:
        level = 150 + min(total_sessions - 150, 849)

    # Streak
    last_session_date = get_state("last_session_date", "")
    streak_days = int(get_state("streak_days", "0"))
    if last_session_date == today:
        pass  # same day, keep streak
    elif last_session_date == _yesterday():
        streak_days += 1
        set_state("streak_days", str(streak_days))
        set_state("last_session_date", today)
    else:
        streak_days = 1
        set_state("streak_days", "1")
        set_state("last_session_date", today)

    streak_milestones = {3, 7, 14, 30}
    streak_milestone = streak_days in streak_milestones

    # Previous level before this session
    prev_total = total_sessions - 1
    prev_level = min(max(prev_total // 5 + 1, 1), 30)
    level_up = level > prev_level

    # Last break
    last_prompt_at = int(get_state("last_prompt_at", "0"))
    last_break_minutes_ago = int((time.time() - last_prompt_at) / 60) if last_prompt_at else 999

    first_session_today = sessions_today == 0

    return {
        "sessions_today": sessions_today,
        "total_time_today_minutes": total_time_today_seconds // 60,
        "total_seconds": total_time_today_seconds,
        "streak_days": streak_days,
        "streak_milestone": streak_milestone,
        "level": level,
        "level_up": level_up,
        "last_break_minutes_ago": last_break_minutes_ago,
        "hour": now.hour,
        "session_duration_seconds": duration_seconds,
        "first_session_today": first_session_today,
        "agent_just_finished": False,  # set by caller
    }


def _yesterday() -> str:
    from datetime import timedelta
    return (date.today() - timedelta(days=1)).isoformat()


if __name__ == "__main__":
    import json
    init_db()
    # Seed fake data for testing
    log_session_start("/tmp/test", "test-session-1")
    log_session_end("test-session-1", 4320)  # 72 min
    ctx = get_context("test-session-1", 4320)
    print(json.dumps(ctx, indent=2))
