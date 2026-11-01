================================================================================
TripleU — OpenFOAM HPC Task
APAC HPC-AI Student Competition 2026
NCI Gadi, queue: normalsr (Intel Xeon Platinum 8470Q Sapphire Rapids)
================================================================================

FINAL RESULT (4-node scored run)
---------------------------------
Job ID       : 182744256.gadi-pbs
Variant      : scotch_r416_numa
MPI ranks    : 416 (104/node x 4 nodes)
endTime      : 150
exit_status  : 0
wall_seconds : 980 (~16 min)
Service Units: 227.41 SU

Average wall-clock time per time step = 2.079045460013424 s
  (mean=2.0790, std=0.0154, min=2.0323, max=2.1286, n=149 steps)

Cd @ step 150 = 0.2919  (target: ~0.28-0.29) PASS
coefficient.dat: output/4node/scotch_r416_numa_182744256.gadi-pbs/coefficient.dat

================================================================================
SYSTEM INFORMATION
================================================================================
Cluster      : NCI Gadi
Queue        : normalsr
Node type    : Intel Xeon Platinum 8470Q (Sapphire Rapids)
CPUs/node    : 104 (2 sockets x 52 cores)
L3 cache     : ~105MB/socket
Memory/node  : 190GB
Interconnect : InfiniBand HDR (200 Gb/s, ~1us latency)
Filesystem   : Lustre (scratch)
OpenFOAM     : v2512 (site module: OpenFOAM/2512)
MPI          : OpenMPI 4.1.7

================================================================================
CASE DEFINITION
================================================================================
Case    : occDrivAerStaticMesh (official 65M cell coarse mesh)
Solver  : simpleFoam (steady-state incompressible RANS)
Physics : kOmegaSST turbulence model
Uinf    : 38.889 m/s
lRef    : 2.78618 m
Aref    : 2.17 m^2

fvSolution (fixedIter, unchanged):
  p solver : GAMG, GaussSeidel smoother, maxIter=12
  U/k/omega: smoothSolver, GaussSeidel, maxIter=15/8/8
  tolerance=0, relTol=0 (fixed iteration count, no early exit)

Preparation chain (per rules):
  decomposePar -constant
  restore0Dir -processor
  renumberMesh -constant -overwrite -parallel   [CuthillMcKee, default]
  potentialFoam -initialiseUBCs -parallel
  applyBoundaryLayer -ybl 0.0450244 -parallel
  simpleFoam -parallel -fileHandler collated

================================================================================
OPTIMIZATION METHODOLOGY
================================================================================

Phase 1: Baseline Establishment
--------------------------------
Observation: normalsr queue uses 104 CPU/node, but default job scripts
requested only ncpus=48 (half a node). This was identified as suboptimal.

Initial baseline (48 ranks, 1-node):
  Job 182732061 | 48 ranks | 18.98 s/step | Cd@40=0.4326 | 30.24 SU

Phase 2: MPI Rank Scaling Study (1-node)
-----------------------------------------
Hypothesis: Case is compute-bound (GAMG pressure solver dominates).
Increasing rank count reduces per-rank working set -> better L3 cache
utilization -> super-linear speedup possible.

Method: Systematic test of 3 rank counts on 1 node, all other variables fixed.

Results:
  Ranks | s/step | Speedup | Efficiency | SU
  48    | 18.981 | 1.00x   | 100%       | 30.24
  72    | 12.307 | 1.54x   |  90%       | 35.32
  104   |  8.482 | 2.24x   | 103%       | 45.30  <- sweet spot

Super-linear efficiency (103%) at 104 ranks explained by cache model:
  - 48 ranks: 65M/48 = 1.36M cells/rank -> working set >> L3 (105MB/socket)
    -> memory-bandwidth bound, high DRAM miss rate, high variability (CV=3.0%)
  - 104 ranks: 65M/104 = 628K cells/rank -> working set fits in L3
    -> compute-bound, stable timing (CV=0.47%), super-linear from cache effect

Amdahl fit: parallel fraction f ~= 0.997 (99.7% parallel)

Phase 3: Decomposition Method Study (1-node, 104 ranks)
---------------------------------------------------------
Hypothesis: hierarchical decomposition produces structured domains with
fewer halo faces -> less MPI communication -> faster than scotch.

Result: hierarchical (13x4x2) = 8.571 s/step vs scotch = 8.482 s/step
  -> hierarchical is 1.05% SLOWER than scotch.

Finding: For unstructured DrivAer mesh, scotch graph-partitioning
minimizes inter-processor faces AND achieves better load balance.
hierarchical produces axis-aligned boxes that are load-imbalanced for
complex car geometry (dense mesh near body, sparse far-field).
Load balance dominates over halo-face count for fixed-iteration RANS.

