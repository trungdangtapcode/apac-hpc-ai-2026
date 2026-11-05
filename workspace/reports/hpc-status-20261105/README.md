# HPC checkpoint and next rank-density question

At 14:29 on 5 November 2026 (Vietnam time), the authenticated Iris login returned an empty shared-user queue. Jobs 2294800 and 2294805 remain COMPLETED; 2294803 remains FAILED. There is no new valid faster solver measurement. The read-only NSCC path check at 14:30 returned NAMESPACE_UNAVAILABLE; SSH authentication was not tested and no MFA prompt was initiated.

The previous preparation-only claim did not reproduce, solver-rank interleave timed out, and forced tuned tiny-Allreduce was slower. Those unchanged candidates stay closed. The next distinct question is whether 48 MPI ranks can improve on 56 with the same 65,334,765-cell physical problem. Fewer ranks increase cells per rank and may reduce some halo/MPI overhead; neither effect establishes the bottleneck or predicts a win.

The first necessary stage is a fresh Scotch48 decomposition and restored fields. It must preserve the official serial mesh and case inputs, audit exactly 48 processor directories and the full cell count, and keep all logs. A cut is not an initialized READY case or a solver result. Parallel initialization and a reviewed same-allocation 48/56 comparison remain later separate gates. No blind 56-rank solver repeat is warranted while that source is absent.

The bounded cut request is at most 40 minutes on one exclusive 56-CPU Iris node, zero GPUs: 37.333333 allocated CPU-hours maximum. It fits 1,220 consumed plus this maximum within the unchanged 1,289 internal stage. Site-billed SU is unknown. NSCC/AI accounting is separate. Definite admission belongs in the submission receipt; preparation alone is not a submission.
