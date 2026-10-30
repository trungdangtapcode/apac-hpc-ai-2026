# Panel Q&A preparation

These rehearsal questions reflect feedback supplied by the team, not an official question list. Research remains stopped. Proposed diagnostic methods below are not claimed as completed work.

## Answer with the right evidence level

**Observation** is what a measurement records. **Hypothesis** is the explanation that motivated a test. **Supported conclusion** is what that test/repetition establishes at its configuration. **Unknown** is what was not measured or could not be separated.

Use four short parts: **what happened → what we tested → how we know → limit.**

## What was your biggest bottleneck?

“Early deployment had a concrete transport-setup problem: descriptor preparation scaled with the entire KV pool. Source and cold-start/geometry records motivated request-scoped descriptors, followed by range, real-transfer and response checks. That identifies an early setup problem; it does not prove one global bottleneck in the mature service.”

“The separate profile showed substantial named GEMM, collective and attention work. It motivated controlled trials, but those kernel-duration sums are not a causal end-to-end latency breakdown.”

Use evidence card 1 and slide 13. State that hardware-collection coverage varies by run.

## Why can higher concurrency increase TTFT without improving throughput?

“Our full N62-to-N64 pair gains about 1.083%, while mean TTFT rises from about 1038 to 1110 ms. The N68 full gain was only 0.083%, despite a favorable short screen. N64 had a useful full gain and an independent repeat.”

“Client concurrency controls pipeline inflight requests, not decode batch size directly. Queue pressure, batching, transfers and compute can all contribute. We did not separately measure every request stage.”

The example in the feedback about 8→16 is not one of our claimed pairs; do not present it as our data.

## Was the extra TTFT queueing or computation?

“We observed client TTFT and role queue/running/KV gauges, with later hardware samples. They are sparse and cross-host clocks were not calibrated. They cannot reconstruct each request's stage budget. A causal distinction would need correlated enqueue/dequeue, prefill, KV-transfer and first-decode spans with aligned clocks.”

“We state the observed tradeoff and supported goodput result. Queueing versus computation remains a hypothesis.”

Do not infer queue time from average TTFT and ITL alone.

## Did you measure GPU utilization?

“In later derived full runs, yes: per-role five-second GPU/VRAM/power/temperature/clocks, host CPU/memory and server samples. Separate rank profiles were also retained. The older 24913 extended inspection does not contain a dedicated continuous hardware series.”

“GPU activity is not FLOP utilization; VRAM allocation is not KV token occupancy; zero sampled queue is not proof of an always-empty queue. Named kernel-duration sums are not wall-clock shares.”

Use the exact run's collection scope, not telemetry from an unrelated deployment.

## Why this parallelism and disaggregated topology?

“We measured alternative allocations. Two TP4 prefills feed one TP8/EP8 decode on the second node, keeping tensor-parallel groups within a node and transferring request KV through NIXL.”

“FP8 geometry also constrained choices: a TP8/EP1 MoE split produced 192-element partitions against 128-wide blocks. EP2 produced 384-element partitions, but it was a different layout and still needed response/performance validation.”

Do not claim universal optimality or extrapolate beyond the tested resource range.

## What is the strongest evidence of improvement?

“The N60 matched full model comparison is 24912 at 2838.853 versus 24913 at 2989.175, about +5.295%. An independent treatment repeat was only about 0.033% below the original. This supports the tested backend interaction.”

“The N62-to-N64 gain was about +1.083% and survived an independent deployment. These are stronger claims than the isolated cache peak, whose +0.241% did not pass our useful-gain gate.”

Use the evidence cards to explain latency tradeoffs and missing hardware coverage. Do not add component gains linearly.

## Which results ran on official infrastructure?

“The main H200 experiments ran on the organiser-provided Firmus cluster. H100 was measured separately on NSCC ASPIRE 2A+. Historical H200 pairs used Slurm/Pyxis; later native Enroot and portable replay have separate records.”

“These are our locally reviewed measurements on provided infrastructure, not an organiser-issued ranking or quality certificate. Official full-set model accuracy remains unverified.”

The final package records SGLang 0.5.17, router 0.3.2, NIXL 1.3.2 and AIPerf 0.12.0 with image hashes/checkpoint metadata. Per-run records govern historical claims; a shared image filename alone does not prove historical byte identity.

## Is your best score 3,055.33 or 3,048.45?

“3,048.45 is the highest complete local full pass. Its cache difference is only +0.24%, so we keep replicated N64.”

“3,055.33 is recovered portable raw evidence: the client and both routes completed, but the original job failed in postprocessing. Corrected readers later passed compute-only replay. That does not rewrite the failed job or establish a complete post-repair allocation.”

“The selected historical three-run mean, 3,044.40, is a separate repeated series.”

## What failed, and what did you learn?

Choose one coherent story:

- EAGLE: all-worker SLA failure → wrong KV-validator assumption → corrected decode-only short pass but −4.74% → shallow full pass but −2.08% → close tested branches.
- Prefetch: first order suggested 18.74% walltime saving; reverse order saved only 9.84%, below the 10% gate → no promotion.
- Sparse graphs: capture memory fell 1.15→0.36 GB/rank, but goodput was −0.37% → a better resource metric did not improve the service objective.
- Portable replay: static checks passed; real jobs exposed namespace and canonical-path defects → preserve failures and verify the smallest exact repair.

Explain the reasoning, not a list of failed job IDs.

## Why not another framework or more quantization?

“The task fixes the target and quality requirement. Our results retain the provided FP8 checkpoint. A library headline, unsupported model path or primitive benchmark does not establish a faster complete service.”

“Full Qwen compile failed a concrete native RoPE/KV interface. C++ tree CPU fixtures passed, but do not establish model integration or serving speed. We do not present an untested framework or low-bit target as an improvement.”

## How does it scale beyond 16 GPUs or to another workload?

“We measured particular layouts within the 16-GPU serving envelope and the 4,000/200 load. We do not have a validated curve beyond that or across arbitrary context/output lengths. Communication, expert distribution, KV traffic and phase balance can change.”

“The H100/H200 anchor is one local system calibration, not a universal hardware multiplier.”

## What remains unverified?

“Official full-set quality and a whole-allocation portable replay after the reader repair. Local smoke/retrieval do not certify the at-least-99%-of-reference gate. The published recipe requests 200 tokens; client-retokenized counts are not authoritative generated IDs.”

“More causal performance analysis would need correlated per-request phase spans. Any compile remedy would need a compatible full-model startup and an appropriate matched control.”

These are proposed next steps, not newly scheduled or completed work.

## Team handoff

The first answer owner gives the conclusion and evidence class. A support member adds the exact baseline, configuration or limitation. If evidence is missing, say so. Keep the final PDF, evidence cards and relevant source reviews ready; avoid searching an unfamiliar CLI live.
