#!/bin/sh
python3 ~/.pulse/run.py session-start \
  --session-id "${CLAUDE_SESSION_ID:-}" \
  --cwd "${PWD:-}"
