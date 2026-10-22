#!/usr/bin/env python3
"""Conditionally derive an N64/N68 short screen; --self-test never creates it."""
from pathlib import Path
import argparse, ast, hashlib, json, shutil, subprocess, tempfile, os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "serving-tuning-10/s28-h200-n62-n64-screen"
BUNDLE_ID = "s31-h200-n64-n68-screen"
BUNDLE = ROOT / "serving-tuning-10" / BUNDLE_ID
REVIEW = ROOT / "research-review-25366-20261022/REVIEW.json"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_review(proof):
    """Require an exact, fresh full N64 review and all stated local gates."""
    require(proof.get("job") == "25366", "formal review is not full N64 job 25366")
    require(proof.get("state") == "LOCAL_PROTOCOL_SLA_OUTPUT_PASS",
            "full N64 review did not pass local protocol/SLA/output gates")
    require(proof.get("full_scored_protocol_equal") is True,
            "review does not establish the full scored protocol")
    point = proof.get("point")
    summary = proof.get("summary")
    require(isinstance(point, dict) and point.get("job") == "25366"
            and point.get("concurrency") == 64, "review lacks the fresh N64 full point")
    metrics = point.get("metrics", {})
    require(metrics.get("sla_pass") is True, "full N64 point failed SLA")
    protocol = point.get("normalized_protocol", {})
    phases = protocol.get("phases", [])
    require(len(phases) == 2 and phases[0].get("duration") == 60.0
            and phases[1].get("duration") == 120.0
            and phases[1].get("grace_period") == 30.0,
            "full N64 point does not match 60/120/30 protocol")
    require(point.get("output_lengths", {}).get("count", 0) > 0,
            "full N64 point lacks scored output evidence")
    require(isinstance(summary, dict) and summary.get("phase") == "confirm"
            and summary.get("concurrency") == 64 and summary.get("sla_pass") is True,
            "review lacks a passing full-protocol N64 summary")
    require(summary.get("errors") == 0 and summary.get("cancelled_requests") == 0
            and summary.get("requests", 0) > 0,
            "full N64 review has errors/cancellations or no requests")
    output = point.get("short_output_comparison", {})
    require(output.get("research_eligible") is True
            and output.get("new_failed_cases") == [],
            "full N64 output behavior did not pass the local comparison")
    return True


def load_loop(benchmark_text):
    start = benchmark_text.index("for N in ${QWEN_TUNE_NS")
    end = benchmark_text.index("if [[ ${QWEN_DIAGNOSTIC_PROFILE", start)
    return benchmark_text[start:end]


def run_gate_fixtures(benchmark_text):
    """Run the inherited shell gate using synthetic CPU summaries only."""
    loop = load_loop(benchmark_text)
    results = []
    cases = (("pass", [64, 68]), ("sla_fail", [64]),
             ("request_error", [64]), ("no_time", []))
    with tempfile.TemporaryDirectory(prefix="n68-load-gate-") as temp:
        base = Path(temp)
        prefix = r'''set -euo pipefail
ART=$1
export ART
QWEN_TUNE_NS="64 68"
QWEN_BENCHMARK_DEADLINE=$(($(date +%s)+10000))
run_benchmark() {
  n=$1
  echo "$n" >> "$ART/calls"
  python3 - "$n" <<'FIXTURE'
import json, os, sys
from pathlib import Path
n=int(sys.argv[1]); case=os.environ['FIXTURE_CASE']
row={'phase':'screen','concurrency':n,
     'sla_pass': not (case=='sla_fail' and n==64),
     'cancelled_requests':0,
     'errors':int(case=='request_error' and n==64),
     'requests':10}
Path(os.environ['ART'],'summary.json').write_text(json.dumps([row]))
FIXTURE
}
'''
        for name, expected in cases:
            art = base / name
            art.mkdir()
            deadline = "QWEN_BENCHMARK_DEADLINE=0\n" if name == "no_time" else ""
            script = prefix + deadline + loop
            proc = subprocess.run(["bash", "-c", script, "n68-gate", str(art)],
                                  env={**os.environ, "FIXTURE_CASE": name},
                                  capture_output=True, text=True)
            require(proc.returncode == 0, f"{name} fixture failed: {proc.stderr}")
            calls = ([int(v) for v in (art / "calls").read_text().splitlines()]
                     if (art / "calls").exists() else [])
            require(calls == expected, f"{name}: ran {calls}, expected {expected}")
            results.append({"case": name, "loads_run": calls, "passed": True})
    return results


