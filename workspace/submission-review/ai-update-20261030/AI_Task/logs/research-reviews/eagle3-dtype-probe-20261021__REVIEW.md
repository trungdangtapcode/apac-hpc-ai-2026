# Native dtype failure reproduced and layer repair validated

222769.pbs111, sealed F/exit0, **157 seconds**, estimated **5.582222 SU**, reviewed 2026-10-21T06:00:15.649406+00:00. Frozen payload/raw hashes pass. This is a one-GPU native layer fixture, not full target/attention inference or a score. No complete hardware series/profiles were requested.

Actual ModelConfig/ServerArgs resolve the **target to BF16 activations with FP8 quantization** under both auto and explicit BF16. The dtype-less public draft resolves **FP16 under auto**, no quantization. After native set_embed shares the real unchanged official target BF16 embedding, native lookup returns BF16 but the draft input-norm weight is FP16. Native FlashInfer reproduces the identical argument1 expected-BF16 failure from 222763. Thus the dtype hypothesis is verified, not merely inferred from KV logs.

With **explicit BF16** and supported draft **unquant** resolving to None, target remains BF16/FP8, draft/norm/embedding are all BF16. The exact same real embedding parameter aliases by object and GPU pointer in this single-rank fixture. Native eager norm succeeds; CUDA graph capture/replay yields **finite bit-identical outputs**. Peak fixture allocation **4949346304 bytes** is not incremental serving overhead or GPU utilization. Target embedding is 151936×4096 from verified official shard1; only that tensor is loaded, not the full target. Retained staging hash plus fresh shard size/small-file hashes is the stated provenance limit, not a new whole-shard rehash.

The earlier R/substate 41 without job-body artifacts was a transient launch observation. The later native fixture executes and passes; do not blame its code or claim a lasting node failure. No cancellation/duplicate was needed.

**Decision:** derive a separately frozen full PD repair with --dtype bfloat16 and --speculative-draft-model-quantization unquant in both roles. This preserves the FP8 target and its existing BF16 activation dtype; no weight/config changes. Keep exact accepted 222761 reference, native verification, transport and semantic gates unchanged. Actual TP4/TP8 full-state/auxiliary transfer, remaining attention/verification graphs, memory and real output equality still require the full allocation. No speculative speedup, quality certification or matched-load claim follows from a layer fixture.

[Complete probe](collection.json), [sealed raw hashes](collected/222769.pbs111/evidence-sha256.json), [native fixture](dtype-probe.py).
