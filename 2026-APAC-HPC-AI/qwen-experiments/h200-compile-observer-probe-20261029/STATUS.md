# Current result: 27338 failed before compilation

29 October 2026, Vietnam time: actual scheduler state is **FAILED 1:0 in 76 seconds**. The source guard inspected the stdlib contextmanager wrapper instead of the SGLang module; no compile or model measurement occurred. Original source/hash checks remain unchanged. [Failure review and bounded derived fix](RESULTS-27338.md). The earlier pending sentence below was inaccurate at publication: its own recorded queue already showed RUNNING. Preserve that historical record and use actual terminal accounting now.

## Historical admission record

# Actual compile-observer prerequisite admission

Observed 2026-10-29T16:22:41.638538+07:00, Vietnam time (UTC+7). Slurm accepted **27338** for this exact frozen payload. It is PENDING at this observation; no actual probe result exists yet. Definite receipt, manifest and reservation are retained separately. Preparation checkpoint is 924dd6ce.

The allocation is one H200, four CPUs, one node, at most four minutes: maximum 0.066667 GPU-hours and no PBS SU. Admission held the own Slurm lock, checked the current queue against cap 5, verified all frozen hashes and validated the sbatch request. Existing interval 4 job 27274 remains untouched. No job was cancelled, no dependency chain or automatic followup was created, and no VPN/MFA action occurred.

The tiny BF16 MLP fixture uses batches 1, 52 and 64. It calls pinned native SGLang compile setup and patch_model, records actual wrapper/call events separately from numerical compiler activity, and uses PyTorch CUDA graph capture/replay. It does not initialize or fake SGLang TP/PP groups. Counter absence or no positive compiler delta remains UNPROVEN. A returned wrapper alone is not proof of compilation. Tolerances are prospective synthetic-fixture limits only. An absolute job-start+205-second deadline leaves cleanup margin against the scheduler's 240-second limit.

Even a positive result would not prove Qwen3, HPC-Ops, eight-rank production capture, startup fit, output accuracy or performance. A separate real-model startup qualification would remain required before a scored compile candidate. Preserve the current full N64 workload and all gates; do not promote this probe into submission materials or an official score.

Current own queue:

```text
             JOBID                     NAME    STATE       TIME  NODES NODELIST(REASON)
             27274          ap42-s100-poll4  PENDING       0:00      2 (Nodes required for job are DOWN, DRAINED or reserved for jobs in higher priority partitions)
             27338              ap42-cmpobs  RUNNING       1:08      1 g4
```

Later result reports belong outside the four frozen source files and their manifest. Source changes must use a derived bundle. Preserve original errors if execution fails. Git captures safe source and receipts; large external artifact bytes are not automatically uploaded by Git.
