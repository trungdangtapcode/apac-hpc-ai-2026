# Matched observed H200 load screen submitted within the actual limit

Definite **25339**, submitted **2026-10-21T19:43:22.504873+00:00**, **16 H200 / two nodes / at most 17 minutes**. The submitter verifies actual hpcai MaxTime before sbatch; accepted job detail confirms 17 minutes and no PartitionTimeLimit reason. [Receipt](slurm-receipts.json), [real partition preflight](partition-preflight.txt), [dated queue](live-initial.txt).

This is an **unranked short screen**, N62 then N64 on one common observed deployment. Each has 20-second warmup / 40-second measurement / 30-second grace, fixed 4000/200 seed 2026 cold prefixes and all native serving/observation controls unchanged. Artifacts use screen/n62 and screen/n64. Never compare short scores directly with full 24962 or promote them as a new contest score. [Plan](PLAN.md), [four actual-shell stop-gate fixtures](load-gate-validation.json).

The independently accepted full N62 point 24962 reproduces 24915 within 0.034327%, justifying the next offered-load boundary at the dense decode graph maximum 64. Same-job observed N62 is the matched control, not observer-off 24962. A >=1% short gain with complete raw/output/runtime and SLA/error gates only permits a fresh full matched confirmation; a lesser/negative/invalid result closes this unchanged load step.

The earlier 22-minute full two-point request 25338 was unschedulable and cancelled PENDING at zero runtime. Its receipt, rejected details and frozen payload remain in ../research-followup-20261021-n64. This fresh separate bundle changes durations/labels equally on both points and validates the real limit. Four older queue positions 24964/24965/25051/25283 remain; new 25339 brings total to five, no sixth. No PBS SU or background work.
