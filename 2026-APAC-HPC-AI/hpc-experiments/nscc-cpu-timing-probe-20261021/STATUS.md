# First ASPIRE-2A CPU submission

25904725.pbs101 was accepted at 2026-10-21T13:53:14.713064+00:00 under CPU
project 59000042. The separate CPU budget lock covered project/own-queue
checks, the read-only AI queue count, maximum reservation and the single qsub.
Eight CPUs/four MPI/24 GB/zero GPU, maximum ten minutes, maximum 1.333333 SU.
The live project report is cached and dated; no AI ledger or payload changed.
Payload hashes match the deployment and the pre-submit intent is retained.

The first qstat collection says the job has already finished and requires -x
for historical status. This proves CPU submission acceptance, not a pass.
Terminal log/accounting collection is in progress. Next review the actual
native compilation, return codes, five solver steps and timing function before
spending on full DrivAer. No CPU Basic result or performance score yet.

## Terminal review: environment setup failed before solver

25904725.pbs101 is F/exit 1 after 2 seconds, 8 CPUs, zero GPUs. Five safe text
artifacts are sealed; submitted source hash matches. There is no solver run,
compiled timing library or valid diagnostic score. The batch output stops
immediately after module purge. Inspecting the actual /app/apps/resetmodule
shows loadedmods=$(module list | grep -vi Modulefiles): with pipefail and
strict errexit, grep's expected empty result aborts the sourced reset script
before loading default programming modules. This is a wrapper/environment
failure, not an OpenFOAM mathematical or compilation failure.

Derive a new payload that sources resetmodule in an if condition and checks
its result plus the required loaded module/runtime. Preserve this submitted
version. Estimated base charge from 8 CPU * 2 s is 0.004444 SU; posted billing
is not individually reconciled and the original 1.333333-SU maximum remains
conservatively retained. Accounting's tiny memory/CPU counters are startup
samples, not proof of low solver memory or zero CPU activity.
