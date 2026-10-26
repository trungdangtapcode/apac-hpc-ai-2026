# H200 NIXL fanout component 26337: prerequisite repaired and small writes pass

Job 26337 completed `0:0` in 1:58 on g1/g4 with 16 H200 GPUs. This is a successful bounded component probe, not a serving result. It answers whether all four roles can register small GPU buffers and exchange/check synthetic writes through the pinned NIXL/UCX API after the earlier missing-source-mount packaging failure.

| Phase | Sender ranks | Write handles | Bytes written | Receiver ranks with full buffer and sentinel check |
|---|---|---:|---:|---:|
| p0 only | 0–3 | 8 | 1,540,096 | 8/8 |
| p1 only | 4–7 | 8 | 1,540,096 | 8/8 |
| Both | 0–7 | 16 | 3,080,192 | 8/8 |
| Total | — | 32 | 6,160,384 | All eight decoders in every phase |

Each write covers 188 regions of 1,024 bytes, and is routed to both matching-rank decoder groups. Independently recomputing each retained decoder SHA256 from the deterministic expected buffer matches all 24 receiver-phase records. That buffer check includes the untouched sentinels as well as written bytes, so a NIXL `DONE` status alone is not the sole evidence. The probe allocated 188 × 4,096-byte regions per GPU; observed peak allocated tensor memory was 1,540,096 bytes on senders and 770,048 bytes on receivers. These are tiny synthetic buffers, not model KV capacity.

All 16 rank records report distinct H200 UUIDs. P0/P1 ranks 0–7 are on g1; D0/D1 ranks 8–15 are on g4. Every rank reports the same native patched source SHA256 `912b7e…`, NIXL Python API SHA256 `27c3ce…`, bindings SHA256 `ffff36…`, and Torch 2.11.0+cu130 identity. The submitted read-only source mount guard passed. Each role used its planned progress setting: eight native progress threads for prefill ranks and zero for decode ranks with explicit polling. All 16 rank logs show NIXL agent and UCX backend initialization and all three phases becoming ready; the per-role launcher logs carry only the mount-verification marker. No rank log contains a transport error or traceback.

This result repairs the interpretation of S68. Job 26308 failed before NIXL agent creation because the exact patched source mount was absent; that failure said nothing about the network. In 26337 the mount is present, and basic sixteen-agent registration, both prefill groups writing concurrently, cross-node two-peer routing, and small destination-buffer integrity all pass. Therefore the old 26081 prefill-0 semantic failure is not explained by a general failure of this small NIXL/UCX route.

The boundary is substantial: no SGLang HTTP bootstrap or room metadata, no actual model KV pointers/layout, no tensor-parallel collective, no production-sized span, and no inference or AIPerf score. Continuous GPU/CPU/InfiniBand diagnostics were not collected. Receiver hashes validate this synthetic write pattern only. Do not call this an end-to-end KV pass, competition improvement, or proof that the old semantic failure is fixed.

A useful next hypothesis, after reviewing the full-serving controls, is that the unresolved prefill-0 asymmetry occurs above basic transport: at SGLang bootstrap/room exchange or translation of native model KV descriptors. A separate model-free probe could replay that exact metadata and descriptor handoff for P0 and P1 with a real one-request completion receipt. Its gate must retain source hashes, route and GPU identities, destination integrity, and a hard timeout. This is a derived diagnostic idea only; 26337 itself does not authorize a full model retry.

Evidence: [machine-readable independent row audit](review.json), the submitted plan and `runs/26337/submitted-payload`, all 16 retained rank JSON/log files, `head-check.json`, and Slurm accounting. `head-check.json` accurately labels the result `PASS_COMPONENT_ONLY`, with quality `NOT_EVALUATED` and goodput `NOT_MEASURED`.
