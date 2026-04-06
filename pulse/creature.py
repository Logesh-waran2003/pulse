"""ASCII creature renderer. No external dependencies."""


ANSI = {
    "reset":  "\033[0m",
    "blue":   "\033[94m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "orange": "\033[33m",
    "purple": "\033[95m",
    "gray":   "\033[90m",
    "bold":   "\033[1m",
}

MOODS = {
    "happy":   {"face": "(^.^)", "color": "blue"},
    "excited": {"face": "(^o^)", "color": "green"},
    "sleepy":  {"face": "(-_-)", "color": "yellow"},
    "worried": {"face": "(>.<)", "color": "orange"},
    "proud":   {"face": "(^_^)", "color": "purple"},
    "egg":     {"face": "(o.o)", "color": "gray"},
}

LEVELS = [
    (1,   10,  "Egg",       "egg"),
    (11,  30,  "Hatchling", "happy"),
    (31,  75,  "Companion", "excited"),
    (76,  150, "Veteran",   "proud"),
    (151, 999, "Legend",    "proud"),
]

FACES = {
    "egg":     "(o.o)",
    "happy":   "(^.^)",
    "excited": "(^o^)",
    "sleepy":  "(-_-)",
    "worried": "(>.<)",
    "proud":   "(^_^)",
    "legend":  "(⊙_⊙)",
}


def _get_level_info(level: int) -> tuple[str, str]:
    """Returns (tier_name, default_mood) for a given level."""
    for lo, hi, name, mood in LEVELS:
        if lo <= level <= hi:
            if level >= 151:
                return name, "legend"
            return name, mood
    return "Legend", "legend"


def _get_mood(ctx: dict) -> str:
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
    _, default_mood = _get_level_info(level)
    return default_mood


def _streak_badge(streak: int) -> str:
    if streak >= 30:
        return "🔥🔥🔥"
    if streak >= 14:
        return "🔥🔥"
    if streak >= 3:
        return "🔥"
    return ""


def render(ctx: dict, message: str) -> str:
    level = ctx.get("level", 1)
    streak = ctx.get("streak_days", 0)
    mood = _get_mood(ctx)
    tier_name, _ = _get_level_info(level)

    face = FACES.get(mood, "(^.^)")
    color_key = MOODS.get(mood, MOODS["happy"])["color"]
    color = ANSI[color_key]
    reset = ANSI["reset"]
    bold = ANSI["bold"]

    badge = _streak_badge(streak)
    streak_str = f" · {badge} {streak}-day streak" if streak >= 3 else ""

    header = f"{bold}{color}─────────────────────────────────{reset}"
    label = f"{bold}{color}Pulse · lv.{level} · {tier_name}{streak_str}{reset}"

    lines = [
        header,
        f"  {color}{face}{reset}",
        f" /|   |\\  {label}",
        f"  d   b",
        f"",
        f'"{message}"',
        header,
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # Show all moods
    ctx_base = {"level": 7, "streak_days": 4, "sessions_today": 3, "last_break_minutes_ago": 30}
    moods_to_test = [
        ({**ctx_base, "hour": 2}, "It's late. Save and close."),
        ({**ctx_base, "agent_just_finished": True}, "Agent's done. Go check what it built."),
        ({**ctx_base, "streak_milestone": True}, "7 days straight. You're unstoppable."),
        ({**ctx_base, "last_break_minutes_ago": 120, "sessions_today": 4}, "Take 5 minutes. Water. Stretch."),
        (ctx_base, "Good session. Keep it up."),
        ({"level": 1, "streak_days": 0, "sessions_today": 1, "last_break_minutes_ago": 0}, "Hi. I'm Pulse. I'll be watching."),
    ]
    for ctx, msg in moods_to_test:
        print(render(ctx, msg))
        print()
