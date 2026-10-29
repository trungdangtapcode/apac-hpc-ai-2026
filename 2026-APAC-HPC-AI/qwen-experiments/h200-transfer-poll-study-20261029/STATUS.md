# Actual full polling admissions

Observed 2026-10-29T13:09:37.801902+07:00, Vietnam time (UTC+7). These are definite Slurm acceptances, not prepared-only candidates. No result is claimed.

| Job | Bundle | Decode transfer polling interval | Purpose |
|---|---|---:|---|
| 27270 | S101 | 1 | Fresh matched target-only control |
| 27272 | S99 | 2 | Reduce completion polls by half |
| 27274 | S100 | 4 | Prospectively bracket lower polling work against admission delay |

All three are PENDING at the recorded observation, with Priority/Resources reasons. Each reserves 16 H200 on two nodes for at most 17 minutes; combined maximum 13.6 GPU-hours, no PBS SU. The own cap is 5; three own jobs were accepted from an empty queue under the admission lock. No existing job was cancelled or reprioritized. No dependency chains or background submitters were created.

All three keep target-only weights, topology, precision, runtime, full N64 cold 4000/200 seed 2026 workload and local source/runtime/KV/semantic/output gates. The exact per-role polling setting is independently checked in raw logs, with pinned consumer source hashes checked before startup. Twenty-seven CPU fixtures pass, including deliberate wrong values, missing/nonliteral settings and missing startup rank records. Tests are not measured candidate performance.

The two candidate intervals were chosen before either result, with a fresh control to address machine drift. Review all actual terminal evidence and compare primarily to 27270. Require >1% useful good-throughput gain with acceptable latency tails before an independent confirmation; close unchanged losses. A terminal error is not a valid measurement. Keep official accuracy UNKNOWN. See PLAN.md, preparation.json, validation.json and each admission directory for exact manifests, reservations and sbatch/scontrol receipts.

The source review's earlier one-candidate proposal is retained as historical preparation; the root prospectively selected this finite three-point bracket before any polling measurement. No additional interval sweep follows automatically. The prior receive-poll experiment changed a different field and is not repeated.

Current actual queue:

```text
             JOBID                     NAME    STATE       TIME  NODES NODELIST(REASON)
             27274          ap42-s100-poll4  PENDING       0:00      2 (Priority)
             27272           ap42-s99-poll2  PENDING       0:00      2 (Priority)
             27270          ap42-s101-poll1  PENDING       0:00      2 (Priority)
```

The completed shallow EAGLE loss 27238 is already preserved in checkpoint 066f282e. This new bracket does not modify the published submission, presentation, HPC payloads or budgets. Git push preserves safe files and recovery manifests; external large artifact bytes still require separate off-host backup.
