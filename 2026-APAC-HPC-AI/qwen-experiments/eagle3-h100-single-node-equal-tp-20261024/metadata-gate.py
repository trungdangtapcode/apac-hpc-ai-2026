#!/usr/bin/env python3
"""Fail-closed role, device, source and single-pair metadata gate."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "pd-observer"))
from validate_receipts import validate

ROLES = ("prefill-0", "decode-0")
MODULE_HASHES = {
    "utils": "db1b6285e08a6949632d9347f546e1cb290359ca4ad077a1a204af19547caf82",
    "conn": "912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f",
}


def verify_sources(root: Path) -> dict:
    output = {}
    for role in ROLES:
        for short, digest in MODULE_HASHES.items():
            path = root / "source-modules" / role / f"{short}.json"
            row = json.loads(path.read_text())
            module = ("sglang.srt.disaggregation.utils" if short == "utils"
                      else "sglang.srt.disaggregation.nixl.conn")
            if row.get("schema") != "eagle3-pd-source-module-v1" or row.get("role") != role \
                    or row.get("module") != module or row.get("sha256") != digest:
                raise ValueError(f"runtime source report mismatch: {path}")
            output[f"{role}/{short}"] = digest
    return output


def verify_devices(art: Path) -> dict:
    rows = {}
    expected = {"prefill-0": [0, 1, 2, 3], "decode-0": [4, 5, 6, 7]}
    for role in ROLES:
        row = json.loads((art / f"devices-{role}.json").read_text())
        if row.get("role") != role or row.get("assigned_gpu_indices") != expected[role]:
            raise ValueError(f"wrong assigned offset record for {role}")
        devices = row.get("devices", [])
        if len(devices) != 4 or len({d.get("uuid") for d in devices}) != 4:
            raise ValueError(f"{role} did not record four distinct devices")
        if any("H100" not in d.get("name", "") or d.get("compute_capability") != [9, 0]
               for d in devices):
            raise ValueError(f"{role} includes a non-H100 or non-SM90 device")
        rows[role] = devices
    p = {d["uuid"] for d in rows["prefill-0"]}
    d = {item["uuid"] for item in rows["decode-0"]}
    if p & d or len(p | d) != 8:
        raise ValueError("P and D do not have eight disjoint assigned H100 UUIDs")
    return {"gpu_indices": expected, "unique_disjoint_h100_uuids": 8}


def validate_pre_warmup(art: Path) -> dict:
    root = art / "pd-observer"
    paths = sorted(root.glob("*/tp-*/metadata.json"))
    if len(paths) != 8:
        raise ValueError(f"expected exactly eight actual TP receipts, found {len(paths)}")
    ranks = validate(paths)
    return {"state": "PRE_WARMUP_METADATA_PASS", "rank_layout": ranks,
            "runtime_sources": verify_sources(root), "assigned_devices": verify_devices(art)}


def validate_post_semantic(art: Path, experiment_id: str) -> dict:
    endpoints = art / "endpoints.tsv"
    rows = [line.split("\t") for line in endpoints.read_text().splitlines() if line.strip()]
    if len(rows) != 2 or {row[0] for row in rows} != set(ROLES):
        raise ValueError("expected exactly one P4 and one D4 endpoint")
    token = hashlib.sha256(f"{experiment_id}-single-semantic".encode()).hexdigest()[:32]
    from warmup_semantic import check
    receipt = check(art / "pair-warmup-receipts/single", endpoints, token)
    if receipt.get("pair_count") != 1:
        raise ValueError("expected exactly one independently replayed semantic P/D receipt")
    markers = [json.loads(x) for x in (art / "phase-markers.jsonl").read_text().splitlines()]
    start = next((int(x["utc_ns"]) for x in markers if x.get("event") == "semantic_start"), None)
    end = next((int(x["utc_ns"]) for x in markers if x.get("event") == "semantic_end"), None)
    if start is None or end is None or end <= start:
        raise ValueError("missing or invalid semantic phase timestamps")
    observed = {}
    for kind in ("send_kvcache_slice", "send_aux"):
        events = []
        for p in sorted((art / "pd-observer/prefill-0").glob("tp-*/transfers.jsonl")):
            for line in p.read_text().splitlines():
                event = json.loads(line)
                if start <= int(event.get("time_unix_ns", 0)) <= end and event.get("kind") == kind:
                    events.append(event)
        outcomes = [x.get("marker") for x in events]
        if "start" not in outcomes or not any(x in {"returned_handle", "exception"} for x in outcomes):
            raise ValueError(f"missing actual native observer markers for {kind}")
        observed[kind] = {"start_markers": outcomes.count("start"),
                          "returned_handle_markers": outcomes.count("returned_handle"),
                          "exception_markers": outcomes.count("exception"),
                          "returned_handle_proves_completion": False}
    return {"state": "ONE_SEMANTIC_PD_RECEIPT_PASS", "receipt": receipt,
            "native_send_observations": observed}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("pre-warmup", "post-semantic"))
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--experiment-id")
    args = parser.parse_args()
    try:
        result = (validate_pre_warmup(args.artifact) if args.stage == "pre-warmup"
                  else validate_post_semantic(args.artifact, args.experiment_id or ""))
    except Exception as exc:
        print(f"METADATA_GATE_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    (args.artifact / f"{args.stage}-gate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
