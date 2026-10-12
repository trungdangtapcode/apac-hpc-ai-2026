# TripleU — APAC HPC-AI 2026 Qwen Basic submission

## Declared configuration

**P8-TP4_D8-TP8-EP8, concurrency 48, 16 H200 GPUs.** Node 0 has two prefill
workers (4 GPUs each, TP4/EP1). Node 1 has one decode worker (8 GPUs,
TP8/EP8). Every benchmark request uses the PD gateway. Published FP8 weights,
BF16 KV, no speculative decoding, no model or expert/layer changes.

The NIXL patch is enabled in the primary script. It changes heterogeneous-TP
KV descriptor preparation to operate on request pages instead of the whole
pool; byte geometry, head mapping and notifications are retained. The text
diff is `nixl.patch`, the mounted source is `nixl-conn.py`, and both original
and patched hashes are in `patch-metadata.json`. The worker verifies the
mounted source hash before launching SGLang. The patch passed 720 CPU
byte-range comparisons and served the measured GPU run.

## Rebuild the serving environment

Use the exact organiser-provided SGLang/Pyxis image and AIPerf image recorded
in `environment.json`, and the official published
`Qwen3-235B-A22B-Instruct-2507-FP8` checkpoint. The defaults use the organiser
shared `/scratch` paths. No model weights or image binaries are bundled.
No image rebuild is necessary: the script mounts the included `nixl-conn.py`
read-only at the image's SGLang NIXL module path for prefill/decode workers.
The original image and checkpoint stay unchanged. The pinned offline
tokenizer cache is included.

Required host tools: Slurm, Pyxis/enroot, Python 3, curl and sha256sum.
Worker containers use SGLang 0.5.17, router 0.3.2 and NIXL 1.3.2;
the client image uses AIPerf 0.12.0. External image/model paths can be
overridden using `TRIPLEU_SGLANG_IMAGE`, `TRIPLEU_AIPERF_IMAGE` and
`TRIPLEU_MODEL_PATH`; the staged files must match the recorded environment.

```bash
cd 'VNUHCM - TripleU/AI_Task/job_scripts'
bash setup.sh --check
# Optional full SHA256 check of the two external images:
bash setup.sh --verify-images
sbatch submit.sbatch
```

Submit from this directory, or pass its absolute path with `sbatch --chdir`.
No team account or home directory is hardcoded. The single 17-minute job
allocates two nodes and 16 GPUs, deploys the three workers and gateway,
initializes the two P/D paths using separate setup prompts, then invokes
the exact official closed-loop AIPerf command **once at N48**. There is no
sweep in this entry point. Official timings remain 60/120/30; input/output
lengths remain 4000/200, seed 2026 and both original SLA thresholds.

Slurm output is in `../logs/slurm/`; replay outputs are in
`../logs/reruns/<job>/official/n48/`. Source worker/placement/setup geometry
match measured job 22415; only submission paths and one-point client
orchestration are made portable.

## Evidence and status

Job **22415**, N48 long run: **1912.299955 good output tokens/s**,
**97.440132% SLA**, **1180/1211** good requests, zero errors/cancellations.
This is local evidence, not an official organiser score. The packaged
portable orchestration has static and mock validation; its own GPU replay
status is recorded in `../logs/replay-status.json`.
The organiser full-set accuracy check and official re-verification are
not yet available. No quality pass is claimed.

Rule source (verified at commit 3d050964d1008b97fb6d0d7ec5160087cd6883d9):
https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/1.%20Qwen3%20AI%20Task%20Rules.md
Submission Guidelines require build instructions, one deploy-and-benchmark
Slurm/PBS script, and slides. Q1 permits serving patches that preserve
the model computation; the text patch is supplied for judge review.
