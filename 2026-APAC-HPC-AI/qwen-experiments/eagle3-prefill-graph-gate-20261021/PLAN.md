# Single TP4 prefill graph gate before another full PD allocation

222780 fixes the decode RMSNorm failure and reaches decode readiness, but its
prefills split at the automatic local-memory graph guard. TP3 starts draft
prefill capture with 4.37 GiB; TP0/1/2 skip at 3.98/3.90/3.90 GiB and move on.
No draft-prefill completion or HTTP readiness appears, and the head times out.
This is observed rank divergence; a blocked collective is a hypothesis without
a hang trace, not a proven NIXL fault.

Extracted cuda_graph_setup.py from the recorded organiser image on the login
host using a single CPU worker and only this selected source file. The host's
older unsquashfs does not support -cat; the first attempt failed without
extracting image contents. The subsequent bounded -d extraction succeeds.
The native 4-GiB predicate and disabled-backend early-return functions execute
in CPU fixtures: observed memory values split the automatic decisions; explicit
disabled backend returns the target eager runner and skips draft capture.
This verifies source behavior, not complete GPU initialization or correctness.

The next bounded job uses one node with 4 H100, TP4/EP1, at most 20 minutes and
170.666667 SU maximum. It loads the actual published FP8 target and pinned
BF16/unquant EAGLE3 draft as a single native disaggregated prefill role. Retain
222780 worker/transport/backend/dtype/chunk settings; add only
--cuda-graph-backend-prefill disabled. No decoder, router, serving request,
AIPerf, scoring or dataset traffic is launched. Four GPUs is a diagnostic,
not a scored contest deployment. Keep native eager model mathematics; do not
force graph capture below its safety threshold or patch target computation.

The job verifies the image's source hash, four visible Hopper GPUs, all payload
hashes and mounted NIXL source. The same worker also records role locality and
bounded resources. An independent semantic artifact requires HTTP 200, native
ready log, target/draft disable messages, all four NIXL rank initializations,
no prefill capture start and no matched Python/native fatal patterns. Missing
or failed evidence is a failure even with scheduler exit 0. Three synthetic
artifact fixtures pass. The source-level proof is separate from the actual
runtime source hash and future terminal GPU review.

Require a fresh own queue and published ledger under budget.lock, reconcile
222769/222780 costs uniquely and retain any unposted maxima before reserving.
Use the unchanged 51000 SU cap/13000 SU buffer; never retry an uncertain qsub.
Only definite receipts establish submission. A useful passing readiness probe
permits preparing a separate 16-GPU full-PD repair and exact real-ID comparison;
it does not permit a throughput screen, accepted output equivalence or an
accuracy claim by itself. If it fails, inspect the new evidence before another
hypothesis. No unchanged 16-GPU retry or background AI. The accepted N62
submission remains unchanged until an improvement is actually measured.
