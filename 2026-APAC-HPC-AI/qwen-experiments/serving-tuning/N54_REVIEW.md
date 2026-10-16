## Current result —16Oct2026 10:28UTC

BOTH N54 jobs now have terminal independent reviews.23934 COMPLETED exit0
at08:11:21UTC:2555.4232goodt/s,SLA98.7484%,TTFT751.9882ms,ITL16.8873ms.
Fullseal/raw/protocol/runtime/short pass;47files,802warmup/1598profiling,
0errors/cancel,knownreverse only. DP vs its N52mean:+0.4633% withTTFT+145.1971ms;
vs MNNVL23924 SAME N54:−2.9844%,TTFT+151.5435ms,ITL−0.2229ms.
[Final result and limits](../serving-tuning-08/DP_N54_RESULT.md).
No extraDP repeat/N56; continue queued24009 andwave10. Earlier pending/current
statements below are dated historical snapshots, superseded by this section.

# Matched N54 review preparation — 2026-10-15 22:17 UTC

## Historical result —16Oct2026 05:24UTC

23924 COMPLETED exit0 at04:31:37UTC. Final offline review passed47sealed files,
both N52 baseline seals, raw818warmup/1640profiling, full60/120/30 protocol,
zero requesterrors/cancellations, short7/8 only knownreverse, all8MNNVL/NIXL
ranks and bothP/Dwarmups. Runtime differs from either N52 only in engine seed.
Observed output199–201tokens; goodput retains200tokens/goodrequest convention.

2634.034386goodt/s,SLA98.902439%,TTFT600.444626ms,ITL17.110227ms.
Versus23778/23839 gain+1.615331%/+1.585500%; versus their mean+1.600413%,
TTFT+88.178387ms,ITL−0.030672ms. This is one provisional N54 measurement.
23934 is still PENDING(Resources); no same-load backend ranking is available.
The old pending/no-runtime statements below are historical preparation snapshots.

A separately recorded bounded wave10 extension now confirms this promising
point with24009; it does not open N56 or waive combo gates. See
[plan](../serving-tuning-10/PLAN.md) and
[final review](../nscc-pbs/inspection/wake-20261016-0520UTC/n54-23924-review.json).
The original23924 launcher is no longer retrievable through scontrol after
completion; the queued-time stored capture below remains historical evidence.

Historical scheduler snapshot22:15:28UTC15Oct:23924 and23934 PENDING(Resources).
Historical check16Oct00:50:03UTC: both remain PENDING(Resources), together with23906;
watcher3514431 is alive. No N54 performance or runtime initialization observed.

Both actual Slurm-stored batch scripts match their frozen bundle. SHA256SUMS
and registry payload hashes pass. For EACH of the two matching N52 runs,
all12 operational files are byte-identical to the corresponding N54 bundle.
Config differs only experiment, purpose and concurrency52→54. Normalized
launchers differ only job name, bundle path and QWEN_TUNE_NS52→54. No queued
payload or controller was changed.

| Candidate | Matching N52 jobs | Mean good tokens/s | Mean TTFT ms | Mean ITL ms |
|---|---|---:|---:|---:|
| 23924 MNNVL N54 | 23778,23839 | 2592.542986 | 512.266239 | 17.140899 |
| 23934 DP8+DeepEP N54 | 23780,23859 | 2543.638582 | 606.791063 | 16.959007 |

After terminal, independently check scheduler exit, artifact seal, submitted
payload, full60/120/30 protocol and actual phase timing, nonzero request totals,
errors/cancellations, output lengths, transport/pair initialization and unchanged
eight-case short suite. Recompute goodput and compare against each corresponding
N52 run AND its mean:100*(N54/N52−1). Report absolute TTFT/ITL differences.
A complete SLA failure is a measured frontier point; startup/incomplete export
is not a performance result. A passing N54 point can still have lower goodput
than N52. Larger concurrency alone does not establish improvement.

The N52 launch gate (goodput>=2448.186716, SLA>=95%, meanITL<=19.3ms) authorized
these existing N54 experiments. It is separate from the benchmark's measured
SLA:>=90% requests meeting TTFT3000ms and ITL20ms, with zero errors/cancellations
and the full protocol required for research eligibility. Mean latency alone
cannot determine the fraction of requests passing both thresholds. Do not
silently replace either gate or treat goodput as raw throughput.

Config `matched_concurrency=52`, source_job23576, and older control/reference
fields are inherited provenance. Actual frozen launchers set QWEN_TUNE_NS=54
and config concurrency=[54]. The operational scripts are unchanged, but runtime
load must still be verified in the future export. Preserve the frozen files.

Only after BOTH full N54 results are valid can a same-load backend comparison
be made; each N52→N54 comparison measures a load change within that backend.
One N54 run per branch is provisional. Eight-case non-regression remains distinct
from organiser accuracy. No automatic N56, repeat submission or contest promotion
is added by this guide; scope and shared queue cap5 remain in force.

Evidence: [read-only audit and raw stored scripts](../nscc-pbs/inspection/wake-20261015-2215UTC/).

## Offline reviewer prepared — 2026-10-16 00:50 UTC

After the existing watcher finishes collection, run from the experiment root:

```bash
python3 serving-tuning/review-n54.py 23924 --out /tmp/n54-23924-review.json
python3 serving-tuning/review-n54.py 23934 --out /tmp/n54-23934-review.json
```

The output path must be new. This tool only reads local evidence and writes the
requested report; it does not query or mutate schedulers, authenticate, submit,
or extend the experiment plan. Missing terminal seals report
`INCOMPLETE_OR_INVALID_EVIDENCE`, not a completed measurement. It verifies both
terminal-manifest schemas, sealed required evidence, submitted registry hashes,
raw request counts and lengths, raw good-request count and mean latencies,
full60/120/30 protocol and actual phase duration, zero errors/cancellations,
short-output non-regression, NIXL ranks and both P/D paths. For MNNVL it also
requires all8backend ranks. It checks all12 operational files and resolved
ServerArgs against each matching baseline; only engine random_seed may vary.
It compares each baseline and their mean, preserving TTFT/ITL deltas and observed
length ranges. Complete valid evidence below90%SLA is `MEASURED_SLA_FAIL`.

CPU validation passed21cases plus rehashed/reviewed all four historical N52
runs, reproducing2592.162389/2592.923583/2549.196642/2538.080521goodtokens/s.
This is offline replay, not a new measurement. Actual N54 terminal-path validation
is still pending. Fresh scheduler exit and stored launcher checks remain separate;
the report never certifies BTC accuracy, configuration selection or new jobs.

Timing observation on these four exports: goodput equals good_request_count
divided by profiling manifest elapsed, not the slightly shorter exported
benchmark_duration. Differences are2.798247/3.975055/2.993710/2.870008ms.
Recomputation uses the manifest and retains fixed200tokens/goodrequest convention.
This observation does not establish the cause of the timing difference or a rule
for every AIPerf version. Observed extrema can differ between repetitions; do not
invent an exact200 or identical-extrema quality gate.

Evidence: [validation, timing crosscheck and retained prototype corrections](../nscc-pbs/inspection/wake-20261016-0045UTC/).
