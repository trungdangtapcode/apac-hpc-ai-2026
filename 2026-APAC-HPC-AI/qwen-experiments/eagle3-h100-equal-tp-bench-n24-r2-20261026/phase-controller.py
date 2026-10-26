#!/usr/bin/env python3
"""Absolute allocation-relative deadlines for startup, one request, full benchmark and teardown."""
import argparse
import json

PHASE_SECONDS = {"startup": 850, "semantic": 240, "scoring": 300, "quality": 250, "teardown": 80}
PBS_WALLTIME_SECONDS = 1800
ENVELOPE_SECONDS = sum(PHASE_SECONDS.values())
CUMULATIVE = {"startup": 850, "semantic": 1090, "scoring": 1390, "quality": 1640, "teardown": 1720}


def validate_budget():
    if ENVELOPE_SECONDS >= PBS_WALLTIME_SECONDS:
        raise ValueError("phase envelope must leave PBS walltime margin")
    if tuple(PHASE_SECONDS) != ("startup", "semantic", "scoring", "quality", "teardown"):
        raise ValueError("phase order changed")


def deadline(t0: int, phase: str, start: int) -> int:
    if phase not in PHASE_SECONDS:
        raise ValueError(f"unknown phase: {phase}")
    if phase == "startup" and start != t0:
        raise ValueError("startup must start at allocation T0")
    return min(t0 + CUMULATIVE[phase], start + PHASE_SECONDS[phase])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("deadlines", "deadline", "remaining"))
    parser.add_argument("t0", type=int)
    parser.add_argument("phase", nargs="?")
    parser.add_argument("phase_start", nargs="?", type=int)
    parser.add_argument("now", nargs="?", type=int)
    args = parser.parse_args()
    validate_budget()
    if args.command == "deadlines":
        print(json.dumps({"t0": args.t0, **{f"{p}_deadline": args.t0 + CUMULATIVE[p] for p in PHASE_SECONDS},
                          "main_envelope_seconds": ENVELOPE_SECONDS}, sort_keys=True))
    else:
        if args.phase is None or args.phase_start is None:
            parser.error(f"{args.command} needs PHASE and PHASE_START")
        end = deadline(args.t0, args.phase, args.phase_start)
        if args.command == "deadline":
            print(end)
        else:
            if args.now is None:
                parser.error("remaining needs NOW")
            print(max(0, end - args.now))


if __name__ == "__main__":
    main()
