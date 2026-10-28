# FlashInfer constructed causal prefill diagnostic — PREPARED FOR REVIEW

Prepared 29 October 2026, Vietnam time (UTC+7). This is a bounded follow-up to `../h200-kv-page-primitive-r2-20261028`. It addresses the remaining native FlashInfer prefill coverage at constructed Qwen attention head geometry for page sizes 1 and 16. It is not a model run, a production-backend result, a P/D transfer test, an acceptance-gate pass, or a speed claim.

## Question and scope

Does native FlashInfer causal prefill produce finite, shape-correct outputs for constructed Qwen TP4/TP8 query-head geometry with a BF16 NHD cache at page sizes 1 and 16, for lengths 15, 16, 17, 31, 32, 33 and (if the six-minute envelope allows) 4000? Compare selected oracle rows against a TF32-disabled FP32 causal reference and compare the page-16 output with its page-1 control. Retain the original `relative L2 <= 0.01` and `maximum absolute error <= 0.005` as diagnostic flags, with no threshold adjustment and no correctness-pass state.

Use the same seed 2026, Qwen configuration `/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8/config.json`, BF16 data, NHD native `MHATokenToKVPool` writes, source pins and H200 image as the R2 primitive. Record actual runtime source hashes, shapes, dtypes, errors and all attempted cases. The 4000-token causal oracle may evaluate a bounded set of query rows while the native kernel computes its complete output; describe the sampling exactly. Do not retain raw pointers or environment/authentication material. Reuse `../h200-kv-page-primitive-r2-20261028/native-container.sh` unchanged and the established image and paths.

The pinned SGLang backend has both paged prefill and ragged prefill paths. Its ragged path is used for extend-with-no-prefix and invokes causal attention; therefore cover both native FlashInfer paged causal prefill and ragged causal prefill. The ragged case has no page-size dimension; report it as a separate native execution check. Do not infer full-model registration or worker behavior from these constructed cases.

## Verified native API evidence

The installed image is `/scratch/enroot-images/sglang-harbor.sqsh`. Selective extraction succeeded when archive paths were given relative to the image root (without the `squashfs-root/` listing prefix):

```sh
unsquashfs -processors 2 -no-progress -d NEW_DEST /scratch/enroot-images/sglang-harbor.sqsh \
  sgl-workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py \
  usr/local/lib/python3.12/dist-packages/flashinfer/prefill.py
```

Native FlashInfer source SHA256: `7f4926dcf1610dfd058716e9ba3d8b08f15268e607ea1e28bef7d28b8b2f889e` (`usr/local/lib/python3.12/dist-packages/flashinfer/prefill.py`). Pinned SGLang backend source SHA256: `3cb0b4d5c4d3e8e94724d07c91130ab69d85e73c84cefaf3f69a5ad7813f5c7e` (`sgl-workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py`). See `PROVENANCE.md` for line-level evidence. Earlier extraction attempts incorrectly included the displayed `squashfs-root/` prefix and produced zero files; that failure is corrected here, not treated as API uncertainty.

## Admission and proposed execution

This payload is prepared for root review; no job has been submitted. Before any submission, the AI worker must refresh its live Slurm queue and cap-5 accounting under the `.slurm-admission.lock`, then verify current GPU allocation policy and available budget. PBS CPU/AI queue and PBS-credit checks are for the separate H100/PBS path and do not govern this H200/Slurm job. Bound allocation: one H200, eight CPUs, six minutes (maximum 0.1 GPU-hour), using the already established native container wrapper. No other payload or submission is modified.

After the diagnostic implementation and its SHA256 manifest are complete, the intended invocation is:

```sh
cd /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-prefill-page-diagnostic-20261028
sha256sum --check SHA256SUMS
mkdir -p /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/$SLURM_JOB_ID
srun --exact --gres=gpu:1 bash /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-kv-page-primitive-r2-20261028/native-container.sh \
  /scratch/enroot-images/sglang-harbor.sqsh \
  /scratch:/scratch,/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments:/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments \
  python3 -B /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-prefill-page-diagnostic-20261028/prefill.py
```

The job file and diagnostic implementation are present and SHA256-manifested. The AST validator checks the two native plan/run bindings offline. Root review and live Slurm admission checks remain outstanding; no scheduler action was taken by this worker.

## Root review before admission

Reserve the native dummy first page and write tokens starting at its page-size offset; use pages 1..N for attention. Record actual strides, per-region/item bytes and GPU UUID, without pointers. Shape/dtype/finiteness failures become case execution errors; collect remaining cases, label the final state explicitly and exit nonzero. Numerical original-threshold failures remain diagnostic flags only. A completed scheduler status never implies correctness acceptance. The 4000-token case queries only the final 8 positions; it does not test a full 4000-query cold-prefill launch shape. The external unchanged native-wrapper and exec.rc dependencies are included in the root SHA manifest.
