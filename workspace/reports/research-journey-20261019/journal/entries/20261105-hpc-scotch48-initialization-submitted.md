# Scotch48 initialization accepted

Iris accepted **2294915** at `2026-11-05T08:28:58.038404Z` (UTC). The prerequisite cut 2294914 completed and passed independent mesh, exact 48-domain, full 65,334,765-cell, field and source review. The scientific question remains whether 48 ranks improve matched solver time versus 56; neither this job nor the cut measures that effect.

This frozen 44-file kit runs native `renumberMesh -constant -overwrite -parallel`, `potentialFoam -initialiseUBCs -parallel`, and `applyBoundaryLayer -ybl 0.0450244 -parallel`, in that order. It uses 48 MPI ranks on one exclusive 56-CPU Iris node, zero GPUs, default reported mapping, low QoS, maximum 20 minutes. A 48-rank startup probe and complete cut/source/field checks precede artifact writes. A READY marker is created only after all native stages, source/payload checks and field inventories pass; failure leaves a no-resume marker. No solver or speed score is produced.

The actual cut cost was 4.106667 allocated CPU-hours, conservatively 5. Its maximum reservation retired once, leaving 1,225 consumed. This new job reserves 18.666667 more within the unchanged 1,289 internal stage. Site billed SU is unknown; NSCC/AI accounting is separate. A fresh queue check preceded locked admission and the remote receipt. All 41 case-source files match the reviewed cut; root replayed local acceptance/rejection, syntax and 44 payload hashes before deployment. Artifacts and jobs are not overwritten.

Next: collect terminal accounting and native initialization evidence, independently review every stage and the initialized-source manifest, retire this maximum once, and prepare the bounded matched48-versus 56 solver comparison. No initialized-source or speed result is claimed before that review. No background Codex or automatic follow-up was enabled.

[Frozen kit and exact receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch48-init-20261105).
