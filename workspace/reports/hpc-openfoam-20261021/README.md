# OpenFOAM HPC task: what to do and where to start

The HPC task is a CPU simulation of air flowing around a car. The supplied
DrivAer case contains **65,334,765 mesh cells**. Each cell carries numerical
quantities such as velocity and pressure. OpenFOAM exchanges values across
cell boundaries and repeatedly solves the coupled equations. We must execute
the same numerical work faster, keeping the official geometry and settings.

The owner requested this research on 21 October and said another person
supports AI. This is now the active subject of this chat. No team HPC
measurement exists yet; all numerical results below belong to the organisers.

## What counts as a result

| Item | Requirement |
|---|---|
| Application | Official openfoam.com OpenFOAM v2512 |
| Solver | simpleFoam, a steady-state incompressible turbulent-flow solver |
| Dataset | Official coarse occDrivAerStaticMesh, unchanged |
| Hardware | Four CPU nodes on Gadi normalsr or NSCC ASPIRE-2A |
| Scaling evidence | Separate 1-node / 40-step, 2-node / 80-step, 4-node / 150-step runs |
| Performance quantity | Average wall-clock time per time step, in seconds/step; lower is better |
| Arithmetic | Double precision; GPU acceleration is prohibited in every tier |
| Numerical evidence | Cd from the last row of coefficient.dat, plus original logs |

A “time step” here is a solver iteration toward a steady solution, not one
second of physical driving. The performance number is the case timer's printed
Average from the second iteration onward. It is neither the whole job duration
nor simpleFoam's total process duration. The full preparation chain costs
allocation time even though it is outside that printed Average. [Task rules][rules]

Cd is the dimensionless drag coefficient: a physical output used to detect a
wrong computation. It is not the performance score. In Basic, the approximate
40/80/150-step reference values are a sanity check; there is no published
universal ±0.5% Basic gate. Different decompositions legitimately give different
intermediate Cd values. The stricter ±0.5% rule applies to the stated Bonus
self-proof against an appropriately matched pre-change baseline, with the
pure decomposition-method exception in F2. [Task addendum][rules]

Each task contributes at most 50 points: 20 Basic judging, 15 Bonus judging,
15 performance/re-verification. There is no published exact conversion formula
from seconds/step into those 15 points. Platforms are assessed separately.
[General scoring rules][general]

## The complete execution chain

```mermaid
flowchart LR
    A[Official mesh and case] --> B[decomposePar: split the cells]
    B --> C[restore0Dir: initial fields]
    C --> D[renumberMesh: improve ordering]
    D --> E[potentialFoam: initialize flow]
    E --> F[applyBoundaryLayer: required setup]
    F --> G[simpleFoam: solve on all MPI ranks]
    G --> H[Average seconds per step and Cd]
```

Every step must run, including potentialFoam and applyBoundaryLayer with the
exact required ybl value 0.0450244. Use fvSolution.fixedIter and
controlDict.noWrite, retaining their function objects. Solver tolerances,
iteration counts, schemes, physics and mesh cannot be reduced to get a faster
number. GPU techniques from Qwen do not apply. [Task rules][rules]

## What we can optimize first

An MPI rank is one cooperating process. **Decomposition** decides which mesh
cells each rank owns. A good split balances work and reduces expensive
communication between nodes. **Affinity** assigns ranks to particular CPU cores;
**NUMA locality** keeps their memory near those cores.

The most promising first investigation is decomposition plus rank placement:
compare the two Basic methods, hierarchical and scotch, then test the native
Scotch topology coefficients. After that, inspect whether fewer ranks per node
or different binding reduces memory/communication overhead. These are
hypotheses, not measured improvements. [Parallel decomposition documentation][parallel]

I independently parsed **21 public reference runs**. Their reported Average
agrees with every retained per-step sample, and the partition cell totals and
reciprocal interface counts pass consistency checks. The findings are in
[the reference analysis](../../../2026-APAC-HPC-AI/hpc-experiments/reference-analysis-20261021/RESULTS.md).

| Organiser four-node full-chain reference | Hierarchical (s/step) | Scotch (s/step) |
|---|---:|---:|
| Gadi: 416 ranks | 2.379600 | 2.126043 |
| ASPIRE-2A: 512 ranks, original defaults | 3.414517 | 3.575991 |

These are different machines and rank counts. Do not compare the rows as an
algorithmic speedup. On ASPIRE-2A, repeated Scotch runs span about 3.191–3.576
s/step with identical coefficient.dat files. A single apparent improvement can
therefore be misleading. The original defaults also show an MPI teardown
fault; later documented remedies exit cleanly. [Gadi notes][gadi], [ASPIRE notes][aspire]

The raw ASPIRE four-node split has nearly perfect cell-count balance for
hierarchical, but a maximum of **119,912 processor-interface faces per rank**.
Scotch allows about **1.072%** cell imbalance yet lowers that maximum to
**22,214**. Its maximum neighbor count rises from 20 to 66. This tradeoff is
why balanced cell counts or fewer total cut faces alone do not identify the
fastest decomposition. We still need actual rank-to-host mapping and MPI
profiling to identify expensive cross-node traffic.

## Save budget before increasing the experiment count

The organisers allow a small serial preparation job followed by a dependent
parallel job. decomposePar is serial; holding four full nodes idle during that
step wastes service units. Their Scotch 1/2/4-node sets cost about **217 SU on
Gadi** and **167 SU on ASPIRE-2A** with the split chain, compared with about
371/258 SU in the respective one-job examples. These are historical examples,
not a quote for our account or a guarantee of the same charge. Splitting saves
allocation cost; it does not by itself establish a solver speedup. [Gadi notes][gadi], [ASPIRE notes][aspire]

On Iris, practise the case, scripts and profiler first; Iris times are not
contest scores. Our ASPIRE-2A+ H100 access is a different service from CPU
ASPIRE-2A. Neither our old GPU balance nor its charging rate should be silently
reused as a CPU budget. [Iris notes][iris], [NSCC access guide][access]

## Current access and next work

The supplied SSH endpoint now accepts the provided private key after changing
its file permissions from 0644 to 0600. No private key bytes were read or copied.
It returns hostname instance-20210305-2210 and has no scheduler client or the
documented Iris kit at its expected path. Its relay inventory calls that local
machine iris, but this name alone does not prove access to Iris compute nodes.
The owner was asked for any next-hop instructions. Other users' Gadi aliases
were not used. Existing AI access/jobs remain unchanged.

The exact source case is now recovered and 12 Basic text preparations pass static checks; see [case recovery](CASE_RECOVERY.md). This is not a numerical run.

Read the [experiment plan](PLAN.md), [allowed-change table](RULES.md) and
[technical evidence](EVIDENCE.md). The first milestone is a valid full-chain
practice baseline; only then a small, evidence-driven contest-machine campaign.
No CPU job or budget reservation was made in this research turn.

[rules]: https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/2.%20OpenFOAM%20HPC%20Task%20Rules.md
[general]: https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/README.md#r4-scoring
[gadi]: https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/4.2%20OpenFOAM%20Application%20Notes%20-%20Gadi.md
[aspire]: https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/4.3%20OpenFOAM%20Application%20Notes%20-%20ASPIRE-2A.md
[iris]: https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/4.1%20OpenFOAM%20Application%20Notes%20-%20Iris.md
[parallel]: https://www.openfoam.com/documentation/user-guide/3-running-applications/3.2-running-applications-in-parallel
[access]: https://help.nscc.sg/aspire2a/faqs/
