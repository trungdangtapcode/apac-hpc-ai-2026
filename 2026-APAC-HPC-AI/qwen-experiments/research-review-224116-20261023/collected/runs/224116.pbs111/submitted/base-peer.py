#!/usr/bin/env python3
"""Two-rank, no-model NIXL GPU peer probe."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
import socket
import sys
import time
import uuid
from pathlib import Path
from typing import Any

SIZES = (4096, 64 * 1024 * 1024)
REPETITIONS = 20
TRANSFER_TIMEOUT_S = 15.0
OVERALL_TIMEOUT_S = 300.0
BUFFER_BYTES = 128 * 1024 * 1024
HALF_BYTES = BUFFER_BYTES // 2
EXPECTED_RUNTIME_SHA256 = "912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f"
EXPECTED_NIXL_API_SHA256 = "27c3ce3c4fe58480aa3bce5e5c158c7659821a3bf1e84680778645adfdaa1bea"


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    with tmp.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, separators=(",", ":"))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def wait_path(path: Path, deadline: float, what: str) -> None:
    while not path.exists():
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Overall 300-second deadline waiting for {what}")
        time.sleep(0.05)


def wait_transfer(agent: Any, handle: Any, deadline: float) -> None:
    posted_at = time.time()
    if posted_at >= deadline:
        raise TimeoutError("Overall deadline expired before NIXL post")
    state = agent.transfer(handle)
    if state == "ERR":
        raise RuntimeError("NIXL transfer() returned ERR")
    end = min(deadline, posted_at + TRANSFER_TIMEOUT_S)
    while True:
        if time.time() >= end:
            raise TimeoutError("NIXL transfer exceeded its bounded deadline")
        state = agent.check_xfer_state(handle)
        if state == "DONE":
            return
        if state == "ERR":
            raise RuntimeError("NIXL transfer entered ERR state")
        # Match the pinned worker loop: NIXL backends may expose different
        # intermediate labels; only ERR and DONE are terminal states here.
        if time.time() >= end:
            raise TimeoutError("NIXL transfer exceeded its 15-second deadline")
        time.sleep(0.001)


def transfer_one(agent: Any, peer_name: str, source: Any, remote_ptr: int,
                 size: int, gpu_id: int, notification: str,
                 deadline: float) -> None:
    """Post one production-signature NIXL WRITE and wait for terminal DONE."""
    if time.time() >= deadline:
        raise TimeoutError("Overall deadline expired before NIXL descriptors")
    import numpy as np
    src_array = np.asarray([[int(source.data_ptr()), size, gpu_id]], dtype=np.uint64)
    dst_array = np.asarray([[int(remote_ptr), size, gpu_id]], dtype=np.uint64)
    src_descs = agent.get_xfer_descs(src_array, "VRAM")
    dst_descs = agent.get_xfer_descs(dst_array, "VRAM")
    if src_descs is None or dst_descs is None:
        raise RuntimeError("NIXL get_xfer_descs returned no descriptors")
    handle = agent.initialize_xfer(
        "WRITE", src_descs, dst_descs, peer_name, notification.encode("ascii")
    )
    if handle is None or handle is False:
        raise RuntimeError("NIXL initialize_xfer returned no handle")
    wait_transfer(agent, handle, deadline)


def pattern_bytes(size: int, sender_rank: int, sequence: int) -> bytes:
    """Generate deterministic, distinct bytes without any model dependency."""
    base = bytes(range(1, 252))
    rotation = (sender_rank * 71 + sequence * 29) % len(base)
    block = base[rotation:] + base[:rotation]
    whole, remainder = divmod(size, len(block))
    return block * whole + block[:remainder]


def safe_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(4 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def active_ib_devices() -> list[str]:
    root = Path("/sys/class/infiniband")
    devices = []
    if root.exists():
        for device in sorted(root.iterdir()):
            try:
                layer = (device / "ports/1/link_layer").read_text().strip()
                state = (device / "ports/1/state").read_text().strip()
            except OSError:
                continue
            if layer == "InfiniBand" and state == "4: ACTIVE":
                devices.append(f"{device.name}:1")
    return devices


def wait_until(predicate, deadline: float, what: str) -> None:
    while not predicate():
        if time.time() >= deadline:
            raise TimeoutError(f"Overall 300-second deadline waiting for {what}")
        time.sleep(0.05)


def result_rows_valid(rank0: dict[str, Any], rank1: dict[str, Any]) -> tuple[bool, str]:
    """Require 80 unique transfers and matching sender/receiver receipts."""
    by_rank = {rank0.get("rank"): rank0, rank1.get("rank"): rank1}
    if set(by_rank) != {0, 1}:
        return False, "rank results must be exactly ranks 0 and 1"
    if rank0.get("host") == rank1.get("host"):
        return False, "ranks must run on two distinct hosts"
    if not rank0.get("gpu_uuid") or not rank1.get("gpu_uuid") or rank0["gpu_uuid"] == rank1["gpu_uuid"]:
        return False, "ranks must report distinct nonempty GPU UUIDs"
    if (not rank0.get("agent_id") or not rank1.get("agent_id")
            or rank0["agent_id"] == rank1["agent_id"]
            or rank0.get("peer_id") != rank1["agent_id"]
            or rank1.get("peer_id") != rank0["agent_id"]):
        return False, "rank agent and peer IDs are not distinct and reciprocal"
    for left, right in ((rank0, rank1), (rank1, rank0)):
        if (left.get("peer_metadata_bytes") != right.get("metadata_bytes")
                or left.get("peer_metadata_sha256") != right.get("metadata_sha256")):
            return False, "peer metadata receipt does not match the other rank"
    for field in ("runtime_source_sha256", "nixl_api_sha256", "nixl_bindings_sha256"):
        if not rank0.get(field) or rank0.get(field) != rank1.get(field):
            return False, f"rank source/library hash mismatch: {field}"
    sent: dict[int, dict[str, Any]] = {}
    received: dict[int, dict[str, Any]] = {}
    for rank, result in by_rank.items():
        if result.get("status") != "complete":
            return False, f"rank {rank} did not complete"
        if len(result.get("sent", [])) != 40 or len(result.get("received", [])) != 40:
            return False, f"rank {rank} must report exactly 40 sent and 40 received rows"
        for row in result["sent"]:
            seq = row.get("sequence")
            if not isinstance(seq, int) or seq in sent or row.get("state") != "DONE":
                return False, "duplicate or non-DONE send row"
            if row.get("sender_rank") != rank or row.get("sha256") != row.get("expected_sha256"):
                return False, "send identity or checksum mismatch"
            sent[seq] = row
        for row in result["received"]:
            seq = row.get("sequence")
            if not isinstance(seq, int) or seq in received or row.get("status") != "verified":
                return False, "duplicate or unverified receive row"
            if row.get("receiver_rank") != rank or row.get("sha256") != row.get("expected_sha256"):
                return False, "receive identity or checksum mismatch"
            received[seq] = row
    expected = set(range(80))
    if set(sent) != expected or set(received) != expected:
        return False, "missing or extra sequence in the 80 transfer rows"
    for seq in range(80):
        send, recv = sent[seq], received[seq]
        for key in ("sender_rank", "receiver_rank", "size", "sha256", "expected_sha256"):
            if send.get(key) != recv.get(key):
                return False, f"sender/receiver receipt mismatch for sequence {seq}: {key}"
        if send["receiver_rank"] != 1 - send["sender_rank"]:
            return False, f"invalid direction for sequence {seq}"
        if send["size"] not in SIZES:
            return False, f"invalid transfer size for sequence {seq}"
    expected_sizes = {size: 40 for size in SIZES}
    actual_sizes = {size: sum(1 for row in sent.values() if row["size"] == size)
                    for size in SIZES}
    if actual_sizes != expected_sizes:
        return False, "expected 40 transfers for each size"
    for direction in ((0, 1), (1, 0)):
        if sum(1 for row in sent.values()
               if (row["sender_rank"], row["receiver_rank"]) == direction) != 40:
            return False, "expected 40 transfers in each direction"
    return True, "80 transfers completed with matching GPU byte hashes"


def check_results(artdir: Path) -> dict[str, Any]:
    try:
        r0 = json.loads((artdir / "rank0-result.json").read_text())
        r1 = json.loads((artdir / "rank1-result.json").read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "fail", "reason": f"cannot read both rank results: {exc}"}
    passed, reason = result_rows_valid(r0, r1)
    result = {
        "status": "pass" if passed else "fail",
        "reason": reason,
        "rank_result_sha256": {
            "0": safe_file_sha256(artdir / "rank0-result.json"),
            "1": safe_file_sha256(artdir / "rank1-result.json"),
        },
        "scope": "base NIXL peer and VRAM WRITE only; no SGLang KV, EAGLE3, or inference",
    }
    atomic_json(artdir / "final.json", result)
    return result


def _source_identity() -> dict[str, Any]:
    runtime = Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py")
    if not runtime.is_file():
        raise RuntimeError(f"Pinned runtime NIXL source is unavailable: {runtime}")
    runtime_hash = safe_file_sha256(runtime)
    if runtime_hash != EXPECTED_RUNTIME_SHA256:
        raise RuntimeError(
            "Pinned runtime NIXL source hash mismatch; refusing API assumptions "
            f"(expected {EXPECTED_RUNTIME_SHA256}, got {runtime_hash})"
        )
    nixl_api = importlib.import_module("nixl._api")
    nixl_bindings = getattr(nixl_api, "nixlBind", None)
    if nixl_bindings is None:
        raise RuntimeError("nixl._api does not expose its imported native nixlBind module")
    torch = importlib.import_module("torch")
    nixl_api_path = Path(nixl_api.__file__).resolve()
    nixl_bindings_path = Path(nixl_bindings.__file__).resolve()
    torch_path = Path(torch.__file__).resolve()
    for path in (nixl_api_path, nixl_bindings_path, torch_path):
        if not path.is_file():
            raise RuntimeError(f"Expected installed source/library file not found: {path}")
    nixl_api_hash = safe_file_sha256(nixl_api_path)
    if nixl_api_hash != EXPECTED_NIXL_API_SHA256:
        raise RuntimeError(
            "Installed NIXL Python API snapshot mismatch; refusing alternate API "
            f"(expected {EXPECTED_NIXL_API_SHA256}, got {nixl_api_hash})"
        )
    required = ("nixl_agent", "nixl_agent_config", "nixl_thread_sync_t")
    if any(not hasattr(nixl_api, name) for name in required):
        raise RuntimeError("Installed nixl._api does not match pinned SGLang API")
    return {
        "runtime_source_sha256": runtime_hash,
        "nixl_api_sha256": nixl_api_hash,
        "nixl_bindings_sha256": safe_file_sha256(nixl_bindings_path),
        "torch_file_sha256": safe_file_sha256(torch_path),
        "nixl_api_path": str(nixl_api_path),
        "nixl_bindings_path": str(nixl_bindings_path),
        "torch_path": str(torch_path),
        "nixl_version": _nixl_distribution_version(),
        "torch_version": torch.__version__,
    }


def _nixl_distribution_version() -> str:
    candidates = importlib.metadata.packages_distributions().get("nixl", [])
    for name in candidates:
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return "unknown"


def run_rank(rank: int, artdir: Path, sharedir: Path) -> dict[str, Any]:
    if rank not in (0, 1):
        raise ValueError("rank must be 0 or 1")
    artdir.mkdir(parents=True, exist_ok=True)
    private = sharedir / ".nixl-peer-probe-private"
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(private, 0o700)
    for path in (artdir, sharedir):
        if not path.is_dir():
            raise RuntimeError(f"not a directory: {path}")
    start_file = private / "start.json"
    if rank == 0:
        atomic_json(start_file, {
            "start_epoch_s": time.time(),
            "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
    wait_path(start_file, time.monotonic() + 10, "rank 0 start marker")
    start = json.loads(start_file.read_text())
    # monotonic clocks are host-local; derive one common deadline from rank 0's
    # shared epoch marker so rank 1 cannot silently extend the run window.
    deadline = float(start["start_epoch_s"]) + OVERALL_TIMEOUT_S

    ib_devices = active_ib_devices()
    if not ib_devices:
        raise RuntimeError("no active InfiniBand port found using worker autodetection")
    ib_value = ",".join(ib_devices)
    if os.environ.get("UCX_NET_DEVICES") != ib_value:
        raise RuntimeError("UCX_NET_DEVICES differs from active worker autodetection")
    if os.environ.get("UCX_POSIX_USE_PROC_LINK") != "n":
        raise RuntimeError("UCX_POSIX_USE_PROC_LINK must be n, matching the worker")

    identity = _source_identity()
    import torch
    import numpy as np
    from nixl._api import nixl_agent, nixl_agent_config, nixl_thread_sync_t

    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("probe requires exactly one visible CUDA GPU per process")
    torch.cuda.set_device(0)
    props = torch.cuda.get_device_properties(0)
    gpu_uuid = str(getattr(props, "uuid", ""))
    if not gpu_uuid:
        raise RuntimeError("installed Torch does not expose the GPU UUID")
    gpu_name = props.name
    agent_config = nixl_agent_config(
        backends=[], num_threads=8,
        sync_mode=nixl_thread_sync_t.NIXL_THREAD_SYNC_STRICT,
    )
    agent = nixl_agent(f"peer-probe-{rank}-{uuid.uuid4()}", agent_config)
    agent.create_backend("UCX", {"num_threads": "8"})
    required_agent_methods = (
        "get_agent_metadata", "add_remote_agent", "register_memory",
        "get_xfer_descs", "initialize_xfer", "transfer", "check_xfer_state",
    )
    if any(not callable(getattr(agent, name, None)) for name in required_agent_methods):
        raise RuntimeError("installed NIXL agent lacks pinned SGLang methods")

    allocation = torch.empty(BUFFER_BYTES, dtype=torch.uint8, device="cuda:0")
    allocation[:HALF_BYTES].zero_()
    allocation[HALF_BYTES:].zero_()
    torch.cuda.synchronize()
    gpu_id = torch.cuda.current_device()
    memory_row = (int(allocation.data_ptr()), BUFFER_BYTES, gpu_id, "")
    reg_descs = agent.register_memory([memory_row], "VRAM")
    if reg_descs is None or reg_descs is False:
        raise RuntimeError("NIXL GPU memory registration failed")

    local_metadata = agent.get_agent_metadata()
    if not isinstance(local_metadata, bytes) or not local_metadata:
        raise RuntimeError("get_agent_metadata must return nonempty bytes")
    metadata_file = private / f"agent-{rank}.bin"
    with metadata_file.open("xb") as stream:
        os.chmod(metadata_file, 0o600)
        stream.write(local_metadata)
        stream.flush()
        os.fsync(stream.fileno())
    local_info = {
        "rank": rank, "agent_name": agent.name,
        "metadata_file": metadata_file.name,
        "metadata_bytes": len(local_metadata),
        "metadata_sha256": hashlib.sha256(local_metadata).hexdigest(),
        "base_ptr": int(allocation.data_ptr()),
        "receive_ptr": int(allocation.data_ptr()) + HALF_BYTES,
        "gpu_id": gpu_id,
    }
    atomic_json(private / f"rank-{rank}.json", local_info)
    other_rank = 1 - rank
    other_file = private / f"rank-{other_rank}.json"
    wait_until(other_file.exists, deadline, f"rank {other_rank} agent metadata")
    other_info = json.loads(other_file.read_text())
    other_metadata = (private / other_info["metadata_file"]).read_bytes()
    if (len(other_metadata) != other_info["metadata_bytes"] or
            hashlib.sha256(other_metadata).hexdigest() != other_info["metadata_sha256"]):
        raise RuntimeError("peer metadata length/hash mismatch")
    agent.add_remote_agent(other_metadata)

    local_ready = {
        "rank": rank, "ready": True, "agent_name": agent.name,
        "gpu_uuid": gpu_uuid, "gpu_name": gpu_name, "ib_devices": ib_devices,
        **identity,
    }
    atomic_json(private / f"ready-{rank}.json", local_ready)
    wait_until(lambda: all((private / f"ready-{i}.json").exists() for i in (0, 1)),
               deadline, "both ranks ready")

    sent_rows = []
    received_rows = []
    sequence = 0
    for size in SIZES:
        for repetition in range(REPETITIONS):
            for sender_rank in (0, 1):
                receiver_rank = 1 - sender_rank
                txid = f"tx-{sequence:03d}"
                recv_ready = private / f"{txid}-receiver-ready.json"
                done_file = private / f"{txid}-done.json"
                verified_file = private / f"{txid}-verified.json"
                if rank == receiver_rank:
                    allocation[HALF_BYTES:HALF_BYTES + size].zero_()
                    torch.cuda.synchronize()
                    atomic_json(recv_ready, {"sequence": sequence, "receiver_rank": rank})
                    wait_until(done_file.exists, deadline, f"{txid} transfer completion")
                    done = json.loads(done_file.read_text())
                    if done.get("state") != "DONE" or done.get("sequence") != sequence:
                        raise RuntimeError(f"{txid} sender did not report DONE")
                    actual = allocation[HALF_BYTES:HALF_BYTES + size].detach().cpu().numpy().tobytes()
                    actual_hash = hashlib.sha256(actual).hexdigest()
                    if actual_hash != done.get("expected_sha256"):
                        raise RuntimeError(f"{txid} destination GPU checksum mismatch")
                    receive_row = {
                        "sequence": sequence, "sender_rank": sender_rank,
                        "receiver_rank": rank, "size": size,
                        "expected_sha256": done["expected_sha256"],
                        "sha256": actual_hash, "status": "verified",
                    }
                    received_rows.append(receive_row)
                    atomic_json(verified_file, receive_row)
                else:
                    wait_until(recv_ready.exists, deadline, f"{txid} receiver readiness")
                    expected = pattern_bytes(size, sender_rank, sequence)
                    expected_hash = hashlib.sha256(expected).hexdigest()
                    source = allocation[:size]
                    source.copy_(torch.from_numpy(np.frombuffer(expected, dtype=np.uint8).copy()).to("cuda:0"))
                    torch.cuda.synchronize()
                    transfer_one(
                        agent, other_info["agent_name"], source,
                        int(other_info["receive_ptr"]), size, gpu_id, txid, deadline,
                    )
                    send_row = {
                        "sequence": sequence, "sender_rank": rank,
                        "receiver_rank": receiver_rank, "size": size,
                        "expected_sha256": expected_hash, "sha256": expected_hash,
                        "state": "DONE",
                    }
                    sent_rows.append(send_row)
                    atomic_json(done_file, send_row)
                    wait_until(verified_file.exists, deadline, f"{txid} checksum receipt")
                    receipt = json.loads(verified_file.read_text())
                    if receipt != {
                        "sequence": sequence, "sender_rank": rank,
                        "receiver_rank": receiver_rank, "size": size,
                        "expected_sha256": expected_hash, "sha256": expected_hash,
                        "status": "verified",
                    }:
                        raise RuntimeError(f"{txid} receiver checksum receipt mismatch")
                sequence += 1

    result = {
        "schema": "nixl-peer-probe-result-v1", "rank": rank,
        "status": "complete", "host": socket.gethostname(),
        "peer_id": other_info["agent_name"], "agent_id": agent.name,
        "metadata_bytes": len(local_metadata),
        "metadata_sha256": hashlib.sha256(local_metadata).hexdigest(),
        "peer_metadata_bytes": other_info["metadata_bytes"],
        "peer_metadata_sha256": other_info["metadata_sha256"],
        "gpu_uuid": gpu_uuid, "gpu_name": gpu_name, "ib_devices": ib_devices,
        "ucx_net_devices": os.environ["UCX_NET_DEVICES"],
        **identity,
        "started_utc": start.get("start_utc"),
        "sent": sent_rows, "received": received_rows,
        "scope": "base NIXL peer and VRAM WRITE only; no SGLang KV, EAGLE3, or inference",
    }
    atomic_json(artdir / f"rank{rank}-result.json", result)
    if rank == 0:
        wait_until(lambda: (artdir / "rank1-result.json").exists(), deadline,
                   "rank 1 result")
        final = check_results(artdir)
        if final["status"] != "pass":
            raise RuntimeError(final["reason"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rank", type=int, choices=(0, 1))
    parser.add_argument("--art", "--artdir", dest="artdir", type=Path)
    parser.add_argument("--exchange-dir", "--sharedir", dest="sharedir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if args.artdir is None:
            parser.error("--check requires --artdir")
        result = check_results(args.artdir)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == "pass" else 1
    if args.rank is None or args.artdir is None or args.sharedir is None:
        parser.error("rank mode requires --rank, --artdir, and --sharedir")
    try:
        run_rank(args.rank, args.artdir, args.sharedir)
    except Exception as exc:
        failure = {
            "schema": "nixl-peer-probe-result-v1", "rank": args.rank,
            "status": "failed", "error_type": type(exc).__name__,
            "error": str(exc), "host": socket.gethostname(),
            "scope": "base NIXL peer and VRAM WRITE only; no SGLang KV, EAGLE3, or inference",
        }
        args.artdir.mkdir(parents=True, exist_ok=True)
        atomic_json(args.artdir / f"rank{args.rank}-result.json", failure)
        print(json.dumps(failure, sort_keys=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
