# H200 gains repeat; three new controlled trials — 18 October 2026, 18:46 UTC

## Independent repeat and fresh control

| Job | Configuration at concurrency 56 | Good tokens/s | Joint SLA success | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
|24573|DeepGEMM prefill, chunk 6144, auto decode|2737.410|98.9437%|717.263|16.472|
|24574|HPC-Ops prefill, chunk 4096, auto decode|2728.962|98.8249%|714.981|16.536|
|24575|Fresh DeepGEMM prefill, chunk 4096, auto decode control|2714.097|98.8187%|750.639|16.457|

All three terminal allocations pass the full local checks: sealed artifacts, exact frozen payload, unchanged 60-second warmup / 120-second scoring / 30-second grace, intended resolved runtime and layout, no request errors/cancellations, short-output nonregression and all 12 long retrieval checks. The two candidate reviewers explicitly compare each role's runtime with the fresh control, permitting only the intended chunk/graph geometry or main/inherited speculative MoE runner settings. Speculative decoding stays disabled. Native FP8 model weights, BF16 key/value cache, NIXL patch, routing, MNNVL and FlashInfer decode attention are retained. Organiser full-set accuracy at 99% of the reference evaluation score remains unverified.

The larger prefill chunk now has two consistent observations: original 24528 = 2737.011, repeat 24573 = 2737.410. The repeat is **+0.8590%** versus fresh 24575, compared with the original +0.7798% versus its control. The descriptive two-observation mean is **2737.210 good tokens/s**. This supports a small repeated gain at N56, not a statistical confidence interval or an automatic prediction at another concurrency.

HPC-Ops prefill also repeats positively: original 24529 = 2732.459, repeat 24574 = 2728.962. The repeat is **+0.5477%** versus fresh 24575, compared with the original +0.6122%. Descriptive mean **2730.711 good tokens/s**. Fresh control 2714.097 is close to prior controls around 2715–2717; these small effects remain dependent on the tested hardware, load and implementation.

Good tokens/s means the exported rate of requests satisfying both latency conditions multiplied by 200. Each qualifying request must have TTFT ≤ 3,000 ms and per-request mean ITL ≤ 20 ms. At least 90% of all requests must pass both, including failures in the denominator. Table means do not replace this joint gate.

## Hypotheses submitted now

The separately repeated prefill changes now justify a bounded combination test. Combining changes does not guarantee additive gains. Existing measured HPC-Ops decode also creates a separate load hypothesis.

| New Slurm job | Configuration | Comparison and stopping rule |
|---|---|---|
|**24639**|DeepGEMM prefill chunk 4096 + HPC-Ops decode, N58|Job 24538 demonstrated N56 mean ITL 14.858 ms with passing runtime/output. Test whether this generation headroom permits a better N58 score. Compare pending same-load auto-decode control 24589, plus N56 source 24538 for load context. Do not mix a load increase and runner change into one isolated gain; no automatic N60.|
|**24640**|HPC-Ops prefill chunk 6144, auto decode, N56|Combine separately repeated changes. Compare 24574 to isolate chunk effect within HPC-Ops and 24573 to isolate runner effect at chunk 6144. If the interaction loses, retain the better single change rather than automatically increasing chunk.|
|**24641**|HPC-Ops prefill and decode, chunk 4096, N56|Add the already GPU-validated decode runner to repeated HPC-Ops prefill. Compare 24574 for the decode change and 24538 for the prefill change. H100 both-phase success motivates direct testing, not conversion of its measured gain. Repeat a useful combined gain before adoption.|

All three actual returned IDs were persisted and verified pending Resources. Existing 24588 (chunk 8192 N58 repeat) and 24589 (fresh chunk 4096 N58 control) retain positions. Five active H200 jobs, each 16 GPUs / 17 minutes; no sixth allocation. The original N58 peak 2786.696 from 24544 still awaits its independent repeat and fresh same-load control. Do not promote it based only on the historical comparison.

Frozen syntax and payload validation is in next-validation.json. Benchmark client, protocol, quality scripts and transport are byte-identical to source. Only one intended load, chunk or role-specific runner factor changes relative to each declared source. Both changed roles retain early Hopper/HPC-Ops checks before model loading. Every new result still needs terminal runtime, SLA/error and output gates; successful prior individual changes do not prove their combination. Close backend/output failures rather than unchanged retries. No slides, official-script promotion, HPC_Task content or organiser upload changed.

## H100 access remains unavailable

At 18:44 UTC the SSH wrapper still fails before SSH because no matching live VPN process exists. The last sanitised client-log finding remains IKE SA expired at 14:08:45 UTC. No reauthentication, password prompt, DUO request or cache modification was attempted this turn. Do not infer current PBS job results or credit from the old snapshot. Local VPN loss does not itself cancel PBS jobs, but actual status needs restored access.

Latest validated H100 evidence remains the both-phase N50 observations 221315/221339 at 2371.961/2371.341; descriptive mean 2371.651. The later control 221340, N52 candidate 221341 and profile 221346 remain unreviewed because they are remote. No new qsub or budget reconciliation is attempted without live queue/credit access. Preserve the existing conservative maximum reservations. Last ledger is a historical 21:40:01 SGT snapshot, not live credit.

Codex autopilot stays disabled. Existing non-AI Slurm refresh/submission functions ran interactively under their lock; no background AI, watcher or schedule was launched. Raw artifacts and all failures remain preserved.
