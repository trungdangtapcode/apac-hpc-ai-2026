#!/usr/bin/env python3
"""Validate a lightweight observer around pinned SGLang compile and graph APIs."""

from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import os
from pathlib import Path
import signal
import sys
import time
import traceback
from types import SimpleNamespace

OUT = Path(os.environ["QWEN_PROBE_OUT"])
EXPECTED_PATCH_SHA256 = "77b1e38dba14788800b6b6351af1b5b8a80d9e42b91b57e9484ea4561d33a48c"
EXPECTED_CONTEXTLIB_SHA256 = "8b7a477f978a8532852fd81e241c78182516bc4975d672d580a5848a76e11eb6"
RESULT = {
    "state": "RUNNING_TINY_BF16_COMPILE_AND_GRAPH_INTERFACE_PROBE",
    "scope": (
        "Single H200; tiny synthetic BF16 module only. This validates observer, "
        "compile-callable and PyTorch CUDA graph interfaces. It does not validate Qwen, "
        "HPC-Ops, distributed ranks, startup budget, model quality or performance."
    ),
    "shapes": [1, 52, 64],
    "results": [],
    "observer_events": [],
}


class ProbeDeadline(Exception):
    pass


def on_alarm(_signum, _frame):
    raise ProbeDeadline("probe reached its 195-second internal deadline")


def write_result():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(RESULT, indent=2, sort_keys=True) + "\n")


def flatten_counters(torch):
    """Read numeric Dynamo counters generically; tolerate version differences."""
    try:
        counters = torch._dynamo.utils.counters
    except Exception as exc:
        return {}, {"available": False, "reason": f"{type(exc).__name__}: {exc}"}
    flat = {}
    for category, values in counters.items():
        if not hasattr(values, "items"):
            continue
        for name, value in values.items():
            if isinstance(value, (int, float)):
                flat[f"{category}.{name}"] = value
    source_path = inspect.getsourcefile(torch._dynamo.utils)
    source = Path(source_path).read_text(errors="replace") if source_path else ""
    observed = sorted(flat)
    unique_key = next((key for key in observed if key.endswith(".unique_graphs")), None)
    cache_keys = [
        key for key in observed
        if "cache" in key.lower() and ("inductor" in key.lower() or "fxgraph" in key.lower())
    ]
    supported = {
        "source_path": source_path,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest() if source_path else None,
        "counter_keys_observed": observed,
        "unique_graphs_key": unique_key,
        "unique_graphs_source_mentions_key": bool(unique_key and unique_key.rsplit(".", 1)[1] in source),
        "inductor_cache_keys": cache_keys,
        "inductor_cache_keys_supported_by_runtime_counters": bool(cache_keys),
        "unavailable_counter_note": "Counter fields are discovered from the installed runtime; absent fields are not inferred.",
    }
    return flat, supported


def counter_delta(before, after):
    return {
        key: after[key] - before.get(key, 0)
        for key in sorted(after)
        if isinstance(after[key], (int, float))
    }


def inductor_metrics_snapshot(torch):
    """Discover numeric compile/cache/kernel metrics exposed by this Torch build."""
    try:
        import torch._inductor.metrics as metrics
    except Exception as exc:
        return {}, {"available": False, "reason": f"{type(exc).__name__}: {exc}"}
    values = {
        name: value
        for name, value in vars(metrics).items()
        if any(part in name.lower() for part in ("kernel", "cache", "compile"))
        and isinstance(value, (int, float))
    }
    path = inspect.getsourcefile(metrics)
    return values, {
        "available": True,
        "source_file": path,
        "source_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest() if path else None,
        "numeric_compile_cache_kernel_fields": sorted(values),
    }


def callable_description(fn):
    fields = (
        "_torchdynamo_orig_callable",
        "_torchdynamo_inline",
        "get_compiler_config",
        "__wrapped__",
    )
    return {
        "callable": callable(fn),
        "type_module": type(fn).__module__,
        "type_name": type(fn).__qualname__,
        "callable_fields_present": {name: hasattr(fn, name) for name in fields},
    }


def safe_signature(fn):
    try:
        return {"supported": True, "value": str(inspect.signature(fn))}
    except (TypeError, ValueError) as exc:
        return {"supported": False, "reason": f"{type(exc).__name__}: {exc}"}


