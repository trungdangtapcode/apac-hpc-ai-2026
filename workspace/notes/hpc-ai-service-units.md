# HPC and AI service units are separate project balances

Verified from retained NSCC account/project reports on 21 October 2026. The owner asked whether HPC service units are shared with AI.

| Workload | NSCC project | Relationship |
|---|---|---|
| ASPIRE-2A CPU / OpenFOAM | 59000042 | Separate CPU project, grant 30,000 SU |
| ASPIRE-2A+ H100 / Qwen | 59010042 | Separate AI project balance, managed by the GPU worker |

Submitting our OpenFOAM job with `#PBS -P 59000042` consumes CPU-project units; it does not debit the separate 59010042 AI project. The CPU project's observed queue rate is 1 SU per allocated core-hour: 128 allocated cores for 10 minutes estimate 21.333333 SU, regardless of MPI work utilization. Requested walltime reserves a maximum; terminal allocated core-hours estimate actual use. A posted per-job billing export has not been obtained.

The **100-SU first-wave ceiling** in the HPC plan is a research spending limit for this initial experiment set. It is not the 30,000-SU project grant and is not the current balance. Do not silently raise this ceiling based on grant availability. The project usage display is stale relative to retained terminal accounting; current planning uses conservative terminal-resource estimates plus a buffer, and keeps both sources of evidence. The initial grant is not a claim that 30,000 SU remain.

Firmus H200 is another cluster with its own Slurm access and resource limits; it is not either of these two NSCC CPU/AI project balances. This note does not authorize changes to AI work or imply unlimited cluster use.

Evidence: hpc-experiments/nscc-cpu-timing-probe-20261021/cpu-budget.json and its dated reconciliation/pre-submit reports; the separate AI project ID is preserved in the session handoff and existing GPU budget records. Keep credentials and authentication state out of these notes.

## Later owner-directed expansion

After this clarification the owner explicitly requested substantially more HPC research/submissions. The CPU continuation now uses a bounded cumulative 1,000-SU planning ceiling, including the original first wave. The original 100-SU description above is historical for that first phase. Separate project balances and all queue/budget/AI-preservation rules remain. See hpc-experiments/cpu-continuation-20261021/PLAN.md and the CPU ledger ceiling_history.

## 23 October: current CPU campaign ceiling

The 21 October 1,000-SU continuation is historical. The owner explicitly approved a **5,000-SU cumulative CPU research ceiling including conservative shared use**. This is a local campaign spending limit, not the site's 30,000-SU grant or an AI-credit change. Current ledger commitment after submitting 25940700 is **4,865.533333 SU**, including intentionally overlapping posted-display usage and retained unknown-job maxima. Exact historical charges remain unproven. See [current funding](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/cpu-continuation-20261023/BUDGET.md) for the arithmetic. No old unknown reservation was released.
