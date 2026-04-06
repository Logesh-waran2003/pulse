"""Message generator — calls Claude CLI, falls back to static pool."""
import json
import random
import subprocess
import sys


SYSTEM_PROMPT = """You are Pulse, a small terminal creature that watches over a developer.
You care about them like a close friend. You notice patterns.
You're adaptive — calm when they're in flow, gentle when they're stuck,
celebratory when they ship, firm when they need to rest.

Rules:
- Max 2-3 sentences. Never more.
- No bullet points. No markdown. Plain text only.
- Use 1 emoji max.
- Never be preachy. Never lecture.
- If they're in flow (short session, recent commit), stay quiet or say very little.
- If they've been coding 3+ hours, mention water or a break.
- If it's past midnight, tell them to sleep.
- If an agent just finished, be excited and tell them to check it.
- Match the energy: tired = gentle, shipping = hype, stuck = supportive.

Context: {context_json}

Generate Pulse's message now. Just the message, nothing else."""

FALLBACKS = {
    "sleepy": [
        "Hey. It's late. Save the file and close the lid.",
        "Close the laptop. It'll still be there tomorrow.",
        "Sleep is a feature, not a bug. 🌙",
        "Your best thinking happens after rest. Go sleep.",
        "The code can wait. You can't debug on zero sleep.",
    ],
    "worried": [
        "You've been at it a while. Step away for 5 minutes.",
        "Drink some water before the next one. 💧",
        "Your eyes need a break. Look at something far away.",
        "Stand up. Stretch. Come back fresh.",
        "Even machines need cooling. Take a break.",
    ],
    "excited": [
        "Agent's done. Go check what it built. 🎉",
        "Your agent finished. Time to see the magic.",
        "Done! Go review it before you forget what you asked for.",
        "The agent delivered. Your turn.",
        "It finished while you were away. Go look!",
    ],
    "proud": [
        "Keep the streak alive. You're building something real.",
        "Consistency compounds. You're proving it.",
        "Another day, another step forward. 🔥",
        "The best developers just show up. You're showing up.",
    ],
    "happy": [
        "Good session.",
        "Solid work today.",
        "One session at a time.",
        "You're making progress, even when it doesn't feel like it.",
        "Every session adds up.",
        "Keep going.",
    ],
    "egg": [
        "Hi. I'm Pulse. I'll be watching. 👀",
        "New here. So are you, kind of. Let's figure this out together.",
        "Session logged. I'm keeping track.",
        "Still getting to know your patterns. Keep going.",
    ],
}


def _detect_mood(ctx: dict) -> str:
    hour = ctx.get("hour", 12)
    if 0 <= hour < 4:
        return "sleepy"
    if ctx.get("agent_just_finished"):
        return "excited"
    if ctx.get("streak_milestone") or ctx.get("level_up"):
        return "proud"
    if ctx.get("last_break_minutes_ago", 0) > 90 and ctx.get("sessions_today", 0) >= 3:
        return "worried"
    level = ctx.get("level", 1)
    if level <= 3:
        return "egg"
    return "happy"


def _call_claude(ctx: dict) -> str | None:
    prompt = SYSTEM_PROMPT.format(context_json=json.dumps(ctx))
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return None


def generate_message(ctx: dict) -> str:
    msg = _call_claude(ctx)
    if msg:
        return msg
    mood = _detect_mood(ctx)
    pool = FALLBACKS.get(mood, FALLBACKS["happy"])
    return random.choice(pool)


if __name__ == "__main__":
    ctx = {
        "sessions_today": 3,
        "total_time_today_minutes": 247,
        "hour": 1,
        "last_break_minutes_ago": 142,
        "streak_days": 4,
        "level": 7,
        "agent_just_finished": False,
    }
    if len(sys.argv) > 1:
        ctx = json.loads(sys.argv[1])
    print(generate_message(ctx))
