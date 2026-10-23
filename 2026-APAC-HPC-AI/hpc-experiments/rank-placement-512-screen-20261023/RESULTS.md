# Four-node logical rank-group screen

## Result

The retained 512-way Scotch processor graph admits a balanced four-group mapping with **261,110 unique interface faces crossing logical groups**, compared with **337,324** for the declared contiguous control `rank // 128`. This is a reduction of **76,214 faces (22.59%)** in the graph-cut proxy, or **2.604% of all 2,927,022 unique interface faces**. The candidate contains exactly 128 rank IDs per group, keeps rank 0 first in the rendered group-major permutation, and leaves the processor decomposition and all processor directories unchanged.

This result identifies a candidate mapping for independent review. It does not predict solver speedup. The graph groups are hypothetical logical hosts; the historical rank-to-host map was not retained, and no rank-reordering payload or MPI run was created.

## Graph provenance and checks

The graph uses 512 existing ASCII `boundary` dictionaries collected from native job **25921488.pbs101**, plus its `10_decomposePar.log`. The intake manifest reports **7,014,012 bytes** across the retained intake. Every boundary file strictly decodes as ASCII, remained the same size and modification time during the local read, and matches the collection SHA256. Although the dictionaries say `format binary`, the bytes are ASCII text with no NUL bytes; that header did not cause rejection. The native decomposition log matches the earlier sealed log byte for byte. The validated graph file SHA256 is `3ba8612bf5e0521f2cfb39fdd4c9d0642f689c6e5a86a9bb93accad212b7a209`.

Validation found **2,887 unique undirected processor edges** and **2,927,022 unique interface faces**. All 512 rank IDs occur exactly once. Each processor patch has a single reciprocal patch with the same `nFaces`; duplicate neighbors and edges are rejected. The extracted neighbor-face rows and processor-face subtotals match the native decomposition log for every rank. The native log reports **65,334,765 cells** in total, from 126,323 to 128,975 cells per rank. Details, per-member hashes and the full weighted edge list are in [graph-validation.json](graph-validation.json) and [graph.json](graph.json).

## Group interface summaries

The matrices below count each undirected edge once in the upper triangle. Diagonal entries are within-group faces; entry `(i, j)` for `i < j` is the number of unique faces between those two logical groups. The lower triangle is zero by convention.

| Control group | G0 | G1 | G2 | G3 |
|---|---:|---:|---:|---:|
| G0 | 756,926 | 140,232 | 8,750 | 41,762 |
| G1 | 0 | 650,539 | 59,793 | 14,135 |
| G2 | 0 | 0 | 608,004 | 72,652 |
| G3 | 0 | 0 | 0 | 574,229 |

| Candidate group | G0 | G1 | G2 | G3 |
|---|---:|---:|---:|---:|
| G0 | 876,071 | 33,841 | 53,690 | 52,580 |
| G1 | 0 | 633,016 | 44,732 | 34,633 |
| G2 | 0 | 0 | 521,419 | 41,634 |
| G3 | 0 | 0 | 0 | 635,406 |

The cut affects **11.524%** of all unique faces in the control and **8.921%** in the candidate. Summing the external faces incident to each logical group counts cross-group edges at both endpoints. Those per-group totals are **190,744; 214,160; 141,195; 128,549** for the control and **140,111; 113,206; 140,056; 128,847** for the candidate. The maximum logical-group total falls from **214,160** to **140,111** faces. This is a graph-derived per-group proxy; it is not measured per-node network load.

The boundary dictionaries were not sealed at the original submission. Agreement with the retained native log strengthens provenance, but does not establish complete mesh identity, frozen submission identity, or historical rank placement. The graph is consequently limited to the retained artifacts described here.

## Search and balance

The deterministic search used seed **2026**, up to **1,500,000** balanced cross-group swap proposals, then a deterministic best-improvement swap scan from both the contiguous baseline and the annealing best. It completed 1,500,000 proposals in **5.68 seconds** of annealing and **9.10 seconds** total local elapsed time, below the 30-second limit. The baseline-anchored scan reached a single-swap local minimum of 294,358 faces. The annealing mapping reached 261,110 faces; the full deterministic scan found no further improving single balanced swap from that candidate. This is a local result, not a global optimum claim. [screen.json](screen.json) retains the full 512-rank group assignment, full permutation, accepted-improvement trail, search parameters, and 128 random swap-delta checks; every incremental delta matched a full graph recomputation.

The native cell counts allow a simple hypothetical group-balance check. The control group totals are **16,354,229; 16,339,979; 16,321,436; and 16,319,121 cells**, a range of 35,108 cells (0.215% of the mean). The candidate totals are **16,393,858; 16,327,121; 16,279,147; and 16,334,639 cells**, a range of 114,711 (0.702% of the mean). Both retain equal rank counts. These totals assign existing rank cell counts to proposed groups; no cells moved and no runtime load balance was measured.

## Interpretation limits and next decision

Interface-face count is a graph-cut proxy. It does not measure bytes transferred, message sizes, MPI wait, network topology, solver critical path, memory locality, or elapsed solver time. The installed Cray MPICH 8.1.15 and PALS 1.1.6 documentation review supports a small four-rank MPI rank-reordering interface probe as the next low-cost compatibility check. That probe should verify MPI world-rank to host behavior before any larger runtime test; it does not establish a solver gain. A future solver test still requires actual rank-to-host/core validation, an identity control, unchanged numerical work, and current queue and budget checks. This offline screen performed no SSH, MPI, solver, scheduler, or budget operation.
