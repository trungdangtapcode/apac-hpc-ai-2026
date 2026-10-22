# Native NIXL registration probe (prospective)

The preceding descriptor probe demonstrated 24 real KV writes through source-extracted NIXL methods, but its registered GPU buffers were grouped into larger regions and it did not exercise the native registration method's separate host auxiliary-buffer path. This small two-agent followup targets those two code paths directly, without loading a model or claiming inference correctness.

Each physical rank allocates 190 independent 1 KiB CUDA tensors, one per K/V layer region, and three pinned CPU tensors with per-slot widths 16, 32, and 64 bytes across four slots. The pinned, SHA-checked SGLang `NixlKVManager.register_buffer_to_engine` is AST-extracted and invoked on the real NIXL agent. The probe requires its actual registration calls to be one 190-entry `VRAM` group and one three-entry `DRAM` auxiliary group, with state arrays empty. This tests registration behavior on small allocations; it does not establish that a production-size KV pool or all production host allocations register successfully.

The source rank then invokes the pinned `_init_hetero_tp_prep_handle` and `send_kvcache_slice` for the three geometries: 94→94, 94→95, and 95→95 layers. Each case writes pages 1 and 3 into destination pages 0 and 2. The receiver checks all bytes across all 190 regions against an independently built expected layout and confirms untouched pages and unused layer regions remain sentinels. The sender waits for each receiver verification acknowledgment before proceeding, keeping the peer alive through validation.

After the KV cases, the actual pinned `send_aux` transfers slot 1 to slot 2 for each pinned host buffer. Both ranks use the same source pin and two-host/two-GPU identities; NIXL metadata and pointer-bearing endpoint records remain inside a per-job mode-0700 exchange directory. The public result contains no addresses or metadata bytes, only source/peer identities, geometry, states, and content hashes.

CPU fixtures exercise the actual extracted `register_buffer_to_engine` and `send_aux` methods against a recording mock agent, including the 190/3 registration counts, DRAM widths, slot offsets, and registered peer name. They also test layout sentinels and reject missing or mismatched semantic evidence. These tests validate fixture logic only; they do not simulate GPU registration or network transport. No virtual eight-GPU topology is claimed, and this probe does not establish EAGLE correctness, model equivalence, production-pool registration, or a serving score.


## Bounded execution, corrections and acceptance

Maximum allocation: two H100 GPUs, one per distinct node, ten minutes,
42.666667 SU at 128 SU per GPU-hour. Reuse the successful partial-node allocation
mask, pinned image/adapter and active-IB environment. A fresh locked own-GPU
queue and credit check must precede one definite submission receipt. No model,
accuracy benchmark, extra budget or HPC CPU access is involved.

Root review caught a case-local pointer bug before freezing: every case initially
exposed 190 pointers, so a 94-layer case would fail its 188-pointer plan check.
The corrected configure_case keeps all 190 allocations registered but supplies
only the correct active source/destination lists to the actual native helper.
CPU fixtures execute the exact helper across all three geometries. Additional
real-NumPy rehearsal executes actual registration, configure, KV send and DRAM
aux send against a CPU memory backend and checks all expected bytes. This is
arithmetic/contract coverage, not native backend simulation.

Both physical ranks write public complete receipts containing reciprocal agent
and metadata hashes, actual observed 190-entry VRAM/three-entry DRAM registration
groups, runtime/source identity and destination byte hashes. The independent
head checker requires both receipts and recomputes the expected hashes. A printed
success marker or remote shell return alone cannot pass. Raw pointer tables and
NIXL metadata bytes stay outside the collected artifact tree. No custom matched
hardware sampler is deployed; automatic coarse PBS counters are collected if
present and require separate coverage/mapping review.

All 190 tensors are distinct advertised ranges; the CUDA allocator may back them
with shared allocation slabs, so this is not proof of 190 separate physical
memory registrations or production-size pools. A pass closes only this small
multi-region/DRAM component. A full retry still needs native actual KV geometry
receipts and the independent semantic pair warmup gate; no throughput or model
output equivalence follows automatically.

CPU reproduction before a fresh freeze: create a temporary Python virtual
environment, install requirements-cpu.txt, then set APAC_CPU_PYTHON to that
interpreter when running prepare.py. The standard-library CPU regression runs
with python3; only the separate NumPy rehearsal needs the pinned package.
Existing SHA256SUMS or submitted payloads must never be rebuilt in place.
