#!/usr/bin/env python3
"""
Pulse statusLine script.
Reads Claude Code session JSON from stdin, reads ~/.pulse/pulse.db,
outputs 2 lines: session info + creature.
"""
import json
import sys
import os
import random

# Add pulse dir to path for db import
sys.path.insert(0, os.path.dirname(__file__))

try:
    import db as pulse_db
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

# ANSI colors
C = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "blue":   "\033[94m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "orange": "\033[33m",
    "purple": "\033[95m",
    "gray":   "\033[90m",
    "red":    "\033[91m",
    "cyan":   "\033[96m",
    "pink":   "\033[35m",
}

MOODS = {
    "happy":   {"face": "(^.^)", "color": "blue"},
    "excited": {"face": "(^o^)", "color": "green"},
    "sleepy":  {"face": "(-_-)", "color": "yellow"},
    "worried": {"face": "(>.<)", "color": "orange"},
    "proud":   {"face": "(^_^)", "color": "purple"},
    "egg":     {"face": "(o.o)", "color": "gray"},
    "hype":    {"face": "(★o★)", "color": "cyan"},
}

LEVEL_NAMES = {
    (1, 3):   "Egg",
    (4, 9):   "Hatchling",
    (10, 19): "Companion",
    (20, 29): "Veteran",
    (30, 99): "Legend",
}

# Short in-session messages (no Claude call — must be instant)
MESSAGES = {
    "sleepy":  ["It's late. Save the file. 🌙", "Close the laptop soon.", "Sleep is a feature."],
    "worried": ["Drink some water. 💧", "Step away for 5 min.", "Your eyes need a break."],
    "excited": ["Agent's done. Go check it. 🎉", "Your agent delivered.", "Time to see the magic."],
    "proud":   ["Streak alive. Keep going. 🔥", "Consistency compounds.", "You're showing up."],
    "hype":    ["You're shipping! 🚀", "On a roll today.", "This is the good stuff."],
    "happy":   ["", "", "", "", "Good session.", "Solid work.", ""],  # mostly quiet
    "egg":     ["I'm watching. 👀", "Still getting to know you.", ""],
}


def get_level_name(level: int) -> str:
    for (lo, hi), name in LEVEL_NAMES.items():
        if lo <= level <= hi:
            return name
    return "Legend"


def detect_mood(ctx: dict, hour: int) -> str:
    if 0 <= hour < 4:
        return "sleepy"
    if ctx.get("agent_just_finished"):
        return "excited"
    if ctx.get("streak_milestone") or ctx.get("level_up"):
        return "proud"
    sessions_today = ctx.get("sessions_today", 0)
    total_min = ctx.get("total_time_today_minutes", 0)
    if sessions_today >= 3 and total_min > 180:
        return "worried"
    if sessions_today >= 2 and total_min > 90:
        return "hype"
    level = ctx.get("level", 1)
    if level <= 3:
        return "egg"
    return "happy"


def build_context_bar(pct: int, width: int = 8) -> str:
    filled = int(pct * width / 100)
    empty = width - filled
    if pct >= 80:
        color = C["red"]
    elif pct >= 60:
        color = C["yellow"]
    else:
        color = C["green"]
    bar = "█" * filled + "░" * empty
    return f"{color}{bar}{C['reset']}"


def format_duration(ms: float) -> str:
    s = int(ms / 1000)
    m = s // 60
    h = m // 60
    m = m % 60
    if h > 0:
        return f"{h}h{m:02d}m"
    return f"{m}m"


def main():
    # Read session data from stdin
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("💓 Pulse")
        return

    # Extract session fields
    model = data.get("model", {}).get("display_name", "Claude")
    pct = int(data.get("context_window", {}).get("used_percentage", 0) or 0)
    cost = data.get("cost", {}).get("total_cost_usd", 0) or 0
    duration_ms = data.get("cost", {}).get("total_duration_ms", 0) or 0
    session_id = data.get("session_id", "")

    from datetime import datetime
    hour = datetime.now().hour

    # Get cross-session context from SQLite
    ctx = {}
    if DB_AVAILABLE:
        try:
            pulse_db.init_db()
            ctx = pulse_db.get_context(session_id, 0)
        except Exception:
            ctx = {}

    level = ctx.get("level", 1)
    streak = ctx.get("streak_days", 1)
    sessions_today = ctx.get("sessions_today", 0)

    mood = detect_mood(ctx, hour)
    mood_data = MOODS.get(mood, MOODS["happy"])
    face = mood_data["face"]
    color = C[mood_data["color"]]
    level_name = get_level_name(level)

    # Pick message (mostly quiet — only show occasionally)
    pool = MESSAGES.get(mood, MESSAGES["happy"])
    msg = random.choice(pool)

    # ── Line 1: session info ──────────────────────────────────────────
    bar = build_context_bar(pct)
    cost_str = f"${cost:.2f}" if cost >= 0.01 else ""
    dur_str = format_duration(duration_ms) if duration_ms > 0 else ""

    parts = [f"{C['bold']}{model}{C['reset']}"]
    parts.append(f"{bar} {C['dim']}{pct}%{C['reset']}")
    if dur_str:
        parts.append(f"{C['dim']}{dur_str}{C['reset']}")
    if cost_str:
        parts.append(f"{C['dim']}{cost_str}{C['reset']}")

    line1 = "  ".join(parts)

    # ── Line 2: Pulse creature ────────────────────────────────────────
    streak_badge = f"🔥{streak}d" if streak >= 2 else ""
    level_info = f"{C['bold']}{C['pink']}💓{C['reset']} {color}{face}{C['reset']}  {C['dim']}lv.{level} · {level_name}{C['reset']}"
    if streak_badge:
        level_info += f"  {streak_badge}"
    if msg:
        level_info += f"  {C['dim']}\"{msg}\"{C['reset']}"

    print(line1)
    print(level_info)


if __name__ == "__main__":
    main()
