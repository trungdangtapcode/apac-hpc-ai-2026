"""CPU checks for absolute phase windows and PBS walltime headroom."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

O = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("phase_controller", O / "phase-controller.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.validate_budget()
t0 = 1_800_000_000
d = module.deadlines(t0)
assert d == {"t0": t0, "startup_deadline": t0 + 900,
            "warmup_deadline": t0 + 1080, "client_deadline": t0 + 1380,
            "head_deadline": t0 + 1440, "teardown_deadline": t0 + 1530,
            "main_envelope_deadline": t0 + 1530}
assert module.remaining(t0, "startup", t0, t0) == 900
assert module.remaining(t0, "warmup", t0 + 900, t0 + 900) == 180
assert module.remaining(t0, "client", t0 + 1080, t0 + 1080) == 300
assert module.remaining(t0, "head", t0 + 1380, t0 + 1380) == 60
assert module.remaining(t0, "teardown", t0 + 1440, t0 + 1440) == 90
assert module.remaining(t0, "teardown", t0 + 1530, t0 + 1530) == 0
assert module.deadline(t0, "warmup", t0 + 100) == t0 + 280
assert module.deadline(t0, "warmup", t0 + 950) == t0 + 1080
assert module.MAIN_ENVELOPE_SECONDS < module.PBS_WALLTIME_SECONDS
result = subprocess.run([sys.executable, str(O / "phase-controller.py"), "remaining",
                         str(t0), "client", str(t0 + 1080), str(t0 + 1080)], capture_output=True, text=True)
assert result.returncode == 0 and result.stdout.strip() == "300", result
(O / "phase-controller-validation.json").write_text(json.dumps({
    "passed": True,
    "phase_seconds": module.PHASE_SECONDS,
    "main_envelope_seconds": module.MAIN_ENVELOPE_SECONDS,
    "pbs_walltime_seconds": module.PBS_WALLTIME_SECONDS,
    "scope": "Pure CPU absolute-deadline and phase-budget checks; no PBS or GPU access."
}, indent=2) + "\n")
print("R4 phase controller fixture PASS")
