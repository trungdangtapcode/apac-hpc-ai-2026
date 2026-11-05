# Scotch48 native initialization passes

Job **2294915 COMPLETED 0:0** on iris001 in **111 seconds**, 56 allocated CPUs. Independent replay verifies all 26 collected artifacts, all 44 payload checks before/after, 41 source inputs before/after, 288 initialized field records, the complete 48-rank startup probe, and all three required native stages: renumberMesh, potentialFoam, applyBoundaryLayer. Each stage reports v2512/scalar64/nProcs48/End without fatal markers. READY is present; 48 initialized field hashes change as expected. No solver was run and no seconds-per-step result is established.

The initialized source is sealed separately: 896 core file hashes, 13 ancillary hashes, exact directories and one allowed serial-mesh symlink. These pins are evidence for a later clone/source check, not a copy of all large source bytes in Git. GNU time process peak RSS is 1,302,612 /2,442,748 /1,371,628 KiB for the three stages; it is not aggregate MPI resident memory or bandwidth. Hardware counters were not collected.

Actual allocated cost is **1.726667 CPU-hours**, conservatively 2. Retire the 18.666667 maximum once: 1,227 consumed /zero reserved under the unchanged 1,289 internal stage. Site-billed SU is unknown.

The next distinct rank-density trial uses **40 steps for every arm**, comparing 48 and 56 in one ABBA allocation. Both physical inputs and work are fixed, but decomposition-specific intermediate Cd can differ under Basic; retain those differences and same-treatment repeat checks. This is not a re-run of the rejected graph mapping.
