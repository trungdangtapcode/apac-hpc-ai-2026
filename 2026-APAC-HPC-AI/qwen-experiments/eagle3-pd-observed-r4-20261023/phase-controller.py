#!/usr/bin/env python3
"""Pure absolute-deadline controller seams for the bounded PBS allocation."""

import argparse
import json


PHASE_SECONDS = {
    "startup": 900,
    "warmup": 180,
    "client": 300,
    "head": 60,
    "teardown": 90,
}
MAIN_ENVELOPE_SECONDS = sum(PHASE_SECONDS.values())
PBS_WALLTIME_SECONDS = 1800
CUMULATIVE_CAPS = {
    "startup": 900,
    "warmup": 1080,
    "client": 1380,
    "head": 1440,
    "teardown": 1530,
}


def deadlines(t0: int) -> dict[str, int]:
    result = {"t0": t0}
    elapsed = 0
    for phase, duration in PHASE_SECONDS.items():
        elapsed += duration
        result[f"{phase}_deadline"] = t0 + elapsed
    result["main_envelope_deadline"] = t0 + MAIN_ENVELOPE_SECONDS
    return result


def deadline(t0: int, phase: str, phase_start: int) -> int:
    if phase not in PHASE_SECONDS:
        raise ValueError(f"unknown phase: {phase}")
    if phase == "startup" and phase_start != t0:
        raise ValueError("startup phase must start at batch T0")
    return min(t0 + CUMULATIVE_CAPS[phase], phase_start + PHASE_SECONDS[phase])


def remaining(t0: int, phase: str, phase_start: int, now: int) -> int:
    if now < phase_start:
        raise ValueError(f"{phase} phase has not started")
    return max(0, deadline(t0, phase, phase_start) - now)


def validate_budget() -> None:
    if MAIN_ENVELOPE_SECONDS != 1530 or MAIN_ENVELOPE_SECONDS >= PBS_WALLTIME_SECONDS:
        raise AssertionError("main absolute phase envelope must remain below PBS walltime")
    if tuple(PHASE_SECONDS) != ("startup", "warmup", "client", "head", "teardown"):
        raise AssertionError("phase order changed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("deadlines", "deadline", "remaining", "check"))
    parser.add_argument("t0", type=int)
    parser.add_argument("phase", nargs="?")
    parser.add_argument("phase_start", nargs="?", type=int)
    parser.add_argument("now", nargs="?", type=int)
    args = parser.parse_args()
    validate_budget()
    if args.command == "deadlines":
        print(json.dumps(deadlines(args.t0), sort_keys=True))
    elif args.command == "deadline":
        if args.phase is None or args.phase_start is None:
            parser.error("deadline requires PHASE PHASE_START")
        print(deadline(args.t0, args.phase, args.phase_start))
    elif args.command == "remaining":
        if args.phase is None or args.phase_start is None or args.now is None:
            parser.error("remaining requires PHASE PHASE_START NOW")
        print(remaining(args.t0, args.phase, args.phase_start, args.now))
    else:
        if args.phase is None or args.phase_start is None or args.now is None:
            parser.error("check requires PHASE PHASE_START NOW")
        value = remaining(args.t0, args.phase, args.phase_start, args.now)
        if value <= 0:
            raise SystemExit(f"phase deadline expired: {args.phase}")
        print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
