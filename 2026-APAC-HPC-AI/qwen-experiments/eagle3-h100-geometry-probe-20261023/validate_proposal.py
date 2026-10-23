#!/usr/bin/env python3
"""Reproducible local integrity, syntax, and CPU-fixture validation."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAYLOAD = ROOT / "payload"
PROVENANCE = json.loads((ROOT / "SOURCE_PROVENANCE.json").read_text())
checks = []
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def require(label: str, condition: bool, detail: str = "") -> None:
    checks.append({"check": label, "passed": bool(condition), "detail": detail})
    if not condition:
        raise AssertionError(f"{label}: {detail}")

manifest = subprocess.run(["sha256sum", "--check", "SHA256SUMS"], cwd=PAYLOAD, capture_output=True, text=True)
require("payload_sha256_manifest", manifest.returncode == 0, manifest.stdout.strip() + manifest.stderr.strip())

for name, record in PROVENANCE["source_files"].items():
    path = Path(record["path"])
    require(f"source:{name}", path.is_file() and sha(path) == record["sha256"], str(path))
require("derived_nixl_digest", sha(PAYLOAD / "nixl-conn-instrumented.py") == PROVENANCE["derived_module_sha256"], "instrumented module matches reviewed derived source")
require("geometry_helper_digest", sha(PAYLOAD / "kv_geometry.py") == PROVENANCE["geometry_helper_sha256"], "geometry helper matches reviewed source")
require("shared_value_validator_digest", sha(PAYLOAD / "geometry_value_validator.py") == PROVENANCE["shared_value_validator_sha256"], "strict validator is byte-identical to reviewed shared validator")
copy_map = {
    "capture-worker-locality.py": "base_capture_worker_locality",
    "resource-sampler.py": "base_resource_sampler",
    "verify-draft.py": "base_verify_draft_py",
    "asset-contract.json": "base_asset_contract",
    "target-staging-record.json": "base_target_staging_record",
    "expected-source.json": "base_expected_source",
}
for copied, source_key in copy_map.items():
    expected = PROVENANCE["source_files"][source_key]["sha256"]
    require(f"copy:{copied}", sha(PAYLOAD / copied) == expected, "exact source byte copy")

scripts = [PAYLOAD / "component.pbs", PAYLOAD / "entry.sh", PAYLOAD / "worker.sh"]
for script in scripts:
    result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    require(f"bash_syntax:{script.name}", result.returncode == 0, result.stderr.strip())
for path in sorted(PAYLOAD.glob("*.py")):
    result = subprocess.run([sys.executable, "-m", "py_compile", str(path)], capture_output=True, text=True)
    require(f"python_syntax:{path.name}", result.returncode == 0, result.stderr.strip())

result = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_probe.py"], cwd=ROOT,
                        capture_output=True, text=True)
checks.append({"check": "adversarial_cpu_fixtures", "passed": result.returncode == 0,
               "detail": (result.stdout + result.stderr).strip()})
if result.returncode:
    raise SystemExit(result.returncode)

# Verify the absolute timing contract and dynamic ID flow without executing PBS or a cluster command.
component = (PAYLOAD / "component.pbs").read_text()
entry = (PAYLOAD / "entry.sh").read_text()
checker = (PAYLOAD / "check_probe.py").read_text()
require("single_absolute_deadlines", all(x in component for x in ["T0=$(date +%s)", "T0 + 1100", "T0 + 1140", "T0 + 1170"]), "single T0 and absolute startup/check/cleanup bounds")
require("dynamic_experiment_id", "${PBS_JOBID}-${job_uuid}" in component and "QWEN_EXPERIMENT_ID=\"$experiment_id\"" in component and 'experiment_id=$3' in entry and 'experiment_id, job_id, context_path' in checker, "PBS job ID plus UUID passed across container and checker")
require("bounded_cleanup", "cleanup_end=$(( $(date +%s) + 15 ))" in component and "timeout --signal=TERM --kill-after=5s" in component, "container cleanup is bounded within T0+1170")

validation = {"schema": "eagle3-h100-geometry-proposal-validation-v1", "passed": all(c["passed"] for c in checks),
              "scope": "Local prospective-payload integrity, shell/Python syntax, and CPU adversarial fixtures only; no cluster access, submission, GPU run, performance result, or reservation.",
              "checks": checks}
(ROOT / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
print(json.dumps({"passed": validation["passed"], "check_count": len(checks)}, sort_keys=True))
