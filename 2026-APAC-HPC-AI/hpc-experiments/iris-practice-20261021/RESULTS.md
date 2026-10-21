# First Iris toy gate submitted

The exact organiser script hash matches the retained kit. Slurm returned job
2293751 at 2026-10-21T11:26:30.902750+00:00. A subsequent own-job query confirms
RUNNING on iris031 at 30 seconds, 56 allocated CPUs, one node. The request uses
four MPI ranks and maximum five minutes. The scheduler allocates the whole
node despite four ranks. This establishes successful submission and compute
allocation, not the completed toy gate or a 65M result.

Preserve submitted source and receipt. Inspect scheduler terminal status,
module/ELF output, all ten toy stage logs, both split identities and solver End
markers. Missing performance Average is allowed in this toy's protocol; do not
invent the 65M score from its ClockTime. No GPU or national-supercomputer project
is used. Keep actual terminal outcome separate from the receipt.

## Terminal review — 2026-10-21T11:30:34.133595+00:00

2293751 completes with exit 0:0 in 30 seconds, 56 CPUs allocated on iris031.
Both hierarchical and scotch run four native v2512 MPI ranks for 10 toy steps.
All ten stage logs are retained; the four native-utility logs per method have
End and no fatal/signal marker, restore0Dir output is retained, SPLIT identity
matches each method, and the script prints PASS. Native scalar64 and all
sealed hashes pass. Both runs warn that ten steps are insufficient for the
timer's requested statistical confidence; retain this limitation. Toy Average
is diagnostic only, not the 65M score. No CPU utilization/NUMA/network/power
series was collected. Actual billed SU is not reported or inferred from the
allocated core-seconds. No GPU or national project was involved.

The next research decision is to inspect the 65M script chain and inputs on
this actual site before a bounded full-case practice run. The toy's missing
applyBoundaryLayer is intentional for its separate motorBike setup; it cannot
waive that mandatory step for DrivAer. There is no scored 65M or Cd result yet.