Phase 4: Multi-node Scaling Validation (2-node)
-------------------------------------------------
Purpose: Validate that 104 ranks/node efficiency holds across nodes
before committing to expensive 4-node run.

Results:
  Config        | Ranks | s/step | Nodes | Efficiency vs r104 1-node
  scotch r96    |    96 |  9.120 |     2 | (different rank count)
  scotch r208   |   208 |  4.213 |     2 | ~101% (vs ideal 2x of r104)

Cross-node scaling is excellent. Decision: proceed to 4-node with 416 ranks.

Phase 5: Runtime Optimization Study (1-node, 104 ranks)
---------------------------------------------------------
5a. NUMA Binding (--map-by socket --bind-to core)
  Baseline: 8.482 s (std=0.040)
  NUMA:     8.418 s (std=0.039)
  95% CI overlap -> NOT statistically significant on 1-node.
  Rationale for keeping: zero overhead, eliminates pathological placement
  risk on multi-node, ensures 52 ranks/socket = local NUMA memory access.

5b. UCX Transport (UCX_TLS=sm)
  Result: FAILED - "PML ucx cannot be selected" on Gadi OpenMPI 4.1.7
  Fix attempted: --mca btl self,vader (OpenMPI native shared memory)
  Conclusion: Default OpenMPI transport already optimal for intra-node.
  UCX flags not needed for 1-node. For multi-node, default auto-detection
  of InfiniBand is sufficient.

5c. masterCoarsest processorAgglomerator (Bonus tier)
  Theory: Concentrate GAMG coarsest level on 1 master rank to eliminate
  ~72 latency-dominated MPI_Allreduce/step (estimated 626us/step saving
  from Hockney-Jesshope model with IB HDR: alpha=1us, P=104).
  Result: 12.96 s/step vs baseline 8.42 s/step -> 54% SLOWER on 1-node.
  Explanation: On single node with shared memory, concentrating coarsest
  solve on 1 rank creates CPU bottleneck. masterCoarsest beneficial only
  when inter-node Allreduce cost exceeds single-rank compute cost.
  Decision: REJECTED. Risk of Cd drift + negative performance on 1-node.

5d. collated fileHandler (-fileHandler collated)
  Theory: 416 concurrent file writes to Lustre causes metadata contention.
  collated reduces I/O ranks -> less Lustre overhead.
  Decision: Added to final 4-node run (zero risk, potential benefit).
  Confirmed active: "I/O : collated [unthreaded]" in simpleFoam log.

Phase 6: Final 4-node Run
--------------------------
Configuration: scotch + 416 ranks + NUMA binding + collated I/O
Job: 182744256.gadi-pbs | 16:24 walltime | 227.41 SU

Result: 2.079 s/step (mean, n=149)
Scaling efficiency vs 1-node r104: 8.482/(4x2.079) = 102% (super-linear)

Cd sanity check:
  step  40: 0.4326  (target ~0.43) PASS
  step  80: ~0.34   (target ~0.34) PASS  [from 2-node run]
  step 150: 0.2919  (target ~0.28-0.29) PASS

================================================================================
COMPLETE RUN HISTORY
================================================================================

Job ID       | Variant              | Nodes | Ranks | s/step  | SU    | Status
-------------|----------------------|-------|-------|---------|-------|--------
182730681    | scotch               |     1 |    48 | -       | -     | INCOMPLETE (no finished_at)
182731157    | scotch               |     1 |    48 | 18.43   | 29.52 | FAILED (postprocessing error)
182731882    | scotch               |     1 |    48 | -       | 0.05  | FAILED (script path error)
182732061    | scotch               |     1 |    48 | 18.981  | 30.24 | OK - baseline
182732552    | scotch               |     2 |    96 |  9.120  | 62.29 | OK - 2node baseline
182733763    | scotch_r72           |     1 |    72 | 12.307  | 35.32 | OK - rank scaling
182733764    | scotch_r104          |     1 |   104 |  8.482  | 45.30 | OK - rank scaling
182735265    | scotch_r208          |     2 |   208 |  4.213  | 99.84 | OK - 2node scaling
182737425    | scotch_r104_numa     |     1 |   104 |  8.418  | 45.12 | OK - NUMA test
182737426    | scotch_r104_ucx      |     1 |   104 | -       | ~5    | FAILED (UCX/PMIx error)
182737427    | hierarchical_r104    |     1 |   104 |  8.571  | 40.56 | OK - decomp test
182738160    | scotch_r104_numa_ucx |     1 |   104 | -       | ~5    | FAILED (UCX/PMIx error)
182741960    | scotch_r104_numa_mc  |     1 |   104 | 12.957  | 55.18 | OK - masterCoarsest test
182744256    | scotch_r416_numa     |     4 |   416 |  2.079  |227.41 | OK - FINAL SCORED RUN

