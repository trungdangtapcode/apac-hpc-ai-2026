# Two-node NIXL peer probe

Status: CPU-reviewed probe source; no scheduler job has run. This is a no-model
transport diagnostic for one GPU on each of two nodes. It checks the live NIXL
agent/UCX peer path and remote VRAM writes on the selected node pair. It does
not test SGLang's TP4-to-TP8 descriptor mapping, EAGLE3, KV layout, or inference.

The historical target-only run 222761 already passed on the same TP4-prefill /
TP8-decode topology class: both routes warmed and all eight exact-ID requests
passed. It used another node pair and speculative decoding was disabled. The
failed native-draft run 223055 used prefill dgx019 and decode dgx031. Its first
pair warmup failed with `NIXL_ERR_REMOTE_DISCONNECT`; later `NIXL_ERR_NOT_FOUND`
was observed in `initialize_xfer` after that failure. This probe distinguishes
basic NIXL peer/VRAM transport on the new pair from failures that require the
SGLang heterogeneous descriptor or draft-KV path.

## Protocol

Launch `entry.sh` separately on each allocated node with rank `0` or `1`, the
same shared artifact directory, and the same shared runtime scratch directory.
Each process binds one visible GPU, discovers active InfiniBand devices using
the worker's existing `/sys/class/infiniband` rule, and exports the resulting
list as `UCX_NET_DEVICES`. It creates the NIXL agent with strict thread sync,
creates the UCX backend with eight progress threads, and registers one 128 MiB
GPU allocation. The lower 64 MiB is the send half; the upper 64 MiB is the
receive half.

The processes exchange agent metadata and device-buffer addresses through
atomic files in `--exchange-dir/.nixl-peer-probe-private`, a mode-0700 runtime
scratch subdirectory. Those files contain NIXL metadata and raw GPU addresses,
so they must remain outside the artifact directory and be excluded from capture.
Per transfer, the receiver clears its destination and signals readiness. The
sender fills its source with an iteration-specific
pattern, posts a NIXL `WRITE`, and requires terminal `DONE` within 15 seconds.
The receiver verifies the GPU destination bytes against the expected SHA-256
and acknowledges the matching checksum. Transfers are serialized.

There are 20 repetitions per size and direction: 4 KiB and 64 MiB, both ways.
That is 80 unique transfer rows total, with 40 sends and 40 receives per rank.
One shared 300-second deadline covers handshake and all transfers. Each rank
writes a redacted result JSON to the artifact directory. Rank 0 waits for both
results and runs the explicit checker; it writes `final.json` only when all 80
transfer and checksum receipts match.

| Result file | Send rows | Receive rows |
|---|---:|---:|
| `rank0-result.json` | 40 | 40 |
| `rank1-result.json` | 40 | 40 |
| `final.json` gate | 80 paired unique transfers | 80 matching GPU checksums |

## Fail-closed checks

The probe requires exactly one visible CUDA GPU, an active InfiniBand device,
the installed `nixl._api` signatures used by the pinned SGLang NIXL manager, and
the expected patched runtime source hash from 223055. Any import, source-hash,
backend, metadata, descriptor, transfer-state, timeout, or checksum mismatch
fails the rank. It does not fetch remote source or force an alternate API.

The output records peer IDs, metadata byte counts and hashes, GPU UUIDs, active
IB devices, NIXL/Torch versions, and source/library hashes. It excludes raw NIXL
metadata, memory addresses, session data, and credentials. Rank outputs and
`final.json` are evidence of this probe only. A pass establishes that base NIXL
agent discovery and GPU-to-GPU writes work on the tested node pair; it does not
validate SGLang's heterogeneous head slicing or prove a cause for 223055.

## CPU review

Run `python3 CPU-test.py`. The test injects a mock NIXL agent and CPU-backed
tensor adapter to exercise the exact descriptor/transfer call sequence and
also checks that the final semantic gate rejects missing, duplicated, failed,
or checksum-mismatched rows. These tests do not establish GPU or network
transport.

The API snapshot is pinned to SHA-256
`27c3ce3c4fe58480aa3bce5e5c158c7659821a3bf1e84680778645adfdaa1bea`, extracted
from the same runtime image as the expected SGLang source. The binding module
is resolved from `nixl._api.nixlBind`, so the output hashes the native module
actually imported by that API.

Primary API reference: NVIDIA NIXL's
[`basic_two_peers.py`](https://github.com/ai-dynamo/nixl/blob/main/examples/python/basic_two_peers.py).
The runtime API is pinned to the 223055 `nixl-conn.py` usage of
`nixl_agent`, `nixl_agent_config`, `register_memory`, `get_agent_metadata`,
`add_remote_agent`, `get_xfer_descs`, `initialize_xfer`, `transfer`, and
`check_xfer_state`.

## Allocation and attribution limits

One bounded trial requests two nodes with one H100 each, at most ten minutes,
maximum 42.666667 SU at 128 SU/GPU-hour. Preserve each PBS task's actual GPU
allocation mask inside the container. Do not use a hard-coded physical GPU0
on a partially allocated node. The head independently checks both actual rank
artifacts, because pbsdsh status alone masked the previous remote failure.
No model weights, tokenizer, draft, official workload or AIPerf score is loaded.

The scheduler may choose a different node pair from failed 223055. Record actual
hosts/UUIDs/IB and state that a pass on a different pair cannot clear the earlier
pair or prove EAGLE3 transport correct. Raw metadata and memory addresses stay
in runtime-peer-state outside runs and are excluded from capture/collection.
Runtime/library hashes, redacted peer receipts, task logs and checksums remain.

Before submission hold the AI budget lock, refresh own GPU queue/AI project,
reconcile only uniquely posted prior charges, retain other maxima, reserve this
maximum and record a definite receipt once. Require an empty own GPU queue,
retain the conservative one-CPU-slot allowance without connecting to HPC, and
keep the existing 51000-SU cap / 13000-SU reserve. No uncertain retry, changed
budget or background schedule. Failure selects a supported transport/interface
repair or closes the branch; a pass calls for a small descriptor/path isolation
before another full-Qwen allocation. No automatic model retry follows.
