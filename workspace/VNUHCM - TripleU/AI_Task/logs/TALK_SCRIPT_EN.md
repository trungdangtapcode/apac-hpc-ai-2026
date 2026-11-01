# AI speaker script — English

Proposed spoken script for the 16-slide AI route. This has not been delivered or timed by the team. Rehearse to approximately 10–11 minutes and leave the agreed OpenFOAM time inside the combined 15–20-minute talk. The public rules allow a separate 10-minute Q&A. The AI and HPC speakers must agree the split; the 10–11 minute AI target leaves at least four minutes for HPC if the combined talk is the 15-minute minimum.

## Slide 1 — The score has a latency condition

Our task is to serve Qwen3-235B on two nodes with eight H200 GPUs each. The workload is fixed at 4,000 input tokens and 200 generated output tokens. A request counts only when its first token arrives within three seconds and its average gap between later tokens is within twenty milliseconds. At least ninety percent of all requests, including errors, must meet both limits. So the goal is useful goodput under a service constraint, not raw token speed alone.

## Slide 2 — Three kinds of work

We separate three claims. Choosing how to split a fixed GPU budget is an engineering decision. Repairing request-scoped KV transfer setup is our implementation work. Measuring backend and load choices is an experimental finding. We use existing runtime kernels; our evidence is about how we configured and tested the service, not claiming we invented those kernels. This lets us ask first whether a design can run, then whether it helps the measured objective.

## Slide 3 — Why this topology was retained

Seventeen usable topology observations helped us find layouts that could load the FP8 model and serve the two phases. The displayed examples reached different loads, N32, N40 and N48, so their scores cannot rank the layouts by one controlled factor. We retained the two TP4 prefill workers and one TP8/EP8 decode worker because it fit the two-node allocation, passed the required geometry and phase checks, and gave us a usable path that later measurements could repeat. That is a practical operating choice. We did not prove it is the global optimum.

## Slide 4 — Where the work runs

The first node has two prefill workers, each tensor-parallel across four GPUs. Tensor parallelism splits model computations across GPUs; expert parallelism distributes the experts in this mixture-of-experts model. They process the long prompt and send the resulting key-value state across the node boundary through NIXL. The second node has one decode worker using eight-way tensor and expert parallelism to generate the answer. Keeping tensor-parallel groups within their node respects the hardware layout. The tradeoff is that every request must transfer KV state between prefill and decode.

## Slide 5 — A concrete failure before scoring

We investigated a historical heterogeneous-parallelism branch. The model workers loaded and became ready, but the prefill/decode pair failed its warmup after three hundred sixty seconds. AIPerf never produced a score. This tells us the failure was before steady-state benchmarking; it does not tell us which setup component caused it. In source inspection we noticed that descriptor construction appeared to enumerate the reserved KV pool, so we chose that bounded setup path for a first check.

## Slide 6 — Why try descriptors first

The reason was practical and testable: source code showed request setup describing pool regions unrelated to one request, while the proposed change would describe only that request's pages and combine adjacent ranges. We could cheaply test whether the byte ranges stayed equivalent before spending another full serving run. Seven hundred twenty CPU geometry cases passed. The slide compares about 403.8 million source entries per rank for a pool with 188 coalesced ranges for one four-thousand-token request. They are different scopes, not a speed ratio. We did not measure bandwidth, compare KV layouts or rule out scheduling as a cause.

## Slide 7 — What the repair actually established

On the patched path, both model workers were ready and pair warmup completed in about 0.68 to 0.70 seconds per request. A full N32 run measured 1,422.96 good output tokens per second, with 95.87 percent of requests meeting the joint latency rule and no scored errors. That shows this patched path could serve the benchmark. The earlier unpatched path timed out before scoring, so there is no successful unpatched control and no descriptor-only end-to-end speedup. We should not divide the timeout by the patched warmup and call it an acceleration factor.

## Slide 8 — Profiling gives leads, not a cause

A separate N48 diagnostic recorded GPU kernel durations. GEMM, collective plus normalization, and attention were visible candidates. Those percentages are fractions of summed kernel duration; overlapping work means they are not fractions of total request time. Separately, N64 requests show first-token deadline misses, but no per-request phase timing tells us whether they waited in queue, spent longer in prefill, transferred KV slowly or computed more. We use profiling to choose what to investigate, not to announce a proven bottleneck.

