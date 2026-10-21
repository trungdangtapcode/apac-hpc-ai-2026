# NIXL descriptor probe submission

Submitted 2026-10-21T19:54:05.187642+00:00 as **223097.pbs111**. The immediate verified
PBS receipt is RUNNING on nodes a2ap-dgx035 and a2ap-dgx039, one GPU per node,
maximum ten minutes. This is a dated scheduler observation, not a terminal result.

The single receipt follows the frozen six-function CPU regression and 24-case
real-NumPy method rehearsal. Uploaded payload hashes match. The fresh locked
own-GPU queue was empty before submission. Published project Used 46367.710 SU,
Balance 17632.290 SU, In Doubt zero before this job. Maximum reserved charge
42.666667 SU; internal headroom after reservation **4589.623333 SU**.
The 51000 cap and 13000 retained reserve are unchanged. No uncertain submission,
blind duplicate or HPC CPU access was involved.

Read [PLAN.md](PLAN.md) for hypothesis, source identity, byte gates and limits;
[pbs-receipt.json](pbs-receipt.json), [post-submit.txt](post-submit.txt) and
[reconciliation.json](reconciliation.json) preserve the actual receipt and credit
review. No output equivalence, throughput or accuracy result is claimed. Collect
and review both rank artifacts and actual logs after terminal state before a
full-model decision.

## Terminal review

Superseding the running snapshot: **223097 is F/exit0**, 199 seconds, all 24 actual descriptor writes and independently recomputed GPU byte hashes pass. Estimated allocation charge 14.151111 SU; posted reconciliation is pending, so retain the maximum reservation. [Sealed analysis, telemetry correction and next decision](REVIEW.md).
