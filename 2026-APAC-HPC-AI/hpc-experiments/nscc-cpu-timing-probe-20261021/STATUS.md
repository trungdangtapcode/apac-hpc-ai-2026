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
