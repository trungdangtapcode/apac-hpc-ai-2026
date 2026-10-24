# D5 R3 H100 startup-readiness review: job 224555

## Question and correction

R2 job 224553 had passed all five rank metadata observations and the FP8 header-only check, then failed while constructing `ParallelLMHead` because padded vocabulary width 151,936 is not divisible by TP size 5. R3 added SGLang's explicit `--enable-dp-lm-head` option to the same TP5/DP5/EP5 D5 startup configuration. This review asks only whether that source-directed change reaches startup readiness with verified loaded expert replicas, runtime dtypes, map identity and native health.

## Terminal and independent gate result

PBS job `224555.pbs111` ran on `a2ap-dgx037` and finished `F`, exit status 0, stage-out status 1. PBS wall time was 381 seconds (6 minutes 21 seconds), against a 1,020-second maximum. The wall-time allocation estimate is `381 × 5 × 128 / 3600 = 67.733 SU`; the maximum reservation was `1,020 × 5 × 128 / 3600 = 181.333 SU`. These are estimates, not posted ledger charges.

The actual server argv contains `--enable-dp-lm-head`; all five observer records independently report `enable_dp_lm_head=true`. The native health endpoint returned HTTP 200 at 13:36:49 UTC. I independently reran the R3 bundle's `headcheck.py` against copies of the collected job evidence. Its source hash is `bd89fef98e5356ce432216655b21b91a7f2fd49932d0b8034675742d37f37b8d`; it matches the R3 bundle's `SHA256SUMS`. The check passed with state `D5_STARTUP_READINESS_PASS`, verifying ranks 0–4, runtime dtype and dimensions, map digest and replicas, loaded replica bytes, BF16 KV configuration and health receipt. The independent result is retained as `independent-headcheck-result.json`.

## Loaded map, replicas and runtime dtypes

All five ranks report H100 80GB HBM3, compute capability 9.0, and device UUIDs matching the five assigned CUDA devices. All report TP5, DP5, DP attention and DP LM head enabled; EP5 with attention TP1 and MoE TP1; 128 logical and 130 physical experts; and 26 local physical experts. The reported physical-to-logical map has shape `[94, 130]`, consistent digest `c9224e794770eafdb9ceecfce2578998360528167bdf8fe75166841ee29cc84c`, and valid replica layout; each layer's retained map tail is `[0, 1]`.

Every rank reports `torch.bfloat16` model dtype. Loaded expert metadata confirms the `hpc_ops` runner and block-quantized FP8 MoE weights: `w13_weight` is `torch.float8_e4m3fn` with shape `[26, 3072, 4096]`; `w2_weight` is `torch.float8_e4m3fn` with shape `[26, 4096, 1536]`; inverse scales and HPC-Ops scales are `torch.float32` with shapes `[26, 24, 32]` and `[26, 32, 12]` respectively. Runtime block size is `[128, 128]`. Loaded weight hashes confirm replica slot pairs rank 0 slot 0 vs rank 4 slot 24 and rank 0 slot 1 vs rank 4 slot 25 for both FP8 weight tensors and their scales.

The resolved KV dtype is BF16, with four KV heads. The header preflight remains header-only and did not read model tensor payload. Observer evidence hashes metadata for loaded tensors and selected replica slots, not tensor payload artifacts; no weight payload was copied into this review.

## Assessment and limits

R3 resolves the startup-readiness gate that failed in R2 for the captured TP5 configuration: the run reached native health, all five rank checks passed, and selected redundant expert replicas matched byte-for-byte by hash. This is a startup geometry, loaded replica identity, runtime dtype and health result only. No generation request was made. There is no output comparison, quality score, AIPerf result or performance measurement, and the run does not validate multi-node D5 behavior.

GPU allocation accounting and the sparse native health receipt do not establish continuous GPU utilization, peak memory, kernel performance, thermal state or general hardware health. PBS accounting fields are preserved in `qstat-224555.txt`; no hardware-health conclusion is drawn from them.

## Preserved evidence

- `collected/raw-run.tar.gz`: compact complete job directory, preserving remote relative paths.
- `collected/qstat-224555.txt`: terminal PBS accounting and stage-out fields.
- `collected/pbs-joined-output.txt`: PBS stdout/stderr (joined by PBS).
- `collected/`: extracted files for independent review, including rank observer JSONL and health receipt.
- `validation-source/headcheck.py` and `independent-input/`: the checksum-verified R3 gate source and exact copied evidence used for the independent rerun.
- `independent-headcheck-result.json`: independent startup-gate output.
- `REVIEW.json`: machine-readable review summary.
- `collected/SHA256SUMS`, `collected/ARCHIVE_SHA256`, and `REVIEW_SHA256SUMS`: integrity records.
