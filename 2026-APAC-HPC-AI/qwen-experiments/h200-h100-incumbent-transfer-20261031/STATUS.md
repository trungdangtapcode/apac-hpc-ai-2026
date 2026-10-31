# Four-job H200 wave: all scheduler acceptances retained

Observed 2026-10-31T10:34:46.460360+07:00, Vietnam time (UTC+7). New Slurm acceptances:

| Job | Configuration | Concurrency | Scope |
|---|---|---:|---|
| 27777 | DeepGEMM prefill/chunk 8192, FlashInfer decode |64| Existing fresh H200 control |
| 27779 | DeepGEMM prefill/chunk 8192, FA3 decode |64| Existing attention candidate |
| **27781** | HPC-Ops prefill/chunk 4096, FlashInfer decode |54| H100 serving recipe at retained H100 load |
| **27783** | HPC-Ops prefill/chunk 4096, FlashInfer decode |64| Same H100 recipe at current H200 load |

All retain HPC-Ops decode and 16 H200 / two nodes, at most 17 minutes per job.
New pair maximum 9.066667 GPU-hours; total wave 18.133334 GPU-hours, zero PBS SU.
The four measurements include one control; no claim of four distinct winning
H100 optimizations. No performance result exists for the newly submitted pair.

Dated actual queue:

```text
27783|ap42-s113-h100n64|PENDING|0:00|2|(Resources)
27781|ap42-s112-h100n54|PENDING|0:00|2|(Resources)
27779|ap42-s111-fa3|PENDING|0:00|2|(Resources)
27777|ap42-s110-flashinfer|RUNNING|4:08|2|g[1,4]
```

Shared Slurm admission lock protected a fresh own cap-five check, site query,
per-bundle manifest hashes, checksum verification, sbatch test and definite
receipts. [Admission records](admission/) bind actual job IDs to reservations
and manifests; source/CPU qualification was captured and pushed in 538bd026
before submission. Twenty synthetic CPU runtime/client-load fixtures passed,
including rejection of an N64 export/summary as N54. Those are not GPU results.
No older payload, queue position, dependency or job was changed.

Use unchanged full workload and all local runtime/source/physical-KV/ two-semantic
route/output/error gates. Review tail latency, queue/batch/KV, actual backend
activation, hardware samples, startup and allocation cost before accepting scores.
Compare 27783 versus 27777 as a coupled runner/chunk recipe; compare 27781 versus
27783 for load sensitivity. Do not infer an isolated runner effect or pure GPU
speed ratio. Official full-set accuracy remains UNKNOWN.

The owner explicitly expands the earlier two-job initial stage to four total.
Further useful-gain confirmation remains conditional and separately reviewed.
No H100 authentication/spending, HPC changes, schedules, background Codex,
slide/submission change or organiser upload. [Plan](PLAN.md), [CPU validation](validation.json).
