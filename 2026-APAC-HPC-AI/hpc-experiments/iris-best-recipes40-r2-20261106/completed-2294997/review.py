"""Replay R2 terminal evidence without changing the frozen job payload."""
from pathlib import Path
import hashlib
import json
import math
import re
import statistics
import sys
import tarfile

HERE = Path(__file__).resolve().parent.parent
E = HERE
C = E / "completed-2294997"
COLLECTED = C / "collected"
RUN = COLLECTED / "runs" / "2294997"
sys.path.insert(0, str(E))
sys.path.insert(0, str(E.parent / "tools"))
from helpers import runtime_identity_equal
from native_output import review_native_output
from read_rank_proofs import validate_proof_dir
from run import compare_same_partition
from sampler import validate_sample_file

collection = json.loads((C / "collection.json").read_text())
scheduler = collection["scheduler"]
assert scheduler["State"] == "COMPLETED" and scheduler["ExitCode"] == "0:0"
assert scheduler["ElapsedRaw"] == "8059" and scheduler["AllocCPUS"] == "56"
raw = C / "raw-evidence.tar.gz"
assert hashlib.sha256(raw.read_bytes()).hexdigest() == collection["archive_sha256"]
assert raw.stat().st_size == collection["archive_bytes"]
with tarfile.open(raw, "r:gz") as tar:
    members = [m for m in tar.getmembers() if m.isfile()]
    assert len(members) == len(collection["files"]) == 642
    for member in members:
        data = tar.extractfile(member).read()
        meta = collection["files"][member.name]
        assert hashlib.sha256(data).hexdigest() == meta["sha256"]
        assert len(data) == meta["bytes"]

