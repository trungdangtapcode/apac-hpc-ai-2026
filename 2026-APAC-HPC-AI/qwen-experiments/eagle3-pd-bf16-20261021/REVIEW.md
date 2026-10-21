# BF16 repair reaches decode readiness; prefill initialization times out

222780.pbs111 was collected and sealed on 21 October after owner-authorised VPN
and SSH reauthentication. It is F/exit 1, 1661 seconds, estimated 944.924444 SU.
Actual charge posting is not yet reconciled here. Payload hashes pass. No router,
request/actual output IDs, semantic equality or scored throughput was produced.
A terminal job is not a completed measurement.

The previous BF16/FP16 RMSNorm failure does not recur. All eight decode ranks
finish target verification graphs; draft decode and draft extend graphs also
finish. Decode initializes all eight NIXL ranks and reaches HTTP readiness.
This advances the dtype repair beyond its layer fixture, but does not prove
full PD equivalence or source-level embedding pointer identity.

Both TP4 prefills complete target prefill graph capture. In each replica,
TP0/1/2 then skip draft prefill graph capture because available memory is
3.98/3.90/3.90 GiB, below the native automatic 4.00 GiB guard; TP3 instead
starts draft prefill capture with 4.37 GiB and never logs its completion.
TP0/1/2 proceed to NIXL initialization; TP3 never logs NIXL initialization.
The head script eventually times out waiting for prefill-0 HTTP health.
No explicit OOM or native Python traceback explains the stall in the role logs.

This is strong evidence of divergent rank initialization around an automatic
local-memory graph gate, not proof of a particular blocked collective: no GPU
stack trace or distributed hang profile was collected. Do not label it a proven
NIXL transport failure simply because the last other-rank lines mention NIXL.
A supported next hypothesis is to disable prefill CUDA graphs uniformly while
leaving the accepted BF16/unquant repair and native eager mathematics intact.
Validate a single TP4 prefill readiness probe before buying another 16-GPU PD run.
Do not retry the unchanged payload, relax output equality or jump to throughput.

307/307/306 hardware samples were collected for prefill-0/prefill-1/decode,
covering 4/4/8 sampled UUIDs. GPU activity falls to zero during the final wait;
these are startup/stall samples, not scored utilization. Sampled VRAM and server
metrics status are inspected in failure-inspection.json. Node CPU/RAM/network
counters are retained but have not been converted to per-worker demand/rates;
full locality/thread receipt review remains separate. No scoring phase, latency
tails, effective request concurrency or speculative acceptance counters exist.
PBS aggregate GPU statistics include values exceeding an 80-GB device and very
large accumulated low-utilization times; do not treat those fields as reliable
per-job peak VRAM or healthy device proof. Prefer bounded sampler data with
explicit coverage, and retain the raw scheduler record unchanged.

The accepted serving peaks and N62 submission stay unchanged. Full official
accuracy remains unverified. The new capacity contract is still conditional
on successful native integration, not permission to score this failed run.
