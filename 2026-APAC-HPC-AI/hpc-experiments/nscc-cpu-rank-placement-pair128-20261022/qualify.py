"""Offline qualification against retained native evidence; never launches MPI.

Synthetic topology and directory fixtures test validation logic only. They are
not scheduler, placement, mesh or solver-performance evidence for this bundle.
"""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import runpy
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
PAYLOAD = ROOT / "payload"


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


def main():
    manifest = json.loads((ROOT / "payload-sha256.json").read_text())["files"]
    assert set(manifest) == {p.name for p in PAYLOAD.iterdir() if p.is_file()}
    for name, expected in manifest.items():
        assert hashlib.sha256((PAYLOAD / name).read_bytes()).hexdigest() == expected
    subprocess.run(["bash", "-n", str(PAYLOAD / "pair.pbs")], check=True)
    for path in PAYLOAD.glob("*.py"):
        compile(path.read_text(), str(path), "exec")
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "python_version": sys.version, "payload_hashes_verified": len(manifest),
              "bash_and_python_syntax_passed": True, "native_validator_replays": {}}
    with tempfile.TemporaryDirectory(prefix="hpc-placement-qualification-") as folder:
        temp = Path(folder)
        old = BASE / "nscc-cpu-method-pair128-20261021/collected/25907325.pbs101/runs/25907325"
        for role in ("control", "candidate"):
            output = temp / (role + ".json")
            check = run(PAYLOAD / "validate-solve.py", old / role, output)
            assert check.returncode == 0, check.stderr
            reviewed = json.loads(output.read_text())
            assert reviewed["native_timer_samples"] == 39 and reviewed["passed"]
            result["native_validator_replays"][role] = {
                "source": str((old / role).relative_to(BASE)),
                "average_seconds_step_historical": reviewed["average_seconds_step"],
                "max_log_timer_difference_seconds": max(v["absolute_difference_seconds"] for v in reviewed["log_vs_time_function_samples"]),
                "scope": "Historical validator replay, not a result for this unsubmitted pair"}

        probe = BASE / "nscc-cpu-scotch-numa-pair128-20261021/collected-files-only/25907753.pbs101/runs/25907753/rank-placement.jsonl"
        rows = [json.loads(line) for line in probe.read_text().splitlines() if line.strip()]
        check = run(PAYLOAD / "validate-rank-probe.py", "default", probe)
        assert check.returncode == 0, check.stderr
        rendered = run(PAYLOAD / "render_binding.py", PAYLOAD / "placement-screen.json", probe)
        assert rendered.returncode == 0, rendered.stderr
        expected = json.loads(rendered.stdout)
        binding = temp / "binding.json"
        binding.write_text(json.dumps(expected))
        by_cpu = {row["affinity"][0]: row for row in rows}
        candidate = []
        for target in expected["expected_rank_mapping"]:
            row = copy.deepcopy(by_cpu[target["cpu"]])
            row["rank"] = target["rank"]
            candidate.append(row)
        candidate_probe = temp / "candidate.jsonl"
        candidate_probe.write_text("".join(json.dumps(row) + "\n" for row in candidate))
        check = run(PAYLOAD / "validate-rank-probe.py", "candidate", candidate_probe, binding)
        assert check.returncode == 0, check.stderr
        result["historical_default_probe_logic_passed"] = True
        result["synthetic_candidate_probe_logic_passed"] = True
        rejected = []
        for label in ("duplicate_cpu", "duplicate_rank", "mixed_hosts", "wrong_candidate_binding"):
            bad = copy.deepcopy(candidate)
            if label == "duplicate_cpu":
                bad[1]["affinity"] = bad[0]["affinity"]
            elif label == "duplicate_rank":
                bad[1]["rank"] = bad[0]["rank"]
            elif label == "mixed_hosts":
                bad[1]["host"] = "synthetic-other-host"
            else:
                for key in ("affinity", "numa_nodes", "physical_core"):
                    bad[0][key], bad[1][key] = bad[1][key], bad[0][key]
            path = temp / (label + ".jsonl")
            path.write_text("".join(json.dumps(row) + "\n" for row in bad))
            check = run(PAYLOAD / "validate-rank-probe.py", "candidate", path, binding)
            assert check.returncode != 0, "Invalid topology accepted: " + label
            rejected.append(label)
        result["invalid_topology_fixtures_rejected"] = rejected
        # Exercise the actual directory-list helpers used by verify_case. This
        # fixture has no fields/mesh and is never claimed to pass verify_case.
        helper = runpy.run_path(str(PAYLOAD / "verify-inputs.py"))
        names = temp / "directory-list-fixture"
        names.mkdir()
        for rank in reversed(range(128)):
            (names / ("processor" + str(rank))).mkdir()
        assert helper["processor_names"](names) == helper["expected_processor_names"](128)
        (names / "processor127").rmdir()
        assert helper["processor_names"](names) != helper["expected_processor_names"](128)
        result["processor_name_fixture_passed_and_missing_rank_rejected"] = True
    result.update({"state": "STATIC_QUALIFICATION_PASS_UNSUBMITTED",
                   "runtime_binding_or_performance_measured": False,
                   "remote_source_case_validated_on_new_allocation": False,
                   "cluster_SU_spent_by_qualification": 0,
                   "limits": "Historical validator replay and synthetic guard fixtures only; no MPI process, solver, remote modification, scheduler or budget action."})
    (ROOT / "qualification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
