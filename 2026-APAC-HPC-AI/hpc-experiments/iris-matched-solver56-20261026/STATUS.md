# Iris matched pair submitted and running

**2294047** was submitted with a definite receipt and was RUNNING on iris009 at 26 October 08:57:50 UTC. It runs hierarchical then Scotch, 150 time steps each, in one exclusive 56-CPU allocation. Maximum 2 hours 30 minutes / 140 allocated CPU-hours reserved under the Iris branch envelope. No Iris SU rate is inferred.

Both 41-pin source checks passed. The H arm's 1,040 regular inputs and canonical serial-mesh symlink passed full copy/hash/inode validation, and the startup probe verified exactly 56 ranks. H solver measurement has started; the S arm is pending within the same job. No complete pair or improvement exists yet.

See PLAN.md, ROOT_REVIEW.json, submission-receipt.json and live-status.json. Preserve the queue position and original initialized sources. A single H-then-S pair cannot separate ordering and thermal effects.
