# Actual scheduler acceptance

**Job 2294675** was accepted at **3 November 2026 11:33:56 Vietnam (UTC+7)**. At 11:34:15 it was **RUNNING on iris001**, 19 seconds elapsed. This is a dated scheduler snapshot, not a promise that it is still running.

The distinct R2 payload fixes the actual `interleavemask` spelling observed in failed 2294674 and changes the job name. All other runtime files match that frozen parent. The original failed payload remains intact. A fixture from the actual non-sensitive output passes, along with policy-drift, extra-path, source-manifest and syntax checks.

The experiment uses 56 CPU cores, one exclusive node, zero GPUs, low QoS and a ten-minute limit. Four fresh copy/hash arms use inherited / interleaved / interleaved / inherited memory policy. NUMA means memory is arranged near separate CPU sockets; policy can affect where new pages are allocated. The job records actual policies and whole-node counters but runs no solver and cannot establish a speedup.

Admission checked the live queue twice under the budget workflow, froze seven payload hashes and reserved **9.333333 allocated CPU-hours**. Ledger: **985 consumed + 9.333333 reserved = 994.333333**, unchanged internal stage **1009**. Remaining unreserved allowance **14.666667 CPU-hours**. Billed SU remains unknown; NSCC and AI are separate.

Next: collect terminal accounting and all compact result records, verify frozen payload/source-before/source-after and four clone checks, inspect each child's actual policy and counter deltas, and reconcile this maximum once. A failed or partial arm is not a qualified result. Any solver follow-up needs separate frozen settings and a finalization-inclusive runtime budget.
