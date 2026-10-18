# New peaks and next experiments — 18 October 2026, 13:27 UTC

## Completed reviews

| Platform / job | Configuration | Good tokens/s | Joint SLA success | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
| H200 24538 | DeepGEMM prefill, HPC-Ops decode, chunk 4096, N56 |2733.199|98.8284%|1037.104|14.858|
| H200 24544 | DeepGEMM prefill, auto decode, chunk 8192, N58 |**2786.696**|98.8493%|774.057|16.515|
| H100 221314 | Auto prefill, HPC-Ops decode, chunk 4096, N50 |2308.979|98.6842%|669.245|17.831|
| H100 221315 | HPC-Ops prefill and decode, chunk 4096, N50 |**2371.961**|98.7838%|486.401|18.221|
| H100 221316 | Auto prefill, HPC-Ops decode, chunk 4096, N52 repeat |2318.328|98.4869%|820.568|17.780|

All five allocations completed with exit 0 and pass frozen terminal artifacts, exact predeclared payload hashes, full 60-second warmup / 120-second scoring / 30-second grace, intended runtime, short-output nonregression and all 12 long retrieval checks. Runtime differences are explicitly allowlisted by role. All eight decode ranks retain MNNVL and FlashInfer attention, native FP8 model and BF16 key/value cache. Main and inherited speculative runner settings are checked; speculative decoding remains disabled. Official full-set reference-score accuracy remains unverified. Scheduler completion alone is never an accepted benchmark.

Good tokens/s means exported qualifying requests/s multiplied by 200. A qualifying request must satisfy TTFT at most 3,000 ms and its own mean ITL at most 20 ms; joint success must be at least 90%, with errors in the denominator. Mean latencies in this table are descriptive and do not replace the per-request gate.

## Interpretations

**H200 chunk 8192 at N58 becomes the highest observation:** 2786.696 versus historical same-load chunk 4096 job 24352 at 2718.080, **+2.5244%**. Mean TTFT is about 98 ms lower. This is larger than the tiny N56 chunk gains, suggesting a batch/load interaction worth testing. However, the comparator is historical: one observation cannot isolate chunk benefit from node/time drift. Submit both a same-load fresh control and an independent repeat, rather than promote the peak or automatically increase to N60.

**H200 HPC-Ops decode works but changes the latency balance:** 2733.199 is **+0.6395%** versus fresh DeepGEMM-prefill/auto-decode control 24526. Mean ITL improves by 1.586 ms to 14.858 ms, while TTFT increases by 285.824 ms to 1037.104 ms. All local gates pass. The extra decode headroom motivates a future bounded N58 test, but the active queue is now full with the replication/control work below. Do not discard this result or infer the same gain as on H100. No unvalidated prefill-backend combination is introduced on H200.

**H100 prefill HPC-Ops adds a new useful gain:** 2371.961 versus the immediately preceding matched decode-only control 221314 at 2308.979, **+2.7277%**. Decode HPC-Ops, prefetch, load and all other runtime settings are matched; the prefill runner changes from auto to HPC-Ops. TTFT falls from 669.245 to 486.401 ms, while ITL rises from 17.831 to 18.221 ms. Joint success remains 98.7838%. This supports the profile-guided prefill hypothesis, but needs independent replication and a fresh reversed-order control before adoption.

**H100 decode-only N52 repeat is consistent but a small load benefit:** 2318.328, **+0.4049%** versus fresh N50 control 221314; previous N52 was 2314.735. It again raises TTFT to about 820 ms. This is a load comparison, not an isolated runner effect. The new prefill implementation changes the useful operating point, so test N52 with that new configuration once; no automatic N54.

H100 chunk 8192 remains closed after its prior 2.4813% loss. H200 sub-percent chunk 6144 and prefill HPC-Ops gains still await the already queued repeats and fresh control 24573/24574/24575. Preserve their positions.

## Five newly submitted jobs

| Job | Controlled experiment | Acceptance and next decision |
|---|---|---|
| **24588** | Repeat DeepGEMM prefill chunk 8192 N58, auto decode | Reproduce 24544 and compare new same-load control 24589. A peak needs replication and drift context. |
| **24589** | Fresh DeepGEMM chunk 4096 N58 control | Isolate the chunk effect at N58; avoid relying on historical 24352 alone. |
| **221339.pbs111** | Independent HPC-Ops prefill+decode N50 repeat, chunk 4096 | Repeat 2371.961 and compare new decode-only control 221340. Candidate precedes control to reverse the original order. |
| **221340.pbs111** | Fresh auto-prefill/HPC-Ops-decode N50 control | Test whether the prefill gain survives fresh control and time/node drift. |
| **221341.pbs111** | HPC-Ops prefill+decode at N52, chunk 4096 | One adjacent operating-point test after validated N50. Compare same-configuration N50; no automatic higher load. |

The PBS afterany chain 221339 → 221340 → 221341 is verified in scheduler output; one 16-GPU allocation at a time, maximum three active jobs, each 45 minutes / 1,536 SU. The H200 queue contains existing 24573/24574/24575 plus 24588/24589: five active, each 16 H200 / 17 minutes. No sixth job; no cancellation/requeue of existing positions. Frozen syntax and file hashes are in next-validation.json. All source execution/worker/client/quality files remain byte-identical; only job identity/load exports and configuration metadata change. No scoring or output rule changes.

Stop or close a branch on failed latency/error/output gates or lower goodput. Do not retry backend/output failures unchanged. Small or conflicting gains need context, not blind load increases. Next H200 slot, when available and useful: consider HPC-Ops decode N58 from 24538's measured ITL headroom, with matched DeepGEMM-prefill control; do not submit above cap or presume the future result. No official-script promotion from single observations.

## Credit

Fresh ledger as of 18 October 21:20:07 SGT: Used **24,949.192 SU**, Balance **37,514.808 SU**, In Doubt **1,536 SU**. Its increment **918.756 SU** reconciles completed 221314/221315 walltimes 14:36/12:19. Their old reservations are released. Terminal 221316 took 15:14, estimated **519.964 SU**, not yet reflected in Used; retain its full1,536 SU reservation.

The new three-job batch reserves **4,608 SU maximum**. Total outstanding conservative reserve is **6,144 SU**, including terminal ledger lag. Headroom under the unchanged internal 51,000 SU cap is **19,906.808 SU**. The 13,000 SU buffer is our planning choice, not an organiser quota. Balance already excludes In Doubt prepayment; never deduct it twice. Budget.lock guarded reconciliation, reservation and immediate returned-ID records. Uncertain submissions retain their reservation and must never be blindly retried.

No slides, official scripts, HPC_Task content or organiser upload changed. Codex autopilot remains disabled; no background AI or watcher was launched. A first parallel refresh command attempted log redirection before the new report directory existed; it failed locally before running the refresh. The directory-dependent refresh was rerun sequentially. No GPU submission occurred from that failed local command. All raw reviews and failed attempts remain preserved.
