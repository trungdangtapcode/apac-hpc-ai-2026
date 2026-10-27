# Native NSCC three-arm measurement bundle

This is an unsubmitted, fresh-source bundle for one exclusive four-node NSCC allocation. The frozen `payload/sequence.json` selects `S0,Hxyz,Hzyx`. A later reversed allocation must use a separately reviewed derivative with a new frozen sequence; an unrecorded submission-environment override cannot change this payload. The sequence validator accepts exactly these three distinct arms in any order.

| Arm | Method | Hierarchy factors | Order |
|---|---|---|---|
| S0 | Scotch | Not used | Not used |
| Hxyz | Hierarchical | (16 8 4) | xyz |
| Hzyx | Hierarchical | (16 8 4) | zyx |

Each arm gets an independent writable case copy and runs the complete required chain: `decomposePar -constant`, `restore0Dir -processor`, `renumberMesh`, `potentialFoam -initialiseUBCs`, `applyBoundaryLayer -ybl 0.0450244`, then `simpleFoam` for the frozen `endTime 150`. Each arm has its own decomposition and initialized state; no processor tree is reused. The official shared mesh is reused only after the archived eight-member identity check. Field seals are recorded after restore, before solve, and after solve.

The case derivation checker compares every case file against the frozen control template. The S0 case must be byte-identical. Hxyz may change only `decompositionMethod` and `nHierarchical` in `system/include/caseDefinition`; Hzyx may make those same changes and change `order` in `system/decomposeParDict`. The unchanged source template already carries the accepted 512-core and 150-step derivation from the original 128-core, 40-step source. No physical or numerical input is edited here.

The PBS request is 90 minutes, 512 CPUs, at most 768 SU. A 5100-second wrapper deadline reserves five minutes for cleanup inside the 5400-second PBS limit. This is a request ceiling, not a prediction or posted charge. Processing and solves are each bounded by remaining time. Full solves are never shortened to force a completion. Stop status, command return codes, resource records, phase markers, rank host counts, nodefile, an explicit safe environment allowlist, before/after executable and linked-library hashes, source validations, solver outputs and field seals are kept under the job run directory. The safe allowlist includes relevant FI, MPICH, PALS and UCX controls while excluding authentication-like environment names. Compare inherited MPI settings with the retained control before claiming exact runtime parity. The optional prelaunch CPU/mask snapshot is a PBS-dispatched diagnostic and can fail without blocking the solver; it establishes no OpenFOAM rank or helper-thread affinity.

The fixed-work solver validator inherited from the accepted source requires 150 ordered iterations and 149 positive timing rows (Times 2 through 150), as well as the original native solver and force-output gates. A wrapper success marker alone is not a result. Review terminal PBS state, exit status, logs, each arm's validator output, timing distribution, force coefficients, runtime errors and available resource evidence before interpreting a measurement. Offline preparation checks do not prove NSCC runtime behavior or a performance result.

The existing 3.364622070 seconds/step observation is a reference, not an acceptance guarantee. S0 is a fresh reproduction control; the hierarchy arms are distinct Basic candidates. Preserve all outcomes, including incomplete or slower arms. This bundle does not submit itself, alter a budget, or assert a measured win.

## Offline checks

From this directory, use `payload/verify-inputs.py bundle --root .` after regenerating `payload-sha256.json` from payload files. Shell/Python syntax and source-derivation checks are performed before submission. Runtime qualification requires a real accepted NSCC allocation and is not established offline.
