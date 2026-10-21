# Terminal decision — 2026-10-21T03:24:42.830408+00:00

Both local serving/runtime/output gates pass. The actual balanced worker masks are verified, but goodput improves only **0.289035%**, below the prospective **1%** gate. **Close this exact policy, no unchanged repeat or default promotion.** [Full measurement, mapping, tails, profiles, limitations and cost review](PAIR_REVIEW.md). Both costs reconcile; current internal headroom is 7428.590 SU before any new reservation. The submission snapshot below is historical.

# Equal-budget CPU envelope pair submitted — 2026-10-20T17:22:05.154436+00:00

Definite receipts: **222551.pbs111 legacy control → 222552.pbs111 balanced candidate**, verified serial afterany. The candidate receives QWEN_CONTROL_JOB=222551.pbs111 and its bootstrap guard checks the predecessor before loading weights. Each requests 16 H100 / 30 minutes / maximum 1024 SU; total 2048 SU. [Receipts and qsub variables](pbs-receipts.json), [actual scheduler dependency](pbs-post-submit.txt), [plan and gates](PLAN.md), [frozen payload and CPU validation](validation.json).

The only intended treatment is redistribution of the same 32/32/64 logical CPU budget across GPU-local physical cores. The control replays the original ordinal envelope. Both run identical prelaunch metadata code and retain native SGLang locality, official FP8 target/BF16 KV, GPU layout, HPC-Ops/chunk 4096, MNNVL/attention, N54, benchmark, output diagnostics and observers. Actual CUDA UUIDs map to NVML/PCI identity; no ordinal equivalence is assumed. No binding result, score improvement or official accuracy claim yet. H200's five existing positions remain untouched.

Fresh locked ledger: Used 42633.312 / Balance 21366.688 / In Doubt 0 SU, all earlier terminal charges reconciled. New outstanding maxima 2048 SU leave **6318.688 SU** internal headroom under the same 51000 cap/13000 buffer. [Raw source](pbs-pre-submit.txt), [reconciliation](reconciliation.json). No implicit budget increase or overlapping own PBS allocations.

The first submit adapter stopped before any reservation/receipt/qsub on a signed-zero ledger representation. [Retained failure and correction](PRE_SUBMIT_CORRECTION.md) verifies that no uncertain job existed, checks the already-uploaded manifests again, and validates a zero-only normalization before a fresh locked submission. No frozen payload or acceptance gate changed, no duplicate qsub occurred.

After terminal completion, require full local protocol/runtime/output gates, complete actual allocation/envelope/thread maps, intended change and at least 1% goodput gain for a useful provisional pair. Only a useful valid gain merits independent confirmation; losses or neutral/missing mappings close the exact policy. A single pair is not a reproduced improvement. Keep raw failed attempts and inspect tails/errors/queues/KV, resources and separate profiles. Next hypotheses remain independent; no background Codex, new schedule or submission material change.
