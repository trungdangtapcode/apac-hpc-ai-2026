**Four distinct ports fully reviewed — 2026-10-31T21:54:43.696307+07:00, Vietnam time (UTC+7):** all four additional ports **27804/27806/27828/27830** are reviewed local passes; **27826** is their extra explicit mode control, not a candidate. Phase results: control **3039.167093**, decode-only **3039.356215 (+0.006223%)**, prefill-only **3043.141258 (+0.130765%)** good tokens/s on 16 H200/N64. All source/provider/physical KV/semantic/raw/output gates pass, zero scored errors/cancellations, smoke 7/8 non-regression, retrieval 12/12; official full-set accuracy UNKNOWN. No gain reaches the prospective 1% usefulness gate. Keep the current H200 recipe and native no_grad; no repeat, combined sweep or promotion. [Final phase review and completed four-port register](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/RESULTS.md). Own queue empty in the fresh audit. Actual phase stage 9.604444 GPU-hours, zero PBS SU. This completes the standing four-intervention verification; it does not reopen unrelated research, H100 login/spending, HPC, schedules/background Codex or update published PPTX/ZIP.

Earlier admission/queue snapshots below are historical. All three terminal raw runs and the four-intervention register are now reviewed.

# Actual H200 admission: explicit control and the remaining two phase ports

Observed 2026-10-31T14:52:15.009695+07:00, Vietnam time (UTC+7). Slurm accepted all three:

| Job | Prefill native provider | Decode native provider | Role |
|---|---|---|---|
| **27826** | no_grad | no_grad | New explicit control, not a candidate |
| **27828** | no_grad | inference_mode | Decode-only H100-derived port |
| **27830** | inference_mode | no_grad | Prefill-only H100-derived port |

All use 16 H200/two nodes/N64, each at most 17 minutes/4.533334 GPU-hours.
Three-job maximum 13.600000 GPU-hours, zero PBS SU. Actual queue snapshot:

```text
27830|ap42-s118-im-prefill|PENDING|0:00|2|(Resources)
27828|ap42-s117-im-decode|PENDING|0:00|2|(Resources)
27826|ap42-s116-im-control|PENDING|0:00|2|(Resources)
```

These are definite submissions, not measured improvements. Source/native-provider
pins and 21 synthetic gate fixtures were committed/pushed in f5a95ac8 before
admission. A fresh site/own-queue cap-five check, all manifest checksums and
sbatch test ran under the shared Slurm lock. [Admission records](admission/)
bind actual IDs, manifests, reservations and post-submit scheduler observations.
No old job, frozen payload, dependency or queue position was modified.

The four requested distinct H100-derived intervention ports now have accepted
IDs: 27804 chunk 6144 and 27806 chunk 8192 already reviewed; 27828 decode-only and
27830 prefill-only are new unmeasured ports. 27826 is additional control and is
not counted as a fifth candidate. [Candidate register](distinct-port-register.json).
These are source-intervention transfers into platform-appropriate H200 bases,
not four winning full H100 recipe reproductions. Mode source studies used
both-HPC-Ops/chunk 4096/N54; this mode pair uses current H200 DeepGEMM/chunk 8192/N64.
The earlier "two remaining unfilled" snapshot is historical, not the current count.

The previous flat H100 phase results are not advertised as gains. Compare each
mode candidate with 27826 only after its independent full local gate passes.
Native per-role source/context/restoration receipts and full distributed graph,
physical KV, both semantic routes, raw 60/120/30/4000/200/seed 2026/error/output
checks remain mandatory. Host Torch is absent; CPU fixtures did not prove native
mode or GPU readiness. Official full-set accuracy remains UNKNOWN. No speedup,
new optimum, publication or submission promotion is claimed by these acceptances.

Prior chunk ports still lose to the incumbent, despite improving their branch.
No combined-mode sweep, unchanged losing repeat, H100 authentication/spending,
HPC edit, schedules, background Codex or published PowerPoint/ZIP change.
[Plan and limits](PLAN.md), [CPU validation](validation.json).
