# Historical H100 PBS run inventory

`inventory.json` contains one record for each unique PBS scheduler allocation in the retained NSCC AI/Qwen PBS ledger. The ledger has **124 unique GPU allocations**; its 124 job IDs are unique. The count is allocations, not benchmark points: a single allocation can contain several concurrency/load points, warmups, profiling phases, retries inside the client, or validation checks. Internal experiment suffixes are not scheduler IDs.

## Counts

- **124** unique PBS allocations requesting GPUs on the H100 NSCC track.
- **80** have retained PBS exit status 0; **19** have a retained nonzero exit status; **25** have no exit status in the local ledger snapshot.
- **122** are confirmed started from a retained exit status, runtime/charge evidence, or run collection. **One** (224552.pbs111) is explicitly documented as cancelled before allocation. **One** (224466.pbs111) has a terminal state but the inspected local evidence does not establish whether PBS began execution.
- **69** records have a retained good-output-throughput metric in an inspected summary. These are measurements/diagnostics, not necessarily accepted or matched improvements.

## Evidence and lineage

Each record includes its bundle or experiment title, a concise purpose when one was retained, scheduler outcome, a brief metric/result where found, evidence paths, and `parent_job_ids`. Paths are relative to `/home/apacsc42/2026-APAC-HPC-AI`. The budget ledger is the common allocation index; per-job collected summaries/configuration and specific retained result reviews are cited where available.

Lineage edges are included only when the source, control, baseline, original job, or PBS dependency is explicitly named in retained configuration or scheduler records. Similar settings, nearby dates, bundle numbering, or a likely comparison do not create an edge. A listed parent can mean a named control/source or scheduler dependency; it does not by itself claim a causal comparison.

## Limits

The inventory is a bounded reconstruction from the local PBS ledger and retained files; it is not a live scheduler query. Several legacy ledger rows do not retain a submission timestamp, so the recorded calendar date comes from the dated README timeline where available. Exit status 0 only means the submitted script exited successfully; it is not a full benchmark, quality, or research acceptance gate. Missing score metrics are left as missing, not zero. Some historical records lack a standalone hypothesis or complete run review; their purpose is marked as not retained rather than reconstructed from chronology. The unknown accounting/terminal cases remain explicitly unknown unless another cited source resolves them.
