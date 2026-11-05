# Iris Scotch 48-domain cut plan

## Prior evidence

The reviewed Iris Scotch56 cut established the existing workflow: verify all
eight full serial-mesh members against the retained official archive, verify
41 pinned case-source files, run native serial `decomposePar`, restore the six
initial fields, and validate the exact processor tree and 65,334,765 cells.
That prior cut is a workflow reference, not evidence for 48-domain performance.

## Hypothesis and controlled change

A 48-domain Scotch partition has 16.7% more average cells per domain than a
56-domain partition (about 1.361M vs 1.167M). Fewer domains may reduce
communication, while higher per-domain work and partition differences may
increase runtime or imbalance. This diagnostic only produces and validates the
48-domain cut. The only pinned case-source change is `nCores: 512 -> 48`, which
sets `numberOfSubdomains $nCores`; Scotch, mesh, fields, numerical dictionaries,
and native environment stay as in the reviewed recipe.

## Resource envelope and gates

One exclusive Iris node, 56 CPUs, one serial task, zero GPUs, low QoS, maximum
40 minutes (37.333 allocated CPU-hours). `decomposePar` has a 30-minute cap.
The job refuses an existing unique N48 artifact path, checks the complete mesh
identity and source pins, and retains logs. Acceptance requires exactly 48
non-symlink processor directories, all six zero-time fields per directory,
native v2512/scalar64/End with no fatal errors, 48 native domain cell counts,
and their sum exactly 65,334,765.

## Decision after the cut

Even a passing cut is not READY. Review the artifact and evidence, separately
run the required renumberMesh, potentialFoam, and applyBoundaryLayer stages,
then compare matched 48-domain and 56-domain controls using the same initialized
case and solver horizon. No solver job, score, or speedup follows automatically.
