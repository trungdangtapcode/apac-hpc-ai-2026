# Recovered historical CPU work

Discovered on 21 October in the account scratch tree. These files existed
before this session (directory timestamps October 9–10); no claim is made
about their original author, intended reasoning or terminal scheduler states.
All 500 selected text artifacts are sealed. Processor meshes, source archives,
runtime binaries, credentials and session state are excluded.

| Run directory | Logs | Solver steps | Official fixedIter | Observation |
|---|---:|---:|---|---|
| 1n-scotch-25738883 | 2 | 0 | False | Incomplete retained stage chain |
| 1n-scotch-25740167 | 3 | 0 | False | Incomplete retained stage chain |
| 1n-scotch-25740573 | 4 | 0 | False | Fatal error present |
| 1n-scotch-25740784 | 0 | 0 | False | Incomplete retained stage chain |
| 1n-scotch-25740797 | 6 | 0 | True | Solver log stops at native timing-function compilation |
| 2n-scotch-25738882 | 2 | 0 | False | Incomplete retained stage chain |
| 2n-scotch-25740168 | 3 | 0 | False | Incomplete retained stage chain |
| 2n-scotch-25740574 | 4 | 0 | False | Fatal error present |
| 4n-scotch-25738881 | 2 | 0 | False | Incomplete retained stage chain |
| 4n-scotch-25740169 | 2 | 0 | False | Incomplete retained stage chain |

None has an accepted solver End/Average; do not call these completed Basic
measurements or use their attempted walltimes as a score. Earlier templates
include a custom twoStageGaussSeidel smoother missing from native v2512 and
differ from official fixedIter, so reuse is forbidden for Basic. Later official
case 25740797 passes initialization but its retained solver log has zero
steps and stops at Ctoo for the mandatory timing function. The reason it
stopped is not established: no terminal scheduler status or compiler stderr
is retained. Do not label it a compiler bug, timeout or bad CPU from this alone.

The old common script accepts a native End even after nonzero return status.
New wrappers must preserve/check command return codes as well as log semantics.
A cheap native PitzDaily test of the unchanged official coded timing function
comes before a fresh full-case allocation. It tests compilation/runtime only;
toy math and timing are not contest measurements. Preserve all original cases
and use a fresh root and the recovered official text for future Basic work.
