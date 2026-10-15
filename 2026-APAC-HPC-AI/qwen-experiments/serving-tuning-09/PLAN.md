# MNNVL interaction experiments

User requested continuous use of available research time/GPU on2026-10-15.
Keep independent repeats23839/23859 queued. Fill at most three remaining slots,
shared cap5. Source23778 N52:2592.16 goodt/s,99.01%SLA,0errors/cancel.

1. MNNVL plus FlashInfer decode attention. FlashInfer alone yielded2440.39
   with18.71ms ITL. Test whether its attention improvement combines with
   MNNVL; gains cannot be assumed additive.
2. MNNVL with prefill chunk2048.
3. MNNVL with prefill chunk8192.

Chunks test whether the new decode bottleneck changes the earlier4096 choice.
Keep BF16KV, officialFP8 model,8+8topology,RR,full60/120/30 protocol,N52,
request-scoped NIXL and output checks unchanged. Compare against23778 and its
independent repeat; require reproduced advantage before selection. No other
wave's higher-load gates changed. New kernels/configs do not prove accuracy.
All failures retain logs and remain incomplete without full exports.
