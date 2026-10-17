# Reviewed results and the next controlled trials

Updated 17 October 2026, 23:42 UTC. Local research checks are not organiser full-set accuracy validation.

## H200

| Job | Configuration / load | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) | Decision |
|---|---|---:|---:|---:|---:|---|
| 24291 | DeepGEMM prefill, N56 | 2715.842 | 749.053 | 16.446 | 98.8194 | Original candidate |
| 24327 | Independent DeepGEMM repeat, N56 | 2716.787 | 748.991 | 16.451 | 98.8201 | Gain replicated |
| 24352 | DeepGEMM, N58 | 2718.080 | 872.259 | 16.491 | 98.7074 | Peak observation; no meaningful load gain |
| 24322 | Prefill weight prefetch, N56 | 2665.572 | 859.131 | 16.261 | 98.7988 | No ranked-throughput gain |
| 24375 | Single TP8/EP2 prefill, equal-TP repair, N56 | 28.329 | 5013.768 | 16.564 | 1.9978 | Reject: SLA and output regression |

The two N56 DeepGEMM runs average **2716.315 good tokens/s**. Their gain versus the respective fresh controls is 1.8136% and 1.7401%. Full protocol, intended runtime, short nonregression and 12/12 long checks passed. This supports DeepGEMM as the current replicated H200 research choice. Official accuracy is still open.

N58 is only about 0.048% above the N56 repeat while mean TTFT increases by about 123 ms and the joint SLA fraction falls. Do not call it a new confirmed optimum or automatically increase to N60.

Prefetch on H200 is about 0.178% below its fresh control. Its representative prefill loading times were 167.57/159.00 seconds versus control 26.84/27.80 seconds, despite similar graph startup. This does not establish that prefetch intrinsically slows loading: storage cache, node and time are confounded. It does rule out claiming a demonstrated H200 startup improvement from this sequence.

## The transport repair ran, but the candidate is wrong

24375 used the correct equal-TP patch, and all P/D warmup paths completed at 309 seconds. Unlike 24321, it reached scoring. However, only 18 of 901 requests met both latency limits. Short diagnostics passed **0/8**, with seven newly failed cases versus the baseline; long retrieval passed **11/12**. The strict reviewer rejects it at the short-output gate. Reject and quarantine this candidate; no throughput or quality improvement is claimed.

This supersedes any implication that the 936 byte-range tests or earlier job 22809 proved complete output correctness. Those tests establish their defined transfer geometry; previous GPU execution establishes that a deployment ran. Neither proves correct end-to-end model outputs for the new TP8/EP2 configuration. The exact origin of the regression is not isolated. Do not blame the patch alone, silently change tolerances, or retry this configuration unchanged. Preserve all failed outputs and logs.

## H100

| Job | Configuration / N50 | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) | Allocation walltime |
|---|---|---:|---:|---:|---:|---|
| 221151 | Fresh combo control | 2231.429 | 495.915 | 19.386 | 98.4286 | 24:51 |
| 221153 | Prefill weight prefetch | 2241.336 | 478.854 | 19.425 | 98.6467 | 15:45 |
| 221177 | DeepGEMM prefill, repaired readiness | 2232.720 | 492.581 | 19.389 | 98.5011 | 25:28 |

All three have reviewed protocol, frozen payload, task-side runtime, short nonregression and 12/12 long checks. H100 DeepGEMM is only +0.0579% versus the fresh control. Its H200 improvement does not transfer as an observed H100 gain at this load; no further H100 DeepGEMM capacity sweep is justified by this point alone.

Prefetch is +0.4440% versus control, within a range that still needs replication. Its observed walltime is 9:06 shorter, and prefill weight loading was 305.50/306.45 seconds versus 921.13/920.61 seconds in the control. Graph timings remained similar. That is a substantial observed startup association, not causal proof: nodes, cache and ordering remain confounders.

## New submissions

| Platform | Job | Change | Control and purpose |
|---|---|---|---|
| H200 | 24425 | DeepGEMM + chunk8192, N56 | Compare confirmed DeepGEMM chunk4096; graph-on retained |
| H200 | 24426 | DeepGEMM + prefill graph off, N56 | Compare confirmed DeepGEMM graph-on; retain decode graphs |
| H100 | 221194 | Repeat prefetch, N50 | Reverse the earlier order to test repeatability of startup association |
| H100 | 221195 | Fresh no-prefetch control, N50 | Same readiness bound, after the prefetch repeat |

H200 24426 completes the auto/DeepGEMM × prefill-graph-on/off comparison alongside pending 24376 and completed controls. The new chunk candidate does not need to wait for the independent graph-off ablation: it keeps the proven graph-on settings and changes only chunk size. The previous self-imposed graph-review precedence is removed for that reason; the independent DeepGEMM confirmation is now available. Do not combine unreviewed changes or automatically promote one result.

The H100 pair uses identical 1,800-second worker readiness bounds, 45-minute allocation caps and the full N50 protocol. Prefetch runs before control this time. Order reversal reduces one confound but does not randomise nodes or control all filesystem cache effects. Require repeated startup observations and nonregressing goodput before choosing prefetch as an improvement. Preserve no-gain results.

## Cost accounting

The two new H100 jobs reserve at most **3072 SU**. They follow queued graph trial 221181 in a verified afterany chain, with at most one 16-GPU allocation running. Last pre-submission ledger: Used 17612.800 SU, Balance 44851.200 SU and In Doubt 1536.000 SU, as of 18 October 07:20:01 SGT.

Prefetch 221153 charged 537.600 SU and is reconciled. Completed 221177 is not yet reflected in that ledger, so its full 1536 SU reservation is retained conservatively. Including that ledger-lag reserve and the three pending jobs, outstanding reservations total 6144 SU; internal 51000 SU planning headroom is 27243.200 SU. The displayed Balance already excludes In Doubt prepayment; it is not deducted a second time. Reconcile the terminal charge when the ledger updates.

## Review files

- H200: ../serving-tuning-10/prefill-pilot-reviews/24322.json, 24327.json and 24352.json.
- H100: 221153-review.json and 221177-review.json.
- Failed TP8/EP2 candidate: 24375-final-review.json and ../runs/24375/.
- New source-bound reviewer: review-new-slurm.py; H100 reviewer: ../nscc-pbs/review-current-prefill.py.
- Submission receipts, frozen hashes, reversed-order validation and dependency proof are saved in this directory.

No new AI automation, official score claim, submission-script promotion or slide update occurred in this research turn.
