# Qualify five-rank startup with the native DP LM head

Both R2 attempts failed during model construction: the ordinary LM head tried to divide padded vocabulary 151,936 across TP5. The remainder is one. DP attention alone had fixed the attention head geometry but did not switch the LM head group. This is a distinct, actual runtime limitation, not an OOM or numerical error.

R3 adds the pinned runtime's native `--enable-dp-lm-head`. Qwen then uses the attention TP group of size one for vocabulary partitioning. No vocabulary, model weights or arithmetic kernels are edited. All five observer records must prove the new flag is actually enabled, in addition to the existing TP5/DP5/EP5 map, 26 loaded experts, correct FP8 weights and FP32 scales, duplicate row hashes, BF16 KV and native HTTP 200 health gates.

This remains a startup diagnostic on five assigned GPUs for at most 17 minutes. H100 maximum charge is 181.333333 SU. Readiness, if it passes, does not prove inference outputs, full prefill/decode transfer, official accuracy or performance. Preserve the R2 failures and the earlier manifest transcription failure.
