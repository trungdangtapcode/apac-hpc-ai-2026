# Native NIXL auxiliary request-slot layout review

## Finding

The earlier ten-region probe establishes whole-buffer registration/transfer only. Pinned SGLang source defines a per-request metadata layout and `send_aux` uses that row layout: source and destination addresses are `base + item_len * slot_index`, one transfer item per destination buffer. The prior 223788 geometry receipts did not collect `aux_item_lens`, tensor shape/stride/dtype, or a per-slot transfer. Thus the source gives a strong expected layout, but it does not turn the old whole-buffer receipt into proof of those runtime facts.

No model or GPU was loaded for this review. The 223788 terminal status remains F / exit 1 under the original unrelated nonempty-`kv_layer_ids` check. Its ten observed auxiliary lengths remain evidence, and `kv_layer_ids=[]` remains intentional observed data; no work here changes that finding.

## Pinned builder and send path

Source extracted read-only from `/scratch/enroot-images/sglang-harbor.sqsh` is retained under [`source-image/`](source-image/). The image is 26,476,240,896 bytes; its full image hash was not computed. Relevant individual source files are SHA-256 recorded in [`AUX_LAYOUT.json`](AUX_LAYOUT.json).

- [`MetadataBuffers` allocation and ordering](source-image/sgl-workspace/sglang/python/sglang/srt/disaggregation/utils.py#L262): rows are plain `torch.zeros` arrays, with fixed field widths at lines 301–352. `get_buf_infos()` orders pointers/total lengths/item lengths at lines 354–384; item lengths come from `buf[0].nbytes`.
- [Prefill builder](../nixl-production-span-probe-20261023/source/eagle/sgl-workspace/sglang/python/sglang/srt/disaggregation/prefill.py#L182) and [decode builder](../nixl-production-span-probe-20261023/source/eagle/sgl-workspace/sglang/python/sglang/srt/disaggregation/decode.py#L418) both assign `aux_data_ptrs`, `aux_data_lens`, and `aux_item_lens` from `metadata_buffers.get_buf_infos()`.
- [EAGLE3 metadata sizing](source-image/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py#L1294): when the speculation algorithm carries draft hidden states, SGLang gets `hidden_size` and dtype from the draft runner. The source helper returns the runner’s `spec_hidden_size` and model dtype ([`eagle_utils.py:481-487`](source-image/sgl-workspace/sglang/python/sglang/srt/speculative/eagle_utils.py#L481)). Scheduler allocates prefill metadata at `max_running_requests * 2` slots ([`scheduler.py:1361-1372`](source-image/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py#L1361)).
- [Terminal-chunk call site](source-image/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py#L1291) requires `prefill_aux_index` and calls `send_aux` with the decoded destination pointer list and destination slot index. [`send_aux`](source-image/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py#L1975) enumerates destination pointers and indexes the source pointer/item-length arrays by the same `i`; it uses that source item length to offset **both** row indices and submits DRAM WRITE descriptors. The code shown has no explicit check that destination pointer count equals both source lists before indexing.

## Role asymmetry in full PD223055

The P and D sides do not use the same capacity rule:

| Side | Retained configuration | Pinned metadata allocation rule | Slot count conclusion |
|---|---|---|---|
| Prefill P | `223788` reports effective EAGLE3 `max_running_requests=48`; the rule is also the same for P in `223055` | `max_running_requests * 2` | 96, source-derived from the logged cap |
| Decode D | `223055` submitted config declares `decode_max_running_requests=256`; the retained decode `ServerArgs` has `disaggregation_mode='decode'`, `max_running_requests=256`, `speculative_algorithm='EAGLE3'`, and the startup log also reports 256 | `req_to_token_pool.size * 2` for this non-MiniMax Qwen model | 512 if its request pool size is 256. The retained 223055 logs verify the serving cap, but do not log `req_to_token_pool.size`; therefore 512 is the source-rule scenario/expected capacity, not a direct runtime observation. A pool size of 128 would produce 256 metadata rows under the same builder. |

The constructor stores its input as `ReqToTokenPool.size` at [`memory_pool.py:261-275`](source-image/sgl-workspace/sglang/python/sglang/srt/mem_cache/memory_pool.py#L261); scheduler then multiplies that property by two for decode ([`scheduler.py:1311-1327`](source-image/sgl-workspace/sglang/python/sglang/srt/managers/scheduler.py#L1311)). The exact `223055` field values above were read from retained `task-prefill-0`, `task-prefill-1`, and `task-decode-0` logs plus submitted `config.json`; the raw cap is not a measured auxiliary allocation. Do not describe both roles as having 96 slots or claim 512 observed without a pool-size receipt.

For source and destination schemas, each `MetadataBuffers.get_buf_infos()` call declares three parallel lists (`ptrs`, `data_lens`, `item_lens`) in one common order. With optional sampling masks and DSA indices absent, source makes ten entries on each role. The P side's ten-region count is observed in 223788; D's list count and data are not in the old full-PD receipts. Source therefore predicts 10→10 list cardinalities and identical per-item widths only when the P/D draft hidden-state spec and optional fields match. At send time NIXL `send_aux` uses P's `item_lens[i]` as the transfer length and offset multiplier for both P and D. It does not consult a D-side `item_lens` list or compare per-item widths there. Matching role widths are consequently a wire-schema expectation, not a captured 223055 runtime check.

The unequal-capacity scenario is included in [`layout_fixture.py`](layout_fixture.py): P source has 96 slots and D destination is modeled with 512 slots if `req_to_token_pool.size=256`. It checks descriptor-end arithmetic for source slot 0 / destination slot 0 and source slot 95 / destination slot 511 across ten matching-width items. This only checks bounds under that conditional scenario; it does not prove the D pool size, actual alignment/strides, or runtime transfer.

## Expected per-request layout

The raw 223788 prefill log independently reports `max_running_requests=48` after speculative-mode reset. Pinned scheduler source therefore makes the prefill metadata row count 96. That count is not inferred by dividing captured lengths. With the source’s default top-logprob width of 128 and the observed ten-region count (no optional three sampling-mask regions and no optional DSA indices), the fixed source widths are:

| Index | Source buffer | Source-derived bytes per request | Confidence |
|---:|---|---:|---|
| 0 | `output_ids` | 64 | Fixed shape and dtype in source |
| 1 | `cached_tokens` | 64 | Fixed shape and dtype in source |
| 2 | `output_token_logprobs_val` | 64 | Fixed shape and dtype in source |
| 3 | `output_token_logprobs_idx` | 64 | Fixed shape and dtype in source |
| 4 | `output_top_logprobs_val` | 512 | Source default 128 × float32 |
| 5 | `output_top_logprobs_idx` | 512 | Source default 128 × int32 |
| 6 | `output_topk_p` | 64 | Fixed spec-decode shape/dtype |
| 7 | `output_topk_index` | 128 | Fixed spec-decode shape/dtype |
| 8 | `output_hidden_states` | 8,192 if width 4,096 and BF16 | Conditional: source reads draft runner spec; actual runtime width/dtype/stride were not retained |
| 9 | `bootstrap_room` | 64 | Fixed shape and dtype in source |

All ten lengths in the old receipt equal these source-shaped widths × 96 **if** the hidden-state conditional is true. [`layout_fixture.py`](layout_fixture.py) reproduces this with small CPU-only scalar geometry and asserts the arithmetic. This is a source/config consistency check, not a replay of live tensor allocation or transport. The exact observed aggregate lengths and uncollected fields are preserved in [`AUX_LAYOUT.json`](AUX_LAYOUT.json). The full receipt hashes remain in the linked original geometry-source-records file.

Source allocations are regular 2-D `torch.zeros` tensors and `buf[0].nbytes` is the entire first row, so the intended row stride equals that item width for these allocations. The H100 receipts did not log actual `tensor.stride()`, item lens, destination metadata layout, or pointer deltas; those runtime values remain unverified.

## Next minimal informative diagnostic

For the earlier full PD223055 remote NIXL disconnect, run one bounded no-model native transfer using the actual pinned `MetadataBuffers` construction on both endpoints, with the logged P cap and D cap, and record the actual allocated `req_to_token_pool.size` before concluding D's metadata-slot count. Use distinct per-buffer patterns and guards; exercise first and last legal indices independently on each side, including P source slot 95 and D's observed highest legal slot once its actual pool count is captured. Emit one redacted receipt for each side containing buffer index/name/order, shape, stride, dtype, `nbytes`, `buf[0].nbytes`, and list counts; log source/destination row indices and descriptor count; mark remote descriptor creation, transfer initialization, post, completion, and byte/hash comparison separately. Fail before transfer if source/destination counts or corresponding item widths differ. This small operation tests production-style offsets without loading model weights; stage markers tell whether an error occurs before `send_aux` can run. Keep any future attempt separate from the immutable old jobs and stop at the first complete diagnostic receipt.

It would test the auxiliary path and pinpoint transport stage, not explain a failure that occurred solely in KV transfer before auxiliary work. Capture the matching KV/aux operation phase and remote status in the probe if the original disconnect boundary is uncertain. This source-only review did not execute or reserve that diagnostic. Any runtime successor still needs a separately reviewed payload and fresh selected queue/credit checks under the standing authorised research loop.

## Reproduction

`python3 layout_fixture.py` prints ordered row widths and 96-slot aggregate lengths, then checks slot-bound arithmetic for a conditional 96-source/512-destination scenario. The fixture allocates no tensors, loads no model, accesses no GPU, and touches only this review directory.
