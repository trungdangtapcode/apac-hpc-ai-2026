# Offline sweep review — 2026-10-15 21:08 UTC

`review-load-sweep.py` prepares the evidence review for220575 without accessing
NSCC or changing frozen pilots. It reads a local `collect-run.py` snapshot,
verifies the snapshot seal, checks the unchanged synthetic protocol and actual
phase intervals, cross-checks completed/error/cancel counts, and compares the
eight short cases against the retained H100 baseline220562. It reports each
load independently. A failed higher load does not erase a complete passingN32.

When existing access works again, first refresh all ownPBS states and credit.
Collect220575 with `python3 nscc-pbs/collect-run.py 220575.pbs111` from the
qwen-experiments directory. Preserve the resulting timestamped snapshot, then
run (replace `SNAPSHOT` with that collection directory):

```bash
python3 nscc-pbs/review-load-sweep.py SNAPSHOT \
  --baseline-smoke nscc-pbs/collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json \
  --out FRESH-REVIEW.json
```

Output refuses overwrite. `n32_research_evidence_pass` is an offline evidence
flag, not a submission decision. The operator must still check live ownqueue,
credit, maximum reservation under budget.lock, matching bundle/runtime and
terminal220575 before submitting04. Nonzero exit requires inspection even when
N32 completed; long-check errors/deferments block quality promotion. Pilot04
then05 retain priority; no new job or reservation is introduced here.

Validation used the historical220562 snapshot and controlled local mutations:
11 checks passed, including seal changes, wrong protocol, truncated actual
profiling, manifest errors, SLA failure, new/missing short cases, running
snapshot, independent higher-load failure and output overwrite refusal.
HistoricalN32 reproduces1565.161394goodtokens/s. Comparing that snapshot's smoke
with itself validates tool behavior only; this is not another model run or an
independent repeat. No new GPU measurement or organiser accuracy is claimed.

AIPerf omits `error_request_count` in the successful220562 export. The reviewer
requires explicit empty `error_summary` plus zero-error manifest and completed
phase log in this case; it does not generally convert missing counters to0.
The initial development report falsely rejected this omitted metric; retained
`offline-review-220562.json` is historical. Final validated result is
`inspection/wake-20261015-2105UTC/offline-review-220562-final.json`, with
`offline-review-validation.json`. Frozen04/05/06 are unchanged.
