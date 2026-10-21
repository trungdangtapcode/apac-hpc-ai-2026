# Repair only the generated control-header comparison

25904959 failed after 16 seconds before mesh work because native dictionary
expansion labels each input filename in a comment. Both retained expansions
are otherwise byte-identical. Change only that comparison: require each known
filename comment exactly once, replace it with the same neutral marker and
reject any remaining byte difference. Retain raw expanded files and the diff.
No numerical entries, source function bodies, mesh or native flags change.

Fresh independent root and payload. Keep 32 CPUs/96 GB/one serial process/
zero GPUs/max 15 minutes, maximum 8 SU. The existing project 59000042 CPU
lock/ledger retains all earlier maxima: 10.666667 + 8 = 18.666667 SU. A later
conditional 128-CPU init+40-step solver is now limited to 35 minutes, maximum
74.666667 SU, for a whole-wave maximum of 93.333334 SU below the 100-SU ceiling.
Only this preparation is submitted now. Check current balance and own queues.

Keep the original case, mesh archive/member identity checks, decomposition and
restore gates unchanged. All content hashing and preprocessing run inside PBS.
Do not alter old failed payloads or processor trees. On success review the
complete mesh identity, exact 128 processor cells/fields and stage/accounting
before the separate parallel initialization and 40-step baseline. Do not skip
required initialization or treat CUT_READY as a solver result.
