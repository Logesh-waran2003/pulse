#!/bin/sh
cat > /dev/null  # consume stdin
python3 ~/.pulse/run.py agent-stop
