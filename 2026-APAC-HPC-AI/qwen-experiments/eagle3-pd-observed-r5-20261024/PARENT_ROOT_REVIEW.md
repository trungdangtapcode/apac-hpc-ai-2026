# Root review draft — observed H100 EAGLE3 P/D correctness candidate

**State: ready for final root review; not a submission receipt or runtime result.**
This candidate has not been uploaded or run. The root owns final packaging,
queue/budget decisions, and any conditional submission after the active
prerequisite completes.

## Question and prior evidence

The preserved R3 full H100 attempt, **223055.pbs111**, failed F/exit 1 after
734 seconds with zero completed diagnostic responses. Its first reported
failure was HTTP 500 / `NIXL_ERR_REMOTE_DISCONNECT`; later requests reported
missing remote-agent metadata. The chronology does not identify whether the
first failed operation was KV or auxiliary transfer. R3 printed
`ALL_PAIRS_WARM` after its remote task traceback, so that marker is not accepted
as evidence of a successful warmup. See
[R3 review](../eagle3-pd-eager-prefill-r3-20261021/REVIEW.md).

The accepted H100 target-only control is **222761.pbs111**. Its retained
reference contains eight successful requests, 200 actual output IDs per
request (1,600 IDs), four stable target-a/target-b pairs, and matching request,
IDs, and length finish reasons. The reference is bound to target identity
SHA-256
`61b899e3acfb6570e93049dfeca03cf66ae5cb3a2bdf89c03938f3d98da44aeb`.
The candidate's retained target staging record matches R3's staged record
byte-for-byte at SHA-256
`003a91e4c881f4500a14d58ddb63a174bb180c182b96d5e434323ef1fe4ffb2d`.
The copied candidate reference file is byte-identical to R3's staged copy:
SHA-256
`a1b5234892b8ccdedb64837f15d2e4357b479565faf0210502e85dada0382e18`.
This is a tiny exact-output diagnostic, not official accuracy or performance
evidence. See
[accepted reference review](../eagle3-reference-corpusfix-20261021/REVIEW.md).

## Candidate hypothesis and gates

R4 keeps the native NIXL source byte-identical to the failed R3 payload at
SHA-256
`912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`.
The source check in each worker verifies this mounted file before launching
SGLang. The observer only records actual metadata and method invocation/API
return-or-exception; a returned handle is not transfer completion.

Before semantic warmup, `observer-gate.py pre-warmup` requires 16 actual rank
receipts (P0 TP4, P1 TP4, D0 TP8), six loaded-source reports, and matching
ordered metadata names and per-item widths across all roles. It retains and
reports measured per-role row counts; it does not assume equal row counts.
Warmup then requires two independently replayed semantic P/D response
receipts, plus `send_kvcache_slice` and `send_aux` start and return/exception
observations from both prefill roles. Neither `ALL_PAIRS_WARM` nor a returned
handle is treated as a pass by itself.

Only after those gates does the client collect two repeated four-case EAGLE3
responses with 200 actual IDs each. The head checker requires both candidate
repeats to match each other and all four accepted target reference cases in
request body, every output ID, and finish reason: 1,600 observed candidate IDs
across the two repeats. This is exact equality for the four retained prompts,
not a full-set accuracy claim.

Draft identity is checked by hashing the full `model.safetensors` file against
the pinned SHA-256
`bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86` and
checking the draft and publisher configs agree except for architecture. The
target identity gate compares the candidate's runtime metadata record with the
accepted reference identity. **Large target weight shards are checked by
expected size at runtime, not rehashed during the allocation**; the identity
includes their retained full SHA-256 staging records. Preserve this limitation
in any later claim.

## Runtime bounds and launch review

PBS requests two scattered exclusive 8×H100 nodes for at most 30 minutes.
The main absolute T0 envelope is startup 900 s, warmup 180 s, client 300 s,
head gate 60 s, and cleanup 90 s (1,530 s total), below the 1,800 s PBS
walltime. Every stage deadline is clipped against its T0 cumulative boundary.
Client calls are also time-bounded. Resource sampling shares the 1,530 s cap;
no heavy profiler or score run is launched.

The scheduler batch, topology launcher, remote PBS task shim, and container
launcher all use explicit Bash/non-login invocation. The compute-node container
launcher initializes Environment Modules from the explicit
`/cm/local/apps/environment-modules/4.5.3/init/bash` path when `module` is not
already defined, then loads Singularity 4.1.5. The child Bash warmup/client
dispatch preserves exported `srun`, arguments, timeout, and task status in the
mocked launcher fixtures. Real PBS remote-status behavior remains unverified.

## Review finding fixed in this draft

Independent inspection found that `observer-gate.py` imported
`validate_receipts` from the bundle root even though the shipped module is in
`pd-observer/`. That would abort before checking any pre-warmup receipts. The
candidate now adds the bundle-owned observer directory to `sys.path` before
importing the validator and has a CPU regression test that verifies the gate
reaches its expected “16 receipts missing” validation failure instead of an
import error. The source hashes and native NIXL file were not changed.

## Current CPU verification and limits

The rerun passed: Python compilation, Bash syntax, eight PBS launcher fixtures,
absolute phase-controller fixtures, semantic receipt and exact-reference head
fixtures, the new observer-gate import regression, six observer tests, and the
17-entry retained R3 source checksum check. These checks establish source and
CPU fixture behavior only. They do not establish H100 loading, actual P/D
metadata receipts, invoked native transfer paths, remote task exit propagation,
or exact candidate output equality.

## Conditional decision

Candidate may be considered for the root's conditional `afterok:224275` chain
only after that prerequisite succeeds and root rechecks current PBS capacity,
AI budget, and the source/package manifest. A failure in any pre-warmup or
semantic gate must stop before client correctness calls. Preserve all raw
runtime receipts and distinguish a handle return from completed transport.
There is no score, speedup, full-set accuracy, or successful R4 run at this
draft stage.

## Final root amendment, 24 October

The conditional child may reserve a queue position with `afterok:224275.pbs111`; it must independently validate and retain the actual passing four-rank parent receipt before starting any model worker. A parent failure prevents the child from running. Root also propagates batch T0 through topology startup so checks before model launch count toward the same 1,530-second envelope. This amendment supersedes the draft wording that required waiting for parent completion before admitting a conditional child. The root submit controller preserves the global combined cap and CPU-before-AI lock order.
