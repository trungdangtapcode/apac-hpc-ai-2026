# Correct the FP8 cache evidence checker

Job 25864 allocated actual FP8 cache on all 16 ranks but failed before routing, semantic requests and load because an inherited checker required BF16. This is our validation bug, not a measured FP8 loss. The raw failed job stays unchanged. S52 derives a new frozen bundle, changes only the allocation checker and storage description, and retains the actual passing control 25863 plus all quality, SLA and no-error gates.

Actual six-role BF16/FP8 log replay and CLI negative fixtures pass. Only exact configured dtypes and complete unique ranks pass. A successful parser replay does not make the old failed job a successful benchmark. Compare the new candidate only with the matched short control, not the full historical incumbent. A valid gain above 1% would justify newly derived full confirmations; cancelled 25875/25877 remain historical.
