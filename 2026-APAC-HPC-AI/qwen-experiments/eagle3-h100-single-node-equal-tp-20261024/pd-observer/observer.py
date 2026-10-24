"""Bounded CPU-metadata-only observers for the prospective EAGLE3 PD bundle."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable


METADATA_FIELDS = (
    "output_ids",
    "cached_tokens",
    "output_token_logprobs_val",
    "output_token_logprobs_idx",
    "output_top_logprobs_val",
    "output_top_logprobs_idx",
    "output_token_sampling_mask_len",
    "output_token_sampling_mask_idx",
    "output_token_sampling_logprobs",
    "output_topk_p",
    "output_topk_index",
    "output_hidden_states",
    "output_dsa_topk_indices",
    "bootstrap_room",
)
MAX_TRANSFER_RECORDS = 128
_lock = threading.Lock()
_transfer_counts: dict[str, int] = {}
_transfer_dropped: dict[str, int] = {}


def _role_rank() -> tuple[str, int, Path]:
    role = os.environ.get("QWEN_ROLE_NAME", "").strip().lower()
    if role not in {"prefill-0", "decode-0"}:
        raise RuntimeError("observer requires a reviewed QWEN_ROLE_NAME worker identity")
    # Import lazily: this function runs after the server initializes SGLang TP.
    import torch.distributed as dist
    from sglang.srt.distributed import get_tp_group

    if not dist.is_initialized():
        raise RuntimeError("observer requires initialized torch.distributed")
    group = get_tp_group()
    rank = getattr(group, "rank", None)
    if isinstance(rank, bool) or not isinstance(rank, int) or rank < 0:
        raise RuntimeError("observer cannot establish initialized TP-group rank")
    artdir = os.environ.get("QWEN_ARTDIR", "").strip()
    if not artdir:
        raise RuntimeError("observer requires QWEN_ARTDIR")
    root = Path(artdir)
    out = root / "pd-observer" / role / f"tp-{rank}"
    out.mkdir(parents=True, exist_ok=True)
    return role, rank, out


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".observer-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, sort_keys=True, separators=(",", ":"))
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def _json_safe_int(value: Any) -> int | None:
    try:
        out = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return out if out >= 0 else None


def _metadata_record(instance: Any, result: Any, role: str, rank: int) -> dict[str, Any]:
    if not isinstance(result, tuple) or len(result) != 3:
        raise RuntimeError("get_buf_infos returned unexpected result shape")
    ptrs, lens, item_lens = result
    tensors: list[tuple[str, Any]] = []
    for name in METADATA_FIELDS:
        tensor = getattr(instance, name, None)
        if tensor is not None:
            tensors.append((name, tensor))
    rows = []
    ptr_equal = len(ptrs) == len(tensors)
    lens_equal = len(lens) == len(tensors)
    item_lens_equal = len(item_lens) == len(tensors)
    total_bytes = 0
    for i, (name, tensor) in enumerate(tensors):
        shape = [int(x) for x in tensor.shape]
        strides = [int(x) for x in tensor.stride()]
        nbytes = _json_safe_int(tensor.nbytes)
        row_nbytes = _json_safe_int(tensor[0].nbytes) if shape and shape[0] else None
        item_len = _json_safe_int(item_lens[i]) if i < len(item_lens) else None
        if nbytes is None or row_nbytes is None:
            raise RuntimeError("could not measure CPU metadata tensor byte widths")
        rows.append({
            "name": name,
            "shape": shape,
            "strides": strides,
            "dtype": str(tensor.dtype),
            "row_nbytes": row_nbytes,
            "item_len": item_len,
            "row_count": shape[0] if shape else 0,
            "nbytes": nbytes,
        })
        total_bytes += nbytes
        # Compare, but never serialize, pointer values.
        ptr_equal = ptr_equal and i < len(ptrs) and _json_safe_int(ptrs[i]) == _json_safe_int(tensor.data_ptr())
        lens_equal = lens_equal and i < len(lens) and _json_safe_int(lens[i]) == nbytes
        item_lens_equal = item_lens_equal and item_len == row_nbytes

    return {
        "schema": "eagle3-pd-metadata-v1",
        "role": role,
        "role_kind": role.split("-", 1)[0],
        "tp_rank": rank,
        "rank_source": "initialized sglang.srt.distributed.get_tp_group().rank",
        "ordered_names": [row["name"] for row in rows],
        "tensor_count": len(rows),
        "total_row_count": sum(row["row_count"] for row in rows),
        "ptr_list_count": len(ptrs),
        "lens_list_count": len(lens),
        "item_lens_list_count": len(item_lens),
        "total_bytes": total_bytes,
        "original_ptrs_equal_tensor_data_ptrs": ptr_equal,
        "original_lens_equal_tensor_nbytes": lens_equal,
        "original_item_lens_equal_tensor_row_nbytes": item_lens_equal,
        "rows": rows,
    }


def wrap_get_buf_infos(method: Callable[..., Any]) -> Callable[..., Any]:
    """Append one bounded receipt after the source method and return its tuple."""
    state = {"written": False}

    def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        result = method(self, *args, **kwargs)
        # Fail closed on missing role/rank, but preserve the native return value.
        role, rank, out = _role_rank()
        if not state["written"]:
            record = _metadata_record(self, result, role, rank)
            record["recorded_unix_ns"] = time.time_ns()
            _atomic_json(out / "metadata.json", record)
            state["written"] = True
        return result

    wrapped.__name__ = getattr(method, "__name__", "get_buf_infos")
    wrapped.__doc__ = getattr(method, "__doc__", None)
    wrapped.__wrapped__ = method  # type: ignore[attr-defined]
    return wrapped


def metadata_observer(method: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for a source-derived MetadataBuffers implementation."""
    wrapped = wrap_get_buf_infos(method)
    wrapped.__observer_wrapped__ = True  # type: ignore[attr-defined]
    return wrapped


