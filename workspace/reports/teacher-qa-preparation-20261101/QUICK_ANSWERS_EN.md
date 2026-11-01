# Quick AI Q&A rehearsal cards

Proposed answers, not a performed mock. Numbers are good output tokens/s unless stated otherwise. The [detailed guide](ANSWERS_EN.md) adds follow-up answers, slide numbers, sources and limits. No change to the released PowerPoint or ZIP.

## Q1. Why choose two TP4 prefills and one TP8/EP8 decode worker?

We selected a practical operating layout under the fixed two-node, sixteen-H200 budget. It passed FP8 parallel-shape compatibility, completed real prefill-to-decode requests and later supported full-run latency-qualified repeats. Keeping tensor-parallel groups within a node also avoided a cross-node tensor group. The seventeen topology observations helped constrain the choice, but their different loads do not prove this layout is globally best.

## Q2. What was the most significant bottleneck, and how did you identify it?

We distinguish a deployment blocker from a steady-state performance bottleneck. On one historical branch, workers were ready but pair warmup timed out before any benchmark score; that made setup a concrete investigation target. Later N64 request records show that the remaining deadline failures are first-token failures. They identify the failed latency condition, but we have not isolated a single dominant server-side cause of those tails.

## Q3. Does profiling at N48 represent the selected N64 point?

Not quantitatively. N48 profiling gave us diagnostic leads: GEMM, collective-plus-normalisation and attention were visible components. Their percentages are shares of summed recorded kernel durations, which can overlap. N64 has separate request-level and sampled runtime evidence. We therefore do not transfer the N48 percentages into an N64 wall-time budget or claim that the profile proved which optimisation would work.

## Q4. What was wrong with KV transfer, and why try descriptors before bandwidth, layout or scheduling?

The symptom was a pre-score warmup timeout, not a measured bandwidth limit. Source inspection exposed request setup enumerating the reserved KV pool, including regions unrelated to the immediate request. We chose request-scoped descriptor construction because it was a narrow, source-visible hypothesis and we could cheaply check byte-range equivalence before another distributed run. We did not measure away bandwidth, layout or scheduling as competing causes.

## Q5. How much did the descriptor change improve end-to-end performance?

We cannot give a descriptor-only end-to-end percentage. The unpatched attempt timed out before scoring, so it is not a successful throughput baseline. The patched attempt completed real P/D warmup in about 0.68–0.70 seconds per request after workers were ready, then a full N32 benchmark reached 1,422.96 good output tokens per second with 95.87% joint latency success and zero scored errors. That demonstrates a usable patched path, with causal attribution still limited.

## Q6. Can you isolate the contribution of each optimisation to goodput?

Only for comparisons supported by their controls, and even then at the tested service-configuration scope. At full N60, the automatic-decode control reached 2,838.85 and the HPC-Ops treatment repeat reached 2,989.17 good output tokens per second, about 5.30% higher. The intended change was decode implementation. That is stronger than the historical progression chart, but it does not identify one kernel's causal contribution or justify adding all optimisation gains together.

## Q7. Why did more concurrency increase TTFT? Queueing or computation? Did you inspect GPU usage?

More in-flight requests can keep the pipeline busy, but they can also increase waiting or contention. In the full N64/N68 comparison, goodput rose only 0.083%, while mean TTFT rose from about 1,113.6 to 1,347.1 milliseconds. We did inspect role-specific queues, running requests, GPU activity, memory and power. Those sparse samples do not separate each request's queue wait from computation, so we report the tradeoff without assigning an unproved cause.

## Q8. How far has model quality been verified? Could FP8 change the answers?

Official model quality remains unverified by our team. The criterion is at least 99% of the organiser's reference score on the official accuracy evaluation; it is not 99% request success or exact answer-string equality. We used the supplied FP8 target and retained small smoke and retrieval checks as regression screens. Those checks do not replace the full official evaluation, so we do not claim quality certification or official ranking acceptance.

## Q9. Why run H100 experiments? How can they tell you what is better on H200?

H100 was a second experimental platform for screening compatible settings and hypotheses; its scores do not rank H200 configurations. We therefore tested selected alternatives directly against fresh H200 controls. The transferred full H100 recipe at N64 reached 2,721.82 versus the H200 control's 3,038.02, a 10.41% loss. The additional chunk and phase-mode ports also failed our useful-gain gate, so the direct evidence supports retaining the H200-specific recipe.

## Q10. Which result should we defend, and how reproducible is it?

Defend the retained N64 operating recipe, not the single largest number. Three historical full H200 runs average 3,044.40 good output tokens per second; a separate native run reached 3,045.50. A cache trial was higher at 3,048.45 but only 0.241% above its own control, below the useful-gain gate. We retain the repeated operating level while preserving lower runs and the limits of hardware diversity and statistical evidence.

## Q11. What did not work, and what did you learn?

We learned to separate a promising proxy from the full service objective. Sparse decode graphs reduced logged capture memory from 1.15 to 0.36 gigabytes per rank, but measured goodput was 0.37% lower than its comparison. A shallow EAGLE3 full trial lost about 2.08%. We closed those tested settings rather than promoting a smaller memory counter or a functioning feature as a performance improvement.

## Q12. How would this behave on more nodes, GPUs or a different workload?

We have not measured that scaling, so we do not claim linear improvement beyond sixteen GPUs or beyond the fixed 4,000/200-token workload. More nodes would change the balance between replicas, model parallelism and cross-node KV or collective traffic. A different prompt/output ratio would also change prefill and decode demand. The H100-to-H200 tests already show why a configuration should be revalidated on its target system.

## Q13. Which contributions are actually yours?

Our work is the engineering investigation: selecting a usable topology and operating load, implementing and checking request-scoped heterogeneous-TP descriptor construction, validating actual runtime paths, and comparing candidates with controls and repeats. FlashInfer, DeepGEMM, HPC-Ops, MNNVL and the serving runtime are reused implementations. We distinguish our integration and experimental evidence from the kernels developed by their authors.

## Q14. What does the benchmark score actually mean?

AIPerf runs closed-loop at our selected concurrency, replacing completed requests with new ones rather than imposing a fixed arrival rate. Requested lengths are 4,000 input and 200 output tokens, with seed 2026 and cold prefixes. A request qualifies only if TTFT is at most 3,000 milliseconds and its mean ITL is at most twenty milliseconds. At least ninety percent of all requests must jointly qualify. The displayed score is exported Goodput in requests per second multiplied by 200.

## OpenFOAM handoff

The independent HPC speaker must answer why 128 MPI ranks/node and explain measured variability from their own CPU evidence. Hand over rather than inventing those explanations.
