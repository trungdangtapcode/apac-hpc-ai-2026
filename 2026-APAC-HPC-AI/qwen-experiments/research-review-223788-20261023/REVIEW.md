# H100 223788: real registration data exposed an invalid diagnostic assumption

The original PBS job is **F / exit 1**, and its original semantic result is **FAIL**. It reached actual native readiness and HTTP 200; all source/H100/draft/HPC-Ops/config checks, eight BF16 target/draft allocation records, eight eager-prefill messages and four native NIXL ranks pass. The sole final rejection is our rule that explicit KV layer IDs must be nonempty. Original frozen bytes/result remain unchanged. [Original result](collected/runs/223788.pbs111/probe-result.json).

## Actual observations

Each of the four ranks has an atomic before/after pair, stable geometry and a successful native registration return. Each advertises **190 VRAM regions**, 76,132,096 bytes each, totaling **14,465,098,240 advertised bytes per rank**. Item/token byte stride is 256, page size 1 and page count 297391. Local/total KV head metadata is 1/4. There are **10 auxiliary regions** with lengths `[6144,6144,6144,6144,49152,49152,6144,12288,786432,6144]` bytes and no advertised state regions. `kv_layer_ids` is explicitly observed as `[]`, not missing; no semantic layer sequence was captured or invented.

The pinned native `get_mha_kv_ptrs_with_pp` computes positional counts from pointer-list length and PP ranges, without requiring `kv_layer_ids`. Thus our nonempty invariant was unsupported. [Exact source excerpt](native-positional-mha-source.py.txt), source SHA `ba33d63c6920f87b55cf57f9224bb7d08af67e1476bd70b8e1a70067f33a29d7`. This does not separately establish why the runtime leaves the field empty or prove semantic pointer ordering.

A separately derived candidate-local validator now permits this observed-empty field only for the known 190-region/head 1, total 4 / page 1 Qwen MHA contract; every rank must still have stable successful before/after receipts and valid bounded values. Missing/null/string/malformed or mismatched shapes still fail. The original shared validator is preserved. Replay of these eight actual hash-verified receipts avoids paying for another startup simply to reclassify retained metadata. Candidate 25682 must still collect and validate its own H200 data, both P/D transfers and all 1600 exact outputs.

## Cost and observability

Actual allocated runtime: **319 seconds**, four H100 GPUs on a2ap-dgx038; estimated charge **45.368889 SU**. Posted charge is **45.369 SU**; the maximum reservation is released. Internal headroom is **4550.370 SU** under the unchanged cap and reserve.48 hardware samples cover four UUIDs; sampled VRAM spans 0–75226 MiB. These are startup/native-health observations, not a scored load, utilization proof, startup speedup or physical-region accounting.

Local registration does not prove remote transfer, correct generation, EAGLE3 speedup or official accuracy. Ten actual auxiliary buffers also show why the earlier three-buffer component probe was narrow; per-request auxiliary strides remain uncollected. Keep original failure, useful raw data and corrected interpretation distinct. [Complete raw hashes](collected/evidence-sha256.json), [detailed assessment](REVIEW.json).
