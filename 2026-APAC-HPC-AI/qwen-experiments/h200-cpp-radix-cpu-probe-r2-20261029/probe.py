#!/usr/bin/env python3
"""CPU-only source/JIT and radix-tree invariant probe; no model or GPU work."""
from __future__ import annotations
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

OUT = Path(os.environ["APAC_CPP_RADIX_RESULT"])
ROOT = Path(os.environ["APAC_CPP_RADIX_SOURCE_ROOT"])
IMAGE_SHA256 = "b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5"
started = time.monotonic()
result = {
    "state": "RUNNING",
    "scope": "CPU-only C++ extension and synthetic radix-tree data structure; not RadixCacheCpp integration, P/D, Qwen, or performance.",
    "image": "/scratch/enroot-images/sglang-harbor.sqsh",
    "image_sha256_from_pinned_provenance": IMAGE_SHA256,
    "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    "nvidia_visible_devices": os.environ.get("NVIDIA_VISIBLE_DEVICES"),
    "cases": [],
}

def save():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2) + "\n")
    tmp.replace(OUT)

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def tool_version(cmd: list[str]) -> str | None:
    exe = shutil.which(cmd[0])
    if exe is None:
        return None
    p = subprocess.run([exe, *cmd[1:]], text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=5, check=False)
    return p.stdout.splitlines()[0] if p.stdout else f"exit={p.returncode}"

def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)

