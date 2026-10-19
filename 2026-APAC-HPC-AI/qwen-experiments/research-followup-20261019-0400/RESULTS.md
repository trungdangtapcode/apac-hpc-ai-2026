# Live queue, recovered access and completed results — 19 October 2026

Checked UTC: 2026-10-19T04:04:27.163739+00:00. Scheduler and accounting evidence is stored beside this report.

Both own queues are empty. All five H200 allocations and the three recovered PBS allocations finished with exit status zero. This is a dated observation, not a promise about future queue state. No new GPU allocation was submitted during this status/login request.

## H200 results

All five measurements pass the unchanged raw protocol, joint latency/error gate, frozen submitted payload hashes, short-output nonregression and all 12 long retrieval checks. Actual logs retain BF16 KV, speculation disabled, all decode NIXL/MNNVL/attention ranks and HPC-Ops preflight where requested. The independent repeat 24647 has only intended prefill chunk/graph geometry differences versus fresh control 24589, apart from random seeds. The 360-second whole-client guard did not fire; it contains a stall rather than proving its underlying cause is repaired.

| Job | Configuration | Good tokens/s | Joint SLA (%) | TTFT mean (ms) | ITL mean (ms) |
|---|---|---:|---:|---:|---:|
|24589|DeepGEMM prefill, chunk 4096, auto decode, N58 control|2718.797|98.7066|873.129|16.486|
|24639|DeepGEMM prefill, chunk 4096, HPC-Ops decode, N58|2724.552|98.7119|1183.274|14.851|
|24640|HPC-Ops prefill, chunk 6144, auto decode, N56|2714.903|98.7013|755.146|16.412|
|24641|HPC-Ops prefill and decode, chunk 4096, N56|2742.207|98.8325|1019.339|14.881|
|24647|DeepGEMM prefill, chunk 8192, auto decode, N58 bounded repeat|2780.483|98.8453|784.494|16.505|

24647 reproduces the useful chunk-8192 result at **2780.483 good tokens/s**, **+2.2688%** versus fresh same-load control 24589 (2718.797). Original 24544 was 2786.696; the two completed observations have descriptive mean 2783.589. Retain failed warmup attempt 24588 as a failed attempt, not a score. No statistical confidence claim. Official full-set accuracy remains unverified.

24639 adds only +0.2117% versus the same-load auto-decode control, while raising TTFT. 24640 does not improve the better separate chunk/runner observations; do not assume additive gains. 24641 is a useful 2742.207 observation but remains below the chunk-8192 N58 result and needs its own repeat before promotion.

## H100 results recovered after VPN restoration

VPN was restored at 04:01:09 UTC through the existing tmux-owned IPsec/TCPT client, keeping the private cache. Only the old dead terminal was removed. SSH password authentication then succeeded on a2ap-login01. The initial batch-only SSH rejection was an SSH authentication failure after the VPN was already connected. No additional MFA code was requested by this client; phone-side DUO behaviour was not observed. The tunnel was detached from the tool terminal and left running. No credentials or session material are part of this report.

All three recovered allocations pass terminal accounting, collected evidence hashes, frozen planned payload, full protocol, joint latency/error, short output, long retrieval and intended resolved runtime checks.

| Job | Configuration | Good tokens/s | Joint SLA (%) | TTFT mean (ms) | ITL mean (ms) |
|---|---|---:|---:|---:|---:|
|221340|Auto prefill, HPC-Ops decode, N50 fresh control|2302.223|98.6806|691.593|17.781|
|221341|HPC-Ops prefill and decode, N52|2398.728|98.7316|602.260|18.211|
|221346|HPC-Ops prefill and decode, N50; separate post-score profile|2375.807|98.8521|482.657|18.228|

New H100 highest observation is **221341: 2398.728 good tokens/s**, +1.1285% versus prior N50 peak 221315 (2371.961). That comparison changes concurrency and is not an isolated backend effect or an independently repeated N52 result. Job 221346 provides another both-phase N50 observation at 2375.807, +3.1962% versus fresh N50 decode-only control 221340. Its GPU profile files were recovered but kernel classification was not performed in this status turn. H100 and H200 scores remain separate measured platforms.

## Credit and evidence limits

Fresh project ledger as of 19 October 12:00:01 SGT: grant 64000.000 SU, Used 27199.147 SU, Balance **36800.853 SU**, In Doubt 0.000 SU. Used increased 1352.249 SU, matching 16 GPUs at 128 SU/GPU-hour for the three recovered walltimes (14:43, 11:35, 13:19), within ledger rounding. Reconciled their reservations under budget.lock. Internal operating headroom under the unchanged 51000-SU bound is 23800.853 SU, with the separate 13000-SU planning buffer. These planning bounds are not organiser quotas.

Good tokens/s is the qualifying request rate multiplied by the prescribed 200 output tokens. Each qualifying request must satisfy TTFT ≤ 3000 ms and mean ITL ≤ 20 ms; at least 90% of all requests must pass jointly. Mean latency values alone do not establish this gate. Synthetic short/long checks are research safeguards, not the official 99%-of-reference accuracy evaluation. Raw artifacts and failures remain preserved.

Autopilot remains disabled. No background AI, new job, slide, official package or organiser upload was created.
