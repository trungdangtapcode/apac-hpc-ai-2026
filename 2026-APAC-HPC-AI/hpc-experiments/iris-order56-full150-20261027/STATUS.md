# Iris full150 matched pair submitted and running

Updated 2026-10-27T17:33:06.657738+00:00. **Actual job 2294234 is RUNNING on iris024** in the fresh 17:29:25 UTC snapshot on 27 October (00:29:25 Vietnam time on 28 October). This is an accepted Slurm job, not the earlier test-only scheduler prediction.

Submission confirmed at **2026-10-28T00:28:44.398145+07:00**, Vietnam time. [Actual receipt](submission-receipt.json), [durable intent](submission-intent.json), [fresh state](post-submit-status.json).

- One exclusive Iris CPU node, 56 ranks, zero GPUs, QoS low, maximum 3 hours.
- First `zyx`, then `xyz`, each 150 full solver steps and 149 native timing intervals.
- Both start from their owned, verified initialized source with hierarchy factors (7 4 2), unchanged physics/fixed iterations/function objects, and full source/copy/zero-field checks.
- Actual first progress: runtime hashes captured, initial source hash gate passed in 31.46 seconds, and zyx clone started. No new mean or performance win exists yet.
- Maximum reservation **168 allocated CPU-hours**; internal Iris consumed allowance 219 + reserved 168 = 387 under the newly documented 392-hour ceiling. SU rate/charge unknown. NSCC ledger unchanged.

## Scientific interpretation

This closes the missing full-length Iris comparison if both arms pass. A completed first arm alone is a partial result; require complete native output and sources for both arms, stable actual runtime identities, terminal Slurm exit, all 150 force rows and all 149 timing samples before a matched performance conclusion. Retain slow intervals and native confidence warnings.

Iris is a practice machine. Its raw seconds/step cannot be ranked against the four-node NSCC 3.364622070 observation. Any useful configuration still needs a fresh NSCC measurement when that access is available.

## Preserve and collect

Remote root: `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-orderfull150-20261027T172755Z`. Frozen kit: `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-orderfull150-20261027T172755Z/kit`. Worker logs/results are under `root/runs/2294234` and independent cases under `root/cases/zyx` and `root/cases/xyz`; Slurm stdout/stderr are `kit/runs/2294234.out/.err`. Keep the 49 source hashes unchanged. No runtime-cache, credentials or private authentication state belongs in the archive.

The payload and all admission receipts are captured in Git. Large remote processor meshes/fields are not uploaded by Git. After terminal completion, derive the existing Iris collector/replay against this exact root and compare raw native output with recorded summaries before retiring the reservation once. Do not cancel or requeue solely because it takes time. No background Codex or automatic chat notifications are enabled.
