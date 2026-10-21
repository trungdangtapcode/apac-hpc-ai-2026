# NIXL descriptor-path probe

This no-model fixture tests the patched SGLang NIXL KV slice path on two actual GPU agents on distinct nodes. It reuses the peer-probe initialization, installed NIXL API/source identity checks, and metadata handshake from `base-peer.py`. Runtime methods are AST-extracted from the installed, hash-checked NIXL and common-connection files; the exact installed `compute_head_slice_params` helper is imported and called for each mapping. The retained public `staging_buffer.py` snapshot is pinned at SHA256 `52693777d6ee25d1919555a5b910677ba58fa6c18e35782faa7a0470b43839ab` and must match the deployed file.

The run has three pointer geometries: target-only 94 to 94 layers, decode-only draft 94 to 95 layers, and both sides with draft 95 to 95 layers. With four global KV heads, the eight logical routes follow GQA replication: decoder ranks 0 and 1 use source head rank 0, ranks 2 and 3 use source 1, ranks 4 and 5 use source 2, and ranks 6 and 7 use source 3. The staging helper validates slice offsets and head count but does not choose the source rank: its pinned implementation returns `(0, 1, 0, 1)` for every TP4-to-TP8 source/destination pair. The fixture therefore derives eligibility from the consecutive-rank GQA rule, then checks the helper output for each selected pair. It does not test partial-head slicing. Every pair is sent once in each geometry: 24 actual NIXL WRITE handles total, with eight backend threads and a 300-second overall deadline.

Each logical rank owns one registered contiguous VRAM allocation containing 190 synthetic K/V regions. Each region contains four pages; native per-layer registration is not tested. A page has size one and 256 bytes. Source pages `[1, 3]` map to destination pages `[0, 2]`, keeping the backend descriptors noncontiguous. Distinct deterministic byte patterns identify logical rank, case, K/V layer region, and source page. Destination buffers start with sentinel `0xA5`. Exact descriptor arrays from the extracted `send_kvcache_slice` are range-checked against registered local or peer regions immediately before the backend converts them. The receiver compares the entire GPU allocation with an independently constructed CPU expectation, including gaps, unused pages, and draft regions, before acknowledging each handle.

All source/destination item lengths must have the same 256-byte stride and be divisible by page size. This is required because `_init_hetero_tp_prep_handle` derives one scalar stride from `kv_item_lens[0]` and one scalar peer item length. A mixed-stride layout fails the fixture. Equal synthetic strides validate descriptor mechanics only; they do not establish that native EAGLE KV arguments have uniform item lengths.

The private agent metadata and raw pointer tables live only in `EXCHANGE_DIR/.descriptor-private`, outside the collected artifact. The archived rank results contain host/GPU identity, source hashes, case/rank identities, NIXL terminal states, and destination hashes, with no pointer values or metadata bytes. `descriptor.py --check` is standard-library-only and requires both ranks, distinct host/GPU identities, reciprocal peer identities, matching pinned source hashes, all 24 completed handles, and 24 verified destination rows.

`CPU-test.py` exercises the installed common helper's pointer selection, the actual patched device-ID and send methods with a mock agent that accepts only the registered peer name, descriptor range arithmetic, deterministic pattern separation, and untouched sentinel pages. CPU checks exercise actual extracted methods with a mock backend, not a GPU or NIXL backend simulation. The independent result checker recomputes each expected destination hash, rejecting a well-formed wrong hash. Run it with:

```sh
python3 CPU-test.py
```

## Bounded execution and decision

The frozen PBS bundle requests two H100 GPUs on two distinct nodes, one visible GPU per rank, for at most ten minutes (maximum 42.666667 SU at 128 SU per GPU-hour). It preserves the actual partial-node GPU allocation mask, supplies active InfiniBand-derived `UCX_NET_DEVICES`, and keeps raw peer exchange outside the collected artifact tree. A fresh locked own-GPU queue and credit check precedes the single receipt; budget cap and retained reserve are unchanged. No HPC CPU queries or ledger changes are needed.

Question: does the actual patched SGLang descriptor path correctly select noncontiguous KV pages and 94/95-layer pointer layouts after base NIXL passes? The control is the sealed 223091 base transport pass, not a matched throughput comparison. Success requires all 24 unique native WRITE handles to complete and all destination bytes, untouched sentinels, source identities, peer identities and independent hashes to match. Scheduler exit and a printed marker alone never pass.

This fixture has uniform 256-byte strides, tiny buffers and virtual TP ranks on two physical GPUs. It does not test native large KV registrations, actual eight-rank collectives, hidden-state/auxiliary transfers, SGLang bootstrap lifecycle or the failed 019/031 node pair. It cannot establish full EAGLE3 correctness, performance or accuracy. Hardware utilization/power/CPU-demand telemetry is not collected; device identity, backend logs and actual transfer checks are inspected instead. On failure, preserve artifacts and repair only a demonstrated cause. On success, inspect native KV argument layout and require explicit per-pair semantic warmup receipts before a bounded full-model retry; no automatic scoring allocation follows this job.


## CPU review before freezing

The source-only review caught and repaired a duplicate AST selector, a case label
used instead of the registered peer name, and an incorrect assumption that the
head-slice helper itself selects eligible TP routes. The final fixture uses the
explicit GQA route and validates the pinned helper's offsets. The start marker
is published atomically to avoid a partial-JSON race. The final checker rebuilds
the deterministic expected bytes itself; even two matching but false recorded
hashes fail. Negative fixtures also reject incomplete cases and swapped routes.

`numpy-rehearsal.py` executes the actual extracted init and send functions with
real NumPy, including the whole-head coalescing branch and all 24 synthetic
pointer layouts. Its CPU memory backend checks every descriptor and reproduces
full expected destination bytes. This is additional Python arithmetic coverage,
not native NIXL registration or transport coverage. The temporary CPU environment
uses NumPy 2.0.2 on Python 3.9. An initial 2.2.6 install was unavailable for this
Python version; no source payload or GPU state was affected.
