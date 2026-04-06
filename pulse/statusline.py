#!/usr/bin/env python3
"""
Pulse statusLine — lives in Claude Code's status bar.
Reads session JSON from stdin + ~/.pulse/pulse.db for cross-session context.
Configurable via ~/.pulse/config.json
"""
import json, sys, os, random
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

try:
    import db as pulse_db
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

# ── ANSI ──────────────────────────────────────────────────────────────────────
C = {
    "reset":  "\033[0m",  "bold":   "\033[1m",  "dim":    "\033[2m",
    "blue":   "\033[94m", "green":  "\033[92m", "yellow": "\033[93m",
    "orange": "\033[33m", "purple": "\033[95m", "gray":   "\033[90m",
    "red":    "\033[91m", "cyan":   "\033[96m", "pink":   "\033[35m",
}

# ── CONFIG ────────────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.expanduser("~/.pulse/config.json")
DEFAULT_CONFIG = {
    "persona": "adaptive",   # adaptive | caring | hype | zen | silent
    "show_cost": True,
    "show_duration": True,   # shows today's total coding time
    "show_streak": True,
    "show_level": True,
    "show_message": True,
    "creature_name": "Pulse",
}

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG

# ── PERSONAS ──────────────────────────────────────────────────────────────────
PERSONAS = {
    "caring": {
        "sleepy":  ["Close the laptop. I'll be here tomorrow. 🌙",
                    "You said you'd sleep by midnight.",
                    "Rest. The code will still be there."],
        "worried": ["Drink some water before the next one. 💧",
                    "You've been at this a while. Take 5 minutes.",
                    "Step away. Come back fresh."],
        "excited": ["Your agent finished! Go take a look 👀",
                    "Done! Go check it before you forget what you asked.",
                    "It delivered. Your turn now."],
        "proud":   ["I'm proud of you. Keep the streak alive. 🔥",
                    "Look at you showing up every day.",
                    "Consistency is everything. You're doing it."],
        "hype":    ["You're on a roll today! 🚀", "This is good work.", "Keep going."],
        "happy":   ["", "", "", "", "Good session.", ""],
        "egg":     ["Hi. I'm Pulse. I'll be watching. 👀", "Still getting to know you.", ""],
    },
    "hype": {
        "sleepy":  ["BRO it's late. CLOSE THE LAPTOP 😭", "Sleep is a cheat code. Use it.",
                    "Your future self will thank you. Go sleep."],
        "worried": ["DRINK WATER BESTIE 💧", "Stand up. Stretch. You got this.",
                    "5 minute break = 2x productivity. Science."],
        "excited": ["LETS GOOO YOUR AGENT FINISHED 🚀🚀🚀", "IT DELIVERED. GO CHECK IT NOW.",
                    "YOUR AGENT ATE. Go review."],
        "proud":   ["STREAK INTACT. YOU'RE BUILT DIFFERENT 🔥", "ANOTHER DAY ANOTHER W.",
                    "THE CONSISTENCY IS INSANE."],
        "hype":    ["YOU'RE SHIPPING 🔥", "ON A ROLL TODAY.", "THIS IS THE GOOD STUFF."],
        "happy":   ["", "", "", "good session.", "", ""],
        "egg":     ["NEW ACCOUNT WHO DIS 👀", "LET'S BUILD SOMETHING CRAZY.", ""],
    },
    "zen": {
        "sleepy":  ["The work will be there tomorrow.", "Rest is part of the process.",
                    "What you build tomorrow depends on how you sleep tonight."],
        "worried": ["You've been here a while. The answer might come after a walk.",
                    "Sometimes the best debugging happens away from the screen.",
                    "Water. Stretch. Return."],
        "excited": ["The agent finished. Take a breath before you look.",
                    "Something completed. Observe before reacting.",
                    "Done. Review with fresh eyes."],
        "proud":   ["Showing up is the practice.", "The streak is a side effect of the habit.",
                    "Small steps, compounding."],
        "hype":    ["You're in flow. Stay there.", "Good momentum.", ""],
        "happy":   ["", "", "", "", "", ""],
        "egg":     ["Every expert was once a beginner.", "The journey starts here.", ""],
    },
    "silent": {
        "sleepy": [""], "worried": [""], "excited": [""], "proud": [""],
        "hype": [""], "happy": [""], "egg": [""],
    },
}
# adaptive = caring by default, switches based on context
PERSONAS["adaptive"] = PERSONAS["caring"]

