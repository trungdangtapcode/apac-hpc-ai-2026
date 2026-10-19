# Continue with the prepared attention trial

At 14:18 UTC all three preceding H100 allocations were terminal with exit zero. Their 39:11 total allocation time costs approximately 1337.458 SU at the published 128 SU/GPU-hour; this matches the Used increase and releases their 4608-SU maximum reservations. The ledger at 22:00:01 SGT reports Used 30729.102 SU, Balance 33270.898 SU and In Doubt zero.

Submitted **221880.pbs111**, the previously frozen dense FlashInfer-prefill N54 trial. Fresh control 221827 passes all local gates at 2413.802 good tokens/s. The new trial keeps both-phase HPC-Ops, chunk4096, all decode settings and the ranked 4000/200, 60/120/30 protocol unchanged. Its post-score profile must prove the actual attention path. It has no performance result yet.

New maximum reserve: 1536 SU; internal headroom 18734.898 SU under the unchanged 51000-SU operating cap and 13000-SU buffer. Submission was definite and did not require authentication or a VPN restart. Two PBS slots remain available for distinct evidence-backed followups. H200 retains five pending jobs; do not alter their queue positions.

The previous chunk and scoped-protocol observations are being preserved in separate review checkpoints. The protocol setting alone does not prove execution: the separate N48 traces still show Ring LL, so no actual Simple-kernel gain is established. The first chunk review held an automatically derived graph configuration; a source-grounded validator now resolves that without changing any submitted payload.

Evidence: pbs-receipts.json, pbs-post-submit.txt, pbs-pre-submit.txt, reconciliation.json and budget-before.json. This checkpoint covers the new submission and its budget transaction, not a claim that all raw results have already been archived.
