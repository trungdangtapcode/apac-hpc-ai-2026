# Job 26076: ready workers, semantic-route timeout, no benchmark

Reviewed on 25 October 2026. Slurm records FAILED 1:0 after 7 minutes 33 seconds on g1/g4, allocating 16 H200 GPUs. This is a failed pre-scoring run. Goodput, scored TTFT/ITL, joint-SLA fraction, profiling errors and quality are not measured.

All four workers reached health/readiness. The corrected native KV validator passed 32 before/after records across 16 ranks. This resolves the previous validator failure; it does not prove a working P/D transfer. Four route routers activated workers. Four initial HTTP 503 responses reported no prefill workers; subsequent requests entered processing but timed out without semantic receipts. There is no AIPerf export. Worker shutdown logs contain AbortReq KVTransferError messages after the client timed out; those messages alone do not identify the initiating cause.

The warmup helper allowed a total 180 seconds but imposed a 30-second timeout on each semantic HTTP request and raised immediately on TimeoutError. Thus it never used the available initialization budget for a slow first transfer. Historical job 22219 took up to 150.55 seconds to initialize routes, as already retained in the S62r2 plan. A bounded derived S62r4 will allow one request to use the remaining shared 180-second deadline, without retrying timed-out work or relaxing output/route checks. If it still cannot produce all four semantic receipts, stop and inspect transport before another full-topology retry.

Resource sampling files exist for all four roles; file presence and counts were inspected in inspection.json. Scored hardware/server sampling is unavailable because scoring never started. No CPU/GPU saturation or transport root cause is claimed. Scheduler allocation equals 2.0133 GPU-hours; this Slurm job does not consume the separate PBS SU ledger. Official full-set accuracy remains unknown.

Raw logs, submitted payloads, KV receipts and resource records remain in runs/26076. Frozen submitted files are unchanged. See [inspection](inspection.json). The prior AI handoff describing 26076 as pending is historical.
