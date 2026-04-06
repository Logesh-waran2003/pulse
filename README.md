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

- 🕐 **Watches all your sessions** — knows how long you've been coding today
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

Pulse hooks into Claude Code's event system:

| Event | What Pulse does |
|---|---|
| `SessionStart` | Logs session start |
| `UserPromptSubmit` | Tracks activity |
| `Stop` | Logs duration, maybe speaks |
| `SubagentStop` | Always alerts you |

All data stays local in `~/.pulse/pulse.db`. Pulse uses a Claude subagent (your existing subscription) to generate messages — no extra API keys needed.

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