# ── MOODS ─────────────────────────────────────────────────────────────────────
MOODS = {
    "happy":   {"frames": ["(^.^)", "(^-^)", "(^.^)", "(^~^)"], "color": "blue"},
    "excited": {"frames": ["(^o^)", "(★o★)", "(^o^)", "(>o<)"], "color": "green"},
    "sleepy":  {"frames": ["(-_-)", "(-.-)", "(-_-)", "(-.-)"], "color": "yellow"},
    "worried": {"frames": ["(>.<)", "(>.>)", "(>.<)", "(<.<)"], "color": "orange"},
    "proud":   {"frames": ["(^_^)", "(★_★)", "(^_^)", "(✿_✿)"], "color": "purple"},
    "egg":     {"frames": ["(o.o)", "(o_o)", "(o.o)", "(.o.)"], "color": "gray"},
    "hype":    {"frames": ["(★o★)", "(^o^)", "(★o★)", "(>o<)"], "color": "cyan"},
}

HEARTS = ["💓", "🩷", "💓", "❤️"]

def get_frame(mood_data: dict) -> tuple[str, str]:
    """Return (face, heart) for current time-based frame."""
    import time
    frame = int(time.time() * 0.4) % 4
    face = mood_data["frames"][frame]
    heart = HEARTS[frame]
    return face, heart

LEVEL_NAMES = [(1,3,"Egg"),(4,9,"Hatchling"),(10,19,"Companion"),(20,29,"Veteran"),(30,99,"Legend")]

def get_level_name(level):
    for lo, hi, name in LEVEL_NAMES:
        if lo <= level <= hi:
            return name
    return "Legend"

def detect_mood(ctx, hour):
    if 0 <= hour < 4:
        return "sleepy"
    if ctx.get("agent_just_finished"):
        return "excited"
    if ctx.get("streak_milestone") or ctx.get("level_up"):
        return "proud"
    if ctx.get("sessions_today", 0) >= 3 and ctx.get("total_time_today_minutes", 0) > 180:
        return "worried"
    if ctx.get("sessions_today", 0) >= 2 and ctx.get("total_time_today_minutes", 0) > 90:
        return "hype"
    if ctx.get("level", 1) <= 3:
        return "egg"
    return "happy"

def context_bar(pct, width=8):
    filled = int(pct * width / 100)
    color = C["red"] if pct >= 80 else C["yellow"] if pct >= 60 else C["green"]
    bar = "█" * filled + "░" * (width - filled)
    return f"{color}{bar}{C['reset']}"

def fmt_minutes(minutes):
    """Format total minutes into human-readable duration."""
    h = int(minutes) // 60
    m = int(minutes) % 60
    if h > 0:
        return f"{h}h{m:02d}m"
    return f"{m}m"

def main():
    cfg = load_config()

    try:
        data = json.load(sys.stdin)
    except Exception:
        print(f"💓 {cfg['creature_name']}")
        return

    model = data.get("model", {}).get("display_name", "Claude")
    pct   = int(data.get("context_window", {}).get("used_percentage", 0) or 0)
    cost  = data.get("cost", {}).get("total_cost_usd", 0) or 0
    sid   = data.get("session_id", "")
    hour  = datetime.now().hour

    # Cross-session context from SQLite
    ctx = {}
    if DB_AVAILABLE:
        try:
            pulse_db.init_db()
            ctx = pulse_db.get_context(sid, 0)
        except Exception:
            pass

    level   = ctx.get("level", 1)
    streak  = ctx.get("streak_days", 1)
    # Use today's total coding time (from SQLite) — NOT session wall-clock time
    today_min = ctx.get("total_time_today_minutes", 0)

    mood      = detect_mood(ctx, hour)
    mood_data  = MOODS.get(mood, MOODS["happy"])
    color      = C[mood_data["color"]]
    face, heart = get_frame(mood_data)
    level_name = get_level_name(level)

    persona = cfg.get("persona", "adaptive")
    messages = PERSONAS.get(persona, PERSONAS["adaptive"])
    pool = messages.get(mood, [""])
    msg  = random.choice(pool)

    # ── Line 1: session info ─────────────────────────────────────────────────
    bar = context_bar(pct)
    parts = [f"{C['bold']}{model}{C['reset']}", f"{bar} {C['dim']}{pct}%{C['reset']}"]

    if cfg.get("show_duration") and today_min > 0:
        parts.append(f"{C['dim']}{fmt_minutes(today_min)} today{C['reset']}")

    if cfg.get("show_cost") and cost >= 0.01:
        parts.append(f"{C['dim']}${cost:.2f}{C['reset']}")

    line1 = "  ".join(parts)

    # ── Line 2: creature ─────────────────────────────────────────────────────
    name = cfg.get("creature_name", "Pulse")
    line2_parts = [f"{C['pink']}{heart}{C['reset']} {color}{face}{C['reset']}"]

    if cfg.get("show_level"):
        line2_parts.append(f"{C['dim']}lv.{level} · {level_name}{C['reset']}")

    if cfg.get("show_streak") and streak >= 2:
        line2_parts.append(f"🔥{streak}d")

    if cfg.get("show_message") and msg:
        line2_parts.append(f"{C['dim']}\"{msg}\"{C['reset']}")

    line2 = "  ".join(line2_parts)

    print(line1)
    print(line2)

if __name__ == "__main__":
    main()
