# Local review: pre-exec affinity job 25957725

Reviewed from retained local artifacts only. No cluster access, submission, or
source payload modification was performed. The frozen source remains at
`hpc-experiments/nscc-cpu-mpi-exec-affinity-20261024`.

## Observation

The 512-rank `mpi_identity` phase started at 03:48:07 UTC and ended at
03:48:13 UTC. Its wrapper log contains 145 distinct pre-exec records:

- 128 records succeeded and proceeded through the capture wrapper's `exec` path
  (PMI ranks 0–127).
- 17 records were rejected by `capture-affinity-exec.py` with
  `launcher_mask_not_single_cpu` (ranks 262, 266, 271, 272, 280, 321, 322,
  324, 331, 333, 353, 355, 357, 361, 362, 363, and 372).
- 367 ranks have no retained wrapper record.

PALS reported rank 280 exiting with code 125. This matches a wrapper rejection.
The captured MPI command returned 143; its `/usr/bin/time` record shows 4.25 s
elapsed against a 184 s timeout. Thus 143 does not establish timeout expiry.
The wrapper ended with status 1 after 82.19 s total and its post-run payload
hash check returned 0. All recorded setup and validation stages before
`mpi_identity` returned 0.

The wrapper rejections occurred before those ranks called `execve` for the MPI
probe. The 128 successful capture records mean those ranks entered the exec
path, but the retained probe stdout is empty and there are no retained PMPI or
post-init topology records. The evidence neither establishes whether MPI
initialization was reached by any successful rank nor identifies a single
MPI-initialization cause. It also does not identify the exact cancellation
sequence for ranks without records.

## Metadata and accounting limits

The retained collection has 46 manifest entries; their local files match the
recorded byte counts and SHA-256 hashes. Its terminal PBS map is empty. The
captured scheduler query returned `Unknown Job Id 25957725.pbs101`, so final PBS
state, final exit status, and actual resource accounting are unavailable.
The earlier post-submit snapshot only records the job queued for insufficient
`node_pool`; it is not terminal evidence.

There are internal metadata disagreements. The frozen PBS script requests
300 s, while `batch-lifecycle.json` says 180 s. The script sets a 255 s internal
deadline, while that lifecycle record says 135 s. The observed 184 s timeout
at the start of `mpi_identity` is consistent with 255 s less the approximately
71 s already spent in setup. Separately, the submission receipt estimates
42.6667 SU maximum, while the lifecycle record says 25.6 SU maximum. Treat these
as provenance inconsistencies, not proof of billed usage. No actual charged SU
was collected.

## Decision and limits

This run did not qualify the affinity-preservation path and provides no solver
result. Preserve it as a failed, partial launcher observation. Any future
launcher diagnostic should continue collecting all ranks when a mask is wide,
record hostname and complete affinity per rank, and make the collective decision
after gathering the evidence. This review itself does not authorize another
submission.

`replay-review.py` re-parses the retained records and writes `review.json`.
Run it with Python 3 from any directory; it reads only the adjacent local
collection and does not contact the cluster.
