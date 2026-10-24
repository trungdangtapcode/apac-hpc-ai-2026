# D5 R2 H100 readiness review: job 224553

## Question and prior evidence

This one-node, five-H100 D5 readiness attempt asked whether the pinned SGLang runtime could initialize the Qwen3-235B-A22B-Instruct-2507-FP8 configuration with TP5, DP5 attention, and EP5 on the selected H100 allocation. It was a startup/readiness gate, not an inference benchmark. The job's prerequisite receipt checks and submitted-file checksum checks passed before launch.

## Terminal result and first failure

PBS job `224553.pbs111` ran on `a2ap-dgx037` and finished `F`, `Exit_status=1`, `Stageout_status=1`. PBS reports allocated walltime `00:02:37` (157 seconds), CPU time `00:06:36`, 70 CPUs, and 5 GPUs. At 128 SU per GPU-hour, the walltime-based allocation estimate is `157 × 5 × 128 / 3600 = 27.911 SU`; the maximum 17-minute request was 181.333 SU. These are allocation estimates, not a posted ledger charge.

The first substantive model startup failure is in `qwen3_moe.py` while constructing `ParallelLMHead`: `AssertionError: 151936 is not divisible by 5`. The model's padded vocabulary width is not divisible by TP size 5. The native server did not reach health readiness. Logs show rank scheduler processes failing at the same divisibility assertion and then the parent observing scheduler death. This is a launch-configuration/model-head partition failure, not an FP8 expert-tensor header failure or a GPU health finding.

## What passed before the failure

- All submitted checksum entries were verified by the job before server launch; prerequisite and root receipt checks reported pass.
- The safetensors header-only preflight passed with configuration SHA-256 `f056921e486d3e22aed125b5218b87146ea2ac838ccf1521dea5b08f809e8d59`. It read 352,848 header bytes and explicitly did not read tensor payloads.
- The header reports expert weight tensors as FP8 E4M3 and scales as BF16:

| Tensor | Header dtype | Shape |
|---|---|---|
| Expert 0 `down_proj.weight` | F8_E4M3 | `[4096, 1536]` |
| Expert 0 `down_proj.weight_scale_inv` | BF16 | `[32, 12]` |
| Expert 0 `gate_proj.weight` | F8_E4M3 | `[1536, 4096]` |
| Expert 0 `gate_proj.weight_scale_inv` | BF16 | `[12, 32]` |
| Expert 0 `up_proj.weight` | F8_E4M3 | `[1536, 4096]` |
| Expert 0 `up_proj.weight_scale_inv` | BF16 | `[12, 32]` |

- The source preflight reported `PASS_PINNED_RUNTIME_SOURCES` for 13 listed files, with `gpu_import=false`.
- Five observer records were written, one per rank, before model loading failed. Each reports `model_dtype=bfloat16`, `tp_size=5`, `dp_size=5`, `moe_ep_size=5`, `moe_runner_backend=hpc_ops`, `logical_experts=128`, `physical_experts=130`, `local_physical_experts=26`, and `physical_to_logical_replicas_valid=true`. Each retained map summary has shape `[94, 130]`, SHA-256 `c9224e794770eafdb9ceecfce2578998360528167bdf8fe75166841ee29cc84c`, and a tail of `[0, 1]` for each of 94 rows. The complete map values were not serialized in these observer records; the validity flag and digest are retained evidence, not a full map dump.
- The five assigned CUDA devices are H100 80GB HBM3, compute capability 9.0, each with 85,019,590,656 bytes reported memory. `CUDA_VISIBLE_DEVICES`, `devices.json`, and the five observer records agree on the ordered UUIDs:

| CUDA index / TP rank | Assigned GPU UUID |
|---:|---|
| 0 | `eed14ddb-7e9b-df97-75e6-d0d564b6b106` |
| 1 | `0552d274-a9ea-e6ca-cda2-d632fa354f02` |
| 2 | `ad861754-3262-1722-30e3-2ff560f0eaa3` |
| 3 | `f753d63f-2e63-3b8d-3bea-0db8353f1909` |
| 4 | `4ad0ee57-aba1-744d-4103-5bc02de06d34` |

PBS lists device nodes `/dev/nvidia7`, `/dev/nvidia6`, `/dev/nvidia5`, `/dev/nvidia4`, and `/dev/nvidia2`; the retained records do not map each device node to a CUDA index, so no such mapping is inferred.

## Limits and next step

No checkpoint tensor payload was read by the header preflight, no model weights finished loading, no native health check passed, and no request, token, quality score, or performance measurement exists. Observer metadata does not demonstrate successful model initialization. PBS GPU accounting fields are retained in the terminal record, but they are not treated as device-health telemetry or an explanation for the LM-head assertion.

The root's derived R3 follow-up explicitly enables SGLang's DP language-model head (`--enable-dp-lm-head`) and was submitted as job 224555 after 224554. That is the source-directed configuration correction to review next; this record does not claim it resolved the failure. Review its exact terminal failure or readiness evidence before any quality or performance stage.

## Preserved evidence

`collected/` contains the raw selected run files and terminal `qstat -xf` output. The raw archive preserves the remote relative paths; `SHA256SUMS` and `ARCHIVE_SHA256` cover the collected evidence. Raw source bundle and submitted payload remain unchanged at the remote run directory.
