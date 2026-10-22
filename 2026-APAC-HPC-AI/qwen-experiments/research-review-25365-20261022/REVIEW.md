# Fresh full observed N62 control passes

Reviewed 2026-10-22T00:20:57.655133+00:00. **25365 is COMPLETED/0:0**,687 seconds, with all allocation
cleanup finished before sealing. Full60/120/30, fixed4000/200/seed2026/cold-prefix
client protocol and all operational payload checks pass against observed24964.
Only client concurrency changes60→62; resolved server arguments differ only in
per-process random seed. This is the fresh matched control for N64 job25366.

Score **3011.875113 good output tokens/s**,1855/1879 jointly good (**98.722725%**),
zero errors/cancellations. TTFT mean/p95 **1037.629662/1316.527172 ms**;
request-mean ITL mean/p95 **14.957663/15.209486 ms**. All24 failures are TTFT
breaches from requests started in the first35.45ms of profiling. Long retrieval
passes12/12; short output comparison introduces no new failure versus its local
baseline. Official accuracy>=99% reference remains unverified.

The requested output is nominal200 tokens; exported counts are1874 at200 and
five at199. These recurring exported-length differences are retained, not a
claim of actual generated token-ID equality. Raw joint classification matches
all per-request flags. [Initial cohort evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/phase-transition-review-20261022/REVIEW.md).

Role logs preserve native BF16 KV and have no inspected NIXL_ERR or CUDA-OOM
pattern. Full server/hardware telemetry and phase markers are collected; their
phase-aligned demand analysis and profile-control lifecycle inspection are not
included in this checkpoint and must not be inferred healthy. Tracebacks are
counted in REVIEW.json without attributing them to scored requests. The actual
scored exports have zero errors. Diagnostic traces are separate from scoring.

The first offline queue check used squeue -j after Slurm retired the job ID,
which returns Invalid job id rather than an empty queue. The helper now checks
the own-user queue before requiring terminal sacct; no job or raw evidence was
changed. All terminal raw files and their hashes are retained.

Keep observer-off best24962=3023.072304 unchanged. Fresh N64 must pass the same
full/local gates and be compared against this3011.875113 control before any new
performance claim. Hardware, output and official-accuracy limits remain explicit.
