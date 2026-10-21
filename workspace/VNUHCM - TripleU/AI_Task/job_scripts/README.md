# TripleU Qwen Basic deployment

The declared point is **N62 on two 8-GPU H200 nodes**. Two TP4/EP1 prefill
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
runs the official AIPerf command once at N62. It retains closed-loop 4000/200,
seed 2026, cold-prefix cache busting, 60s warmup / 120s scoring / 30s grace,
and the original TTFT 3000 ms / request-mean ITL 20 ms goodput thresholds.
The exported goodput in requests/s multiplied by 200 is the score in good
output tokens/s; the joint good fraction must be at least 0.90.

Output: ../logs/slurm/<job>.out/.err and ../logs/reruns/<job>/official/n62/.
performance-gate.json independently rejects missing/incomplete/error/SLA-failed
artifacts even when a client or scheduler reports exit 0. It reads existing
exports and requests after the unchanged client command; it does not modify
benchmark traffic or recalculate goodput from a guessed window duration.

## Evidence and limits

Reviewed source job 24915: 3022.034919 good output tokens/s, 1860/1884 good
requests (98.726115%), zero errors/cancellations. This is one local N62
observation. Its independent repeat 24962 was still pending at packaging.
N60 independently repeated at 2990.150791 and 2989.174711; see the retained raw
exports and results table for exact values. All platform comparisons remain
separate. The portable entry point is statically checked and exercised with
mock orchestration and replayed artifacts; it has no separate GPU replay yet.

The organiser full-set accuracy check (at least 99% of reference) remains
unverified. Small output checks and SLA acceptance do not certify it.
See ../logs/README.md for measured evidence, review scope and reproduction status.

Rules: https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/1.%20Qwen3%20AI%20Task%20Rules.md
