# Repair the observed CPU module-reset boundary

Control: frozen 25904725.pbs101 failed in two seconds before default modules
loaded. The actual site resetmodule expects grep to return no matches after
purging, incompatible with its caller's strict errexit/pipefail context.

Change only reset sourcing to an if condition, check its final return and keep
all existing version/precision/executable gates. The job display name changes
to distinguish the repair. Native tutorial, official timing-source bytes,
module/compiler choice, four MPI ranks, five steps, timeout, resource envelope
and output gates are unchanged. No unbounded retry, numerical change or
suppressed native exit is introduced. This is a diagnostic, not Basic scoring.

Fresh deployment/root and receipt; eight CPUs/24 GB/four MPI/zero GPUs, at most
10 minutes/1.333333 SU. Reserve through the existing parent probe's CPU budget
lock/ledger for project 59000042; retain the first maximum conservatively until
posted reconciliation. Combined maxima 2.666667 SU remain below the first-wave
100-SU planning ceiling. Own CPU queue must be empty; combined own PBS cap three.
Run only if the corrected payload is separately backed up and hash verified.

On failure collect the exact boundary/phase and refine only with evidence.
On success, accept clean terminal exit plus actual native compilation/library,
five solver steps and timing Average. Then prepare the fresh official 65M case
under a separately reserved bounded allocation; keep old processor trees and
historical cases untouched. No AI jobs/payloads/budget changes.
