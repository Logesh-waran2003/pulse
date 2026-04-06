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

Pulse lives in your **status bar** — visible during every message, not just after the session.

[![Demo](https://asciinema.org/a/BvzkDmh2UN81PZt0.svg)](https://asciinema.org/a/BvzkDmh2UN81PZt0)

```
Sonnet 4.6  ████░░░░ 23%  1h13m today  $0.12
💓 (^.^)  lv.7 · Hatchling  🔥4d  "You're on a roll. I'll stay quiet 🤫"
```

```
Sonnet 4.6  ████████ 85%  3h42m today  $2.50
💓 (>.<)  lv.7 · Hatchling  🔥4d  "Drink some water before the next one. 💧"
```

```
Sonnet 4.6  █░░░░░░░ 12%  0m today  $0.02
💓 (o.o)  lv.1 · Egg  "Hi. I'm Pulse. I'll be watching. 👀"
```

```
Sonnet 4.6  ████░░░░ 45%  2h10m today  $0.55
💓 (^o^)  lv.7 · Hatchling  🔥4d  "Your agent finished! Go take a look 👀"
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
Lv 1–10    (o.o)  Egg         first week
Lv 11–30   (^.^)  Hatchling   2–3 weeks
Lv 31–75   (^o^)  Companion   1–2 months
Lv 76–150  (★.★)  Veteran     3–6 months
Lv 151+    (⊙_⊙)  Legend      6+ months
```

Mood changes based on context: happy, excited, sleepy, worried, proud.

---

## Why it's different from /buddy

Anthropic shipped `/buddy` for April Fools — 18 species, gacha rarity, hats, chaos/wisdom stats. A fun easter egg buried in the code.

Pulse is different:
- **Lives in the status bar** — always visible, not a hidden easter egg
- **Cross-session memory** — knows you've been coding 4 hours today
- **Health nudges** — water, sleep, breaks
- **Agent alerts** — notifies when your subagent finishes
- **Evolves** based on your coding habits
- **Configurable personas** — caring, hype, zen, silent

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
