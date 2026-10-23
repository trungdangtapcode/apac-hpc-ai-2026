# MPI reorder preflight: submitted, result pending

At 2026-10-23T15:51:33.303663Z, job **25943865.pbs101** is **H/qdev** with `afterany:25940700.pbs101@pbs101`. This is the expected dependency hold: the four-rank interface check starts after the existing four-node confirmation finishes. It is not an MPI failure and no runtime mapping result exists yet. The parent remains Q/q5 for insufficient node_pool resources. Preserve both jobs and their queue/dependency positions.

The new request is one shared node, four CPUs/four ranks, 4 GB, zero GPUs and three minutes. Its requested-core envelope is 0.2 SU at the retained rate; the budget conservatively reserves 6.4 SU (128 cores for three minutes). Total consumed allowance plus retained maxima is **4,871.933333 / 5,000 SU**, leaving **128.066667 SU**. Unknown own/shared costs remain reserved. These are planning allowances, not posted charges.

The receipt, pre-submit queue/rate/balance checks, frozen 10-file outer manifest and source-body 9-file seal are retained beside this file. The driver atomically records the budget/intention before one qsub and refuses a second submission intent. Actual target C compilation, two MPI launches, mapping validation, final PBS exit/resources and cost are pending.

The graph candidate that motivated this preflight has 22.5937% fewer crossing interface faces in a logical four-host assignment. A pass here verifies only four-rank single-node reorder semantics; it does not prove that graph mapping on 512 ranks/four hosts, a solver speedup, or a contest score. Next review 25940700 and this preflight, then consider the distinct larger mapping only within budget and after a fresh graph/mapping validation.

A later read-only check at 2026-10-23T17:49:37.514429Z still finds parent Q/q5 and child H/qdev under the same dependency. No result or queue change is inferred from elapsed waiting time.
