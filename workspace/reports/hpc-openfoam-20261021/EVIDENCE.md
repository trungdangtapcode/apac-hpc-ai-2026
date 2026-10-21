# Technical evidence and limits

## Source identity

The official contest repository main resolved on 21 October to
b4df52907f5bbb9152ef6ae902c925fc79d54417. The selected snapshot contains 177
public files totalling 8,663,586 bytes: rules, three application notes, selected
raw baseline/repeat/transport-remedy logs and dictionaries. Each download's
Git blob SHA1 matches the pinned tree; SHA256 and URLs are retained separately.
No pull/reset changed the existing research checkout. These are published
organiser measurements and are never presented as our jobs.

[Source manifest](../../../2026-APAC-HPC-AI/hpc-experiments/upstream-20261021/manifest.json)

The official source tag OpenFOAM-v2512 resolves through git ls-remote to
87ed40d256d22ea38fcc648dfc82a22162427b18, matching the public module log's
87ed40d256 build prefix. The pinned scotchDecomp.C and metisLikeDecomp.C are
retained with their GPL notice and COPYING. An initially guessed parent path
returned 404; the actual decompositionMethods/metisLikeDecomp path succeeds.
The source manifest preserves both observations. No OpenFOAM code is modified.

[Native source manifest](../../../2026-APAC-HPC-AI/hpc-experiments/source-review-20261021/manifest.json)

The original committee case URLs failed through the web tool. Attempts at a
GitLab relocated committee namespace redirect to a sign-in page. The full case,
Allrun, fvSchemes and fvSolution.fixedIter have therefore not been independently
retrieved in this turn. The public reference dictionaries are not a substitute
for that missing complete case. Recover the official kit on the actual practice
machine or a working official case endpoint before preparing runs.

## What the raw analysis actually verifies

The Python standard-library parser recomputes 21 retained solver runs. It checks
contiguous iterations 1..endTime, all timing samples, measured count=endTime-1,
printed Average against the sample mean, an End marker, native scalar64,
coefficient.dat column names and row/end-time completeness. For each available
decomposition, it verifies 65,334,765 total cells, every rank, reciprocal neighbor
interfaces and the total number of unique faces. No computation is run.

[Analysis code](../../../2026-APAC-HPC-AI/hpc-experiments/tools/analyze_reference.py),
[results](../../../2026-APAC-HPC-AI/hpc-experiments/reference-analysis-20261021/RESULTS.md),
[structured output](../../../2026-APAC-HPC-AI/hpc-experiments/reference-analysis-20261021/reference-results.json),
[validation](../../../2026-APAC-HPC-AI/hpc-experiments/reference-analysis-20261021/validation.json).

An initial parser draft matched the ordinary “Floating point exception trapping
enabled” startup message too broadly. It was corrected before accepting the
analysis: actual fatal markers are distinguished from enabled exception
trapping, and all retained reference logs must have no unexpected fatal marker.
Signal 7 after End is a separate field, not quietly removed. The public default
ASPIRE solver can have valid written artifacts plus an MPI teardown failure;
it is not relabelled a clean end-to-end team result.

The samples identify cell and interface imbalance. They do not provide our
rank-to-core/NUMA map, off-node byte rates, cache misses, memory bandwidth,
energy or critical-path MPI fractions. Those are uncollected, not zero. There
is no causal bottleneck claim based solely on the interface counts.

## Why node-aware Scotch is the first distinct hypothesis

Native scotchDecomp.C reads processorWeights first. If that branch is absent,
it reads domains/domainWeights and constructs SCOTCH_archTleaf; the final
mapping is SCOTCH_graphMap. The native coefficient reader chooses a method's
Coeffs dictionary. Thus it is possible to retain method scotch and express a
node/core hierarchy through its coefficients, rather than changing to the
separate method multiLevel. F1 explicitly permits scotchCoeffs.

For a verified four-node full-rank Gadi deployment, proposed domains are
(4 104); for CPU ASPIRE-2A they are (4 128). Candidate weights (1 0.01) encode
that intra-node links should be cheaper. This does not measure the actual
cost ratio or enforce physical placement. The planned test must verify that
rank IDs and CPU binding match the tree, confirm coefficient parsing in the
site v2512 build, measure partition/communication effects, and compare fresh
same-platform solver runs. There is no predicted percentage speedup.

Source: [pinned v2512 Scotch implementation](https://gitlab.com/openfoam/core/openfoam/-/raw/87ed40d256d22ea38fcc648dfc82a22162427b18/src/parallel/decompose/scotchDecomp/scotchDecomp.C).
The official [parallel-operation release note](https://www.openfoam.com/news/main-news/openfoam-v2306/parallel)
also describes native scotch domains/domainWeights; its retrieved search
excerpt is supporting historical context, not proof of the deployed version.
A direct web fetch of that release page returned 403 on this turn.

## Access and cost are separate facts

The existing SSH helper reaches ASPIRE-2A+, a2ap-login01, PBS pbs111. At the
read-only query it lists no openfoam/2512 match, no simpleFoam executable, and
no readable CPU-reference mesh at the documented path. The published account
ledger still describes the AI2A+ allocation. This does not prove whether the
same identity is enrolled on CPU ASPIRE-2A, and is not permission to spend a
separate CPU allocation.

The owner then supplied a private-key path and an SSH endpoint for
rdmaworkshop30. The first attempt failed because the key was 0644; chmod 600
allowed authentication. Key contents, authentication caches and known-host
files are not copied into research or Git. The endpoint hostname is
instance-20210305-2210, with no scheduler client and no official Iris kit at its
documented location. Its local hpc-relay identifies itself as iris; routing a
command to that self alias does not reach a separate scheduler. Other account
entries are not used. A next-hop clarification is pending.

[Sanitised access facts](../../../2026-APAC-HPC-AI/hpc-experiments/access-20261021/).
No HPC job, large mesh download, installation or budget reservation has occurred.

## Next evidence to obtain

First identify the genuine practice/contest account and complete case. Then
record a successful full chain, hashes of invariant inputs, native build/MPI
identity, mapped resources, returned exit codes, full endpoint Cd, Average and
actual billed cost. Finalists need repeated four-node runs and separate 1/2/4
scaling. Keep hardware/profiler observations distinct from the contest timer.
All candidate configurations in this research tree are unsubmitted plans.
