Historical plan — superseded before GPU execution. The 22-minute request 25338 exceeded the actual 17-minute partition ceiling and was cancelled pending at zero runtime. See RESULTS.md. Preserve the original prospective text below; the next separately named bundle uses a short matched screen and validates the live partition limit.

# Observed H200 N62 to N64 load frontier

The exact independent N62 repeat 24962 passes full local gates at 3023.072304
good output tokens/s, agreeing with 24915's 3022.034919 within 0.034327%.
Both have about 98.727% joint-good requests, zero errors/cancellations and
mean/p95 request-mean ITL about 14.97/15.13 ms against the 20 ms threshold.
The worker explicitly captures decode graph batch sizes 1..64. N64 is the next
bounded offered-load question within that graph maximum; no higher load or
speedup follows automatically from this margin.

Use one fresh observed deployment: two TP4/EP1 DeepGEMM/chunk8192 prefills and
TP8/EP8 HPC-Ops decode, dense 1..64 graphs, FlashInfer, MNNVL, round_robin, native
FP8 target/BF16 KV and unchanged NIXL. The derived source is already frozen
24964's observed control. Benchmark, workers, samplers, phase markers, output
and post-score diagnostic files remain byte-identical to that control. Run
N62 and then N64 with the same observers and all serving settings held fixed.
The observer-off repeat remains context; compare N64 to its fresh observed
N62 rather than applying an assumed overhead correction to the old best.

Each point retains full closed-loop 4000/200, seed 2026, cold-prefix traffic,
60-second warmup/120-second measurement/30-second grace. The actual inherited
shell loop stops load increase on failed SLA/error/cancellation gate and does
not begin an under-budget point. Four CPU fixtures exercise both successful
points, failed control SLA, control request error and insufficient time. These
fixtures do not establish real load behavior.

Request one 22-minute allocation of 16 H200 / two nodes. One shared startup replaces
two separate 17-minute deployments; the extra five-minute ceiling allows a
second full point and unchanged post-score/output diagnostics, based on the
684-second one-point repeat. Adjust only the allocation/deadline ceiling, names
and offered load; no shortened scoring, quality shortcut or more CUDA graphs.
Under watcher.lock require room within five active/pending jobs and preserve
24964/24965/25051/25283. No PBS SU reservation or background scheduling.

Require both complete raw protocol/runtime/output gates, zero errors or
cancellations, joint SLA >=0.90 and at least 1% N64 canonical goodput gain versus
same-job N62 before confirmation. Inspect actual resolved graph/policy/dtype,
TTFT/ITL tails, phase-aligned sampler/queue/running/KV and logs; mark unavailable
CPU/network conclusions unknown. Do not pool the two order-dependent points as
independent observations. A gain needs a later independent or reverse-order
confirmation; a loss/subthreshold result closes this exact load increase and
returns to a distinct supported hypothesis. Official >=99% reference accuracy
remains unverified. No submission promotion or global-optimum claim.
