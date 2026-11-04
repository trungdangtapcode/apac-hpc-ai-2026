# Correct policy applied, native candidate loses the bounded trial

Job 2294803 FAILED 1:0 after 2,667 seconds. A1 completes 40 steps/39 timings at 24.758556905 s/step with native replay; B1 returns 124 at 1,500 seconds, 33 completed intervals averaging 41.846495650 diagnostically and step 35 incomplete. Remaining arms never start. No complete candidate or four-arm score exists. All 56 actual pre-exec policy/affinity records in each started arm pass and 34 completed force rows match the control prefix; source/runtime after gates are absent, not passed.

The mechanism was correctly applied before exec, but the partial runtime direction is unfavorable and the candidate exceeds its frozen cap. Close this unchanged interleave-all candidate; do not extend the cap just to finish it. This does not reject all NUMA hypotheses. The JIT missing-library startup line appears in the successful control too; native execution afterwards means it is not established as the timeout cause. CPU/memory/vmstat telemetry is available; pressure is absent. Timed-out GNUtime reports 0% CPU despite active native steps, so that aggregate cannot diagnose hardware idleness.

Actual 41.486667 CPU-hours, conservatively 42, retires 112 reserved once; 1,219 consumed /0 reserved /stage 1,289. A distinct small collective-runtime probe is considered from actual MPI library evidence and official documentation, not inferred as the cause of this failure. No new acceptance is claimed without receipt.

[Detailed result and raw artifacts](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-solver-rank-interleave40-20261105/completed-2294803/RESULTS.md).
