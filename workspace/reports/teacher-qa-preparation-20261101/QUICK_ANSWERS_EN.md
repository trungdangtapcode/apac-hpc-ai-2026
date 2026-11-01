# Quick AI Q&A rehearsal cards — reasoning first

Start with [the thinking process](THINKING_PROCESS_EN.md): prior observation → mechanism/hypothesis → counterhypothesis → controlled test → lesson/decision. These are proposed spoken answers, not recorded original thoughts or a performed mock. Numbers are good output tokens/s unless stated otherwise. The [detailed guide](ANSWERS_EN.md) provides evidence, follow-ups and limits. Released slides and ZIP remain unchanged.

## Q1. Why choose two TP4 prefills and one TP8/EP8 decode worker?

We considered this split because prefill and decode perform different work and may benefit from different worker shapes. Two TP4 prefills and one TP8/EP8 decode worker fit the two-node allocation while keeping each TP group inside a node. The counter-risk was added KV transfer and an unbalanced pipeline. We therefore used compatibility and real-request gates, then full-run repeats to retain the operating point; we did not know its final score beforehand.

## Q2. What was the most significant bottleneck, and how did you identify it?

We first asked where progress stopped. Ready workers followed by failed pair warmup pointed to setup, rather than a scored steady-state bottleneck. Source inspection then gave us a narrow avoidable-work hypothesis to test. On later working deployments we checked which request deadline failed before proposing another fix. That is how observations narrowed the next question; they did not establish one universal bottleneck for the whole journey.

## Q3. Does profiling at N48 represent the selected N64 point?

Not quantitatively. N48 profiling gave us diagnostic leads: GEMM, collective-plus-normalisation and attention were visible components. Their percentages are shares of summed recorded kernel durations, which can overlap. N64 has separate request-level and sampled runtime evidence. We therefore do not transfer the N48 percentages into an N64 wall-time budget or claim that the profile proved which optimisation would work.

## Q4. What was wrong with KV transfer, and why try descriptors before bandwidth, layout or scheduling?

The failure occurred before scoring, and the source built metadata for the reserved KV pool although a request needed only a subset. That gave us a specific hypothesis: remove request-irrelevant setup work without changing the transferred ranges. We chose it because equivalence was cheap to check in 720 CPU cases before a GPU trial. We expected less metadata work; bandwidth, layout and scheduling remained possible competing causes.

## Q5. How much did the descriptor change improve end-to-end performance?

Our hypothesis was that constructing only the request ranges would remove unnecessary setup work and could make the failing path usable. We checked range equivalence, then tested real serving. The patched path completed warmup and a full N32 run at 1,422.96 good output tokens per second. That supports the engineering change, but no successful unpatched scored control exists, so a descriptor-only throughput improvement is still unknown.

## Q6. Can you isolate the contribution of each optimisation to goodput?

We did not assume an implementation had one fixed effect. Earlier results and the changed prefill runner and chunk gave us a new interaction to test. We compared decode choices with the same load and serving setup, then repeated the promising candidate. The full N60 comparison gained about 5.30%, with worse TTFT and better ITL. That supports the tested interaction; it does not let us add independent kernel speedups.

## Q7. Why did more concurrency increase TTFT? Queueing or computation? Did you inspect GPU usage?

After improving the service configuration, we rechecked the load instead of assuming the old concurrency remained best. More in-flight requests could improve pipeline work, but could also increase waiting. We used bounded full tests and repeats: N64 gained about 1.08% over N62, while N68 added only 0.083% and raised mean TTFT substantially. We therefore kept N64; sparse monitoring does not isolate the queue-versus-compute cause.

## Q8. How far has model quality been verified? Could FP8 change the answers?

Official model quality remains unverified by our team. The criterion is at least 99% of the organiser's reference score on the official accuracy evaluation; it is not 99% request success or exact answer-string equality. We used the supplied FP8 target and retained small smoke and retrieval checks as regression screens. Those checks do not replace the full official evaluation, so we do not claim quality certification or official ranking acceptance.

## Q9. Why run H100 experiments? How can they tell you what is better on H200?

H100 supplied hypotheses, not a prediction of H200 performance. We tested the full recipe on H200; it lost, but runner and chunk changed together. That prompted a narrower test: keep HPC-Ops and match the larger chunk. It recovered part of the losing branch but stayed below the H200 incumbent. The tests refined the explanation and supported retaining the H200-specific recipe rather than converting scores between GPUs.

## Q10. Which result should we defend, and how reproducible is it?

We wanted an improvement attributable to a repeatable setting rather than one lucky run. That is why a candidate needed its own fresh control, a useful margin and a repeat. Historical N64 runs averaged about 3,044.40 good output tokens per second. The higher cache point gained only 0.241% against its control and worsened p95 TTFT, so it did not displace the repeated operating choice.

## Q11. What did not work, and what did you learn?

We used failures to reject assumptions. Smaller graph capture memory looked promising as a resource change, but the full workload did not gain goodput. A functional shallow EAGLE path also lost throughput. Those observations told us that lower resource use and feature support were insufficient selection criteria. We closed the tested settings and kept the evidence, instead of accumulating optimisations that had not improved the actual objective.

## Q12. How would this behave on more nodes, GPUs or a different workload?

We have not measured that scaling, so we do not claim linear improvement beyond sixteen GPUs or beyond the fixed 4,000/200-token workload. More nodes would change the balance between replicas, model parallelism and cross-node KV or collective traffic. A different prompt/output ratio would also change prefill and decode demand. The H100-to-H200 tests already show why a configuration should be revalidated on its target system.

## Q13. Which contributions are actually yours?

Our work is the engineering investigation: selecting a usable topology and operating load, implementing and checking request-scoped heterogeneous-TP descriptor construction, validating actual runtime paths, and comparing candidates with controls and repeats. FlashInfer, DeepGEMM, HPC-Ops, MNNVL and the serving runtime are reused implementations. We distinguish our integration and experimental evidence from the kernels developed by their authors.

## Q14. What does the benchmark score actually mean?

AIPerf runs closed-loop at our selected concurrency, replacing completed requests with new ones rather than imposing a fixed arrival rate. Requested lengths are 4,000 input and 200 output tokens, with seed 2026 and cold prefixes. A request qualifies only if TTFT is at most 3,000 milliseconds and its mean ITL is at most twenty milliseconds. At least ninety percent of all requests must jointly qualify. The displayed score is exported Goodput in requests per second multiplied by 200.

## OpenFOAM handoff

The independent HPC speaker must explain the 128-ranks/node decision and variability using their CPU evidence. Do not fabricate that reasoning in the AI account.
