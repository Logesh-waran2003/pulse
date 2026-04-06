#!/bin/sh
# CLAUDE_SESSION_DURATION is in seconds, provided by the Stop hook
python3 ~/.pulse/run.py stop \
  --session-id "${CLAUDE_SESSION_ID:-}" \
  --duration "${CLAUDE_SESSION_DURATION:-0}" \
  --cwd "${PWD:-}"