def _bounded_transfer_record(kind: str, peer_name: Any, marker: dict[str, Any]) -> None:
    role, rank, out = _role_rank()
    key = f"{role}:{rank}"
    with _lock:
        if sum(_transfer_counts.values()) >= MAX_TRANSFER_RECORDS:
            _transfer_dropped[key] = _transfer_dropped.get(key, 0) + 1
            return
        _transfer_counts[key] = _transfer_counts.get(key, 0) + 1
        record = {
            "schema": "eagle3-pd-transfer-v1",
            "role": role,
            "role_kind": role.split("-", 1)[0],
            "tp_rank": rank,
            "kind": kind,
            "peer_name_sha256": hashlib.sha256(str(peer_name).encode("utf-8", "replace")).hexdigest(),
            **marker,
        }
        path = out / "transfers.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def _arg_count(args: tuple[Any, ...], kwargs: dict[str, Any], name: str, index: int) -> int | None:
    value = kwargs.get(name, args[index] if len(args) > index else None)
    try:
        return len(value)
    except (TypeError, AttributeError):
        return None


def wrap_transfer(method: Callable[..., Any], kind: str) -> Callable[..., Any]:
    """Record method call and API return/exception; handles do not imply completion."""
    def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        peer = kwargs.get("peer_name", args[0] if args else "")
        if kind == "send_kvcache_slice":
            src_pages = _arg_count(args, kwargs, "prefill_kv_indices", 1)
            dst_pages = _arg_count(args, kwargs, "dst_kv_indices", 2)
            details = {"source_page_count": src_pages, "destination_page_count": dst_pages}
        else:
            dst_ptrs = kwargs.get("dst_aux_ptrs", args[2] if len(args) > 2 else None)
            details = {
                "row_indices": list(range(len(dst_ptrs))) if dst_ptrs is not None and len(dst_ptrs) <= 64 else None,
                "row_count": len(dst_ptrs) if dst_ptrs is not None else None,
                "source_request_page_index": _json_safe_int(kwargs.get("prefill_aux_index", args[1] if len(args) > 1 else None)),
                "destination_request_page_index": _json_safe_int(kwargs.get("dst_aux_index", args[3] if len(args) > 3 else None)),
            }
        started = time.time_ns()
        _bounded_transfer_record(kind, peer, {"marker": "start", "time_unix_ns": started, **details})
        try:
            result = method(self, *args, **kwargs)
        except BaseException as exc:
            _bounded_transfer_record(kind, peer, {
                "marker": "exception", "time_unix_ns": time.time_ns(),
                "exception_type": type(exc).__name__, **details,
            })
            raise
        _bounded_transfer_record(kind, peer, {
            "marker": "returned_handle", "time_unix_ns": time.time_ns(),
            "handle_is_none": result is None,
            "handle_type": type(result).__name__,
            "completion_semantics": "returned handle is not transfer completion",
            **details,
        })
        return result

    wrapped.__name__ = getattr(method, "__name__", kind)
    wrapped.__doc__ = getattr(method, "__doc__", None)
    wrapped.__wrapped__ = method  # type: ignore[attr-defined]
    return wrapped


def transfer_observer(kind: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory for a fully derived native NIXL module."""
    def decorate(method: Callable[..., Any]) -> Callable[..., Any]:
        wrapped = wrap_transfer(method, kind)
        wrapped.__observer_wrapped__ = True  # type: ignore[attr-defined]
        return wrapped
    return decorate


def install_metadata(module: Any) -> None:
    cls = getattr(module, "MetadataBuffers", None)
    method = getattr(cls, "get_buf_infos", None) if cls else None
    if method is None or getattr(method, "__observer_wrapped__", False):
        return
    wrapped = wrap_get_buf_infos(method)
    wrapped.__observer_wrapped__ = True  # type: ignore[attr-defined]
    cls.get_buf_infos = wrapped


def install_nixl(module: Any) -> None:
    cls = getattr(module, "NixlKVManager", None)
    if cls is None:
        raise RuntimeError("pinned NIXL module lacks NixlKVManager")
    for name in ("send_kvcache_slice", "send_aux"):
        method = getattr(cls, name, None)
        if method is None:
            raise RuntimeError(f"pinned NIXL module lacks {name}")
        if not getattr(method, "__observer_wrapped__", False):
            wrapped = wrap_transfer(method, name)
            wrapped.__observer_wrapped__ = True  # type: ignore[attr-defined]
            setattr(cls, name, wrapped)
