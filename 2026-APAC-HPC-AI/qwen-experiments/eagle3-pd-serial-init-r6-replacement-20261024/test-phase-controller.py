"""CPU checks for the R6 bounded serial/concurrent warmup phase windows."""
import importlib.util, json, subprocess, sys
from pathlib import Path
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("phase_controller",O/"phase-controller.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.validate_budget()
t0=1_800_000_000
assert module.deadlines(t0)=={"t0":t0,"startup_deadline":t0+650,"serial_deadline":t0+740,"concurrent_deadline":t0+830,"teardown_deadline":t0+920,"main_envelope_deadline":t0+920}
assert module.remaining(t0,"startup",t0,t0)==650
assert module.remaining(t0,"serial",t0+650,t0+650)==90
assert module.remaining(t0,"concurrent",t0+740,t0+740)==90
assert module.remaining(t0,"teardown",t0+830,t0+830)==90
assert module.remaining(t0,"teardown",t0+920,t0+920)==0
assert module.deadline(t0,"serial",t0+100)==t0+190
assert module.deadline(t0,"serial",t0+700)==t0+740
assert module.MAIN_ENVELOPE_SECONDS<module.PBS_WALLTIME_SECONDS
r=subprocess.run([sys.executable,str(O/"phase-controller.py"),"remaining",str(t0),"concurrent",str(t0+740),str(t0+740)],capture_output=True,text=True)
assert r.returncode==0 and r.stdout.strip()=="90",r
(O/"phase-controller-validation.json").write_text(json.dumps({"passed":True,"phase_seconds":module.PHASE_SECONDS,"main_envelope_seconds":module.MAIN_ENVELOPE_SECONDS,"pbs_walltime_seconds":module.PBS_WALLTIME_SECONDS,"scope":"Pure CPU absolute-deadline checks for the serial and concurrent diagnostic phases."},indent=2)+"\n")
print("R6 phase controller fixture PASS")
