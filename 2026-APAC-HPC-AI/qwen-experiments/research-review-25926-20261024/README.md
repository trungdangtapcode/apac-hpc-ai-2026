# Actual five-H200 startup qualification passed

Job **25926** completed with exit **0:0** after **253 seconds**. Independent replay confirms all five assigned H200 UUIDs, TP5/DP5 with attention TP1, native DP LM head, EP5 with 130 physical expert slots and 26 local slots, matching expert maps, FP8 expert weights, FP32 runtime scales and selected redundant-slot byte hashes. BF16 model/KV, four KV heads and native HTTP 200 health also pass.

This resolves the observed R2 vocabulary-divisibility failure for startup. It does not prove generated answers, full prefill/decode transfer, official accuracy or performance. Loaded duplicate hashes cover the first selected MoE layer, not every tensor in the model. Only assigned-device metadata was collected; continuous hardware telemetry and kernel profiling were not collected.
