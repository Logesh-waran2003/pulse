#!/bin/sh
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null || echo "")
CWD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null || echo "${PWD:-}")
python3 ~/.pulse/run.py session-start \
  --session-id "$SESSION_ID" \
  --cwd "$CWD"
