# H200 reference 25495: client mount prerequisite failure

The allocation is terminal **FAILED / 1:0**, elapsed **406 seconds**. Its exact submitted payload and every retained sealed artifact were independently hash-verified. All three workers/router became ready; real BF16 KV allocation records cover 4+4+8 ranks, and independent replay of both actual semantic P/D warmup receipts passes. These are real readiness/transfer observations, not a complete target reference.

The first concrete client-stage failure is Pyxis refusing the token-client container: `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/home/25495/token-client` does not exist. `mounts()` advertises this role HOME, but the launcher creates the worker, router and pair-warmup directories only. The actual token client never started. No target-reference.json exists and **zero diagnostic output IDs were captured**. The independent head checker subsequently rejects the missing file; that traceback is downstream of the mount error.

The earlier CPU launcher fixture mocked srun without checking container mount prerequisites. It verified failure propagation but missed this actual deployment bug. Preserve that earlier evidence and correct its coverage description; it was never an actual Pyxis launch test.

Derive a separate native Slurm bundle adding only `mkdir -p` for the token-client HOME before that srun. Test the real shell launcher with a mount-validating Slurm stub: old source must reproduce a missing-mount rejection; repaired source must reach the fake token client and still propagate its deliberate failure. Keep actual client/head asset-binding fixtures and all worker, transport, token protocol, corpus, precision and deadline bytes unchanged. The fix is a concrete supported reason for one new reference allocation, not an unchanged full-model retry.

No throughput, EAGLE3 correctness, official accuracy or accepted reference is claimed. Scheduler cleanup cancellations of long-running worker steps are distinct from the top-level failure and its earliest client cause. [Machine-readable review](REVIEW.json), [review script](review.py), [terminal raw evidence](../runs/25495/artifact-manifest.json).