def review_fixtures():
    """Check pass, failure, error, and missing-review branches without file writes."""
    valid = {"job": "25366", "state": "LOCAL_PROTOCOL_SLA_OUTPUT_PASS",
        "full_scored_protocol_equal": True,
        "point": {"job": "25366", "concurrency": 64,
                  "metrics": {"sla_pass": True},
                  "normalized_protocol": {"phases": [
                      {"duration": 60.0},
                      {"duration": 120.0, "grace_period": 30.0}]},
                  "output_lengths": {"count": 100},
                  "short_output_comparison": {"research_eligible": True,"new_failed_cases": []}},
        "summary": {"phase": "confirm", "concurrency": 64,"sla_pass": True,
                    "errors": 0,"cancelled_requests": 0,"requests": 100}}
    validate_review(valid)
    failures = []
    for mutate in (
        lambda x: x.update(state="LOCAL_PROTOCOL_SLA_OUTPUT_FAIL"),
        lambda x: x["summary"].update(errors=1),
        lambda x: x["summary"].update(cancelled_requests=1),
        lambda x: x["point"]["short_output_comparison"].update(new_failed_cases=["reverse"]),
    ):
        bad = json.loads(json.dumps(valid)); mutate(bad)
        try: validate_review(bad)
        except ValueError: failures.append(True)
        else: failures.append(False)
    require(all(failures), "review failure/error fixtures were accepted")
    try: validate_review({})
    except ValueError: pass
    else: raise ValueError("missing future review fixture was accepted")
    return {"pass": True, "review_failures_rejected": len(failures)+1}


def assert_candidate_unused():
    require(not BUNDLE.exists(), f"refusing to overwrite existing candidate: {BUNDLE_ID}")
    registry_path = ROOT / "serving-tuning/registry.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text())
        require(not any(entry.get("id") == BUNDLE_ID for entry in registry.get("entries", [])),
                "candidate ID already exists in serving registry")
    pilots_path = ROOT / "serving-tuning-10/prepared-pilots.json"
    if pilots_path.exists():
        pilots = json.loads(pilots_path.read_text()).get("pilots", [])
        require(not any(pilot.get("id") == BUNDLE_ID for pilot in pilots),
                "candidate ID already exists in prepared pilot plan")


def verify_source():
    sums = SOURCE / "SHA256SUMS"
    require(sums.is_file(), "source bundle checksum manifest missing")
    subprocess.run(["sha256sum", "--check", "SHA256SUMS"], cwd=SOURCE,
                   check=True, capture_output=True, text=True)
    files = [line.split("  ", 1)[1] for line in sums.read_text().splitlines()]
    require(files and all((SOURCE / name).is_file() for name in files),
            "source manifest has missing files")
    return files


