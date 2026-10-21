# Single TP4 native prefill readiness passes

223005.pbs111 is sealed F/exit 0 after 406 seconds on a2ap-dgx037, four requested
H100 GPUs. Estimated allocated charge is 57.742222 SU; actual posting is not
reconciled in this review. All raw evidence hashes and the twelve copied
submitted files match the frozen deployment manifest. The complete original
manifest is retained; it names build-only files not copied into the job's
submitted subset, so subset verification is explicit rather than silently
ignoring required files. The independent native artifact gate replays PASS.

Each of TP0/1/2/3 logs two disabled-prefill-graph paths (target and draft), and
both KV allocations in every rank report BF16. All four NIXL ranks initialize,
HTTP health returns 200 and native readiness is logged. No prefill graph capture
begins and no matched Python/native fatal error occurs before readiness. The
actual image graph-source hash and four Hopper devices pass the compute entry
check. Uniform eager prefill is therefore a usable native initialization
configuration on this node; it is not yet a full PD correctness result.

66 startup hardware samples cover four distinct visible UUIDs and record GPU
activity, VRAM, power/clocks/temperature, node CPU/RAM/network counters and
server metrics status. REVIEW.json records ranges and actual coverage. Node
counters have not been turned into per-worker CPU/network rates. Only the
launcher CPU mask was captured; the one-shot probe does not request the later
full scheduler/rank/thread locality capture. No scoring interval, user workload,
latency tail or speculative acceptance distribution exists here. Native health
may execute its internal one-token forward, so this is not a claim of zero
kernel/model execution. No benchmark or explicit user generation request was
sent. Post-readiness SIGTERM and the detokenizer -15/SIGQUIT messages are the
controlled driver cleanup and remain preserved; they are not hidden from review.

The failed full run 222780 used a different physical node and two prefill replicas.
This is a validated repair configuration and source-consistent progress, not a
matched startup speedup estimate or proof of a specific blocked collective.
The next justified test derives a new full 16-GPU PD bundle from 222780, adding
the same disabled graph flag only on both prefills. Preserve decode graphs,
BF16/unquant, official FP8 target, native verification, transport and sealed
reference/corpus. Earlier shared-context HPC steering is superseded by the
owner's verified GPU/AI session assignment; no HPC job or CPU ledger is changed.

Before scoring, require all endpoint/runtime/resource gates and all 1600 actual
output IDs matching the sealed target reference. Keep full-PD readiness and
phase timeouts inside the original 30-minute allocation, reserving time for
token checks and cleanup rather than letting readiness consume the client
window. No speculative speedup, quality certificate or submission promotion
follows from this single-prefill pass.
