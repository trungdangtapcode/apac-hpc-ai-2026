# Queue and review readiness

Checked 17 October 2026, 19:43–19:44 UTC. No new benchmark results are available.

## H200

Jobs 24322, 24327, 24352, 24375 and 24376 are pending for Resources. The two nodes in hpcai, g1 and g4, are allocated. Each of our jobs requires both nodes and all 16 GPUs. Slurm reports no estimated start time. This snapshot does not indicate a new deployment error. Preserve existing queue positions; do not cancel and resubmit without a concrete scheduler reason.

## H100

221153 is queued; 221177 and 221181 have expected afterany holds. Project balance remains 46,924.800 SU, used 17,075.200 SU, In Doubt 0, from the ledger as of 18 October 03:40:01 SGT. Outstanding maximum reservation remains 4,608 SU. No new allocation was submitted in this turn.

## Work completed while waiting

Added nscc-pbs/review-current-prefill.py for all three pending H100 trials. It requires a terminal collected snapshot, frozen payload and seal checks, full N50 protocol, short-output nonregression, BF16 KV allocation, intended TP/EP, task-side runtime logs and all eight decode backend ranks. Each prefill candidate must activate exactly its intended prefetch, DeepGEMM or graph setting; other resolved runtime changes are rejected except engine random seeds. It compares scored metrics against fresh control 221151 and preserves startup diagnostic lines separately. Official accuracy remains unverified.

Pending jobs correctly return WAITING without creating a result. The actual reviewed control 221151 was deliberately presented to each candidate runtime gate; all three correctly rejected it for not activating the proposed change. These are gate checks, not evidence that pending GPU jobs work.

Next: collect and review the first completed allocation. Reconcile terminal PBS usage before another qsub. Keep the DeepGEMM/chunk8192 candidate conditional on the pending confirmation and graph results. Existing non-AI watcher remains active; no new AI automation was enabled.
