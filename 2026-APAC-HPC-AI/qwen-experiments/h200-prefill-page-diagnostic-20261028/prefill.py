#!/usr/bin/env python3
"""Constructed BF16 FlashInfer causal prefill diagnostic; never an acceptance test."""
import hashlib
import inspect
import json
import math
import os
import traceback
from pathlib import Path
from types import SimpleNamespace

Q = Path("/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments")
D = Q / "h200-prefill-page-diagnostic-20261028"
A = Q / "runs" / os.environ["SLURM_JOB_ID"]
POOL_SHA = "29ef7b37d2e12b1a4b674b97c33b3ceb05cd8421a3742eb33cb6a75f52896ddc"
PREFILL_SHA = "7f4926dcf1610dfd058716e9ba3d8b08f15268e607ea1e28bef7d28b8b2f889e"
BACKEND_SHA = "3cb0b4d5c4d3e8e94724d07c91130ab69d85e73c84cefaf3f69a5ad7813f5c7e"
LENGTHS = (15, 16, 17, 31, 32, 33, 4000)
PAGES = (1, 16)
TP = (4, 8)
SCALE = 1.0 / math.sqrt(128)

result = {
    "state": "RUNNING_DIAGNOSTIC_ONLY",
    "scope": "Constructed one-layer Qwen GQA geometry on one H200; no model, P/D, gate-pass, or speed claim.",
    "criteria": "Original relative-L2 <= 0.01 and max-absolute <= 0.005 are recorded as flags only; completion never means pass.",
    "seed": 2026,
    "lengths_tokens": list(LENGTHS),
    "page_sizes_tokens": list(PAGES),
    "tp_hypotheses": list(TP),
    "cases": [],
}


def save():
    A.mkdir(parents=True, exist_ok=True)
    (A / "prefill.json").write_text(json.dumps(result, indent=2) + "\n")


def case_record(**fields):
    result["cases"].append(fields)
    save()


