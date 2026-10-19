# New H200 and H100 operating-point observations — 19 October 2026

Checked UTC: 2026-10-19T05:32:52.311985+00:00. This report follows the user-requested status check during the authorised optimisation work. Full raw snapshots, reviewer code, scheduler receipts and new frozen bundles are retained beside it or in their source-linked run directories.

## Accepted local measurements

| Platform | Job | Configuration | Good tokens/s | Joint SLA (%) | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---|---:|---:|---:|---:|
| H200 | 24721 | Fresh DeepGEMM prefill chunk 8192 / auto decode, N58 | 2780.403 | 98.7889 | 784.526 | 16.498 |
| H200 | 24722 | Same serving configuration, N60 | 2839.532 | 98.7606 | 825.556 | 16.556 |
| H100 | 221589 | Both-phase HPC-Ops, chunk 4096, N52 independent repeat | 2411.304 | 98.7401 | 558.195 | 18.308 |
| H100 | 221590 | Same serving configuration, N54 | 2430.891 | 98.6211 | 708.093 | 18.163 |

**H200 24722 is a new highest observation: 2839.532 good tokens/s, +2.1266% versus fresh same-platform N58 control 24721.** That control (2780.403) differs from the previous independent N58 repeat 24647 (2780.483) by only about −0.003%. The changed factor is concurrency 58 to 60. The new N60 result still needs its own independent repeat; it is not a reproduced gain or a statistical significance claim.

**H100 221590 is a new highest observation: 2430.891 good tokens/s, +0.8123% versus the fresh N52 repeat 221589.** Original N52 job 221341 scored 2398.728, and this N52 repeat scores 2411.304. Preserve both observations rather than choosing the lower comparator. The N54 gain is small and requires independent confirmation. Its higher mean TTFT and lower mean ITL are both reported; the joint per-request gate determines acceptance.

All four completed allocations have successful terminal accounting, complete unchanged 60-second warmup / 120-second scoring / 30-second grace, sealed raw exports, frozen payload hashes, zero request errors/cancellations, intended runtime, short-output nonregression and all 12 long retrieval checks. PBS long answers were also checked against the retained response text and expected values, not only their precomputed pass flags. H200 runtime differs from the accepted source only in random seeds; PBS runtime likewise retains both-phase HPC-Ops, BF16 KV, speculation disabled, the intended TP/EP layout and all decode backend ranks. The H200 360-second whole-client guard did not fire.

Good tokens/s is the rate of requests satisfying both TTFT ≤ 3000 ms and request-mean ITL ≤ 20 ms, multiplied by the prescribed 200 output tokens. At least 90% of all requests must pass jointly. Latency table entries are means in milliseconds. Local synthetic output checks do not establish full organiser accuracy at 99% of the reference score.

## Next jobs actually submitted

| Platform | Job | Trial and comparison | Maximum request |
|---|---|---|---|
| H200 | 24732 | Independent N60 repeat of 24722 | 16 GPUs / 17 min |
| H200 | 24733 | One N62 trial, same serving configuration; compare 24732 | 16 GPUs / 17 min |
| H100 | 221645.pbs111 | Independent N54 repeat of 221590 | 16 GPUs / 45 min |
| H100 | 221646.pbs111 | One N56 trial, same serving configuration; afterany 221645 | 16 GPUs / 45 min |

The higher-load points are new explicit decisions after the preceding source point passed every local gate. They are not automatic retries or an unchanged continuation of a failed load. The repeated source observations have joint SLA success above 98%, TTFT below 1 second and mean ITL below the 20-ms bound. This motivates one bounded next load test, not a prediction that it passes. Worker, client, precision, quality scripts and transport are byte-identical to the source in every new bundle; only concurrency and identifying metadata differ. No automatic N64 on H200 or N58 on H100. Stop a losing/error/quality branch and retain its data.

H200 24723 (chunk 12288 at N58) and 24724 (HPC-Ops decode with chunk 8192 at N58) retain their original positions. They are independent factors; do not wait for them before reviewing completed load trials. Current exact queue/accounting snapshots are slurm-latest.txt, slurm-latest-accounting.txt and pbs-latest.txt. New jobs have no score yet.

## Credit and preservation

Pre-submission ledger as of 19/10/2026-13:20:02 SGT: Used 27577.458 SU, reported Balance 34886.542 SU, In Doubt 1536.000 SU. Only charges reflected in Used were reconciled. Any terminal job awaiting the ledger retains its full maximum reservation. The new two-job PBS reservation is **3072 SU**, not actual expenditure. Internal headroom after all conservative reservations is **18814.542 SU**, under the unchanged 51000-SU bound and 13000-SU buffer. Balance already excludes prepayment; do not deduct In Doubt twice. The ledger is a dated published snapshot, not a live second-by-second total.

No VPN restart, reauthentication, background AI, automatic watcher, slide, official submission package or organiser upload occurred. Full source data and failures remain preserved; capture this milestone with actual Git dates and keep the external object store with the archive.
