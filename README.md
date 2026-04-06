<div align="center">

# 💓 Pulse

**Your terminal has a heartbeat now.**

A companion for Claude Code that watches all your sessions, tracks your patterns, and talks to you like a caring friend — not a productivity tool.

```
npx pulse-dev install
```

</div>

---

## What it does

Pulse lives in Claude Code's **status bar** — always visible, every session.

```
Sonnet 4.6  ████░░░░ 57%  2h42m  $0.88
💓 (^.^)  lv.7 · Hatchling  🔥4d  "You're on a roll. I'll stay quiet 🤫"
```

- 💓 **Lives in your status bar** — visible during every session, not just after
- 🕐 **Watches ALL your sessions** — knows you've been coding 4 hours today
- 💧 **Tells you to drink water** after 2+ hours without a break
- 🎉 **Celebrates when your agent finishes** — "Come take a look 👀"
- 🌙 **Says close the laptop** when it's 1am
- 📈 **Grows as you code** — levels up from Egg → Hatchling → Companion → Legend

**Uses your existing Claude subscription. Zero extra cost. Zero extra API keys.**

---

## Demo

```
✓ Claude Code session ended (4m 32s)
─────────────────────────────────
  (^.^)
 /|   |\  Pulse · lv.7 · Hatchling · 🔥 4-day streak
  d   b

"That's session 3 today. You've been coding
 for 4h 12m. Drink some water before the
 next one? 💧"
─────────────────────────────────
```

```
● Subagent finished
─────────────────────────────────
  (^o^)
 /|   |\  Pulse · lv.7 · Hatchling
  d   b

"Done! Go review it before you forget
 what you asked for. 👀"
─────────────────────────────────
```

---

## Install

```bash
npx pulse-dev install
```

Requires: Python 3.8+ and Claude Code.

**Uninstall:**
```bash
npx pulse-dev uninstall
```

---

## How it works

Pulse has two parts:

**1. Status bar** — `statusLine` script runs after every assistant message, shows your creature live.

**2. Session hooks** — track sessions, log time, trigger alerts.

| Event | What Pulse does |
|---|---|
| `SessionStart` | Logs session start |
| `UserPromptSubmit` | Tracks activity |
| `Stop` | Logs duration, updates creature |
| `SubagentStop` | Triggers excited creature alert |

All data stays local in `~/.pulse/pulse.db`. No API keys. No external services.

## Configure

Edit `~/.pulse/config.json` to customize:

```json
{
  "persona": "adaptive",
  "show_cost": true,
  "show_duration": true,
  "show_streak": true,
  "show_level": true,
  "show_message": true,
  "creature_name": "Pulse"
}
```

**Personas:**
- `adaptive` — reads the room, adjusts tone (default)
- `caring` — warm, nurturing, like a friend who checks in
- `hype` — energetic, celebrates wins, roasts procrastination
- `zen` — calm, observational, minimal
- `silent` — creature only, no messages

---

## The creature

```
Lv 1–3   (o.o)  Egg
Lv 4–9   (^.^)  Hatchling
Lv 10–19 (^o^)  Companion
Lv 20–29 (★.★)  Veteran
Lv 30+   (⊙_⊙)  Legend
```

Mood changes based on context: happy, excited, sleepy, worried, proud.

---

## Why it's different from Crumpet

Anthropic shipped `/buddy` (Crumpet) for April Fools — a cute creature that watches you code inside Claude Code.

Pulse goes further:
- Works across **all** your sessions, not just the current one
- Has **cross-session memory** — knows you've been coding 4 hours today
- Gives **health nudges** — water, sleep, breaks
- **Alerts you** when agents finish
- **Evolves** based on your coding habits

---

## Contributing

PRs welcome for:
- New creature designs
- New personality modes
- Windows support
- Additional hook events

---

## License

MIT
