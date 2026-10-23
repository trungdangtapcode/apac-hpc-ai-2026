# Nonlogin repair submitted as 224157

**224157.pbs111** was accepted at **2026-10-23T15:49:28.547700+00:00**, immediate state **R** on **a2ap-dgx037 / a2ap-dgx039**, one H100 per node, ten-minute maximum. The native byte and exit gates are unchanged. Only launcher environment setup is repaired: ordinary Bash at parent/node boundaries and explicit required-module bootstrap. No user profile was edited. A runtime pass is not claimed at submission.

The source, actual remote CPU reproduction and frozen repair were pushed before qsub; repair checkpoint 70f4094b. [Exact controlled repair](PLAN.md), [definite receipt](pbs-receipt.json), [prior failed job and CPU isolation](../research-review-224155-20261023/REVIEW.md).

Selected AI credit 46484.545 used / 17515.455 balance / 0 In Doubt; prior 224155's 18.631-SU charge uniquely reconciles and releases its maximum. Reserve at most 42.666667 SU for 224157, leaving **4472.788333 SU** internal headroom under unchanged 51000 cap / 13000 reserve. Preserve the new maximum until its charge posts. The published ledger is a dated pre-submit snapshot.

The preceding actual-host module preflight uses no image/GPU and selects Singularity 4.1.5 in a nonlogin shell. That is supporting CPU evidence, not the runtime confirmation. Require final PBS exit 0, complete byte proof and all zero-exit/cleanup receipts. No full model, EAGLE output, score or official accuracy is established by this diagnostic. The old full 223055 NIXL disconnect and live auxiliary-row layout remain separate questions. H200 25682/25712/25713 are untouched.
