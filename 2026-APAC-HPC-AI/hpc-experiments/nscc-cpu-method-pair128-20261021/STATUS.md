# Same-node method comparison submitted

**25907325.pbs101**, accepted 2026-10-21T19:06:38.629513+00:00, is **Q** in the retained 2026-10-21T19:06:52.767507+00:00 snapshot. One exclusive ASPIRE-2A CPU node, 128 MPI ranks, 440 GB, no GPU; maximum 29 minutes, 61.866667 SU. Queue waiting is additional; no start-time prediction or candidate speedup exists yet.

Fresh CPU queue was empty and the separate GPU queue was inspected read-only under the CPU submission lock. Project 59000042 balance and the unchanged 100-SU first-wave limit pass. Durable intent/reservation precede exactly one qsub. Conservative commitment is 29 SU consumed ceiling + 8 SU terminal prep maximum retained pending reconciliation + 61.866667 SU pair = **98.866667 SU**. No AI ledger, payload, queue or schedule changes.

Scotch preparation 25907236 passes full review before this submission. The candidate runs all mandatory initialization once, then hierarchical and Scotch each run 40 fixed-work steps on the same node. Control initialized fields are immutable and checked against 768 SHA256 records before reuse; both trees are checked after noWrite solves. Exact native inputs, fixed iterations, force outputs, timers and exits are gates. Atomic placement diagnostics occur outside solver timing. The payload, deployment hashes, checks, receipt, raw observations and source reviewer are retained.

This is a first ordered H→S pair. Report cache/order and single-pair limitations, all tails and Cd, including a losing result. No four-node/150-step score or repeated improvement is claimed. See PLAN.md and PRE_SUBMIT_REVIEW.md. Do not modify the submitted payload or resubmit unchanged.

Remote root: `/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-method-pair128-20261021T190634Z`.