class ObservedCallable:
    def __init__(self, fn, events, batch_size):
        self._fn = fn
        self._events = events
        self._batch_size = batch_size

    def __call__(self, *args, **kwargs):
        self._events.append({
            "event": "torch_compile_wrapper_invoked",
            "batch_size": self._batch_size,
            "arg_count": len(args),
        })
        return self._fn(*args, **kwargs)


@contextlib.contextmanager
def observed_patch_model(decoration, torch, model, enabled, num_tokens, tp_group, events, batch_size):
    """Observe the real native context manager without editing its source."""
    native_torch_proxy = decoration.torch
    native_compile = torch.compile

    class CompileProxy:
        nn = torch.nn
        no_grad = torch.no_grad

        @staticmethod
        def compile(*args, **kwargs):
            events.append({
                "event": "torch_compile_called",
                "batch_size": batch_size,
                "mode": kwargs.get("mode"),
                "dynamic": kwargs.get("dynamic"),
            })
            compiled = native_compile(*args, **kwargs)
            description = callable_description(compiled)
            description.update({"event": "torch_compile_wrapper_returned", "batch_size": batch_size})
            events.append(description)
            if not description["callable"]:
                raise TypeError("native torch.compile did not return a callable")
            return compiled

    decoration.torch = CompileProxy
    try:
        with decoration.patch_model(
            model, enable_compile=enabled, num_tokens=num_tokens, tp_group=tp_group
        ) as native_callable:
            events.append({
                "event": "patch_model_callable_yielded",
                "batch_size": batch_size,
                **callable_description(native_callable),
            })
            if not callable(native_callable):
                raise TypeError("native patch_model did not yield a callable")
            yield ObservedCallable(native_callable, events, batch_size)
    finally:
        decoration.torch = native_torch_proxy


