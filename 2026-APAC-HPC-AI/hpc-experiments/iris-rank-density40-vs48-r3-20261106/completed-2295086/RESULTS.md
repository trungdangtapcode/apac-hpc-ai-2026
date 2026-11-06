# Iris job 2295086 review

**Assessment: invalid as a matched performance measurement.** The Slurm job
ended `FAILED` (`ExitCode 1:0`) after 3,037 seconds on `iris001` with 56
allocated CPUs. Only the first control and candidate arms started; the other
two arms did not start.

## Retained numeric observations

| Arm | Status | MPI ranks | Solver horizon | Timed intervals | Mean interval time |
|---|---|---:|---:|---:|---:|
| A1 control, 48-rank Scotch | Completed, native return 0 | 48 | 40 steps | 39 | 25.168843727282052 s/step |
| B1 candidate, 40-rank Scotch | Timed out at 1,800 s | 40 | started steps 1–36 | 34 | 49.67608234055882 s/interval, diagnostic only |
| B2 candidate | Not started | — | — | — | not collected |
| A2 control | Not started | — | — | — | not collected |

The local `native_output.py` review API passes for A1: the log reaches `End`,
contains steps 1–40 and 39 positive timings, and its time-step, wall-clock,
fixed-iteration, force-coefficient and resource records agree. The A1 force
coefficient file has all 40 steps. This validates A1 as a control observation;
it does not make the incomplete A/B sequence a comparison. B1 lacks a terminal
native return and full horizon, so it is not eligible for the native review
API or a performance result.

## Integrity and placement evidence

Replay verified the raw archive SHA-256 and all **207** collected file hashes;
the frozen payload manifest contains and matches **100** hashes. The
pre-execution accepted-source checks returned 0 for both rank configurations.
The archive has no post-run source-check record, so source-after integrity is
not claimed.

Recorded per-rank CPU masks are one CPU each and unique. Intersecting those
masks with the recorded hardware lists (NUMA node 0: even CPUs 0–54; NUMA node
1: odd CPUs 1–55) gives 48 ranks as **28/20** and 40 ranks as **28/12** across
nodes 0/1. These records establish launcher affinity before `MPI_Init` only;
they do not establish MPI-initialized solver-thread placement or explain the
timing difference causally.

## Diagnostics and limits

The run collected 5-second, whole-node telemetry: 211 A1 samples and 361 B1
samples; both samplers stopped successfully. These are aggregate node samples,
not process-attributed bandwidth evidence. Per-arm resource timing records are
present (A1 exit status 0; B1 was terminated by the 1,800-second timeout). The
scheduler reports 13:57:32 total CPU time and blank job-level MaxRSS; the batch
record reports 136,724,052 KiB MaxRSS. These data do not isolate solver memory
or a cause for B1's slow progress. Billing/site SU was not present in this
collection and remains unknown. Allocated wall-clock CPU capacity was
47.24 CPU-hours (56 × 3,037 / 3,600), an accounting quantity rather than billed
SU.

Because B1 timed out and B2/A2 never started, there is no replicated,
order-balanced matched result. Do not interpret A1 versus B1 as a rank-density
speedup. The only supported new evidence is that, in this launch, the recorded
40-rank launcher mask used 28/12 CPUs across the two NUMA nodes while the
48-rank mask used 28/20. The next test should separately balance the 40 ranks
20/20 across sockets and retain a complete 40-step control/candidate sequence.

## Replay

Run `python3 replay_review.py` from any directory. It verifies the archive and
frozen hashes, validates A1 through the native output API, checks both strict
rank-file sets, derives NUMA counts from the actual recorded CPU lists, and
rewrites `REVIEW.json`. `REVIEW.json` records numeric metrics and missing-data
states separately from this assessment.
