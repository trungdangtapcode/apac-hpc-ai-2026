"""Rank-local, startup-only receipts for native SGLang torch.compile wrappers.

Loaded by sitecustomize in every Python worker. The native SGLang source is
never edited; this module wraps its public context manager and PyTorch graph
context manager, and writes one atomic JSON receipt per process.
"""

from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import os
from pathlib import Path
import socket
import threading
import time
import traceback

EXPECTED_NATIVE_SHA256 = "77b1e38dba14788800b6b6351af1b5b8a80d9e42b91b57e9484ea4561d33a48c"
_LOCK = threading.RLock()
_TLS = threading.local()
_RECEIPT = None
_SHAPES = {}
_ORIGINAL_PATCH = None
_ORIGINAL_GRAPH = None
_DECORATION = None
_OBSERVATION_ACTIVE = True
_EXPECTED_CAPTURE_SHAPES = (1, 2, 4, 8, 16, 32, 48, 50, 52, 54, 56, 64)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rank_info(torch):
    initialized = bool(torch.distributed.is_available() and torch.distributed.is_initialized())
    rank = int(torch.distributed.get_rank()) if initialized else int(os.getenv("RANK", "-1"))
    world = int(torch.distributed.get_world_size()) if initialized else int(os.getenv("WORLD_SIZE", "0"))
    return initialized, rank, world


def _flat_counters(torch):
    try:
        counters = torch._dynamo.utils.counters
        return {
            f"{cat}.{key}": value
            for cat, values in counters.items() if hasattr(values, "items")
            for key, value in values.items() if isinstance(value, (int, float))
        }, None
    except Exception as exc:  # Keep missing instrumentation explicit.
        return {}, f"{type(exc).__name__}: {exc}"


def _metrics(torch):
    try:
        import torch._inductor.metrics as metrics
        vals = {k: v for k, v in vars(metrics).items()
                if isinstance(v, (int, float)) and any(x in k.lower() for x in ("kernel", "cache", "compile"))}
        return vals, None
    except Exception as exc:
        return {}, f"{type(exc).__name__}: {exc}"


def _shape_entry(n):
    key = str(n if n is not None else "unknown")
    return _SHAPES.setdefault(key, {
        "num_tokens": n,
        "patch_model_context_entries": 0,
        "compiled_callable_materialized": False,
        "callable_fields": {},
        "callable_invocations": 0,
        "successful_cuda_graph_captures": 0,
        "failed_cuda_graph_captures": 0,
        "compiler_activity": "UNPROVEN_NOT_YET_OBSERVED",
    })


def _refresh_rank(torch):
    """Ranks may be assigned after sitecustomize runs; refresh before first model hook."""
    if not _RECEIPT:
        return
    initialized, rank, world = _rank_info(torch)
    if rank >= 0:
        previous = Path(_RECEIPT["receipt_path"])
        _RECEIPT.update(rank=rank, world_size=world, distributed_initialized_at_hook=initialized)
        _RECEIPT["receipt_path"] = str(
            Path(os.environ["QWEN_TORCH_COMPILE_RECEIPT_DIR"]) / f"rank-{rank}-pid-{os.getpid()}.json"
        )
        if rank >= 0:
            _flush()
        if previous != Path(_RECEIPT["receipt_path"]):
            previous.unlink(missing_ok=True)