def main():
    signal.signal(signal.SIGALRM, on_alarm)
    started = time.monotonic()
    absolute_deadline = int(os.environ["QWEN_PROBE_DEADLINE_EPOCH"])
    remaining = absolute_deadline - int(time.time())
    if remaining <= 0:
        RESULT.update(
            state="FAIL_DEADLINE_EXPIRED_BEFORE_PYTHON_START",
            absolute_deadline_epoch=absolute_deadline,
            seconds_remaining_at_python_start=remaining,
        )
        write_result()
        raise SystemExit(124)
    alarm_seconds = min(195, remaining)
    signal.alarm(alarm_seconds)
    RESULT["deadline"] = {
        "absolute_epoch": absolute_deadline,
        "seconds_remaining_at_python_start": remaining,
        "python_alarm_seconds": alarm_seconds,
        "slurm_wall_seconds": 240,
        "cleanup_margin_seconds_from_job_start": 35,
    }
    try:
        import torch
        from torch import nn
        from sglang.srt.compilation import torch_compile_decoration as decoration

        assert torch.cuda.is_available(), "CUDA is unavailable"
        assert torch.cuda.device_count() == 1, f"expected one visible GPU, got {torch.cuda.device_count()}"
        gpu_name = torch.cuda.get_device_name(0)
        assert "H200" in gpu_name, f"expected H200, got {gpu_name}"
        decorated_patch_model = decoration.patch_model
        wrapper_file = Path(inspect.getfile(decorated_patch_model))
        wrapper_hash = hashlib.sha256(wrapper_file.read_bytes()).hexdigest()
        assert wrapper_hash == EXPECTED_CONTEXTLIB_SHA256, f"unexpected contextmanager wrapper source: {wrapper_hash}"
        native_patch_model = inspect.unwrap(decorated_patch_model)
        assert native_patch_model.__module__ == decoration.__name__, (
            f"inspect.unwrap did not return a function from {decoration.__name__}: "
            f"{native_patch_model.__module__}"
        )
        patch_file = Path(inspect.getsourcefile(native_patch_model))
        module_file = Path(decoration.__file__)
        patch_hash = hashlib.sha256(patch_file.read_bytes()).hexdigest()
        module_hash = hashlib.sha256(module_file.read_bytes()).hexdigest()
        assert patch_hash == EXPECTED_PATCH_SHA256, f"pinned unwrapped patch_model source hash mismatch: {patch_hash}"
        assert module_hash == EXPECTED_PATCH_SHA256, f"pinned SGLang module source hash mismatch: {module_hash}"
        os.environ["SGLANG_ENABLE_TORCH_COMPILE"] = "1"
        compile_before_config = callable_description(torch.compile)
        decoration.set_torch_compile_config()
        compile_after_config = callable_description(torch.compile)

        cuda_graph_info = {
            "graph_callable": callable(torch.cuda.graph),
            "graph_signature": safe_signature(torch.cuda.graph),
            "graph_class": f"{torch.cuda.CUDAGraph.__module__}.{torch.cuda.CUDAGraph.__qualname__}",
        }
        assert cuda_graph_info["graph_callable"] and callable(torch.cuda.CUDAGraph)
        RESULT.update({
            "gpu": gpu_name,
            "visible_gpu_count": torch.cuda.device_count(),
            "torch_version": torch.__version__,
            "native_patch_model_source": str(patch_file),
            "native_patch_model_sha256": patch_hash,
            "decorated_patch_model_wrapper_source": str(wrapper_file),
            "decorated_patch_model_wrapper_sha256": wrapper_hash,
            "unwrapped_callable_module_file": str(module_file),
            "unwrapped_callable_module_sha256": module_hash,
            "native_compile_configuration": {
                "set_torch_compile_config_called": True,
                "enable_env": os.environ["SGLANG_ENABLE_TORCH_COMPILE"],
                "torch_compile_callable_before": compile_before_config,
                "torch_compile_callable_after": compile_after_config,
                "torch_compile_signature_after_config": safe_signature(torch.compile),
            },
            "pytorch_cuda_graph_interface": cuda_graph_info,
            "sglang_distributed_graph_capture_executed": False,
            "distributed_initialized": torch.distributed.is_initialized(),
        })
        assert not torch.distributed.is_initialized(), "probe must remain single-rank"

        dynamo_utils_file = inspect.getsourcefile(torch._dynamo.utils)
        RESULT["counter_source"] = {
            "dynamo_utils_source_file": dynamo_utils_file,
            "torch_compile_signature": safe_signature(torch.compile),
        }

        class TinyBF16(nn.Module):
            def __init__(self):
                super().__init__()
                self.up = nn.Linear(32, 64, bias=True, dtype=torch.bfloat16)
                self.down = nn.Linear(64, 32, bias=True, dtype=torch.bfloat16)

            def forward(self, x):
                return self.down(torch.nn.functional.gelu(self.up(x))) + x

        torch.manual_seed(2026)
        model = TinyBF16().eval().cuda()
        tp_group = SimpleNamespace(ca_comm=None)
        for batch_size in RESULT["shapes"]:
            events = RESULT["observer_events"]
            x = torch.randn((batch_size, 32), device="cuda", dtype=torch.bfloat16)
            with torch.no_grad():
                eager = model(x).clone()
            counters_before, counter_support = flatten_counters(torch)
            inductor_before, inductor_support = inductor_metrics_snapshot(torch)
            event_start = len(events)
            with observed_patch_model(
                decoration, torch, model, True, batch_size, tp_group, events, batch_size
            ) as forward:
                warmup_stream = torch.cuda.Stream()
                warmup_stream.wait_stream(torch.cuda.current_stream())
                with torch.cuda.stream(warmup_stream):
                    for _ in range(2):
                        forward(x)
                torch.cuda.current_stream().wait_stream(warmup_stream)
                torch.cuda.synchronize()
                counters_warm, support_warm = flatten_counters(torch)
                inductor_warm, _ = inductor_metrics_snapshot(torch)

                capture_stream = torch.cuda.Stream()
                capture_stream.wait_stream(torch.cuda.current_stream())
                graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph, stream=capture_stream):
                    captured = forward(x)
                graph.replay()
                graph.replay()
                torch.cuda.synchronize()
                actual = captured.clone()
                counters_captured, support_captured = flatten_counters(torch)
                inductor_captured, inductor_support_captured = inductor_metrics_snapshot(torch)

            diff = (actual.float() - eager.float())
            abs_error = diff.abs().max().item()
            rel_l2 = (torch.linalg.vector_norm(diff) / torch.linalg.vector_norm(eager.float()).clamp_min(1e-12)).item()
            shape_events = events[event_start:]
            compile_invoked = any(e.get("event") == "torch_compile_called" for e in shape_events)
            wrapper_returned = any(e.get("event") == "torch_compile_wrapper_returned" for e in shape_events)
            wrapper_used = any(e.get("event") == "torch_compile_wrapper_invoked" for e in shape_events)
            assert compile_invoked and wrapper_returned and wrapper_used, f"observer missed compile callable lifecycle at batch {batch_size}"
            assert abs_error <= 0.02 and rel_l2 <= 0.01, f"eager-vs-replay mismatch at batch {batch_size}: abs={abs_error}, rel_l2={rel_l2}"
            warm_delta = counter_delta(counters_before, counters_warm)
            capture_delta = counter_delta(counters_warm, counters_captured)
            unique_graph_delta = sum(
                value for key, value in warm_delta.items()
                if key.endswith(".unique_graphs") and isinstance(value, (int, float))
            )
            lower_compile_deltas = {
                key: value for key, value in warm_delta.items()
                if any(marker in key.lower() for marker in ("inductor", "fxgraph", "generated_kernel", "kernel_compile"))
                and isinstance(value, (int, float))
            }
            inductor_metric_delta = {
                key: inductor_warm[key] - inductor_before.get(key, 0)
                for key in sorted(inductor_warm)
                if isinstance(inductor_warm[key], (int, float))
            }
            inductor_capture_delta = {
                key: inductor_captured[key] - inductor_warm.get(key, 0)
                for key in sorted(inductor_captured)
                if isinstance(inductor_captured[key], (int, float))
            }
            positive_compile_metrics = {
                key: value for key, value in inductor_metric_delta.items()
                if value > 0
            }
            numeric_compile_activity = (
                any(value > 0 for value in lower_compile_deltas.values())
                or bool(positive_compile_metrics)
            )
            compile_activity_status = (
                "PROVEN_NUMERIC_COMPILER_ACTIVITY"
                if unique_graph_delta > 0 and numeric_compile_activity
                else "UNPROVEN_COUNTERS_UNSUPPORTED_OR_NO_POSITIVE_DELTA"
            )
            RESULT["results"].append({
                "batch_size": batch_size,
                "num_tokens": batch_size,
                "compile_invoked": compile_invoked,
                "torch_compile_wrapper_returned": wrapper_returned,
                "torch_compile_wrapper_invoked": wrapper_used,
                "compiler_activity_status": compile_activity_status,
                "dynamo_unique_graphs_delta_after_warmup": unique_graph_delta,
                "lower_compiler_counter_deltas_after_warmup": lower_compile_deltas,
                "inductor_metric_support": inductor_support,
                "inductor_metric_support_after_capture": inductor_support_captured,
                "inductor_metric_delta_after_warmup": inductor_metric_delta,
                "inductor_metric_delta_after_graph_capture": inductor_capture_delta,
                "positive_inductor_compile_metrics_after_warmup": positive_compile_metrics,
                "graph_capture_and_two_replays": "PASS",
                "max_abs_error": abs_error,
                "relative_l2_error": rel_l2,
                "tolerance": {"max_abs_error": 0.02, "relative_l2": 0.01},
                "dynamo_counter_support_by_stage": {
                    "before": counter_support,
                    "after_warmup": support_warm,
                    "after_graph_capture_and_replay": support_captured,
                },
                "counter_delta_after_warmup": warm_delta,
                "counter_delta_after_graph_capture": capture_delta,
                "observer_events": shape_events,
            })
            write_result()
        any_compile_activity = any(
            item["compiler_activity_status"] == "PROVEN_NUMERIC_COMPILER_ACTIVITY"
            for item in RESULT["results"]
        )
        RESULT["compiler_activity_claim"] = (
            "PROVEN_FOR_AT_LEAST_ONE_FIXTURE_SHAPE"
            if any_compile_activity
            else "UNPROVEN_COUNTERS_UNSUPPORTED_OR_NO_POSITIVE_DELTA"
        )
        RESULT.update(
            state=(
                "PASS_TINY_BF16_OBSERVER_GRAPH_AND_NUMERIC_COMPILE_ACTIVITY"
                if any_compile_activity
                else "PASS_OBSERVER_GRAPH_INTERFACE_COMPILE_MATERIALIZATION_UNPROVEN"
            ),
            elapsed_seconds=time.monotonic()-started,
        )
    except BaseException as exc:
        RESULT.update(
            state="FAIL_TINY_BF16_COMPILE_OBSERVER_OR_GRAPH_INTERFACE",
            error_type=type(exc).__name__,
            error=str(exc),
            traceback=traceback.format_exc(),
            elapsed_seconds=time.monotonic()-started,
        )
        write_result()
        raise
    finally:
        signal.alarm(0)
        write_result()
    print(RESULT["state"], flush=True)


if __name__ == "__main__":
    main()
