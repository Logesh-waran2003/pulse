#!/bin/sh
# Claude Code Stop hook — receives JSON on stdin
# Extract session_id from stdin JSON, pass to run.py
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null || echo "")
python3 ~/.pulse/run.py stop \
  --session-id "$SESSION_ID" \
  --cwd "${PWD:-}"
