# Full matched N62/N64 confirmation

The sealed short job 25339 passes raw fixed 4000/200, seed 2026, cold-prefix, local
output and latency/SLA gates. N64 yields 2891.760212 good output tokens/s versus
2811.316116 at N62, a 2.861439% within-job gain. Both fractions exceed 0.96 and have
zero request errors/cancellations. This exceeds the prospective 1% screening gate,
but a short fixed-order pair is not a full ranking result.

Freeze two fresh equally observed deployments from the full observed 24964 recipe:
N62 control first, N64 candidate afterok the control. Each receives 16 H200 on two
nodes for at most 17 minutes, the actual partition ceiling. Each uses the full
60-second warmup,120-second measurement and 30-second grace. All operational
payload files are byte-identical; only job/config identity and offered concurrency
differ. Keep two TP4/EP1 DeepGEMM 8192 prefills, TP8/EP8 HPC-Ops decode, dense graphs
1..64, MNNVL, FlashInfer decode, round_robin, official FP8 target and BF16 KV.
Observer settings and collectors are identical across the pair.

Verify actual raw protocol, zero errors, joint SLA fraction>=0.90, output lengths,
short output regression and long 12-case checks, then compare candidate versus the
fresh full N62 control. Require at least 1% goodput gain before a further independent
repeat. Do not compare short 2891 directly against full 3023 as proof of regression,
or promote a single noisy score as global optimality. The observer-off best 24962
remains 3023.072304 until full eligible evidence supports a change. Fixed evaluation
order and deployment/node variation remain limits; replication precedes conclusions.

Collect role-specific scheduler queues/inflight/KV and bounded hardware telemetry,
phase markers, runtime/error logs, actual concurrency/latency tails and diagnostic
outputs. Inspect actual coverage; missing telemetry is not healthy/zero. Full
organiser accuracy remains unverified. No model conversion or new PBS SU is used.
Submit only under the existing queue lock/cap 5, with partition-time and definite
receipt checks. No background Codex, authentication change or HPC CPU access.

Exported lengths contain a recurring one-token variation despite fixed nominal200 request settings; see the short review. Do not claim every generated token-ID count was verified.