================================================================================
KEY FINDINGS SUMMARY
================================================================================

1. RANK COUNT IS THE DOMINANT OPTIMIZATION FACTOR
   48 -> 104 ranks/node: 2.24x speedup (103% efficiency)
   Root cause: L3 cache working set transition from memory-bound to
   compute-bound. Sapphire Rapids L3 (~105MB/socket) fits 628K cell
   subdomain at 104 ranks but not 1.36M cells at 48 ranks.

2. SUPER-LINEAR SCALING OBSERVED AT EVERY SCALE
   1-node 48->104:  103% efficiency
   2-node r208:     ~101% efficiency vs r104 ideal
   4-node r416:     102% efficiency vs r104 ideal
   Consistent cache-induced super-linear behavior across all scales.

3. SCOTCH > HIERARCHICAL FOR UNSTRUCTURED CFD MESH
   Hierarchical decomposition 1.05% slower due to load imbalance on
   complex geometry. Graph-based scotch partitioning better for DrivAer.

4. NUMA BINDING: ZERO-COST INSURANCE, NOT MEASURABLE GAIN ON 1-NODE
   95% CI overlap on 1-node (not statistically significant).
   Applied to 4-node as protective measure against pathological placement.

5. masterCoarsest INEFFECTIVE ON 1-NODE
   54% slower due to single-rank bottleneck on coarsest GAMG level.
   Beneficial only when inter-node Allreduce cost > single-rank compute.

6. PERFORMANCE VARIABILITY SOURCE
   High variability at r48 (CV=3.0%): memory-bandwidth bound,
   sensitive to DRAM contention and OS jitter.
   Low variability at r104 (CV=0.47%): compute-bound with L3 cache,
   stable and reproducible. 4-node r416 also stable (CV=0.74%).

================================================================================
SCALING TABLE (all valid runs)
================================================================================

Nodes | Ranks | s/step | Speedup vs r48-1node | Parallel Efficiency
------|-------|--------|----------------------|--------------------
    1 |    48 | 18.981 |                 1.0x |               100%
    1 |    72 | 12.307 |                 1.54x|                90%
    1 |   104 |  8.482 |                 2.24x|               103%
    2 |    96 |  9.120 |                 2.08x|                 -
    2 |   208 |  4.213 |                 4.51x|               101%*
    4 |   416 |  2.079 |                 9.13x|               102%*

* Efficiency calculated vs 1-node r104 scaled ideally

================================================================================
FILE STRUCTURE
================================================================================

run/
  1node.sbatch                  # original baseline (48 ranks)
  1node_r72.sbatch              # rank scaling test
  1node_r104.sbatch             # rank scaling test
  1node_r104_numa.sbatch        # NUMA binding test
  1node_hierarchical_r104.sbatch# decomposition test
  1node_r104_numa_mc.sbatch     # masterCoarsest Bonus test
  2node.sbatch                  # 2-node baseline (96 ranks)
  2node_r208.sbatch             # 2-node full-node (208 ranks)
  4node_r416_numa.sbatch        # FINAL 4-node scored run
  run_official_case.sh          # main run script (all variants)
  variants/
    scotch.conf                 # baseline scotch
    scotch_r72.conf             # 72 ranks
    scotch_r104.conf            # 104 ranks (not used, PBS_NCPUS auto)
    scotch_r104_numa.conf       # NUMA binding
    hierarchical_r104.conf      # hierarchical (13x4x2)
    scotch_r104_numa_mc.conf    # masterCoarsest Bonus
    scotch_r416_numa.conf       # FINAL: scotch+NUMA+collated

output/
  1node/  2node/  4node/        # job output directories
  <variant>_<jobid>.gadi-pbs/
    10_decomposePar.log
    15_restore0Dir.log
    20_renumberMesh.log
    30_potentialFoam.log
    40_applyBoundaryLayer.log
    50_simpleFoam.log
    caseDefinition
    decomposeParDict
    controlDict
    coefficient.dat
    summary.log
    job.out / job.err
    started_at.txt / finished_at.txt

================================================================================
REFERENCES
================================================================================
- APAC HPC-AI 2026 Task Rules: github.com/hpcac/2026-APAC-HPC-AI
- OpenFOAM v2512: openfoam.com
- OHC-1 reference results: Zenodo record 15012221
- NCI Gadi normalsr queue: 104 CPUs/node, Intel SPR, IB HDR
- methology.md: detailed cache model and Hockney-Jesshope MPI analysis

================================================================================
