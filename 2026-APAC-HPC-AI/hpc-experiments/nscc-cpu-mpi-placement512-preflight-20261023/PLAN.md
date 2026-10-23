# Conditional 512-rank MPI placement preflight

## Question and retained graph evidence

The fixed-host refined graph assignment is available at [the offline NUMA screen](../rank-placement-512-numa-screen-20261023/screen.json). It preserves the parent's four logical host groups and its 512-rank partition. The original contiguous host control has 337,324 cross-host face entries. The parent graph mapping has 261,110, and the refined candidate keeps that same cross-host count while reducing the parent's same-host cross-NUMA proxy from 1,097,554 to 732,712. The refined candidate still has 732,712 same-host cross-NUMA faces versus 710,081 in the original contiguous control, 3.19% more. Root independently verified the graph/hash lineage and arithmetic. These face counts are proxies, not bytes, traffic, NUMA page locality, runtime or speedup.

The refined assignment uses four logical host groups of 128 ranks and eight logical NUMA groups of 16 ranks within each host. The actual target nodes' NUMA topology is not known yet. Those eight groups are a hypothesis to verify on the allocated nodes, not physical-domain labels.

## Hypothesis and paired control

The documented method-3 custom order file can realize the refined fixed-host/fixed-NUMA logical grouping on the actual four-node PALS allocation when candidate ranks are rendered against the observed identity control slots. Both arms use the same compiled probe, four-node allocation, MPICH settings, PALS command, CPU binding, and thread environment. Only the rank-order file differs:

- Control: identity sequence `0,1,...,511`.
- Candidate: refined group members placed into observed host/NUMA slots, rendered in original identity slot order.

The renderer first requires the identity arm to show four hosts with 128 distinct physical cores each and exactly eight actual NUMA domains with 16 ranks on each host/domain. If these counts do not match, it aborts before the candidate run; any changed topology requires a new mapping screen. Host group zero is anchored to the physical host observed for identity rank zero. On that host, logical NUMA group zero is anchored to identity rank zero's NUMA domain. The remaining host and domain labels are deterministic. The selected 16-rank group members are assigned to the observed identity slots for each mapped host/domain; no group-major list is assumed to reflect physical slot order. Candidate entry zero remains MPI rank zero.

Every process reports its actual `MPI_COMM_WORLD` rank, world size, MPI processor name, CPU affinity mask, and package/core/NUMA values read locally from that host's sysfs. The expected candidate mapping records the identity slot and intended host/core/NUMA for every candidate rank. The final validator compares each actual rank to that intended slot. `PMI_RANK` is recorded but never used as a substitute for MPI world rank.

## Resource and execution gates

The PBS script requests the normal queue, CPU project 59000042, four exclusive 128-core nodes with 128 ranks per node, 32 GB per node, no GPU, and a three-minute wall limit. The memory request is runtime headroom, not a measured RSS requirement. Its internal deadline is 135 seconds. It compiles on the allocated node with the loaded OpenFOAM 2512/Cray MPICH environment, verifies linked MPICH 8.1.15, captures PALS/module/compiler/runtime evidence, and source-hashes the fixed payload before and after execution. Both arms set `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and `FI_OFI_RXM_USE_SRX=0`; other FI variables remain at module/site defaults and are recorded through an allowlisted capture.

The child job is conditional on `afterok` for both `25940700` and `25943865`. Root handles live queue and budget checks, the active-job cap, conservative 25.6-SU reservation, and qsub under its lock. This preparation performs none of those actions. The nominal four-node/three-minute request is at most 25.6 SU under the recorded core-hour conversion; that is a reservation ceiling, not posted cost.

## Interpretation and limits

A pass establishes only that the method-3 512-rank mapping and observed physical topology match the rendered candidate on this specific allocation. It does not establish OpenFOAM initialization, decomposition or solver behavior, page placement, runtime rank migration, communication volume, a speedup, or a contest score. A future solver test requires separate queue/budget review, exact mandatory-stage integration, retained input and field seals, complete timing/output checks, and final PBS accounting. A failed preflight is preserved and closes this attempt; it is not retried automatically.

See the [runtime gates for any later full-size study](../rank-placement-512-numa-screen-20261023/RUNTIME_GATES.md). The baseline and refinement hashes plus compact rank-group membership are embedded in `payload/assignment.json`; the 512-member source graph is not copied.
