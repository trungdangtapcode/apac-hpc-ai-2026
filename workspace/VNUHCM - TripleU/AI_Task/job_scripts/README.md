# TripleU Qwen Basic deployment

## Submission scope and verified execution

This Basic submission retains the official Qwen3-235B-A22B-Instruct-2507-FP8
checkpoint, all model layers and experts, and BF16 KV. It does not requantise
the checkpoint or intentionally approximate model computation. The work tunes
the serving topology, supported backends, scheduling and KV-transfer metadata.
Model-quality evaluation follows the organiser Q1 protocol.

The complete portable entry passed as **job 28197** on **16 H200 GPUs / N64**:
**3051.518173 good output tokens/s**, **1881/1907 joint SLA passes (98.636602%)**,
zero request errors/cancellations, and successful readers, gate and cleanup.
Total allocation duration was **10 min 11 s**. These are measured serving
results. A later full local MMLU-Pro comparison retained 99.915433% of a measured stock FP8 reference score; this is separate from organiser Q1 certification.

The earlier readiness failure 28194 and reader failures remain historical
evidence under `../logs/`; they are not the status of this accepted entry.

## Retained configuration

## Submission scope and verified execution

This Basic submission retains the official Qwen3-235B-A22B-Instruct-2507-FP8
checkpoint, all model layers and experts, and BF16 KV. It does not requantise
the checkpoint or intentionally approximate model computation. The work tunes
the serving topology, supported backends, scheduling and KV-transfer metadata.
Model-quality evaluation follows the organiser Q1 protocol.

The complete portable entry passed as **job 28197** on **16 H200 GPUs / N64**:
**3051.518173 good output tokens/s**, **1881/1907 joint SLA passes (98.636602%)**,
zero request errors/cancellations, and successful readers, gate and cleanup.
Total allocation duration was **10 min 11 s**. These are measured serving
results. A later full local MMLU-Pro comparison retained 99.915433% of a measured stock FP8 reference score; this is separate from organiser Q1 certification.

The earlier readiness failure 28194 and reader failures remain historical
evidence under `../logs/`; they are not the status of this accepted entry.

## Retained configuration

The declared point is **N64 on two 8-GPU H200 nodes**. Two TP4/EP1 prefill
workers on the first node feed one TP8/EP8 decode worker on the second.
Prefill uses DeepGEMM and chunk8192. Decode uses HPC-Ops, FlashInfer attention,
MNNVL collectives and dense CUDA graph sizes 1–64. Routing is round-robin.
The official published FP8 target, BF16 KV and request-scoped NIXL patch are
retained. There is no speculative decoding in this submission.

## Reconstruct and run

Reuse the organiser images and official FP8 checkpoint specified, with hashes
and versions, in environment.json. No image rebuild is required. setup.sh
checks image sizes and model metadata; --verify-images also hashes the images.
The included text nixl.patch and full nixl-conn.py are mounted read-only into
each worker. Its hash is checked before serving. The patch preserves KV byte
geometry and computation while preparing only the request's transfer pages.
The pinned public tokenizer cache is included; model weights are not included.

Required host tools: Slurm with Pyxis/enroot, Python 3, curl and sha256sum.
The organiser SGLang image must include the recorded HPC-Ops kernels.
TRIPLEU_SGLANG_IMAGE, TRIPLEU_AIPERF_IMAGE and TRIPLEU_MODEL_PATH can relocate
the exact same external objects. Paths and scripts do not depend on a team
account. Place the package on storage shared by both allocated nodes.

```bash
cd 'VNUHCM - TripleU/AI_Task/job_scripts'
bash setup.sh --check
# Optional full image digest check:
bash setup.sh --verify-images
sbatch submit.sbatch
```