## Slide 9 — A separate controlled decode probe

The next result is a separate experiment. We compared a fresh automatic-decode control with a supported HPC-Ops decode implementation at full N60. The topology, prefill implementation and chunk, workload, attention and transport were held fixed. We ran it because decode implementation was a plausible service-level direction among several candidates. The profile percentages did not prove it was the fix. The matched control and repeat are the evidence for the measured configuration.

## Slide 10 — Throughput and latency moved in different directions

Good output throughput rose from 2,838.85 to 2,989.17 tokens per second, about 5.30 percent. Mean time to first token got 125 milliseconds slower, while mean inter-token latency improved by about 1.64 milliseconds. The independent treatment repeat was within 0.033 percent of the original treatment. We therefore kept this tested configuration for further operating-point work, while explaining its first-token tradeoff. This is not an isolated proof about one kernel or a gain that can be added to every other change.

## Slide 11 — Choose N64 from full tests

We compared full N62 and N64 loads. Good output throughput increased about 1.08 percent at N64, then a separate full N64 repeat was essentially unchanged. The N68 short run looked better, but its full result improved only about 0.08 percent and did not reach our team-set one-percent usefulness threshold. We retained N64 as a repeatable operating point. Concurrency here means client requests in flight; it is not GPU count or decode batch size.

## Slide 12 — Which requests miss the rule

The request-level plot comes from a separate full N64 run. Of 1,902 requests, 1,875 met both limits. The 27 misses all exceeded the first-token threshold; none exceeded the mean inter-token threshold, and there were no scored request errors. This identifies the failing metric for that run. It does not diagnose the server-side cause of those slow first tokens.

## Slide 13 — Repeats beat a single peak

Three earlier full N64 runs averaged 3,044.40 good output tokens per second. A separate native run measured 3,045.50, consistent with that operating level. A cache trial reached 3,048.45, but improved only 0.24 percent over its own fresh control, below the one-percent gate. An older valid replay was materially lower and its cause is unresolved. We therefore describe a repeated operating level and preserve the drift, rather than claiming the highest isolated number is the stable winner.

## Slide 14 — Test H100 ideas on H200

H100 helped us screen compatibility and candidate settings, but an H100 score cannot rank an H200 configuration. We then tested selected settings against a fresh control on the same sixteen H200 GPUs. The transferred full H100 recipe scored 2,721.82, about 10.41 percent below the H200 control. FA3 decode was 1.28 percent lower. Two HPC-Ops chunk settings and two phase-mode settings also failed to beat the control by our one-percent gate. These results tell us to keep the H200-specific recipe. They do not prove those libraries are universally slower on every use case.

## Slide 15 — Reject improvements to a proxy

Some changes improved a resource measure without improving the service objective. Sparse decode graphs reduced logged capture memory but goodput was slightly lower than its comparison. A shallow speculative-decoding run also lost goodput. We closed those tested settings. A smaller memory counter or a functioning feature is not enough unless the complete workload improves while meeting the latency and quality requirements.

## Slide 16 — State the limit and hand over

Our current conclusion is a repeatably measured H200 operating recipe: DeepGEMM prefill with chunk size 8,192 and HPC-Ops decode using FlashInfer attention and MNNVL collectives and NIXL cross-role KV transfer at N64. We have not established global optimality. The official full model-quality check against the organiser reference remains unknown, and we have not completed a fresh full GPU replay after repairing the portable result readers. I will now hand the talk to our OpenFOAM presenter, who owns the CPU results.

## Backup for Q&A

Nine additional H200 allocations from 31 October were reviewed. Fresh control 27777 scored 3,038.02; FA3 decode 27779 scored 2,999.25. The H100-derived full recipe at N64, job 27783, scored 2,721.82. HPC-Ops prefill at chunk 6,144 and 8,192 scored 2,821.88 and 2,900.61. Decode-only and prefill-only inference-mode ports scored 3,039.36 and 3,043.14 against their explicit control at 3,039.17. None passed the team's one-percent usefulness rule, so none displaced the selected recipe. All nine completed with local checks; that is not the organiser's quality certification.
