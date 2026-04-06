"""Single entry point for all Claude Code hooks."""
import argparse
import os
import sys
import time

# Add pulse dir to path
sys.path.insert(0, os.path.dirname(__file__))

import db
import generate
import creature


def _should_speak(ctx: dict) -> bool:
    if ctx.get("first_session_today"):
        return True
    if ctx.get("streak_milestone"):
        return True
    if ctx.get("level_up"):
        return True
    if ctx.get("agent_just_finished"):
        return True
    if ctx["sessions_today"] >= 3 and ctx["total_time_today_minutes"] > 180:
        return True
    if 0 <= ctx["hour"] < 4:
        return True
    if ctx["last_break_minutes_ago"] > 90:
        return True
    if 0 < ctx["session_duration_seconds"] < 120:
        return True
    return False


def cmd_session_start(args):
    db.init_db()
    db.log_session_start(args.cwd or os.getcwd(), args.session_id or "unknown")


def cmd_prompt_submit(args):
    db.set_state("last_prompt_at", str(int(time.time())))


def cmd_stop(args):
    session_id = args.session_id or "unknown"
    duration = args.duration or 0

    db.log_session_end(session_id, duration)
    ctx = db.get_context(session_id, duration)
    ctx["agent_just_finished"] = False

    if not _should_speak(ctx):
        return

    msg = generate.generate_message(ctx)
    block = creature.render(ctx, msg)
    print(f"\n{block}\n", flush=True)


def cmd_agent_stop(args):
    ctx = db.get_context()
    ctx["agent_just_finished"] = True

    msg = generate.generate_message(ctx)
    block = creature.render(ctx, msg)
    print(f"\n{block}\n", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Pulse hook runner")
    sub = parser.add_subparsers(dest="event")

    p = sub.add_parser("session-start")
    p.add_argument("--session-id", default="")
    p.add_argument("--cwd", default="")

    sub.add_parser("prompt-submit")

    p = sub.add_parser("stop")
    p.add_argument("--session-id", default="")
    p.add_argument("--duration", type=int, default=0)
    p.add_argument("--cwd", default="")

    sub.add_parser("agent-stop")

    args = parser.parse_args()

    if args.event == "session-start":
        cmd_session_start(args)
    elif args.event == "prompt-submit":
        cmd_prompt_submit(args)
    elif args.event == "stop":
        cmd_stop(args)
    elif args.event == "agent-stop":
        cmd_agent_stop(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