def create_bundle(proof, files):
    assert_candidate_unused()
    temp = BUNDLE.with_name("." + BUNDLE.name + ".preparing")
    require(not temp.exists(), "stale temporary candidate path; inspect before retry")
    temp.mkdir()
    try:
        for name in files:
            shutil.copyfile(SOURCE / name, temp / name)
        job = temp / "job.sbatch"
        text = job.read_text()
        require(text.count("ap42-s28-h200-n62-n64-screen") == 1,
                "unexpected source Slurm job name")
        require(text.count(str(SOURCE)) == 1, "unexpected source bundle path count")
        require(text.count('export QWEN_TUNE_NS="62 64"') == 1,
                "expected source offered-load list not found exactly once")
        expected_job = text.replace("ap42-s28-h200-n62-n64-screen", "ap42-" + BUNDLE_ID)
        expected_job = expected_job.replace(str(SOURCE), str(BUNDLE))
        expected_job = expected_job.replace('export QWEN_TUNE_NS="62 64"',
                                            'export QWEN_TUNE_NS="64 68"')
        text = expected_job
        require("#SBATCH -N 2" in text and "#SBATCH --gres=gpu:8" in text
                and "#SBATCH -t 00:17:00" in text,
                "source allocation no longer matches 16-H200/17-minute plan")
        job.write_text(text)
        config_path = temp / "config.json"
        config = json.loads(config_path.read_text())
        config.update(experiment=BUNDLE_ID, source_experiment=SOURCE.name,
            conditional_full_candidate_job="25366", concurrency=[64, 68],
            control_concurrency=64, candidate_concurrency=68,
            fresh_control_job="same deployment: screen/n64",
            matched_concurrency=None,
            changed_factor={"within_deployment_concurrency": [64, 68]},
            purpose="Conditional unranked N64->N68 short offered-load screen after fresh full N64 gate",
            phase="screen", confirm_warmup_s=20, confirm_measure_s=40,
            grace_s=30, screen_unranked=True, walltime_minutes=17,
            gpus=16, pbs_su_reserved=0, resource_monitor=True,
            quality_validation_required=True, practical_gain_gate_fraction=0.01,
            graph_maximum_decode=64,
            performance_comparison="N68 versus same-deployment observed N64; observer-off results are context only")
        config_path.write_text(json.dumps(config, indent=2) + "\n")
        worker = (temp / "worker.sh").read_text()
        require("--cuda-graph-max-bs-decode 64" in worker,
                "source decode graph cap changed")
        benchmark = (temp / "benchmark.sh").read_text()
        require('run_benchmark "$N" screen 20 40' in benchmark
                and '--warmup-duration "$WARM" --benchmark-duration "$DURATION"' in benchmark
                and '--benchmark-grace-period "${QWEN_GRACE:-30}"' in benchmark,
                "source short measurement protocol changed")
        require('export QWEN_TUNE_NS="64 68"' in job.read_text(),
                "derived load order is not 64 then 68")
        for name in files:
            if name in {"job.sbatch", "config.json"}: continue
            require((temp / name).read_bytes() == (SOURCE / name).read_bytes(),
                    f"serving/runtime observer file changed: {name}")
        for path in temp.glob("*.py"):
            ast.parse(path.read_text(), filename=str(path))
        for path in list(temp.glob("*.sh")) + [temp / "job.sbatch"]:
            subprocess.run(["bash", "-n", str(path)], check=True)
        (temp / "SHA256SUMS").write_text("".join(
            f"{sha(temp / name)}  {name}\n" for name in files))
        # Re-read the guarded proof immediately before making the candidate visible.
        validate_review(json.loads(REVIEW.read_text()))
        require(json.loads(REVIEW.read_text()) == proof,
                "formal review changed during preparation; inspect and rerun")
        temp.rename(BUNDLE)
    except BaseException:
        # Keep an interrupted temporary directory for inspection instead of erasing evidence.
        raise
    return {"bundle": str(BUNDLE), "id": BUNDLE_ID,
            "state": "PREPARED_NOT_SUBMITTED", "gpus": 16, "minutes": 17,
            "pbs_su_reserved": 0,
            "payload_sha256": {name: sha(BUNDLE / name) for name in files}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="exercise the inherited load gate and review guard using CPU fixtures only")
    args = parser.parse_args()
    if args.self_test:
        assert_candidate_unused()
        files = verify_source()
        text = (SOURCE / "benchmark.sh").read_text()
        fixtures = run_gate_fixtures(text)
        review_result = review_fixtures()
        print(json.dumps({"passed": True, "load_gate_fixtures": fixtures,
                          "review_gate_fixtures": review_result,
                          "source_files_checksum_verified": len(files),
                          "candidate_id_unused": True,
                          "scope": "CPU fixtures only; no candidate bundle created"}, indent=2))
        return
    assert_candidate_unused()
    require(REVIEW.is_file(), f"required future full N64 review is missing: {REVIEW}")
    proof = json.loads(REVIEW.read_text())
    validate_review(proof)
    files = verify_source()
    # Validate load gating before any candidate path is created.
    gate_fixtures = run_gate_fixtures((SOURCE / "benchmark.sh").read_text())
    receipt = create_bundle(proof, files)
    receipt["cpu_gate_fixtures"] = gate_fixtures
    (HERE / "prepared-candidate.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
