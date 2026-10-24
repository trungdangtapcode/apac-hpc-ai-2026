#!/usr/bin/env python3
"""Absolute-deadline controller for a two-phase P/D initialization diagnostic."""
import argparse, json
PHASE_SECONDS = {"startup":650, "serial":90, "concurrent":90, "teardown":90}
MAIN_ENVELOPE_SECONDS = sum(PHASE_SECONDS.values())
PBS_WALLTIME_SECONDS = 1200
CUMULATIVE_CAPS = {"startup":650, "serial":740, "concurrent":830, "teardown":920}
def deadlines(t0):
 out={"t0":t0};elapsed=0
 for phase,duration in PHASE_SECONDS.items():
  elapsed+=duration;out[f"{phase}_deadline"]=t0+elapsed
 out["main_envelope_deadline"]=t0+MAIN_ENVELOPE_SECONDS
 return out
def deadline(t0,phase,phase_start):
 if phase not in PHASE_SECONDS: raise ValueError(f"unknown phase: {phase}")
 if phase=="startup" and phase_start!=t0: raise ValueError("startup phase must start at batch T0")
 return min(t0+CUMULATIVE_CAPS[phase],phase_start+PHASE_SECONDS[phase])
def remaining(t0,phase,phase_start,now):
 if now<phase_start: raise ValueError(f"{phase} phase has not started")
 return max(0,deadline(t0,phase,phase_start)-now)
def validate_budget():
 if MAIN_ENVELOPE_SECONDS!=920 or MAIN_ENVELOPE_SECONDS>=PBS_WALLTIME_SECONDS: raise AssertionError("phase envelope must fit within PBS walltime")
 if tuple(PHASE_SECONDS)!=("startup","serial","concurrent","teardown"): raise AssertionError("phase order changed")
def main():
 parser=argparse.ArgumentParser();parser.add_argument("command",choices=("deadlines","deadline","remaining","check"));parser.add_argument("t0",type=int);parser.add_argument("phase",nargs="?");parser.add_argument("phase_start",nargs="?",type=int);parser.add_argument("now",nargs="?",type=int);a=parser.parse_args();validate_budget()
 if a.command=="deadlines": print(json.dumps(deadlines(a.t0),sort_keys=True))
 elif a.command=="deadline":
  if a.phase is None or a.phase_start is None: parser.error("deadline requires PHASE PHASE_START")
  print(deadline(a.t0,a.phase,a.phase_start))
 else:
  if a.phase is None or a.phase_start is None or a.now is None: parser.error(f"{a.command} requires PHASE PHASE_START NOW")
  value=remaining(a.t0,a.phase,a.phase_start,a.now)
  if a.command=="check" and value<=0: raise SystemExit(f"phase deadline expired: {a.phase}")
  print(value)
 return 0
if __name__=="__main__": raise SystemExit(main())