def _flush(state="RUNNING"):
    global _RECEIPT
    if not _RECEIPT:
        return
    receipt = dict(_RECEIPT)
    receipt.update(state=state, shapes=_SHAPES, updated_unix=time.time())
    out = Path(receipt["receipt_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, out)


class _ObservedCallable:
    def __init__(self, fn, entry, torch):
        self._fn, self._entry, self._torch = fn, entry, torch
        # Copy common Dynamo marker attributes for integrations that inspect them.
        for name in ("__wrapped__", "_torchdynamo_inline", "_torchdynamo_orig_callable", "get_compiler_config"):
            if hasattr(fn, name):
                try:
                    setattr(self, name, getattr(fn, name))
                except Exception:
                    pass

    def __call__(self, *args, **kwargs):
        if not _OBSERVATION_ACTIVE:
            return self._fn(*args, **kwargs)
        with _LOCK:
            first = self._entry["callable_invocations"] == 0
            self._entry["callable_invocations"] += 1
            getattr(_TLS, "capture_shapes", set()).add(str(self._entry["num_tokens"]))
            if first:
                before_c, err_c = _flat_counters(self._torch)
                before_m, err_m = _metrics(self._torch)
        try:
            value = self._fn(*args, **kwargs)
        except BaseException:
            with _LOCK:
                self._entry["first_call_error"] = traceback.format_exc(limit=4)
                _flush()
            raise
        if first:
            with _LOCK:
                after_c, err_after_c = _flat_counters(self._torch)
                after_m, err_after_m = _metrics(self._torch)
                dc = {k: after_c[k] - before_c.get(k, 0) for k in after_c if isinstance(after_c[k], (int, float))}
                dm = {k: after_m[k] - before_m.get(k, 0) for k in after_m if isinstance(after_m[k], (int, float))}
                unique = sum(v for k, v in dc.items() if k.endswith(".unique_graphs") and v > 0)
                fx = sum(v for k, v in dc.items() if "fxgraph" in k.lower() and "cache" in k.lower() and v > 0)
                inductor = sum(v for k, v in dc.items() if "inductor" in k.lower() and "cache" in k.lower() and v > 0)
                kernels = {k: v for k, v in dm.items() if "kernel" in k.lower() and v > 0}
                compiled = bool(unique > 0 and (fx > 0 or inductor > 0 or kernels))
                self._entry.update({
                    "counter_delta_first_call": dc,
                    "inductor_metric_delta_first_call": dm,
                    "counter_errors": [x for x in (err_c, err_after_c) if x],
                    "metric_errors": [x for x in (err_m, err_after_m) if x],
                    "dynamo_unique_graphs_positive": unique > 0,
                    "fxgraph_cache_positive": fx > 0,
                    "inductor_cache_positive": inductor > 0,
                    "generated_kernel_positive": bool(kernels),
                    "compiler_activity": "PROVEN_NUMERIC_COMPILER_ACTIVITY" if compiled else "UNPROVEN_NO_POSITIVE_OR_UNAVAILABLE_COUNTERS",
                })
                _flush()
        return value


@contextlib.contextmanager
def _observed_patch(*args, **kwargs):
    bound = inspect.signature(_ORIGINAL_PATCH).bind_partial(*args, **kwargs)
    n = bound.arguments.get("num_tokens")
    enabled = bool(bound.arguments.get("enable_compile", False))
    _refresh_rank(_torch)
    entry = _shape_entry(n)
    entry["patch_model_context_entries"] += 1
    entry["compile_enabled_argument_seen"] = enabled
    with _ORIGINAL_PATCH(*args, **kwargs) as fn:
        markers = {name: hasattr(fn, name) for name in (
            "__wrapped__", "_torchdynamo_inline", "_torchdynamo_orig_callable", "get_compiler_config")}
        entry["compiled_callable_materialized"] = bool(callable(fn) and enabled and any(markers.values()))
        entry["callable_fields"] = markers
        entry["callable_type"] = f"{type(fn).__module__}.{type(fn).__qualname__}"
        _flush()
        yield _ObservedCallable(fn, entry, _torch)


@contextlib.contextmanager
def _observed_cuda_graph(*args, **kwargs):
    previous_shapes = getattr(_TLS, "capture_shapes", None)
    shapes = set()
    _TLS.capture_shapes = shapes
    try:
        with _ORIGINAL_GRAPH(*args, **kwargs):
            yield
    except BaseException:
        with _LOCK:
            for key in shapes:
                _SHAPES.get(key, {}).setdefault("failed_cuda_graph_captures", 0)
                if key in _SHAPES:
                    _SHAPES[key]["failed_cuda_graph_captures"] += 1
            _flush()
        raise
    else:
        with _LOCK:
            for key in shapes:
                if key in _SHAPES:
                    _SHAPES[key]["successful_cuda_graph_captures"] += 1
            _flush()
            captured = {
                int(key)
                for key, entry in _SHAPES.items()
                if key.isdigit() and entry.get("successful_cuda_graph_captures", 0) > 0
            }
        if set(_EXPECTED_CAPTURE_SHAPES).issubset(captured):
            _disable_observation()
    finally:
        _TLS.capture_shapes = previous_shapes if previous_shapes is not None else set()


def _disable_observation():
    """Restore global hooks after all configured CUDA graphs are captured."""
    global _OBSERVATION_ACTIVE
    with _LOCK:
        if not _OBSERVATION_ACTIVE:
            return
        _OBSERVATION_ACTIVE = False
        if _DECORATION is not None:
            _DECORATION.patch_model = _ORIGINAL_PATCH
        _torch.cuda.graph = _ORIGINAL_GRAPH
        if _RECEIPT:
            _RECEIPT["observer_disabled_unix"] = time.time()
            _RECEIPT["observer_disabled_after_capture_shapes"] = sorted(
                int(key)
                for key, entry in _SHAPES.items()
                if key.isdigit() and entry.get("successful_cuda_graph_captures", 0) > 0
            )
        _flush()


def install():
    """Install once per Python worker; source guard is fail-closed."""
    global _RECEIPT, _ORIGINAL_PATCH, _ORIGINAL_GRAPH, _DECORATION, _torch
    if _RECEIPT is not None:
        return
    import torch
    from sglang.srt.compilation import torch_compile_decoration as decoration
    native = inspect.unwrap(decoration.patch_model)
    native_path = inspect.getsourcefile(native)
    module_path = decoration.__file__
    digest = _sha(native_path)
    if digest != EXPECTED_NATIVE_SHA256 or _sha(module_path) != EXPECTED_NATIVE_SHA256:
        raise RuntimeError(f"torch_compile observer source guard failed: {digest}")
    _torch = torch
    initialized, rank, world = _rank_info(torch)
    outdir = os.environ.get("QWEN_TORCH_COMPILE_RECEIPT_DIR")
    if not outdir:
        raise RuntimeError("QWEN_TORCH_COMPILE_RECEIPT_DIR must be set when compile observer is enabled")
    receipt_path = str(Path(outdir) / f"rank-{rank}-pid-{os.getpid()}.json")
    _RECEIPT = {
        "schema": "native-qwen-torch-compile-startup-observer-v1",
        "state": "INSTALLED",
        "receipt_path": receipt_path,
        "job_id": os.getenv("SLURM_JOB_ID"),
        "experiment_id": os.getenv("QWEN_EXPERIMENT_ID"),
        "role": os.getenv("QWEN_ROLE_NAME"),
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "rank": rank,
        "world_size": world,
        "distributed_initialized_at_install": initialized,
        "native_source_path": native_path,
        "native_source_sha256": digest,
        "module_source_sha256": _sha(module_path),
        "installed_unix": time.time(),
        "note": "Startup observer only. Callable materialization is not compile proof; first-call counters and graph-context receipts are separately recorded.",
    }
    _ORIGINAL_PATCH = decoration.patch_model
    _ORIGINAL_GRAPH = torch.cuda.graph
    _DECORATION = decoration
    decoration.patch_model = _observed_patch
    torch.cuda.graph = _observed_cuda_graph


try:
    if os.getenv("QWEN_TORCH_COMPILE_OBSERVER") == "1":
        install()
except Exception:
    # Fail closed: server import must abort; record startup failure if possible.
    raise

