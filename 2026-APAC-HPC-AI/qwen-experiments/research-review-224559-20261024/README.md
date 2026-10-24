# H100 D5 R4 terminal review — 224559.pbs111

## Question and prior evidence

R4 tested whether a single five-GPU H100 Qwen server could start in unified mode and pass bounded local smoke and retrieval diagnostics after adding native DP LM-head support. The prior R3 startup qualification was a prerequisite, not evidence that this R4 candidate had loaded a model or generated output.

## Terminal result and first failure

PBS records job `224559.pbs111` as **F**, exit status **1**, with **8 seconds** of wall time and `Stageout_status=1`. It received five GPU device nodes on `a2ap-dgx037`; the vnode reports five GPUs. The first and only observed failure is in the PBS batch script, before its run directory or controller logs were created:

```text
/var/spool/pbs/mom_priv/jobs/224559.pbs111.SC: line 10: cd: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/dp5-h100-unified-output-r4-20261024: No such file or directory
```

The submitted `benchmark.pbs` sets `B` to that absolute source-checkout path and immediately changes into it. On the remote system the sealed bundle is staged at `/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/dp5-h100-unified-output-r4-20261024`; the failing checkout path is absent on the compute node. The exact remote benchmark bytes match the local frozen benchmark and the remote SHA manifest entry (SHA-256 `14c1f2e3830a9ce65f1cdeac277f863e0299c42e6459a5e52fa9c959931e35bd`). The defect is a path/packaging failure, not an R4 runtime or model result.

## What ran and what did not

The scheduler assigned five device nodes, but the batch script exited on its initial `cd`. No run directory, worker process, loaded model, resolved-mode observer record, health check, head check, smoke response, or retrieval response was produced. R4's unified-mode and DP LM-head acceptance gates remain **untested**. No output-quality, performance, or throughput conclusion follows.

No runtime telemetry was collected. Inspection found no generated observer receipts, sampler files, or server logs; the remote bundle contains only the source observer hook. Missing utilization, memory, queue, KV, and timing measurements are **not collected**, not zero or healthy.

## Cost evidence and limit

The submitted reservation was five GPUs for 17 minutes, maximum **181.333 SU** (`5 × 17/60 × 128`). At the terminal 8-second wall time, a simple allocated-GPU estimate is **1.422 SU** (`5 × 8/3600 × 128`). PBS reports `resources_used.ngpus=0` even though the vnode and device-node fields show five assigned GPUs, so 1.422 SU is an estimate, not the authoritative account charge. No budget ledger was changed by this review.

## Next interpretation

Correct the batch bundle path in a newly reviewed derivative before any retry. Preserve job 224559 as a pre-runtime infrastructure failure; it provides no evidence for or against the unified model topology. Review the new frozen script and its remote staging path before admission. No queue or source changes were made in this review.

## Evidence

Raw terminal qstat, PBS stdout, remote bundle inventory, the exact remote script and manifest, and the R4 plan/provenance are retained under `raw/`. `REVIEW.json` contains the machine-readable summary. `SHA256SUMS` covers this review's retained files.
