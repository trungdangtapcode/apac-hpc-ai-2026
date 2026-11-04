#!/usr/bin/env python3
"""Bounded Open MPI tiny-Allreduce qualification driver for Iris."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import math

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
CANDIDATE = ["--mca", "coll", "tuned,basic,libnbc,self",
             "--mca", "coll_tuned_priority", "100",
             "--mca", "coll_tuned_use_dynamic_rules", "1",
             "--mca", "coll_tuned_allreduce_algorithm", "3"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def record_command(name, argv, timeout=15):
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, timeout=timeout, check=False)
        text = p.stdout
        result = {"argv": argv, "returncode": p.returncode, "output": text}
    except (OSError, subprocess.TimeoutExpired) as exc:
        text = str(exc)
        result = {"argv": argv, "error": text}
    (ROOT / (name if name.endswith((".txt", ".log")) else name+".txt")).write_text(text, encoding="utf-8")
    return result


def selection_evidence(text, component):
    lines = [line.strip() for line in text.splitlines()
             if re.search(r"select|selected|component", line, re.I)
             and re.search(r"coll|tuned|basic|libnbc|self", line, re.I)]
    needle = re.compile(r"\btuned\b", re.I) if component == "tuned" else re.compile(r"\b(?:basic|libnbc|self)\b", re.I)
    selected = any(needle.search(line) and re.search(r"\bselect(?:ing|ed)\s+(?:component\s+)?"+re.escape(component)+r"\b", line, re.I) and not re.search(r"\bnot\b|disabled|failed", line, re.I) for line in lines)
    return {"selected_component_observed": component if selected else None,
            "selection_lines": lines}


def launch(name, extra, app_args, limit):
    mpirun = shutil.which("mpirun")
    if not mpirun:
        return {"name": name, "status": "unavailable", "reason": "mpirun not found"}
    argv = [mpirun] + extra + ["--report-bindings", "--display-map", "-np", "56", str(ROOT / "microbench")] + app_args
    outpath = RUNS / name / "stdout-stderr.log"
    start = time.monotonic()
    try:
        p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, timeout=limit, check=False)
        output = p.stdout
        item = {"name": name, "argv": argv, "returncode": p.returncode,
                "elapsed_seconds": time.monotonic() - start, "status": "completed" if p.returncode == 0 else "failed"}
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "replace")
        output = stdout + "\nTIMEOUT\n" + stderr
        item = {"name": name, "argv": argv, "status": "timeout",
                "elapsed_seconds": time.monotonic() - start}
    (RUNS / name / "stdout-stderr.log").write_text(output, encoding="utf-8", errors="replace")
    item["binding_by_rank"]={m.group(1):m.group(2).strip() for m in re.finditer(r"Rank\s+(\d+)\s+bound to\s+([^\n]+)", output, re.I)}
    item.update(selection_evidence(output, "tuned" if "candidate" in name else "default"))
    return item


def evaluate(results):
    """Require >=10% lower median and p95 in both adjacent ABBA pairs."""
    names = [r.get("name") for r in results]
    if names != ["A1", "B1", "B2", "A2"]:
        return {"promotion_gate": "UNAVAILABLE", "reason": "launch order is not ABBA"}
    maps=[r.get("binding_by_rank",{}) for r in results]
    if any(set(m)!=set(map(str,range(56))) for m in maps) or any(m!=maps[0] for m in maps[1:]):
        return {"promotion_gate":"UNAVAILABLE","reason":"56-rank binding maps unavailable or not identical"}
    records = {}
    for name in names:
        p = RUNS / name / "result.json"
        try:
            records[name] = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"promotion_gate": "UNAVAILABLE", "reason": f"missing/invalid {name} result: {exc}"}
        if records[name].get("correctness") != "PASS":
            return {"promotion_gate": "UNAVAILABLE", "reason": f"correctness failed for {name}"}
        if records[name].get("ranks")!=56 or records[name].get("iterations_per_block")!=1000:
            return {"promotion_gate":"UNAVAILABLE","reason":"wrong rank/iteration count"}
        for payload in records[name].get("payloads",[]):
            if payload.get("count") not in (1,8) or len(payload.get("blocks",[]))!=2:
                return {"promotion_gate":"UNAVAILABLE","reason":"invalid payload/block shape"}
            for block in payload["blocks"]:
                raw=block.get("raw_worst_rank_seconds",[])
                if len(raw)!=1000 or any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0 for x in raw):
                    return {"promotion_gate":"UNAVAILABLE","reason":"invalid timing samples"}
                ordered=sorted(raw)
                if any(abs(block[k]-ordered[i])>1e-9 for k,i in [("median_worst_rank_seconds",499),("p95_worst_rank_seconds",949)]):
                    return {"promotion_gate":"UNAVAILABLE","reason":"nearest-rank quantile replay failed"}
    comparisons = []
    # Both within-process blocks are checked in both adjacent matched contrasts.
    for a_name, b_name in [("A1", "B1"), ("A2", "B2")]:
        a_payloads = {p["count"]: p for p in records[a_name]["payloads"]}
        b_payloads = {p["count"]: p for p in records[b_name]["payloads"]}
        for count in (1, 8):
            if count not in a_payloads or count not in b_payloads:
                return {"promotion_gate": "UNAVAILABLE", "reason": f"missing count {count}"}
            for block in range(2):
                a = a_payloads[count]["blocks"][block]
                b = b_payloads[count]["blocks"][block]
                comparisons.append({"control": a_name, "candidate": b_name, "count": count, "block": block + 1,
                    "median_reduction_fraction": (a["median_worst_rank_seconds"] - b["median_worst_rank_seconds"]) / a["median_worst_rank_seconds"],
                    "p95_reduction_fraction": (a["p95_worst_rank_seconds"] - b["p95_worst_rank_seconds"]) / a["p95_worst_rank_seconds"]})
    passed = all(x["median_reduction_fraction"] >= 0.10 and x["p95_reduction_fraction"] >= 0.10 for x in comparisons)
    return {"promotion_gate": "PASS" if passed else "CLOSED_NO_QUALIFYING_BENEFIT",
            "rule": "every block in both adjacent ABBA contrasts for counts 1 and 8 must have median and p95 >=10% lower",
            "comparisons": comparisons}

def main():
    os.chdir(ROOT)
    assert os.environ.get("SLURM_NTASKS")=="56" and os.environ.get("SLURM_JOB_NUM_NODES")=="1", "one56-rank compute allocation required"
    for name in ["A1","B1","B2","A2","probe-control","probe-candidate"]:
        (RUNS/name).mkdir(parents=True,exist_ok=True)
    src_hash_before = sha256(ROOT / "microbench.c")
    mpicc = shutil.which("mpicc")
    mpirun = shutil.which("mpirun")
    if not mpicc or not mpirun:
        (ROOT / "qualification.json").write_text(json.dumps({
            "status": "NOT_RUN", "reason": "mpicc or mpirun unavailable",
            "mpicc_path": mpicc, "mpirun_path": mpirun,
            "source_sha256_before": src_hash_before,
            "source_sha256_after": sha256(ROOT / "microbench.c")}, indent=2) + "\n")
        return 0

    compile_result = record_command("compile.log", [mpicc, "-O2", "-Wall", "-Wextra",
                                                       "microbench.c", "-lm", "-o", "microbench"], 30)
    if compile_result.get("returncode") != 0:
        (ROOT / "qualification.json").write_text(json.dumps({
            "status": "UNAVAILABLE", "reason": "microbenchmark compilation failed",
            "compile": compile_result, "source_sha256_before": src_hash_before,
            "source_sha256_after": sha256(ROOT / "microbench.c")}, indent=2) + "\n")
        return 0

    version = record_command("mpirun-version.txt", [mpirun, "--version"])
    compiler_version = record_command("mpicc-version.txt", [mpicc, "--showme:version"])
    info_cmd = shutil.which("ompi_info")
    info_version = record_command("ompi-info-version.txt", [info_cmd, "--version"]) if info_cmd else {"error": "ompi_info unavailable"}
    tuned = record_command("ompi-tuned-info.txt", [info_cmd, "--param", "coll", "tuned", "--level", "9"]) if info_cmd else {"error": "ompi_info unavailable"}
    ucx_cmd = shutil.which("ucx_info")
    ucx = record_command("ucx-info-version.txt", [ucx_cmd, "-v"]) if ucx_cmd else {"error": "ucx_info unavailable"}
    tuned_text = (ROOT / "ompi-tuned-info.txt").read_text(encoding="utf-8", errors="replace") if info_cmd else ""
    supports = bool(re.search(r"allreduce.*algorithm|algorithm.*allreduce", tuned_text, re.I)
                    and re.search(r"recursive.?doubling", tuned_text, re.I)
                    and re.search(r"(?:^|\D)3(?:\D|$)", tuned_text))
    meta = {"mpicc_path": mpicc, "mpirun_path": mpirun,
            "mpicc_sha256": sha256(Path(mpicc).resolve()), "mpirun_sha256": sha256(Path(mpirun).resolve()),
            "compiler_version": compiler_version, "mpi_version": version,
            "ompi_info_path": info_cmd, "ompi_info_version": info_version, "tuned_info": tuned,
            "ucx_info_path": ucx_cmd, "ucx_info": ucx,
            "source_sha256_before": src_hash_before,
            "binary_sha256": sha256(ROOT / "microbench"),
            "candidate_algorithm3_documented": supports}
    (ROOT / "qualifier-metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    if not supports:
        meta["status"] = "UNAVAILABLE"
        meta["reason"] = "ompi_info did not establish tuned allreduce algorithm 3 as recursive doubling"
        meta["source_sha256_after"] = sha256(ROOT / "microbench.c")
        (ROOT / "qualification.json").write_text(json.dumps(meta, indent=2) + "\n")
        return 0

    control_probe = launch("probe-control", ["--mca", "coll_base_verbose", "30"], ["--probe"], 20)
    candidate_probe = launch("probe-candidate", ["--mca", "coll_base_verbose", "30", "--mca", "mpi_show_mca_params", "all"] + CANDIDATE, ["--probe"], 20)
    probes = {"control": control_probe, "candidate": candidate_probe}
    (ROOT / "probe-selection.json").write_text(json.dumps(probes, indent=2) + "\n")
    if (candidate_probe.get("selected_component_observed") != "tuned" or candidate_probe.get("returncode") != 0 or control_probe.get("returncode") != 0):
        meta.update({"status": "UNAVAILABLE", "reason": "verbose candidate probe did not establish actual tuned component selection", "probes": probes, "source_sha256_after": sha256(ROOT / "microbench.c")})
        (ROOT / "qualification.json").write_text(json.dumps(meta, indent=2) + "\n")
        return 0

    results = []
    for name, args in [("A1", []), ("B1", CANDIDATE), ("B2", CANDIDATE), ("A2", [])]:
        result = launch(name, args, ["--output", str(RUNS / name / "result.json")], 30)
        results.append(result)
        (ROOT / "launches.json").write_text(json.dumps(results, indent=2) + "\n")
        if result.get("status") != "completed":
            break
    admission = evaluate(results) if len(results) == 4 and all(r.get("status") == "completed" for r in results) else {"promotion_gate": "UNAVAILABLE", "reason": "four successful launches required"}
    (ROOT / "assessment.json").write_text(json.dumps(admission, indent=2) + "\n")
    meta.update({"status": "MEASUREMENTS_COLLECTED" if len(results) == 4 and all(r.get("status") == "completed" for r in results) else "INCOMPLETE",
                 "launches": results, "probes": probes, "assessment": admission,
                 "source_sha256_after": sha256(ROOT / "microbench.c")})
    (ROOT / "qualification.json").write_text(json.dumps(meta, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
