Current update16Oct2026 10:28UTC:23934 is COMPLETED exit0 and independently
reviewed. [Final N54 result](DP_N54_RESULT.md):2555.4232goodt/s,SLA98.7484%,
+0.4633%vs DP N52mean,TTFT+145.1971ms. No extraDP repeat/N56.
Pending23934 statements below describe historical15Oct snapshots.

# DP-attention repeat review — 2026-10-15 22:12 UTC

Job23859 completed exit0 at22:11:34UTC; job23780 is the completed pilot.
The22:07 startup audit below is historical; the final independent review now passes.
The existing watcher remains responsible for collection and gated N54 submission.

Both frozen SHA256SUMS and copied submitted SHA256SUMS pass, all registry payload
hashes match, and Slurm's stored23859 batch script exactly matches the frozen
launcher. All12 operational files including worker, benchmark, placement and
NIXL patch match23780 byte-for-byte. Config differs only experiment/purpose.
The completed23780 artifact manifest was independently rehashed with no failures.
No queued/running payload or controller was modified.

Live log snapshots at22:06:15UTC confirm the same effective decode ServerArgs:
TP8/DP8/EP8, attentionDP enabled, DeepGEMM, DeepEP low_latency, dispatcherFP8,
fused-allreduce disabled, decode chunk1024. Both prefill workers retain chunk4096.
All8decode weight-load completion messages are present in23859. At this snapshot
there are0NIXL-initialized decode rank messages and no full export/smoke; these
absences during startup are not a deployment failure.23780 has8NIXL rank messages.
Raw service log timestamps are UTC+8; do not compare them as UTC scheduler times.

| Job | Package | Good tokens/s | SLA | TTFT mean ms | ITL mean ms |
|---|---|---:|---:|---:|---:|
|23576|RR N52 control|2397.7222|98.9290%|365.2935|19.4565|
|23607|fresh RR N52 control|2400.0231|98.9298%|346.8400|19.5250|
|23780|DP-attention8+DeepEP pilot|2549.1966|98.8708%|596.4419|16.9623|
|23859|independent DP package repeat|2538.0805|98.8651%|617.1402|16.9557|
|23778|MNNVL N52 alternative|2592.1624|99.0068%|516.2843|17.1273|
|23839|MNNVL independent repeat|2592.9236|99.0074%|508.2482|17.1545|

Collection checklist used for the completed23859 audit: verify exit/state, sealed exports and phase timings,
full60/120/30 protocol, request/error/cancel totals and short-output raw cases.
Confirm all8decode DP ranks initialize NIXL, plus both prefill endpoints/router
and pairing warmup; weight loading or ServerArgs alone does not prove transport.
Compare the repeat against23780 and each RR control. Report two-run mean, relative
repeat difference and both TTFT/ITL changes, rather than only higher goodput.
MNNVL's two-run mean2592.542986 is an alternative package comparison, not the
original repeat gate. DP+DeepEP changes scheduling/precision/collectives together;
no isolated kernel or accuracy claim follows from the comparison.

Existing controller N54 gate uses goodput>=2448.1867160875026, SLA>=95%,
meanITL<=19.3ms, full valid measurement,0errors/cancel and no new short failures.
Its conservative reference2400.1830549877477 is retained as configured; do not
replace it with the MNNVL mean or the rounded control shown above. A passing
23859 permits existing gated s8-dpa8-n54 only when the shared cap5 permits it.
Do not manually duplicate the watcher submission, extendN56, or promote a contest
configuration. If incomplete/failing, preserve evidence and investigate.
Eight-case7/8 diagnostic and unverified long transport do not establish organiser
accuracy99%. No new repeat, allocation or SU reservation is created by this review.

Evidence: [audit and raw log snapshots](../nscc-pbs/inspection/wake-20261015-2205UTC/dpa8-repeat-preflight.json),
[initial live access check](../nscc-pbs/inspection/wake-20261015-2205UTC/live-check.json),
[final own scheduler check](../nscc-pbs/inspection/wake-20261015-2205UTC/final-live-check.json).

Final review22:12UTC: full60/120/30 settings and actual phase timings pass,
791 warmup requests and1586 measured requests complete without error/cancel.
All8decode DP ranks initializeNIXL/UCX, both P/D paths warm successfully and
all8connection probes return200. Both manifests rehash without mismatch
(47files pilot,46files repeat; derived reports excluded as stated in each seal).
All12operational files match. Effective client settings match after excluding
only allocation endpoint URLs and job-specific artifact directories. The first
CPU audit falsely rejected the different artifact directory; preserved attempt01
and correction record explain this; no benchmark payload changed.

Two-run DP mean2543.638582goodtokens/s; repeat changes−0.4361%.
Gain over23576/23607 is6.0856%/5.9839%; relative to MNNVL mean2592.542986,
DP is1.8863%lower. MeanTTFT606.791ms,ITL16.9590ms: against23607,
TTFT increases259.951ms whileITL decreases2.56594ms. This reproduces the
DP+DeepEP package improvement overRR but does not establish that it beatsMNNVL.
Both short suites remain7/8, knownreverse only; BTCaccuracy remainsunverified.
The existing N54 gate passes; only the current watcher may submit the gated
follow-up under sharedcap5. No extension beyond existing scope is created.

Final evidence: [independent audit](../nscc-pbs/inspection/wake-20261015-2210UTC/dpa8-repeat-review.json),
[audit code](../nscc-pbs/inspection/wake-20261015-2210UTC/review-dpa8.py),
[terminal scheduler record](../nscc-pbs/inspection/wake-20261015-2210UTC/repeat-accounting.txt).

At22:12:35UTC the existing watcher had submitted DP N54 **23934**, now
PENDING(Resources), alongside23904–23906/23924: sharedcap5full. Its132-response
baseline comparison was independently recomputed for both DP runs; no newly
failed cases. Collect23934 after terminal, use both23780/23859 and mean2543.64
as N52 references, retain measured latency tradeoffs. Scope ends atN54;
no automaticN56 or contest promotion. See final-live-check.json and
short-output-and-next-job.json in the same evidence directory.
