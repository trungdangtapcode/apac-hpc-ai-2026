# CPU campaign: remaining grant authorized before 30 October

The owner explicitly authorized using the remaining CPU grant on **24 October 2026**, replacing the previous cumulative 5,000-SU research limit. The owner's planning deadline is **before 30 October**. `myprojects` currently displays ExpDate 15 November; that site field does not override the owner's earlier research deadline or prove when competition access ends.

CPU project **59000042** has a 30,000-SU grant. The ledger retains the pre-campaign 222.154-SU site baseline outside its campaign allowance, so the new cumulative campaign ceiling is **29,777.846 SU**. After reconciling only known diagnostic job25956623, conservative commitment is **4,706.2 SU**, leaving **25,071.646 SU of planning headroom**. The latest displayed site balance is 27,730.062 SU and can lag recent jobs. Unknown older/shared maxima remain reserved; no cost evidence was discarded to increase headroom.

This authorization covers justified CPU research and confirmation, with fresh rate/balance checks and reservation before every qsub. Keep one active CPU allocation and at most three own combined CPU/AI PBS queued/held/running jobs. It does not authorize AI budget changes, background Codex, schedules or automatic notifications.

## Research sequence

1. **Fix and qualify MPI binding.** Job25956623 directly observed singleton affinity before MPI_Init becoming CPUs0–255 afterward for all512 ranks. Core/NUMA reads were not attempted. Use supported runtime controls, compare actual pre/post masks and verify the exact identity/candidate mapping. Keep diagnostics bounded and separate from solver timing.
2. **Matched solver placement tests.** Once binding qualifies, compare identity versus aggressive and balanced mappings with the same512-way Scotch mesh and initialized fields. Use the same MPI flags, binding and transport in both arms. Run150steps/149timings, preserve all samples and inspect numerical work, finite force history, source/field integrity, tails and resource evidence. Counterbalance arm order with a separate BA confirmation if the first result merits it.
3. **Next independent controls.** Study placement/binding and transport one intervention at a time, informed by prior errors and timing. Preserve losing branches and inspect runtime beyond the mean. Do not treat graph cuts as runtime speedups or change numerical work to improve the score.
4. **Reproduce and deliver.** Reserve time/SU for repeat confirmations, best portable scripts, raw logs, reviewed metrics and the English presentation. Final materials should distinguish native measurements from unmeasured candidates.

At512 cores and rate1, a45-minute job reserves384SU;60minutes reserves512SU. These are per-job maxima, not exact charges or a plan to blindly launch dozens of duplicates. The available25kSU allows broader controlled research; information and reproducibility remain the admission criteria. Existing successful best native mean is3.364622070s/step from the independent default-Scotch repeat, not the unqualified placement candidate.

[Locked authorization and report](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/cpu-campaign-20261024/budget-authorization.json), [failed diagnostic review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/diagnostic-25956623/RESULTS.md).
