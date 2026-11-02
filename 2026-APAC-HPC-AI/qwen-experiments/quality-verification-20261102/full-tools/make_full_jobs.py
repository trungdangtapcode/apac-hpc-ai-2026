#!/usr/bin/env python3
"""Generate frozen-ready paired full-corpus MMLU-Pro quality shards."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
JOBS = STUDY / "jobs"
CORPUS = STUDY / "prepared-4k" / "compiled-corpus.jsonl"
PREPARE_MANIFEST = STUDY / "prepared-4k" / "prepare-manifest.json"
REFERENCE_SOURCE = JOBS / "reference-pilot-r2"
CANDIDATE_SOURCE = JOBS / "candidate-pilot" / "AI_Task" / "job_scripts"
COUNT, ROWS, CONCURRENCY = 8, 12032, 64


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify(root: Path, manifest: Path) -> None:
    for n, line in enumerate(manifest.read_text().splitlines(), 1):
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        path = root / relative
        if not path.is_file() or sha(path) != digest:
            raise ValueError(f"Frozen source mismatch: {manifest}:{n} {relative}")


def replace(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one match, got {count}: {old!r}")
    return text.replace(old, new, 1)


def read_rows() -> tuple[list[int], dict[int, list[int]], str]:
    ids = []
    with CORPUS.open(encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("preparation_status") != "READY":
                raise ValueError(f"Corpus row {n} is not ready")
            ids.append(int(row["question_id"]))
    prep = json.loads(PREPARE_MANIFEST.read_text())
    if (len(ids) != ROWS or len(set(ids)) != ROWS or prep.get("status") != "READY"
            or prep.get("generation_blocked") or prep.get("question_count") != ROWS
            or prep.get("compiled_corpus_sha256") != sha(CORPUS)):
        raise ValueError("Prepared corpus does not match a ready 12,032-row manifest")
    shards = {k: [qid for i, qid in enumerate(ids) if i % COUNT == k] for k in range(COUNT)}
    if any(len(v) != ROWS // COUNT for v in shards.values()):
        raise ValueError("Modulo-8 shard is not balanced at 1,504 rows")
    union = [qid for k in range(COUNT) for qid in shards[k]]
    if len(union) != len(set(union)) or set(union) != set(ids):
        raise ValueError("Shards are not a disjoint complete partition")
    return ids, shards, sha(CORPUS)


def make_reference(k: int) -> Path:
    name = f"full-ref-{k:02d}of08"
    out = JOBS / name
    out.mkdir(parents=True, exist_ok=False)
    for f in ("submit.sbatch", "semantic_probe.py"):
        shutil.copy2(REFERENCE_SOURCE / f, out / f)
    (out / "logs").mkdir()
    (out / "runs").mkdir()
    p = out / "submit.sbatch"
    s = p.read_text(encoding="utf-8")
    changes = [
        ("#SBATCH --job-name=qref-ep8", f"#SBATCH --job-name=qrf{k:02d}"),
        ("/jobs/reference-pilot-r2/logs/%j.out", f"/jobs/{name}/logs/%j.out"),
        ("/jobs/reference-pilot-r2/logs/%j.err", f"/jobs/{name}/logs/%j.err"),
        ("frozen-reference-r2/SHA256SUMS", "frozen-full8/SHA256SUMS"),
        ("PILOT_IDS=$PREPARED_DIR/pilot-ids.json", "SHARD_MANIFEST=$TASK_ROOT/full-tools/full_shard_membership.json"),
        ("bounded 128-question pilot", "bounded 1,504-question full shard"),
        ("out, model, sglang, aiperf, corpus, manifest, ids, nodes = sys.argv[1:]",
         "out, model, sglang, aiperf, corpus, manifest, shard_manifest, nodes = sys.argv[1:]"),
        ("'reference_type': 'two independent stock SGLang colocated replicas, one TP8 replica per H200 node',",
         "'reference_type': 'two independent stock SGLang colocated replicas, TP8/EP8 per H200 node',"),
        ("'corpus': file(corpus), 'prepare_manifest': file(manifest), 'pilot_ids': file(ids),",
         "'corpus': file(corpus), 'prepare_manifest': file(manifest), 'shard_membership': file(shard_manifest),"),
        ("'evaluation_options': {'concurrency':16,'timeout_seconds':120,'deadline_epoch':int(os.environ['TRIPLEU_EVALUATION_DEADLINE']),'deadline_margin_seconds':10},",
         f"'evaluation_options': {{'concurrency':64,'timeout_seconds':120,'deadline_epoch':int(os.environ['TRIPLEU_EVALUATION_DEADLINE']),'deadline_margin_seconds':10,'phase':'full-quality-shard','role':'reference','shard_index':{k},'shard_count':8,'rows':1504,'selection':'stable corpus row order modulo 8'}},"),
        ('printf \'reference: 2 independent TP8 replicas, one per node; model=%s\\n\' "$MODEL" | tee -a "$ART/job-start.log"',
         'cp "$SHARD_MANIFEST" "$ART/shard-membership.json"\nprintf \'FULL_SHARD_BEGIN role=reference shard=' + f"{k:02d}/08 rows=1504 concurrency=64 TP8/EP8 model=%s\\n" + '\' "$MODEL" | tee -a "$ART/job-start.log"'),
        ("echo \"CLIENT_START concurrency=16 deadline_epoch=$EVALUATION_DEADLINE\"",
         f"echo \"FULL_SHARD_CLIENT_START role=reference shard={k:02d}/08 rows=1504 concurrency=64 deadline_epoch=$EVALUATION_DEADLINE\""),
        ('--ids-file "$4" \\', '--shard-index "$8" --shard-count 8 \\'),
        ("--concurrency 16 --timeout 120", "--concurrency 64 --timeout 120"),
        ("REFERENCE_PILOT_COMPLETE", "FULL_SHARD_REFERENCE_COMPLETE"),
    ]
    for old, new in changes:
        s = replace(s, old, new, f"{name} derivation")
    # Remaining occurrences are the run directory, runtime home, and log-dir guard.
    s = s.replace("$TASK_ROOT/jobs/reference-pilot-r2", f"$TASK_ROOT/jobs/{name}")
    s = s.replace("reference-pilot directory", "full-reference shard directory")
    s = replace(s,
        'for required in "$CORPUS" "$PREPARE_MANIFEST" "$PILOT_IDS" "$SGLANG" "$AIPERF" "$MODEL/config.json"; do',
        'for required in "$CORPUS" "$PREPARE_MANIFEST" "$SHARD_MANIFEST" "$SGLANG" "$AIPERF" "$MODEL/config.json"; do',
        "reference required inputs")
    s = replace(s,
        'record_provenance() {\n  python3 - "$ART" "$MODEL" "$SGLANG" "$AIPERF" "$CORPUS" "$PREPARE_MANIFEST" "$PILOT_IDS" "${NODES[*]}" <<\'PY\'',
        'record_provenance() {\n  python3 - "$ART" "$MODEL" "$SGLANG" "$AIPERF" "$CORPUS" "$PREPARE_MANIFEST" "$SHARD_MANIFEST" "${NODES[*]}" <<\'PY\'',
        "reference shard provenance arguments")
    s = replace(s,
        '\' quality-client "$TASK_ROOT/client/quality_client.py" "$CORPUS" "$PREPARE_MANIFEST" "$PILOT_IDS" \\\n    "http://${IP0}:8000/v1"',
        '\' quality-client "$TASK_ROOT/client/quality_client.py" "$CORPUS" "$PREPARE_MANIFEST" "$SHARD_MANIFEST" \\\n    "http://${IP0}:8000/v1"',
        "reference compatibility argument")
    # Keep argument four populated so URL/output/deadline remain positions 5/6/7.
    s = replace(s, '"$EVALUATION_DEADLINE" \\\n  >"$ART/client.log" 2>&1',
                f'"$EVALUATION_DEADLINE" {k} \\\n  >"$ART/client.log" 2>&1', "reference shard index argument")
    if "PILOT" in s or "pilot" in s.lower() or "ids-file" in s:
        raise ValueError(f"{name} retains a pilot-only label or selection")
    if f"--shard-index \"$8\" --shard-count 8" not in s:
        raise ValueError(f"{name} lacks fixed shard selection")
    p.write_text(s, encoding="utf-8")
    (out / "FULL_SHARD.json").write_text(json.dumps({
        "phase": "full-corpus local quality shard", "role": "reference",
        "shard_index": k, "shard_count": 8, "rows": 1504,
        "selection": "stable prepared-corpus row order modulo 8", "concurrency": 64,
        "max_output_tokens": 2048, "temperature": 0.0,
        "official_btc_certification": False,
    }, indent=2, sort_keys=True) + "\n")
    return out


def make_candidate(k: int) -> Path:
    name = f"full-cand-{k:02d}of08"
    bundle = JOBS / name
    bundle.mkdir(parents=True, exist_ok=False)
    task_root = bundle / "AI_Task"
    dest = task_root / "job_scripts"
    shutil.copytree(CANDIDATE_SOURCE, dest)
    (task_root / "logs" / "full-shards-slurm").mkdir(parents=True)
    (task_root / "logs" / "full-shards").mkdir()
    p = dest / "submit.sbatch"
    s = p.read_text(encoding="utf-8")
    for old, new, label in [
        ("#SBATCH --job-name=ap42-qual-cand", f"#SBATCH --job-name=qfc{k:02d}", "candidate job name"),
        ("#SBATCH --output=../logs/slurm/%j.out", "#SBATCH --output=../logs/full-shards-slurm/%j.out", "candidate output path"),
        ("#SBATCH --error=../logs/slurm/%j.err", "#SBATCH --error=../logs/full-shards-slurm/%j.err", "candidate error path"),
        ("export TRIPLEU_QUALITY_CONCURRENCY=16",
         f"export TRIPLEU_QUALITY_CONCURRENCY=64\nexport TRIPLEU_QUALITY_SHARD_INDEX={k}\nexport TRIPLEU_QUALITY_SHARD_COUNT=8",
         "candidate shard and concurrency"),
    ]:
        s = replace(s, old, new, label)
    p.write_text(s, encoding="utf-8")

    p = dest / "deploy-quality.sh"
    s = p.read_text(encoding="utf-8")
    for old, new, label in [
        ('ART="$TASK_ROOT/logs/reruns/$SLURM_JOB_ID"', 'ART="$TASK_ROOT/logs/full-shards/$SLURM_JOB_ID"', "candidate artifact path"),
        ("frozen-pilot/SHA256SUMS", "frozen-full8/SHA256SUMS", "candidate frozen guard"),
        ('local_home="$TASK_ROOT/logs/.runtime-home/$SLURM_JOB_ID/$1"',
         'local_home="$TASK_ROOT/logs/.runtime-home-full/$SLURM_JOB_ID/$1"', "candidate runtime home"),
        ('echo "QUALITY_PILOT_BEGIN after ${SECONDS}s"',
         f'echo "FULL_SHARD_BEGIN role=candidate shard={k:02d}/08 rows=1504 concurrency=64 after ${{SECONDS}}s"', "candidate start label"),
        ('echo "QUALITY_PILOT_COMPLETE after ${SECONDS}s at $(date -Iseconds)"',
         f'echo "FULL_SHARD_COMPLETE role=candidate shard={k:02d}/08 rows=1504 concurrency=64 after ${{SECONDS}}s at $(date -Iseconds)"', "candidate completion label"),
        ("# Independent accuracy experiment: frozen paired MMLU-Pro pilot, not AIPerf scoring.",
         "# Full-corpus quality shard, not AIPerf scoring." , "candidate phase comment"),
    ]:
        s = replace(s, old, new, label)
    p.write_text(s, encoding="utf-8")

    p = dest / "run-quality-client.sh"
    s = p.read_text(encoding="utf-8")
    s = replace(s, "import sys,json", "import os,sys,json", "client provenance import")
    s = replace(s, "'tokenizers':version('tokenizers')",
                "'tokenizers':version('tokenizers'),'phase':'full-quality-shard','shard_index':int(os.environ['TRIPLEU_QUALITY_SHARD_INDEX']),'shard_count':int(os.environ['TRIPLEU_QUALITY_SHARD_COUNT']),'concurrency':int(os.environ['TRIPLEU_QUALITY_CONCURRENCY'])",
                "client provenance fields")
    s = replace(s, '--ids-file "$STUDY/prepared-4k/pilot-ids.json" \\',
                '--shard-index "$TRIPLEU_QUALITY_SHARD_INDEX" --shard-count "$TRIPLEU_QUALITY_SHARD_COUNT" \\',
                "candidate full shard selection")
    s = replace(s, '${TRIPLEU_QUALITY_CONCURRENCY:-16}', '${TRIPLEU_QUALITY_CONCURRENCY:-64}',
                "candidate full shard default concurrency")
    s = replace(s, '  >"$ART/quality-client.log" 2>&1',
                '  >"$ART/quality-client.log" 2>&1\necho "FULL_SHARD_CLIENT_COMPLETE index=${TRIPLEU_QUALITY_SHARD_INDEX}/${TRIPLEU_QUALITY_SHARD_COUNT} concurrency=${TRIPLEU_QUALITY_CONCURRENCY}"',
                "candidate client completion label")
    p.write_text(s, encoding="utf-8")

    (dest / "README.md").write_text(
        "# Full-corpus local quality candidate shard\n\n"
        f"Derived shard {k} of 8 evaluates 1,504 rows from the prepared 12,032-question MMLU-Pro corpus at concurrency 64. It preserves the accepted candidate model, worker flags, precision, topology, NIXL patch, prompt construction, greedy decoding, 2,048-token output limit and scorer. This is internal quality evidence, not BTC certification or ranked AIPerf.\n\n"
        "A corresponding reference shard uses the same question IDs. Aggregate correct counts over the fixed 12,032-question denominator; do not average shard ratios.\n"
    )
    (bundle / "FULL_SHARD.json").write_text(json.dumps({
        "phase": "full-corpus local quality shard", "role": "candidate",
        "shard_index": k, "shard_count": 8, "rows": 1504,
        "selection": "stable prepared-corpus row order modulo 8", "concurrency": 64,
        "max_output_tokens": 2048, "temperature": 0.0,
        "candidate_runtime_changed": False, "official_btc_certification": False,
    }, indent=2, sort_keys=True) + "\n")

    # Regenerate only this derived package's check file. Protected runtime files
    # are verified byte-identical immediately below.
    rows = []
    for f in sorted(x for x in dest.rglob("*") if x.is_file() and x.name != "SHA256SUMS"):
        rows.append(f"{sha(f)}  {f.relative_to(dest).as_posix()}")
    (dest / "SHA256SUMS").write_text("\n".join(rows) + "\n")
    for relative in ("worker.sh", "nixl-conn.py", "config.json", "environment.json", "placement.tsv"):
        if sha(CANDIDATE_SOURCE / relative) != sha(dest / relative):
            raise ValueError(f"Candidate serving payload changed in {name}: {relative}")
    return bundle


def main() -> None:
    for path in (CORPUS, PREPARE_MANIFEST, REFERENCE_SOURCE / "submit.sbatch",
                 REFERENCE_SOURCE / "semantic_probe.py", CANDIDATE_SOURCE / "SHA256SUMS"):
        if not path.is_file():
            raise SystemExit(f"Missing required source: {path}")
    verify(STUDY, STUDY / "frozen-reference-r2" / "SHA256SUMS")
    verify(STUDY, STUDY / "frozen-pilot" / "SHA256SUMS")
    verify(CANDIDATE_SOURCE, CANDIDATE_SOURCE / "SHA256SUMS")
    ids, shards, corpus_sha = read_rows()
    membership_path = STUDY / "full-tools" / "full_shard_membership.json"
    config_path = STUDY / "full-tools" / "full-trials-config.json"
    if membership_path.exists() or config_path.exists():
        raise SystemExit("Refusing to overwrite existing full-tools manifests")
    if any((JOBS / f"full-{role}-{k:02d}of08").exists()
           for role in ("ref", "cand") for k in range(COUNT)):
        raise SystemExit("Refusing to overwrite an existing generated shard bundle")

    membership = {
        "purpose": "paired partition for internal local quality verification; not organizer data",
        "corpus_path": str(CORPUS), "corpus_sha256": corpus_sha,
        "prepared_rows": len(ids), "shard_count": COUNT,
        "rule": "Enumerate nonblank compiled-corpus rows in file order; assign row i to shard i % 8.",
        "rows_per_shard": ROWS // COUNT, "roles_share_identical_membership": True,
        "roles": {role: {f"{k:02d}of08": {
            "row_count": len(shards[k]), "question_ids": shards[k],
            "question_ids_canonical_json_sha256": hashlib.sha256(json.dumps(shards[k], separators=(",", ":")).encode()).hexdigest(),
        } for k in range(COUNT)} for role in ("reference", "candidate")},
        "coverage": {"union_rows": len(ids), "union_unique_question_ids": len(set(ids)),
                     "pairwise_disjoint": True, "same_reference_candidate_ids_per_shard": True},
    }
    membership_path.write_text(json.dumps(membership, indent=2, sort_keys=True) + "\n")
    bundles = []
    for k in range(COUNT):
        bundles += [make_reference(k), make_candidate(k)]

    cfg = {
        "title": "Paired full-corpus local quality verification",
        "phase": "generation and answer-quality evaluation; separate from ranked AIPerf",
        "purpose": "Evaluate the full fixed local test set after the 128-question pilot ratio fell below the local 99% gate; not official BTC certification.",
        "pilot": {"candidate_job": 28368, "candidate_correct": 102, "reference_job": 28371,
                  "denominator": 128, "reference_correct": 104, "ratio_percent": 98.0769230769,
                  "service_errors": 0, "interpretation": "below local threshold on small pilot; full corpus is needed to assess generalization"},
        "corpus": {"path": str(CORPUS), "sha256": corpus_sha, "rows": ROWS,
                   "prepare_manifest_sha256": sha(PREPARE_MANIFEST), "scorer": "unchanged quality_client.py"},
        "sharding": {"count_per_role": COUNT, "rows_each": ROWS // COUNT,
                     "rule": membership["rule"], "paired_ids_identical": True,
                     "membership_path": str(membership_path)},
        "workload": {"concurrency": CONCURRENCY, "temperature": 0.0, "top_p": 1.0,
                     "max_output_tokens": 2048, "stop": ["Question:"],
                     "request_timeout_seconds": 120, "deadline_from_start_seconds": 950,
                     "deadline_margin_seconds": 10},
        "roles": {
            "reference": {"jobs": [f"jobs/full-ref-{k:02d}of08" for k in range(COUNT)],
                          "deployment": "stock FP8 SGLang colocated TP8/EP8, one replica per node; no transport patch or backend tuning"},
            "candidate": {"jobs": [f"jobs/full-cand-{k:02d}of08" for k in range(COUNT)],
                          "deployment": "accepted TP4-prefill and TP8/EP8-decode candidate; protected runtime files are hash-checked unchanged"},
        },
        "admission": {"state": "prepared only; no generated job submitted",
                      "maximum_jobs": 16, "maximum_h200_gpu_hours": round(16 * 16 * 17 / 60, 6),
                      "pbs_su": 0, "per_job": {"nodes": 2, "gpus": 16, "walltime_minutes": 17},
                      "first_pair_gate": "Run one reference and one candidate shard at native concurrency 64 first; review elapsed time, exact coverage, errors/timeouts, tokens and raw answers before deciding on remaining shards.",
                      "forecast_only": "Prior roughly 3,000 output tokens/s is not a measured rate for this long CoT workload."},
        "comparison": {"aggregate_rule": "Sum item-level correct counts over all eight shards per role, validate exact coverage and zero service errors, then calculate candidate_accuracy / reference_accuracy. Do not average shard ratios.",
                       "local_gate": "ratio >= 0.99 on all 12,032 paired items, complete coverage and zero service errors on both deployments; not BTC certification."},
        "bundles": [str(x.relative_to(STUDY)) for x in bundles],
    }
    config_path.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
    (STUDY / "full-tools" / "README.md").write_text(
        "# Full-corpus local quality shard generator\n\n"
        "Creates eight paired reference/candidate shards from the pinned 12,032-question local MMLU-Pro corpus. The unchanged client rule is used exactly: enumerate prepared-corpus rows in file order and select row index modulo 8 equal to the shard index. Each shard contains 1,504 questions; reference and candidate use identical IDs.\n\n"
        "Pilot evidence: candidate job 28368 scored 102/128; reference job 28371 scored 104/128; ratio 98.076923%, with no service errors. This is below the local 99% ratio gate on a small sample, so the complete fixed corpus is needed to assess whether it generalizes. The full test keeps the prepared prompt bytes, parser, greedy decoding and 2,048-token output cap and uses concurrency 64.\n\n"
        "The generator verifies existing frozen pilot/reference payloads and the candidate source manifest. It asserts candidate worker, NIXL patch, config, environment and placement files remain byte-identical. Original pilot bundles and the accepted submission are untouched. It creates no frozen-full8 guard and submits no jobs; review and freeze the generated payload before explicit admission.\n\n"
        "All 16 jobs have a maximum exposure of 72.533333 H200 GPU-hours at full 17-minute allocations and zero PBS SU. Prior roughly 3,000 output tokens/s is only a forecast for long CoT. Review one actual paired concurrency-64 shard for completion time, coverage, errors, timeouts, token totals and responses before admitting the other shards.\n\n"
        "Aggregate correct counts over the full 12,032 denominator for each role, then divide candidate accuracy by reference accuracy. Never average shard ratios. A local >=99% ratio is not BTC certification.\n"
    )
    print(json.dumps({"bundles": len(bundles), "shards_per_role": COUNT,
                      "rows_per_shard": ROWS // COUNT, "corpus_sha256": corpus_sha,
                      "maximum_h200_gpu_hours": round(16 * 16 * 17 / 60, 6),
                      "admitted": False}, indent=2))


if __name__ == "__main__":
    main()

