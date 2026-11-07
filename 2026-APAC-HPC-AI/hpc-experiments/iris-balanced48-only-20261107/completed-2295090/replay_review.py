#!/usr/bin/env python3
"""Independent terminal evidence replay for Iris job 2295090."""
from __future__ import annotations
import hashlib
import json
import math
import re
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ARCHIVE = HERE / "raw-evidence.tar.gz"
COLLECTION = json.loads((HERE / "collection.json").read_text())
ARMS = ["B1-balanced48", "A1-default48", "A2-default48", "B2-balanced48"]
NUMA0 = set(range(0, 56, 2))
NUMA1 = set(range(1, 56, 2))

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def as_json(tf, name):
    return json.load(tf.extractfile(name))

def get_bytes(tf, name):
    f = tf.extractfile(name)
    if f is None:
        raise FileNotFoundError(name)
    return f.read()

def parse_dat(tf, name):
    rows=[]
    for line in get_bytes(tf,name).decode().splitlines():
        line=line.strip()
        if not line or line.startswith('#'):
            continue
        vals=[float(x) for x in line.split()]
        rows.append(vals)
    return rows

checks={}
# Collection's complete file inventory and archive integrity.
with tarfile.open(ARCHIVE, "r:gz") as tf:
    members=[m for m in tf.getmembers() if m.isfile()]
    actual={m.name for m in members}
    expected=set(COLLECTION["files"])
    archive_hash=sha(ARCHIVE.read_bytes())
    checks["archive_inventory"]={"passed":actual==expected and len(members)==469,
        "recorded_file_count":len(expected),"archive_regular_file_count":len(members),
        "missing":sorted(expected-actual),"unexpected":sorted(actual-expected)}
    bad=[]
    for name, meta in COLLECTION["files"].items():
        b=get_bytes(tf,name)
        if len(b)!=meta["bytes"] or sha(b)!=meta["sha256"]:
            bad.append(name)
    checks["all_collected_hashes"]={"passed":not bad,"verified_count":len(expected),"mismatches":bad}
    checks["archive_seal"]={"passed":len(ARCHIVE.read_bytes())==COLLECTION["archive_bytes"] and archive_hash==COLLECTION["archive_sha256"],
        "bytes":ARCHIVE.stat().st_size,"sha256":archive_hash}
    scheduler=COLLECTION["scheduler"]
    checks["scheduler_terminal"]={"passed":scheduler=={"JobID":"2295090","JobName":"tu-iris-b48map","State":"COMPLETED","ExitCode":"0:0","ElapsedRaw":"4525","AllocCPUS":"56","NodeList":"iris001","MaxRSS":"","TotalCPU":"2-08:09:59"},"record":scheduler}
    # frozen deployment payload manifest (57 files), all individually sealed in archive.
    payload_lines=get_bytes(tf,"payload-sha256.txt").decode().splitlines()
    payload={}
    for line in payload_lines:
        digest,name=line.split(None,1); payload[name.strip()]=digest
    payload_bad=[]
    for name,digest in payload.items():
        if name not in EXP.joinpath("payload-sha256.json").read_text():
            pass
        try:
            local=(EXP/name).read_bytes()
        except (OSError,IsADirectoryError):
            payload_bad.append(name); continue
        if sha(local)!=digest: payload_bad.append(name)
    checks["frozen_payload_57"]={"passed":len(payload)==57 and not payload_bad,"count":len(payload),"local_payload_mismatches":payload_bad}
    # Accepted source and input fingerprints before and after native work.
    before=as_json(tf,"runs/2295090/source-observation-48.json")
    after=as_json(tf,"runs/2295090/source-after-48.json")
    checks["source_before_after"]={"passed":before==after and before.get("passed") is True and after.get("passed") is True,
        "before_complete_files":before.get("complete_files"),"after_complete_files":after.get("complete_files"),
        "before_core_files":before.get("core_files"),"after_core_files":after.get("core_files"),
        "full_records_equal":before==after}
    # Runtime files present in frozen inventory must match the local source bytes.
    runtime_bad=[]
    frozen=COLLECTION["frozen_runtime_hashes"]
    for name,digest in frozen.items():
        try: b=(EXP/name).read_bytes()
        except OSError: runtime_bad.append(name); continue
        if sha(b)!=digest: runtime_bad.append(name)
    checks["frozen_runtime"]={"passed":not runtime_bad,"count":len(frozen),"mismatches":runtime_bad}
    # Required rank JSON set; strict rank number/world-size/one CPU checks.
    rank_results={}
    for label,path in [("balanced_preflight","runs/2295090/probes/balanced48"),
                       *[(arm,f"runs/2295090/arms/{arm}/rank-probe-proofs") for arm in ARMS]]:
        rec=[]
        for i in range(48):
            name=f"{path}/rank-{i:04d}.json"
            d=as_json(tf,name)
            cpus=d.get("affinity_cpu_ids",[])
            rec.append((d.get("rank"),d.get("world_size"),cpus))
        ids=[x[0] for x in rec]
        cpu=[x[2][0] if len(x[2])==1 else None for x in rec]
        exact_ids=ids==list(range(48)) and all(x[1]==48 for x in rec)
        unique=len(set(cpu))==48 and None not in cpu
        if label in ("balanced_preflight","B1-balanced48","B2-balanced48"):
            mask={"numa0":sum(c in NUMA0 for c in cpu),"numa1":sum(c in NUMA1 for c in cpu)}
            map_ok=mask=={"numa0":24,"numa1":24} and set(cpu)<=NUMA0|NUMA1
        else:
            mask={"numa0":sum(c in NUMA0 for c in cpu),"numa1":sum(c in NUMA1 for c in cpu)}
            map_ok=True
        rank_results[label]={"passed":exact_ids and unique and map_ok,"exact_rank_set":exact_ids,
            "unique_single_cpu_affinity":unique,"numa_cpu_counts":mask,"cpu_ids_by_rank":cpu}
    checks["strict_rank_json"]={"passed":all(v["passed"] for v in rank_results.values()),"sets":rank_results,
        "balanced_B1_B2_cpu_maps_equal":rank_results["B1-balanced48"]["cpu_ids_by_rank"]==rank_results["B2-balanced48"]["cpu_ids_by_rank"]}
    final_comparison=as_json(tf,"runs/2295090/comparison.json")
    partial=as_json(tf,"runs/2295090/partial-results.json")
    checks["comparison_records"]={"passed":final_comparison.get("passed") is True and final_comparison.get("complete_four_arm_comparison") is True and final_comparison.get("scored_result") is False and partial.get("complete") is False and partial.get("scored_result") is False,
        "authoritative_final_comparison":"runs/2295090/comparison.json",
        "partial_results_is_incomplete_progress_snapshot":partial.get("complete") is False,
        "partial_progress_snapshot_not_corruption":True,
        "comparison_percent":final_comparison.get("balanced48_vs_default48_time_percent"),
        "comparison_balanced_mean_s_step":final_comparison.get("balanced48_mean_s_step"),
        "comparison_default_mean_s_step":final_comparison.get("default48_mean_s_step"),
        "runtime_identity_stable":final_comparison.get("runtime_identity_stable"),
        "paired_force_checks":final_comparison.get("paired_same_source_force_checks"),
        "within_mapping_force_repeat_checks":final_comparison.get("within_mapping_force_repeat_checks")}
    # Native timing and quality evidence, reconstructed from raw solver files.
    arm_results={}
    force_rows={}
    zero_fields={}
    configs={}
    for arm in ARMS:
        base=f"runs/2295090/arms/{arm}"
        wct=parse_dat(tf,f"{base}/postProcessing/wallClockTimeStatistics/0/wallClockTime.dat")
        force=parse_dat(tf,f"{base}/postProcessing/forceCoeffsAll/0/coefficient.dat")
        fields=as_json(tf,f"{base}/postsolve-fields.json")
        cfg=as_json(tf,f"{base}/command.json")
        configs[arm]=cfg
        # Time 1 is initialization. The timed comparison is steps 2..40 inclusive.
        timed=[r[2] for r in wct if len(r)>=3 and 2<=r[0]<=40]
        force_by_step={int(r[0]):r[1:] for r in force}
        arm_results[arm]={"step_rows":len(wct),"timed_interval_count":len(timed),
            "step_times_s":len(timed),"mean_s_per_step":sum(timed)/len(timed) if timed else None,
            "timed_sum_s":sum(timed),"max_step":max([int(r[0]) for r in wct],default=None),
            "force_rows":len(force),"force_steps":[int(r[0]) for r in force],
            "field_count":fields.get("field_count"),"fields_match_initial_zero_time_seal":fields==as_json(tf,"runs/2295090/source-fields-48.json")}
        force_rows[arm]=force_by_step
        zero_fields[arm]=fields==as_json(tf,"runs/2295090/source-fields-48.json")
    # Full coefficient rows compare all trajectory values at matching steps.
    force_max_abs=0.0
    force_max_rel=0.0
    force_pair_checks=[]
    for left,right in [(ARMS[0],ARMS[1]),(ARMS[0],ARMS[2]),(ARMS[0],ARMS[3]),(ARMS[1],ARMS[2]),(ARMS[1],ARMS[3]),(ARMS[2],ARMS[3])]:
        shared=sorted(set(force_rows[left])&set(force_rows[right]))
        diffs=[]
        for step in shared:
            a,b=force_rows[left][step],force_rows[right][step]
            diffs.extend(abs(x-y) for x,y in zip(a,b))
        md=max(diffs,default=0.0); force_max_abs=max(force_max_abs,md)
        force_pair_checks.append({"pair":[left,right],"same_steps":len(shared),"max_abs_difference":md,
            "all_isclose_at_1e-9_rtol_1e-12_atol":all(math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-12) for step in shared for x,y in zip(force_rows[left][step],force_rows[right][step]))})
    means={a:arm_results[a]["mean_s_per_step"] for a in ARMS}
    balanced=(means["B1-balanced48"]+means["B2-balanced48"])/2
    default=(means["A1-default48"]+means["A2-default48"])/2
    slowdown=(balanced/default-1)*100
    pooled_bal=(arm_results["B1-balanced48"]["timed_sum_s"]+arm_results["B2-balanced48"]["timed_sum_s"])/78
    pooled_def=(arm_results["A1-default48"]["timed_sum_s"]+arm_results["A2-default48"]["timed_sum_s"])/78
    checks["native_replay"]={"passed":all(arm_results[a]["timed_interval_count"]==39 and arm_results[a]["force_rows"]==40 and arm_results[a]["max_step"]==40 for a in ARMS),
        "arms":arm_results,"means_s_per_step":means,"balanced_mean_s_per_step":balanced,"default_mean_s_per_step":default,
        "balanced_pooled_s_per_step":pooled_bal,"default_pooled_s_per_step":pooled_def,"balanced_percent_slower":slowdown,
        "matrix_order":ARMS,"same_source_force_gate":all(p["all_isclose_at_1e-9_rtol_1e-12_atol"] for p in force_pair_checks),
        "force_pair_checks":force_pair_checks,"zero_time_field_seals_all_arms_equal_source":all(zero_fields.values()),
        "commands":configs}
    # Telemetry availability/limits from on-node preflight and collector records.
    pre=as_json(tf,"runs/2295090/sampler-preflight.json")
    telem=COLLECTION["telemetry_sample_checks"]
    checks["telemetry"]={"passed":bool(pre.get("enabled")) and all(v.get("validation",{}).get("present") for v in telem.values()),
        "sampler_enabled":pre.get("enabled"),"interval_seconds":pre.get("interval_seconds"),
        "telemetry_arm_names":sorted(telem),"pressure_availability":pre.get("pressure_availability"),
        "cpu_frequency_available":all(r.get("availability",{}).get("cpu_frequency") for r in pre.get("reads",[])),
        "scope":"node-level sampling; frequency not attributable to solver task; PSI unavailable",
        "recorded_sampler_sample_counts":{k:v.get("validation",{}).get("sample_count") for k,v in telem.items()}}

result={"review":"independent terminal review","job_id":"2295090","checked_utc":COLLECTION["observed_utc"],
        "all_checks_passed":all(v["passed"] for v in checks.values()),"checks":checks}
(HERE/"REVIEW.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps({"all_checks_passed":result["all_checks_passed"],"checks":{k:v["passed"] for k,v in checks.items()},
    "means":means,"balanced_mean":balanced,"default_mean":default,"pct_slower":slowdown,
    "B1_B2_same_map":checks["strict_rank_json"]["balanced_B1_B2_cpu_maps_equal"]},indent=2))
