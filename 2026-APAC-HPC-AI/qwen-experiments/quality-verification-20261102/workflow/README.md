# Finite full-quality shard callback

This callback coordinates the **already declared finite set of 16 Slurm jobs** (8 fixed shards for the reference and the same 8 for the candidate). It is ordinary synchronous job-completion handling. It is not a Codex session, watcher, schedule, daemon, timer, retry service, or model runner.

The wrapper calls it once after the existing driver has completed its evaluation and cleanup, while the Slurm allocation is still active. The callback records the supplied driver return code and validates immutable job/run evidence. It does not claim that Slurm has reached a terminal state; `squeue` may still show the current wrapper as running.

## Callback CLI

```bash
python3 workflow/finite_event.py \
  --job "$SLURM_JOB_ID" --role reference --shard 0 --driver-rc "$DRIVER_RC"
```

For a human-reviewed first-pair handoff, use `--no-dispatch` to record and validate only. After reviewing the pair and updating the existing admission review/ledger, an explicit one-time call can resume the same recorded event with `--dispatch-existing`. That option refuses to replace the recorded event.

The callback looks up the exact `role-NN` ledger record and job ID, and then checks the frozen 1,504-ID membership list. Reference results are read from `jobs/full-ref-NNof08/runs/JOB/reference/evaluation`; candidate results are read from `jobs/full-cand-NNof08/AI_Task/logs/full-shards/JOB/evaluation`.

For a successful measurement it requires the exact prepared-manifest and corpus hashes, run status `COMPLETE`, concurrency 64, the pinned generation settings, exact selected IDs and one response per ID, no service errors or deadline skips, and a passing `measurement-validity.json` bound to the response-file hash. It compares every response's prompt/token hashes, shot count, category, and expected label with the prepared corpus. It reparses each raw API body and checks the stored completion/parser fields. The event preserves result counts, source ID membership, paths and hashes.

## Bounded continuation

- A nonzero driver exit or invalid run writes an immutable event plus `workflow/STOP.json`. Existing jobs are not cancelled, retried, or replaced.
- An existing `STOP.json` blocks every later dispatch.
- The first pair must have an explicit reviewed pass in `reviews/first-full-pair-qualification.json`. The existing admission script records that qualification in the ledger while holding its shared admission lock.
- With review in place, the callback queries the current user's Slurm queue. Unknown queue state is deferred, never interpreted as empty. Five or more queued/running jobs returns `DEFERRED_CAP`.
- Below the cap, it invokes only `admit_full.py --wave fill --chain`; that existing admission path owns the shared lock, cap, fixed budget, and definite `sbatch` receipts. This callback never calls `sbatch` directly.
- Once all 16 distinct valid events exist, it invokes `client/aggregate_full.py` on all eight reference and eight candidate run directories and writes `workflow/FULL_COMPARISON.json`. A local 99%-ratio failure is retained as a completed measurement, not reclassified as an infrastructure failure.

An aggregation command error or ambiguous admission failure writes `STOP.json` to avoid blind repeats. Event files and reports are immutable; a repeated callback cannot overwrite evidence. The completed workflow stops after this fixed 16-job batch.

## Local fixture tests

```bash
python3 -m unittest -v workflow/test_finite_event.py
```

The tests use tiny synthetic IDs and injected queue/admission/aggregate functions. They do not submit jobs or contact Slurm.
