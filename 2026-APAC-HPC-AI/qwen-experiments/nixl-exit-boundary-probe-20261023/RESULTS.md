# Exit-boundary diagnostic submitted as 224155

The frozen native-byte diagnostic is submitted as **224155.pbs111** at **2026-10-23T15:29:03.183865+00:00**. Immediate PBS state is **R**, hosts **a2ap-dgx037 / a2ap-dgx039**, one H100 per host, at most ten minutes. No model or scored inference. The unchanged native byte gate and new independent Python-child, container/node cleanup and batch-exit records must be reviewed separately from final scheduler status. No runtime pass is claimed at submission.

Fresh locked selected AI credit uniquely reconciles prior 224116 at 16.284 SU: Used 46465.914 / Balance 17534.086 / In Doubt 0. The new maximum 42.666667-SU reservation leaves internal headroom **4491.419333 SU** under unchanged 51000 cap / 13000 reserve. Preserve the maximum until uniquely posted terminal reconciliation; published pre-submit balance is not the final charge.

SSH to a2ap-login01 was authenticated through the already healthy shared VPN using the previously supplied credential. No VPN restart or fresh DUO step was performed by this worker. The earlier local connection preflight failed before upload/reservation/qsub, so there was no prior uncertain scheduler attempt to duplicate. Its safe record remains in submission-blocked.json as historical evidence.

Original 224116 is F/exit1 despite passing byte proofs; this successor adds boundary observation and cannot prove the original cause merely by passing on a different host pair. Full serving, native per-request auxiliary strides, model output, EAGLE correctness, goodput and official accuracy remain unverified. H200 25682/25712/25713 are preserved separately.

The payload was frozen and pushed in 615e7838 before submission. [Exact hypothesis and timing bounds](PLAN.md), [definite receipt](pbs-receipt.json), [original failed preflight](submission-blocked.json).