comparison = json.loads((RUN / "comparison.json").read_text())
assert comparison["passed"] and comparison["complete_six_arm_recipe_comparison"]
assert not comparison["scored_result"]
assert comparison["runtime_identity_stable"]
arm_order = ["T1-teammate56", "O1-original48", "D1-io48", "D2-io48", "O2-original48", "T2-teammate56"]
rank_counts = {"T1-teammate56":56,"O1-original48":48,"D1-io48":48,"D2-io48":48,"O2-original48":48,"T2-teammate56":56}
arm_rows = {row["arm"]: row for row in comparison["arms"]}
assert [row["arm"] for row in comparison["arms"]] == arm_order
arm_results=[]
for name in arm_order:
    row=arm_rows[name]; ranks=rank_counts[name]; arm=RUN/"arms"/name
    assert row["rank_count"]==ranks and row["steps"]==40 and row["intervals"]==39
    assert len(row["timings_seconds"])==39
    log,timings,forces,iterations=review_native_output(arm, expected_ranks=ranks)
    assert statistics.mean(timings)==row["mean_s_step"]
    assert all(math.isfinite(t) and t>0 for t in timings)
    assert row["fixed_iterations"]==iterations
    assert len(forces)==40
    assert json.loads((arm/"return-code.json").read_text())["returncode"]==0
    assert json.loads((arm/"rank-proofs.json").read_text())["passed"]
    proof_dir=arm/"rank-probe-proofs"
    assert len(list(proof_dir.glob("rank-*.json")))==ranks
    proof_result=validate_proof_dir(proof_dir, expected_ranks=ranks)
    assert proof_result["passed"] and proof_result["rank_count"]==ranks
    assert json.loads((arm/"postsolve-fields.json").read_text())==json.loads((RUN/("source-fields-%d.json"%ranks)).read_text())
    telemetry=validate_sample_file(arm/"telemetry-samples.jsonl",optional=False)
    assert telemetry["present"] and telemetry["sample_count"]==row["telemetry"]["sample_count"]
    assert row["telemetry"]["stop"]["returncode"]==0
    arm_results.append({"arm":name,"recipe":row["recipe"],"ranks":ranks,
        "steps":40,"intervals":39,"mean_s_step":row["mean_s_step"],
        "median_s_step":row["median_s_step"],"p95_s_step":sorted(timings)[math.ceil(.95*len(timings))-1],
        "max_s_step":max(timings),"returncode":0,"rank_proofs":ranks,
        "telemetry_samples":telemetry["sample_count"],
        "max_rss_kib_reported_by_time":int(re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)",(arm/"resource-time.log").read_text())[1])})

before=json.loads((RUN/"runtime-before.json").read_text());after=json.loads((RUN/"runtime-after.json").read_text())
assert runtime_identity_equal(before,after)
source_before={n:json.loads((RUN/("accepted-source-%d-before.status.json"%n)).read_text())["returncode"] for n in (48,56)}
source_after={n:json.loads((RUN/("accepted-source-%d-after.status.json"%n)).read_text())["returncode"] for n in (48,56)}
source_validation={n:json.loads((RUN/("source-after-%d.json"%n)).read_text())["passed"] for n in (48,56)}
payload_before=json.loads((RUN/"payload-before.status.json").read_text())["returncode"]
payload_after=json.loads((RUN/"payload-after.status.json").read_text())["returncode"]
assert all(v==0 for v in source_before.values()) and all(v==0 for v in source_after.values())
assert all(source_validation.values()) and payload_before==payload_after==0
force_repeats={}
for recipe,left,right in (("teammate56","T1-teammate56","T2-teammate56"),("original48","O1-original48","O2-original48"),("io48","D1-io48","D2-io48")):
    result=compare_same_partition(arm_rows[left]["force_coefficients_by_step"],arm_rows[right]["force_coefficients_by_step"])
    assert result["passed"]
    force_repeats[recipe]=result
same_source={}
for left,right in (("O1-original48","D1-io48"),("O2-original48","D2-io48")):
    result=compare_same_partition(arm_rows[left]["force_coefficients_by_step"],arm_rows[right]["force_coefficients_by_step"])
    assert result["passed"]
    same_source[left+"_vs_"+right]=result
means=comparison["recipe_means"]
# Validate the reported pooled recipe means directly from the six native arm means.
for recipe,left,right in (("teammate56","T1-teammate56","T2-teammate56"),("original48","O1-original48","O2-original48"),("io48","D1-io48","D2-io48")):
    expected=(arm_rows[left]["mean_s_step"]+arm_rows[right]["mean_s_step"])/2
    assert math.isclose(expected,means[recipe]["mean_seconds_per_step"],rel_tol=1e-12,abs_tol=1e-12)
telemetry_review={}
for label in arm_order:
    item=collection["telemetry_sample_checks"][label]
    telemetry_review[label]={"samples":item["validation"]["sample_count"],
       "whole_node_procfs_interval_seconds":5,
       "sampler_exit":item["status"]["stop"]["returncode"],
       "pressure_stall_data_available":False,
       "gpu_telemetry_collected":False,
       "scope":"whole-node aggregate; not per-process attribution"}

d1=means["io48"]["mean_seconds_per_step"]; o1=means["original48"]["mean_seconds_per_step"]; t1=means["teammate56"]["mean_seconds_per_step"]
assessment={"io48_vs_original48_percent":100*(d1/o1-1),"io48_vs_teammate56_percent":100*(d1/t1-1),
 "first_paired_contrast_io_vs_original_percent":100*(arm_rows["D1-io48"]["mean_s_step"]/arm_rows["O1-original48"]["mean_s_step"]-1),
 "second_paired_contrast_io_vs_original_percent":100*(arm_rows["D2-io48"]["mean_s_step"]/arm_rows["O2-original48"]["mean_s_step"]-1),
 "recipe_repeat_drift_percent":{k:means[k]["arm_mean_difference_percent"] for k in ("teammate56","original48","io48")}}
review={"job_id":"2294997","terminal_state":"COMPLETED","exit_code":"0:0","measurement_valid":True,
 "complete_six_arm_matrix":True,"scored_result":False,"root_independent_replay":"ROOT_REPLAY.json",
 "verified_files":642,"archive_bytes":collection["archive_bytes"],"archive_sha256":collection["archive_sha256"],
 "elapsed_seconds":8059,"allocated_CPUs":56,"node":"iris001","allocated_CPU_hours":8059*56/3600,
 "actual_su":None,"arms":arm_results,"recipe_means":means,"contrasts":assessment,
 "source_before_return_codes":source_before,"source_after_return_codes":source_after,"source_after_validations":source_validation,
 "payload_before_return_code":payload_before,"payload_after_return_code":payload_after,
 "runtime_identity_stable":True,"rank_proofs_all_passed":True,"same_recipe_force_repeats":force_repeats,"same_source_force_checks":same_source,
 "telemetry_inspected":telemetry_review,
 "assessment":"The six-arm native measurement is complete and all recorded gates pass. The I/O-only collated recipe has a lower pooled mean, but per-arm contrasts reverse direction and every recipe has large repeat drift in this ordered single allocation. This does not establish a robust collated-I/O gain or a stable winner. No recipe beats the retained approximately 22.4 s/step historical Iris control; the 24.688 s/step D2 arm is a single repeat and not a new best claim.",
 "next_decision":"Do not promote collated I/O. Close this branch as inconclusive under substantial temporal drift; use a short, block-balanced native repeat only if a feasible allocated window remains, otherwise retain original48 as practical conservative choice while keeping teammate56 as historical comparison.",
 "limits":["A single ordered six-arm allocation; all pooled/paired contrasts are exposed to time/order drift.","The D/O contrasts isolate the file handler on the same 48-rank source and default mapping, but no independent allocation replication exists.","Comparison with teammate56 bundles rank count, source and mapping configuration.","Rank affinity evidence is sampled before MPI_Init and does not prove solver helper affinity or NUMA page placement.","Node PSI/pressure files are unavailable; telemetry is whole-node procfs sampling, not per-process causality or I/O bandwidth profiling.","MaxRSS reported by `/usr/bin/time` is a per-command peak, not summed MPI memory; Slurm root-job MaxRSS is blank; the retained batch-step row reports 139187772K, which is not a sum of MPI rank RSS.","GPU diagnostics were not collected because this CPU solver allocation requested zero GPUs.","This is a 40-step OpenFOAM microbenchmark, not a full official workload or scored contest result."]}
(C/"REVIEW.json").write_text(json.dumps(review,indent=2,sort_keys=True)+"\n")
lines=["# R2 six-arm native comparison review","", "**Iris 2294997 COMPLETED 0:0**, 8,059 seconds / 56 CPUs / iris001. The full six-arm 40-step matrix passed native output, rank-proof, source, payload, runtime identity and force-repeat gates. This is a valid local measurement; it is not an official contest score.","", "| Recipe | Arm means (s/step) | Pooled mean (s/step) | Mean of arm medians (s) |", "|---|---:|---:|---:|"]
for recipe in ("teammate56","original48","io48"):
    arms=means[recipe]["arms"]; v=means[recipe]
    lines.append(f"| {recipe} | {arm_rows[arms[0]]['mean_s_step']:.3f} / {arm_rows[arms[1]]['mean_s_step']:.3f} | {v['mean_seconds_per_step']:.3f} | {v['mean_of_arm_medians_seconds']:.3f} |")
lines += ["", "The pooled io48 result is 5.94% faster than original48 and 9.86% faster than teammate56 in this allocation. The paired io48/original48 contrasts point in opposite directions: D1 is 2.20% slower than O1, while D2 is 14.86% faster than O2. Recipe repeat drift is 17.12% for teammate56, 8.82% for original48 and 24.04% for io48. This strong within-allocation timing drift means the pooled result does not establish an I/O benefit or a stable winner. The fastest individual arm, D2 at 24.688 s/step, is not a repeat-confirmed record and remains slower than the historical approximately 22.4-second Iris control.","", "All six arms completed steps 1–40 with 39 positive solver intervals and 40 force rows, rank-specific initialization, and exact 48/56 exclusive proof files. All six native logs, sampled pre-MPI rank proofs, telemetry streams, and the 642-file transferred archive were independently replayed. Source checks passed before and after for both rank partitions; payload checks passed before and after; OpenFOAM/MPI binary and linked library identities were stable. Same-recipe force repeat and paired original48/io48 force checks passed their existing tolerance.","", "Inspection found 5-second whole-node procfs samples for each arm, per-command GNU-time peak RSS, runtime identity, node snapshots, and solver resource logs. The collected pressure/PSI sources are unavailable, Slurm root-job MaxRSS is blank (the batch-step row reports 139187772K), and no per-process CPU/I/O bandwidth or GPU telemetry was collected. RSS is not summed MPI memory. These data do not identify why timings drifted.","", "Next: close promotion of collated I/O pending independent block-balanced replication; preserve this complete but drift-confounded measurement and do not claim improvement over the historical Iris result.","", "Evidence: `REVIEW.json`, `ROOT_REPLAY.json`, `collection.json`, `raw-evidence.tar.gz`, and `collected/`."]
(C/"RESULTS.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"passed":True,"measurement_valid":True,"files":642,"means":means,"contrasts":assessment,"review":str(C/"REVIEW.json"),"results":str(C/"RESULTS.md")},indent=2))