try:
    import torch
    import flashinfer
    from sglang.srt.mem_cache.memory_pool import MHATokenToKVPool
    from sglang.srt.layers.attention import flashinfer_backend as sglang_backend

    assert torch.cuda.is_available() and torch.cuda.device_count() == 1
    gpu = torch.cuda.get_device_name(0)
    assert "H200" in gpu, gpu
    pool_source = Path(inspect.getfile(MHATokenToKVPool))
    prefill_source = Path(inspect.getfile(flashinfer.BatchPrefillWithPagedKVCacheWrapper))
    backend_source = Path(inspect.getfile(sglang_backend))
    actual_prefill = hashlib.sha256(prefill_source.read_bytes()).hexdigest()
    assert actual_prefill == PREFILL_SHA, actual_prefill
    actual_backend = hashlib.sha256(backend_source.read_bytes()).hexdigest()
    assert actual_backend == BACKEND_SHA, actual_backend
    actual_pool = hashlib.sha256(pool_source.read_bytes()).hexdigest()
    assert actual_pool == POOL_SHA, actual_pool
    cfg_path = Path("/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8/config.json")
    config = json.loads(cfg_path.read_text())
    assert (config["num_attention_heads"], config["num_key_value_heads"], config["head_dim"]) == (64, 4, 128)

    workspace = torch.empty(128 * 1024 * 1024, dtype=torch.uint8, device="cuda")
    oracle_tf32_before = torch.backends.cuda.matmul.allow_tf32
    torch.manual_seed(2026)
    torch.backends.cuda.matmul.allow_tf32 = False
    tf32_flag = torch.backends.cuda.matmul.allow_tf32
    assert not tf32_flag
    # One common BF16 KV stream for every geometry and page-size pair.
    max_len = max(LENGTHS)
    keys = torch.randn(max_len, 1, 128, device="cuda", dtype=torch.bfloat16)
    values = torch.randn_like(keys)
    q_stream = {tp: torch.randn(max_len, 64 // tp, 128, device="cuda", dtype=torch.bfloat16) for tp in TP}
    pools = {}
    for page in PAGES:
        size = math.ceil(max_len / page) * page
        pool = MHATokenToKVPool(
            size=size, page_size=page, dtype=torch.bfloat16, head_num=1,
            head_dim=128, layer_num=1, device="cuda", enable_memory_saver=False,
            kv_cache_layout="nhd",
        )
        loc = torch.arange(page, page + max_len, device="cuda", dtype=torch.int64)
        pool.set_kv_buffer(SimpleNamespace(layer_id=0), loc, keys, values)
        torch.cuda.synchronize()
        kbuf, vbuf = pool.get_kv_buffer(0)
        assert pool.store_dtype == torch.bfloat16 and pool.kv_cache_layout == "nhd"
        assert torch.equal(kbuf[loc], keys) and torch.equal(vbuf[loc], values)
        ptrs, lens, items = pool.get_contiguous_buf_infos()
        assert len(ptrs) == len(lens) == len(items) == 2
        assert items == [page * 128 * 2] * 2
        pools[page] = (pool, kbuf, vbuf)

    result.update(
        gpu_name=gpu,
        gpu_uuid=str(torch.cuda.get_device_properties(0).uuid),
        model_config_sha256=hashlib.sha256(cfg_path.read_bytes()).hexdigest(),
        pool_source_sha256=actual_pool,
        flashinfer_prefill_source_sha256=actual_prefill,
        sglang_backend_source_sha256=actual_backend,
        tf32_allowed_for_oracle=tf32_flag,
        oracle_tf32_preexisting_allowed=oracle_tf32_before,
        constructed_layers=[0],
        head_geometry="Q heads are model_attention_heads / TP (16 for TP4; 8 for TP8), one KV head, head_dim 128; constructed metadata only.",
        cache="Native MHATokenToKVPool BF16 NHD; exact write/read verified for each page size.",
        long_case_oracle="For length 4000 query the final 8 rows only; reference rows use their causal suffix positions. Native kernels still process all KV tokens.",
    )
    save()

    previous = {}
    # Ragged causal prefill is independent of page size; run once per TP and length.
    for tp in TP:
        qheads = 64 // tp
        for length in LENGTHS:
            nq = min(length, 8) if length == 4000 else length
            q = q_stream[tp][length - nq:length]
            qo_indptr = torch.tensor([0, nq], dtype=torch.int32, device="cuda")
            kv_indptr = torch.tensor([0, length], dtype=torch.int32, device="cuda")
            try:
                wrapper = flashinfer.BatchPrefillWithRaggedKVCacheWrapper(workspace, "NHD")
                wrapper.plan(qo_indptr, kv_indptr, qheads, 1, 128, causal=True,
                             sm_scale=SCALE, q_data_type=torch.bfloat16,
                             kv_data_type=torch.bfloat16)
                output = wrapper.run(q, keys[:length], values[:length])
                torch.cuda.synchronize()
                assert output.shape == q.shape and output.dtype == torch.bfloat16
                assert bool(torch.isfinite(output).all()), 'Nonfinite ragged output'
                ref = []
                for j in range(nq):
                    upto = length - nq + j + 1
                    score = torch.einsum("hd,ld->hl", q[j].float(), keys[:upto, 0].float()) * SCALE
                    ref.append(torch.einsum("hl,ld->hd", torch.softmax(score, dim=-1), values[:upto, 0].float()))
                oracle = torch.stack(ref).to(torch.float32)
                delta = output.float() - oracle
                rel = (torch.linalg.vector_norm(delta) / torch.linalg.vector_norm(oracle).clamp_min(1e-12)).item()
                absmax = delta.abs().max().item()
                case_record(kind="ragged_causal", tp=tp, q_heads=qheads, kv_heads=1,
                            head_dim=128, length_tokens=length, query_rows=nq,
                            sampled_query_positions=list(range(length - nq, length)),
                            q_shape=list(q.shape), k_shape=[length, 1, 128], v_shape=[length, 1, 128],
                            output_shape=list(output.shape), q_dtype=str(q.dtype), kv_dtype=str(keys.dtype),
                            output_dtype=str(output.dtype), finite=bool(torch.isfinite(output).all()),
                            output_shape_and_dtype_ok=(list(output.shape) == list(q.shape) and output.dtype == torch.bfloat16),
                            relative_l2_vs_fp32=rel, max_absolute_vs_fp32=absmax,
                            original_threshold_flags={"relative_l2_le_0_01": rel <= 0.01,
                                                     "max_absolute_le_0_005": absmax <= 0.005},
                            backend=str(getattr(wrapper, "_backend", "not_exposed")), error=None)
            except BaseException as exc:
                case_record(kind="ragged_causal", tp=tp, q_heads=qheads, kv_heads=1,
                            head_dim=128, length_tokens=length, query_rows=nq,
                            error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc())

    # Page-size pair cases. Small lengths query every position; length 4000 queries its final eight rows.
    for tp in TP:
        qheads = 64 // tp
        for page in PAGES:
            pool, kbuf, vbuf = pools[page]
            for length in LENGTHS:
                nq = min(length, 8) if length == 4000 else length
                q = q_stream[tp][length - nq:length]
                npages = math.ceil(length / page)
                qo_indptr = torch.tensor([0, nq], dtype=torch.int32, device="cuda")
                kv_indptr = torch.tensor([0, npages], dtype=torch.int32, device="cuda")
                page_indices = torch.arange(1, npages + 1, dtype=torch.int32, device="cuda")
                last_page_len = torch.tensor([(length - 1) % page + 1], dtype=torch.int32, device="cuda")
                geometry = {"tp_hypothesis": tp, "q_heads": qheads, "kv_heads": 1,
                            "head_dim": 128, "page_size_tokens": page, "length_tokens": length,
                            "query_rows": nq, "sampled_query_positions": list(range(length - nq, length)),
                            "q_shape": list(q.shape),
                            "cache_k_shape": list(kbuf.shape), "cache_v_shape": list(vbuf.shape),
                            "cache_layout": "NHD", "cache_dtype": str(pool.store_dtype),
                            "k_stride": list(kbuf.stride()), "v_stride": list(vbuf.stride()),
                            "first_page_reserved": True,
                            "region_bytes": pool.get_contiguous_buf_infos()[1],
                            "item_bytes": pool.get_contiguous_buf_infos()[2],
                            "page_count": npages, "indptr_shape": list(kv_indptr.shape),
                            "page_indices_shape": list(page_indices.shape),
                            "last_page_len": int(last_page_len.item())}
                try:
                    wrapper = flashinfer.BatchPrefillWithPagedKVCacheWrapper(workspace, "NHD")
                    wrapper.plan(qo_indptr, kv_indptr, page_indices, last_page_len,
                                 qheads, 1, 128, page, causal=True, sm_scale=SCALE,
                                 q_data_type=torch.bfloat16, kv_data_type=torch.bfloat16)
                    cache = (kbuf.view(-1, page, 1, 128), vbuf.view(-1, page, 1, 128))
                    output = wrapper.run(q, cache)
                    torch.cuda.synchronize()
                    assert output.shape == q.shape and output.dtype == torch.bfloat16
                    assert bool(torch.isfinite(output).all()), 'Nonfinite paged output'
                    ref = []
                    for j in range(nq):
                        upto = length - nq + j + 1
                        score = torch.einsum("hd,ld->hl", q[j].float(), keys[:upto, 0].float()) * SCALE
                        ref.append(torch.einsum("hl,ld->hd", torch.softmax(score, dim=-1), values[:upto, 0].float()))
                    oracle = torch.stack(ref).to(torch.float32)
                    delta = output.float() - oracle
                    rel = (torch.linalg.vector_norm(delta) / torch.linalg.vector_norm(oracle).clamp_min(1e-12)).item()
                    absmax = delta.abs().max().item()
                    base = previous.get((tp, length)) if page == 16 else None
                    page_rel = None if base is None else (torch.linalg.vector_norm(output.float() - base) / torch.linalg.vector_norm(base).clamp_min(1e-12)).item()
                    if page == 1:
                        previous[(tp, length)] = output.float().clone()
                    case_record(kind="paged_causal", tp=tp, **geometry,
                                output_shape=list(output.shape), q_dtype=str(q.dtype),
                                output_dtype=str(output.dtype), finite=bool(torch.isfinite(output).all()),
                                cache_write_exact=True,
                                output_shape_and_dtype_ok=(list(output.shape) == list(q.shape) and output.dtype == torch.bfloat16),
                                relative_l2_vs_fp32=rel, max_absolute_vs_fp32=absmax,
                                original_threshold_flags={"relative_l2_le_0_01": rel <= 0.01,
                                                         "max_absolute_le_0_005": absmax <= 0.005},
                                relative_l2_vs_page1=page_rel,
                                page1_delta_le_0_01=None if page_rel is None else page_rel <= 0.01,
                                backend=str(getattr(wrapper, "_backend", "not_exposed")), error=None)
                except BaseException as exc:
                    case_record(kind="paged_causal", tp=tp, **geometry,
                                error_type=type(exc).__name__, error=str(exc),
                                traceback=traceback.format_exc())

    expected = len(TP) * len(LENGTHS) * 3
    result["expected_case_count"] = expected
    result["observed_case_count"] = len(result["cases"])
    result["execution_error_cases"] = sum(c.get("error") is not None for c in result["cases"])
    result["state"] = ("DIAGNOSTIC_CASE_ERRORS_NO_ACCEPTANCE" if result["execution_error_cases"] else
                       "DIAGNOSTIC_COMPLETE_NO_PASS_CLAIM" if len(result["cases"]) == expected else "DIAGNOSTIC_INCOMPLETE_NO_PASS_CLAIM")
    save()
    print(result["state"])
except BaseException as exc:
    result.update(state="SETUP_FAIL", error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc())
    save()
    raise

if result.get("execution_error_cases", 0) or result["state"] == "DIAGNOSTIC_INCOMPLETE_NO_PASS_CLAIM":
    raise SystemExit(2)