save()
try:
    require(os.environ.get("CUDA_VISIBLE_DEVICES", "") == "", "CUDA_VISIBLE_DEVICES must be empty")
    require(os.environ.get("NVIDIA_VISIBLE_DEVICES") == "void", "NVIDIA_VISIBLE_DEVICES must be void")
    import torch
    result.update(
        python=platform.python_version(),
        torch=torch.__version__,
        torch_compiled_cuda_version=torch.version.cuda,
        torch_cuda_available=torch.cuda.is_available(),
        torch_visible_device_count=torch.cuda.device_count(),
        cxx_environment=os.environ.get("CXX", "<default c++>"),
        compiler_path=shutil.which(os.environ.get("CXX") or "c++"),
        compiler_version=tool_version([os.environ.get("CXX") or "c++", "--version"]),
        gxx_version=tool_version(["g++", "--version"]),
        ninja_version=tool_version(["ninja", "--version"]),
        max_jobs=os.environ.get("MAX_JOBS"),
        omp_num_threads=os.environ.get("OMP_NUM_THREADS"),
        home=os.environ.get("HOME"),
        torch_extensions_dir=os.environ.get("TORCH_EXTENSIONS_DIR"),
    )
    require(not torch.cuda.is_available(), "CUDA unexpectedly available in zero-GPU allocation")
    require(torch.cuda.device_count() == 0, "A CUDA device is visible in zero-GPU allocation")
    require(result["compiler_path"] is not None and result["gxx_version"] is not None,
            "C++ compiler missing")
    require(result["ninja_version"] is not None, "Ninja missing")
    result["phase_import_torch_seconds"] = round(time.monotonic() - started, 3)
    save()

    pinned_runtime = Path("/sgl-workspace/sglang/python/sglang/srt/mem_cache/cpp_radix_tree")
    pinned_evidence = ROOT / "cpp_radix_tree"
    prebuild_names = ["radix_tree.py", "tree_v2.cpp", "tree_v2_debug.cpp", "tree_v2.h",
                      "tree_v2_binding.cpp", "tree_v2_impl.h", "tree_v2_node.h", "common.h"]
    prebuild_hashes = {name: sha(pinned_runtime / name) for name in prebuild_names}
    require(prebuild_hashes == {name: sha(pinned_evidence / name) for name in prebuild_names},
            "Native C++ source pin failed before JIT import")
    result["prebuild_runtime_source_sha256"] = prebuild_hashes
    save()

    jit_import_started = time.monotonic()
    from sglang.srt.mem_cache.cpp_radix_tree.radix_tree import RadixTreeCpp
    from sglang.srt.mem_cache.cpp_radix_tree import radix_tree as radix_module
    runtime_dir = Path(radix_module.__file__).resolve().parent
    evidence_tree = ROOT / "cpp_radix_tree"
    source_names = ["radix_tree.py", "tree_v2.cpp", "tree_v2_debug.cpp",
                    "tree_v2.h", "tree_v2_binding.cpp", "tree_v2_impl.h",
                    "tree_v2_node.h", "common.h"]
    runtime_hashes = {name: sha(runtime_dir / name) for name in source_names}
    evidence_hashes = {name: sha(evidence_tree / name) for name in source_names}
    require(runtime_hashes == evidence_hashes, "Runtime C++ extension sources differ from frozen evidence")
    extension_path = Path(radix_module.radix_tree_cpp.__file__).resolve()
    result.update(
        extension_path=str(extension_path),
        extension_sha256=sha(extension_path),
        extension_jit_module=radix_module.radix_tree_cpp.__name__,
        runtime_source_dir=str(runtime_dir),
        runtime_source_sha256=runtime_hashes,
    )
    require("radix_tree_cpp" in result["extension_path"], "Loaded extension path is unexpected")
    extension_dir = Path(os.environ["TORCH_EXTENSIONS_DIR"]).resolve()
    require(extension_path.is_relative_to(extension_dir), "Extension did not build into the private job cache")
    result["phase_jit_import_seconds"] = round(time.monotonic() - jit_import_started, 3)
    save()

    def run_fixture(page_size: int) -> dict:
        tree = RadixTreeCpp(disabled=False, host_size=None, page_size=page_size,
                            write_through_threshold=1)
        key_a = list(range(32))
        key_b = key_a[:16] + list(range(1000, 1016))
        val_a = torch.arange(100, 132, dtype=torch.int64, device="cpu")
        val_a_duplicate = torch.arange(900, 932, dtype=torch.int64, device="cpu")
        val_b = torch.arange(500, 532, dtype=torch.int64, device="cpu")

        handles0, matched0 = tree.writing_through(key_a, val_a)
        require(matched0 == 0 and len(handles0) == 0, f"page{page_size}: first insert mismatch")
        handles1, matched1 = tree.writing_through(key_a, val_a_duplicate)
        require(matched1 == 32 and len(handles1) == 0, f"page{page_size}: duplicate match mismatch")
        indices_a, host_len, node_a, _ = tree.match_prefix(key_a)
        got_a = torch.cat(indices_a) if indices_a else torch.empty(0, dtype=torch.int64)
        require(host_len == 0 and torch.equal(got_a, val_a), f"page{page_size}: original duplicate values not retained")
        indices_prefix, _, _, _ = tree.match_prefix(key_a[:16])
        got_prefix = torch.cat(indices_prefix) if indices_prefix else torch.empty(0, dtype=torch.int64)
        require(torch.equal(got_prefix, val_a[:16]), f"page{page_size}: 16-token prefix mismatch")

        handles_b, matched_b = tree.writing_through(key_b, val_b)
        require(matched_b == 16 and len(handles_b) == 0, f"page{page_size}: overlapping split boundary mismatch: {matched_b}")
        indices_a2, _, node_a2, _ = tree.match_prefix(key_a)
        indices_b2, _, _, _ = tree.match_prefix(key_b)
        got_a2 = torch.cat(indices_a2)
        got_b2 = torch.cat(indices_b2)
        expected_b = torch.cat([val_a[:16], val_b[16:]])
        require(torch.equal(got_a2, val_a), f"page{page_size}: split changed prior key mapping")
        require(torch.equal(got_b2, expected_b), f"page{page_size}: split did not reuse prefix plus new tail")
        require(tree.total_size() == 48, f"page{page_size}: expected 48 unique cached indices, got {tree.total_size()}")

        tree.lock_ref(node_a2, True)
        protected_before = tree.protected_size()
        require(protected_before == 32, f"page{page_size}: lock did not protect prefix path: {protected_before}")
        evicted = tree.evict(10_000)
        evicted_values = torch.cat(evicted) if evicted else torch.empty(0, dtype=torch.int64)
        require(torch.equal(torch.sort(evicted_values).values, torch.sort(val_b[16:]).values),
                f"page{page_size}: eviction freed wrong/unprotected indices")
        require(tree.total_size() == 32 and tree.protected_size() == 32,
                f"page{page_size}: protected path was evicted")
        tree.lock_ref(node_a2, False)
        evicted_after_unlock = tree.evict(10_000)
        freed_after_unlock = sum(t.numel() for t in evicted_after_unlock)
        require(freed_after_unlock == 32 and tree.total_size() == 0,
                f"page{page_size}: unlock did not permit full eviction")
        tree.reset()
        require(tree.total_size() == 0 and tree.evictable_size() == 0 and tree.protected_size() == 0,
                f"page{page_size}: reset size counters are nonzero")
        return {
            "page_size": page_size,
            "interpretation": "page1 is the production-page-size fixture; page16 is metadata-only and does not qualify page16 KV behavior",
            "initial_insert_matched_tokens": matched0,
            "exact_repeat_matched_tokens": matched1,
            "prefix_tokens_checked": 16,
            "overlap_matched_tokens": matched_b,
            "unique_cached_indices_after_split": 48,
            "protected_indices_while_locked": protected_before,
            "indices_evicted_while_locked": int(evicted_values.numel()),
            "indices_evicted_after_unlock": freed_after_unlock,
            "reset_sizes": {"total": tree.total_size(), "evictable": tree.evictable_size(), "protected": tree.protected_size()},
            "result": "PASS",
        }

    for page in (1, 16):
        result["cases"].append(run_fixture(page))
        save()
    result["state"] = "PASS_CPU_FIXTURES_ONLY"
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    save()
    print("PASS_CPU_FIXTURES_ONLY")
except BaseException as exc:
    result.update(state="FAIL", error_type=type(exc).__name__, error=str(exc),
                  traceback=traceback.format_exc(),
                  elapsed_seconds=round(time.monotonic() - started, 3))
    save()
    raise
