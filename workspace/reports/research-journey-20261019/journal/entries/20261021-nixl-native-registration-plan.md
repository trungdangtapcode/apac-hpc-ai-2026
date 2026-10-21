# 21 October: native multi-region registration and host auxiliary hypothesis

Recorded 2026-10-21T23:58:25.746984+00:00. Prospective frozen CPU milestone; no new GPU reservation yet.

Prior real probes223091 and223097 pass base transfers and all24 small native KV
descriptor writes, respectively. The remaining question is whether the actual
native registration method and separate DRAM auxiliary transfer also work,
before another expensive full-model integration attempt.

[New bounded plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-native-registration-probe-20261021/PLAN.md): two physical GPU agents,190 distinct1KiB CUDA
ranges each, three pinned host auxiliary buffers with16/32/64-byte slot widths.
Call the actual pinned register_buffer_to_engine, configure/send KV in94/94,
94/95 and95/95 layouts, then native send_aux slot1 to2. Require both rank-complete
receipts, reciprocal metadata hashes, exact registration groups, destination
GPU/host bytes and untouched sentinels, with an independent head replay.

Root review corrected a fixture bug before GPU execution:94-layer cases
initially exposed190 pointers rather than188. The fixed case-local helper is
exercised inCPU tests, while all190 ranges remain registered. Actual NumPy
rehearsal invokes the pinned registration/init/send methods and reproduces all
expected CPU bytes. These are CPU contract checks, not native-backend proof.

Maximum prospective allocation:2H100 /two nodes /ten minutes /42.666667 SU.
A fresh locked ledger/own GPU queue check precedes one receipt; cap and retained
reserve stay fixed. Actual ranges may share CUDA allocator slabs and are tiny;
no production pool, large memory registration, actual TP collective, native
bootstrap, EAGLE3 equivalence or performance is established. No HPC CPU access.

Next: submit this distinct component only after the frozen safe checkpoint,
review both actual rank artifacts/logs/accounting, then decide whether the real
model deserves a new diagnostic payload with semantic pair warmup evidence.
H200 full matched25365/25366 remain queued independently; no raw score mixing.
