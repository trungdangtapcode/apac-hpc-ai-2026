# CPU N128 preparation: corrected header check submitted

25905006.pbs101 accepted at 2026-10-21T14:15:25.657039+00:00. Fresh frozen
payload/root, only the generated header comparison and job label change from
25904959. Thirty-two CPUs/96 GB/one serial process/zero GPUs, maximum 900 s
and 8 SU. Mesh split target is 128 ranks; this job does not run 128 MPI tasks.

The dedicated CPU lock covers fresh project/queue checks, combined own PBS cap,
intent, reservation and exactly one qsub. Conservative retained maxima are
18.666667 SU; conditional later 128-CPU/35-minute solve is 74.666667 SU, whole
wave 93.333334 SU below the 100-SU planning ceiling. No AI ledger/job changes.

Next review header normalization proof, full archive/member identity,
decomposePar/restore logs, exact processor/field set, native exit and accounting.
CUT_READY is not mandatory initialization or a solver score. The authoritative
raw receipt is submission.json; query live PBS rather than treating this dated
submission as completion.

## Preparation accepted

25905006 is F/exit0, 187 seconds (3 minutes 7 seconds), after about 3 minutes
43 seconds in queue. Published archive MD5/SHA256 and all eight unpacked mesh
members are verified against the existing shared copy. Native v2512/DP,
128 partitions, 65,334,765 cells, unchanged case dictionaries, initial field
checks and strict stage exits pass. Cell counts are 510427–510431; maximum
partition interface faces 131252. Batch memory is 30.3228 GiB, coarse CPUpercent
71 and cput155s. These are not memory bandwidth or off-node communication
measurements. Estimated base charge is 1.662222 SU, not separately posted billing.

Next use a separately frozen 128-rank job for all mandatory parallel
initialization and 40 solver steps, maximum 35 minutes. This job was serial
preparation only. No CPU solver score or improvement yet. Review reproduced
by python3 review.py; sealed data under collected/25905006.pbs101.