Submit from this directory, or use sbatch --chdir with its absolute path.
The single job allocates all 16 GPUs for at most 17 minutes, deploys all workers
and the gateway, warms each transfer path with separate setup prompts, and
runs the official AIPerf command once at N64. It retains closed-loop 4000/200,
seed 2026, cold-prefix cache busting, 60s warmup / 120s scoring / 30s grace,
and the original TTFT 3000 ms / request-mean ITL 20 ms goodput thresholds.
The exported goodput in requests/s multiplied by 200 is the score in good
output tokens/s; the joint good fraction must be at least 0.90.

Output: ../logs/slurm/<job>.out/.err and ../logs/reruns/<job>/official/n64/.
performance-gate.json independently rejects missing/incomplete/error/SLA-failed
artifacts even when a client or scheduler reports exit 0. It reads existing
exports and requests after the unchanged client command; it does not modify
benchmark traffic or recalculate goodput from a guessed window duration.

## Evidence and limits

Reviewed source job 26766: 3045.501509 good output tokens/s, 1875/1902 good
requests (98.580442%), zero errors/cancellations. This is one local N64
observation. The 26766 native-runtime run reproduces the historical N64 score level; this is not a matched runtime gain.
N60 independently repeated at 2990.150791 and 2989.174711; see the retained raw
exports and results table for exact values. All platform comparisons remain
separate. Actual portable jobs 27136 and 27145 completed both semantic routes and the
official GPU client, then failed in result-reader namespace/alias handling.
Their original FAILED states remain. The corrected exact readers passed on
compute CPU job 27152 for both retained raw datasets. The subsequent complete
portable entry, job 28197, passed both semantic routes, the original official
client, corrected readers, the performance gate and cleanup in 611 seconds.

Model-quality evaluation follows the organiser Q1 protocol against the
unchanged official FP8 reference. The checkpoint and model precision are
preserved; performance and answer-accuracy measurements remain distinct.
See ../logs/README.md for measured evidence, review scope and reproduction status.

Rules: https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/1.%20Qwen3%20AI%20Task%20Rules.md


## Semantic warmup and evidence update

Before scoring, the primary job starts two independent P/D routers and sends one semantic request through each route. It validates both response bodies and writes replayable receipts tied to the endpoint inventory and current run token. The warmup has a 13-minute absolute deadline from submit start, leaving at least four minutes for scoring and cleanup, and fails closed on a missing, stale or invalid receipt. The official AIPerf command is invoked once after both paths pass.

The selected primary point is reproduced by H200 job 26766 at 3045.501509 good output tokens/s. See `../logs/measured/latest-results.md` for comparison with the historical three-run N64 mean, losing larger-chunk controls, run limits and accuracy status. The measured patch is the base 912b7 NIXL change; no diagnostic observer wrapper is shipped.


## Reviewed selection on 30 October 2026

Keep this replicated N64 target-only configuration. The highest complete local
full pass, prefill ChunkCache job 27378, scored 3048.446289 good output tokens/s,
only 0.240921% above its fresh native control 27376. That single difference is
below the prospective 1% useful-gain gate, so it does not justify replacing the
prefix-cache policy. No speculative decoding, compile option, C++ cache or
unconfirmed graph setting is added to this primary entry.

The recovered portable raw observation 27145 is 3055.330517 good output tokens/s.
Its failed scheduler status and compute-only reader verification remain explicit.
See ../logs/measured/latest-results.md for source IDs, latency units, validity
classes and the distinction between an isolated peak and a reproduced choice.

For the research decisions behind this unchanged primary, see ../logs/RESEARCH_JOURNEY.md and ../logs/EVIDENCE_CARDS.md. No new serving option is introduced by the presentation revision.

## Complete local answer-quality verification — 3 November 2026

Reference **9460/12032**, candidate **9452/12032**, accuracy retention **99.915433%**. Same 16 H200 and same prepared questions; all sixteen jobs completed, zero service errors. This measured local MMLU-Pro pass is distinct from the 98.636602% latency fraction and from organiser certification. [Method, retained answers and CPU replay](../logs/quality-20261103/README.md).
