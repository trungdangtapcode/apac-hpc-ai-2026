# Iris Scotch rank-density comparison

The owner asked why the selected 21.0512 s/step observation used only 14 steps.
That was a **different graph-placement experiment at 56 ranks**; its complete
reverse comparison lost 5.3685%, so that unchanged branch was closed. It was
never a Scotch48 trial or a matched winner against the organizer/teammate.
This new, distinct rank-density experiment uses 40 steps in every arm.

The arms are 56-rank Scotch, 48-rank Scotch, 48-rank Scotch, 56-rank Scotch.
All use the accepted, initialized sources, same original physics and native
OpenFOAM v2512 double-precision runtime, one exclusive 56-CPU Iris node, the
same `endTime=40`, fixed-iteration settings, default uncollated file handler,
and default Open MPI mapping. Only rank count and the required Scotch
partition differ. Every arm must finish 40 steps and yield all 39 timed
intervals.

The job requests 56 CPUs, zero GPUs, low QoS, and at most 2.5 hours (140
allocated CPU-hours). Each solver arm is capped at 1,800 seconds and each
isolated copy/hash/rank-probe preparation at 150 seconds. The internal deadline
reserves time for both post-run source checks and final review. If a complete
arm no longer fits, the runner stops before starting it; truncated arms do not
produce a complete comparison.

For each rank count, the payload verifies the accepted tree and supplementary
hashes, the 41 pinned inputs, the initialized zero-time fields, and the source
before and after all arms. Clones must not reuse source inodes. Native checks
require the exact rank count, OpenFOAM 2512/scalar64, default uncollated I/O,
steps 1–40, 39 finite positive timings, the full finite force-coefficient
series, fixed linear-solver iteration counts, and normal completion. Same-rank
ABBA repeats use the existing `math.isclose(rel_tol=1e-9, abs_tol=1e-10)` force
repeat check. Cross-partition force drift is reported without an invented
Basic tolerance because different decompositions can change intermediate Cd.

Open MPI `--display-map` and `--report-bindings` are retained for a matching
rank probe and each solver launch. The small Python probe records pre-MPI_Init
OS affinity masks; it must observe every rank exactly once on one host, and
masks must be nonempty and nonoverlapping. This does not establish post-MPI or
solver-thread affinity. No per-socket mapping is assumed; unequal socket rank
counts are possible. The logs provide evidence for later placement review.

This is a native CPU experiment, not a contest score or cross-platform claim.
The 48-domain rank-density hypothesis is that fewer domains may reduce
communication while increasing work per rank; this comparison does not assume
either effect wins. Whole-node samples remain diagnostic and are not
process-attributed bandwidth evidence.
