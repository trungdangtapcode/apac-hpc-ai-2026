# S46 explicit-dtype deterministic target reference preparation

## Question and prior evidence

S44 asked whether the deterministic target deployment repeats exact requests, 1,600 output token IDs, and finish reasons across two passes. Slurm job 25807 (16 H200 GPUs) ended FAILED, exit 1:0, after 309 seconds. All 16 target workers reported BF16 KV allocation; 32 native registration receipts were collected and accepted by the independent geometry validator with 188 target-only KV regions per receipt. The strict runtime checker rejected each resolved `ServerArgs(dtype='auto')` because the frozen contract requires the declared dtype `bfloat16`. No semantic prefill/decode warmup or target output pass ran. This is a launcher/contract preparation failure and does not show that the model actually ran in an incorrect precision. The S44 payload and raw evidence remain unchanged.

## Replay and source-backed correction

Before any GPU replay, all actual logs `runs/25807/{prefill-0,prefill-1,decode-0}.log` were copied into a temporary CPU fixture. The only fixture edit was replacing the parsed `dtype='auto'` field with `dtype='bfloat16'`; the raw logs were not edited. The first replay exposed another contract mismatch: decode-0 contains the native warning `FlashInfer allreduce fusion is forcibly disabled via --enforce-disable-flashinfer-allreduce-fusion.` and resolves `enforce_disable_flashinfer_allreduce_fusion=True`, while the S44 checker required the separate deterministic-handler warning. Pinned `arg_groups/overrides.py` proves these are separate paths: `_enforce_disable_allreduce_fusion` clears the fusion backend before `_deterministic_allreduce_fusion_disable` runs. The actual resolved backend is `None`, so the observed enforced-disable path is valid; it was under-recognized by the old checker.

With only that dtype field patched in temporary fixtures, the S46 checker passes all three real logs: prefill-0 has four BF16 KV and four NIXL rank records; prefill-1 has four and four; decode-0 has eight and eight. Each role passes the source/runtime args and deterministic sampling/attention/allreduce markers. This replay is CPU parser evidence, not new GPU evidence. The target-only geometry validator independently passes the actual 32 receipts: 16 ranks, two phases each, 188 regions. It reports layer IDs and some decode head fields as not collected; they remain unknown.

## Controlled S46 change

S46 derives from frozen S44. The common launch command now explicitly includes `--dtype bfloat16`, while retaining `--enable-deterministic-inference`. The strict runtime checker retains all existing rank, BF16/NIXL, model, graph, deterministic, source and role checks and recognizes either (a) the native deterministic-disable warning or (b) the source-backed enforced-disable flag plus its exact native warning. A CPU launch regression inspects the actual S46 worker command and verifies frozen S44, which omitted `--dtype bfloat16`, fails the same assertion. Canonical bundle identity, parent provenance and SHA256 manifest are updated for S46; S44 files and S45's unbound candidate are untouched.

## Preserved acceptance and limits

The next actual S46 run must still pass all 16 ranks, explicit BF16 resolved dtype and KV allocation, deterministic runtime/source checks, all 32 fresh geometry receipts with 188 target-only regions, both semantic prefill/decode paths, and two exact target passes totaling 1,600 actual IDs with identical requests, IDs and finish reasons. The old 25585 output comparison is informational only. This is a correctness diagnostic, not a score or performance claim. The replay cannot prove GPU behavior, output repeatability, official accuracy, or that every third-party operation is deterministic. Hardware sampling was collected in the failed run but not summarized here. No GPU submission or queue action was performed while preparing S46.

## CPU evidence

- `validate-cpu.py`: all asset-binding, KV-geometry, pinned-source, deterministic runtime, repeat-gate and worker-launch contract fixtures passed.
- Temporary actual-log replay with only declared dtype changed: PASS for all three roles.
- Actual 25807 geometry receipt replay: PASS, 32 receipts / 16 ranks / 188 target-only regions.
- Raw job outcome remains FAILED; no semantic or token output result exists.
