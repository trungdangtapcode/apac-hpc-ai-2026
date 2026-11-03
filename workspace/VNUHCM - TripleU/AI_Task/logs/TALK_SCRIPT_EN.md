# AI speaker script — English

**Rehearsal draft for the 16-slide AI route.** The script is designed for about 12:30 including pauses, at an estimated 115–125 spoken words per minute. It has not been delivered or timed in a live mock. The public slot is 15–20 minutes for AI and HPC together, followed by 10 minutes of Q&A; the team must agree the split. This AI target leaves about 7:30 in a 20-minute combined slot for HPC. If the total slot is 15 minutes, the team must agree a shorter AI cut before rehearsal.

## Slide 1 — Fast tokens count only when requests meet both latency limits

Our question is not simply how fast the model generates tokens. We must serve Qwen3-235B on two nodes with eight H200 GPUs each, using 4,000 input and 200 output tokens. A request qualifies only if its first token arrives within three seconds and average later-token gaps stay within twenty milliseconds. At least ninety percent of all requests, including errors, must meet both limits. So raw speed matters only when enough requests also meet the service conditions.

## Slide 2 — Three investigations support three different kinds of claim

We separate three kinds of claim. The team made a deployment decision about dividing GPUs between prompt processing and generation; we made a bounded implementation change to one KV-transfer setup path; and we measured backend and client-load choices. We reused SGLang, NIXL, DeepGEMM, FlashInfer and HPC-Ops, which are existing projects, not our inventions. Our contribution is local integration, compatibility checks and evidence-based selection. These investigations ask different questions, so their evidence should not be conflated.

## Slide 3 — Replica count and parallel width compete for the same 16 GPUs

The first design question is how to use sixteen GPUs when prefill and decode compete for the same resources. More prefill replicas can process prompts independently; a wider decode worker can use more GPUs for generation. But each choice leaves fewer GPUs for the other phase. We retained two TP4/EP1 prefill workers feeding one TP8/EP8 decode worker because this split fit both nodes, passed model-geometry and phase checks, and supported later full tests. The evidence supports a feasible operating layout, not a controlled ranking of every possible split or a global optimum.

## Slide 4 — Two TP4 prefills feed one TP8 decode within the two-node budget

On node one, two prefill workers each use four GPUs to process long prompts. Tensor parallel divides model operations across GPUs; expert parallel distributes experts in this mixture-of-experts model. They send KV state—the temporary attention state needed to continue generation—to a decode worker on node two, using eight GPUs to generate the answer token by token. This split gives the phases different worker shapes and keeps each tensor-parallel group within a node. The tradeoff is a transfer between roles for every request, which led to a separate investigation of setup and correctness.

## Slide 5 — Ready workers still failed before the first usable benchmark

That transfer question came from a historical branch. Workers loaded and became ready, but the prefill/decode pair did not complete warmup within 360 seconds. AIPerf never started, so there was no score. We knew the failure was between worker readiness and a usable paired request, but not its cause. Source inspection showed descriptor construction enumerating the reserved KV pool. A descriptor is an address-range list, not the KV data itself. This made setup metadata a narrow first hypothesis, not a measured diagnosis of the timeout.

## Slide 6 — Request-scoped descriptors remove work unrelated to the request

Why examine address lists before changing bandwidth, KV layout or scheduling? We had not ruled those alternatives out. Source code showed that setup described pool regions unrelated to an individual request. The proposed change was to construct only the address ranges for that request, while preserving the same byte coverage and transfer meaning. That correctness invariant could be checked cheaply on CPU before another distributed run. Seven hundred twenty geometry cases passed. The reasoning was that avoiding irrelevant metadata was a testable first step—not that fewer descriptors guaranteed faster serving.

## Slide 7 — The patched path became usable; descriptor-only speedup is unknown

With the patch, the real pair completed warmup, served actual requests and finished a full benchmark with zero scored errors. That moved the branch from a pre-benchmark timeout to a usable serving path. But the unpatched branch never produced a successful scored control, and there is no isolated initialization timer. We therefore cannot claim a descriptor-only speedup or assign the whole change to this one mechanism. We retained a bounded implementation that worked end to end, while leaving the size and cause of any performance effect unknown.

## Slide 8 — Profiles identify candidates for investigation, not a proven time budget

A separate N48 diagnostic highlighted compute, communication and attention work. Summed kernel durations overlap; they do not prove where request time is lost. Another important clue was phase specificity: an earlier DeepGEMM decode setting failed the latency gate, but that did not answer whether DeepGEMM would suit prefill, where many prompt tokens are processed together. Testing prefill separately, with decode fixed, was therefore worth trying. This phase-and-shape explanation is retrospective; we do not claim the profile predicted the winner. The evidence comes from the controlled measurements and repeat.

## Slide 9 — Test the decode implementation while holding the serving setup fixed

After changing prefill and its chunk size, we asked whether the earlier decode choice still held under the new operating conditions. This justified revisiting an existing implementation instead of repeating an unchanged losing experiment. We compared fresh automatic-decode control with HPC-Ops decode at full N60, holding topology, prefill, chunk, workload, attention and transport fixed. If the whole service improved and repeated, we could retain that configuration. If it only improved an internal counter or violated the SLA, we would reject it. The experiment tests that decision; it does not identify one causal kernel.

## Slide 10 — Higher goodput came with slower first tokens and faster streaming

Good output throughput rose about 5.30 percent. Mean time to first token worsened by about 125 milliseconds, while mean inter-token latency improved by about 1.64 milliseconds. An independent treatment repeat closely reproduced the result. We retained this tested configuration for further load work, carrying the slower first token forward as a real tradeoff. This is a repeated configuration-level finding for this workload, not proof of one kernel’s mechanism or a gain to add mechanically to other experiments.

## Slide 11 — N64 survives a full repeat; N68 loses its short-test advantage

After changing the backend, we revisited client concurrency. More in-flight requests might help overlap work, or increase waiting and first-token latency. Full N62/N64 tests showed about 1.08 percent more good output throughput at N64, followed by a nearly identical independent N64 repeat. A short N68 test looked promising, but the full result improved only about 0.08 percent, below our one-percent usefulness gate. We retained N64 and closed that N68 branch. Concurrency means client requests in flight, not GPUs or decode batch size.

## Slide 12 — The remaining latency failures are first-token tails

In a separate full N64 run, 1,875 of 1,902 requests met both latency limits. All 27 misses exceeded the first-token threshold; none exceeded average inter-token latency, and there were no scored errors. This tells us which service condition failed. It does not explain why: without phase timing, we cannot assign slow first tokens to queueing, prefill, transfer or another cause. We report the measured symptom and leave internal attribution open.

## Slide 13 — A complete portable run reproduces the retained operating level

The final package also had to become ready, serve real requests, pass the client result reader and clean up correctly. The first readiness check saw a healthy router before the model was registered, so it failed before a benchmark. We tightened readiness to wait for the model list and live workers, then ran accepted job 28197 on the retained recipe. It completed the deployment-to-client-to-cleanup chain and measured 3,051.52 good output tokens per second. With no matched control and no serving-recipe change, this is portable acceptance evidence, not an optimisation claim.

## Slide 14 — Direct H200 tests decide which H100 ideas transfer

We tested selected H100-derived ideas directly against fresh controls on sixteen H200s. The full transferred recipe lost, while changing its chunk recovered part of that branch: the matched chunk trial improved 6.57 percent over its own 4096 control, yet remained 4.52 percent below the H200 incumbent. Some phase-mode variants were positive, but by less than 0.14 percent; none of the tested alternatives cleared the one-percent usefulness gate. We kept the H200-specific recipe. These tests reject promotion under the measured conditions, not the libraries universally.

## Slide 15 — Better proxy metrics did not always improve qualifying throughput

Sparse graph capture reduced a logged memory proxy but slightly lowered goodput. A shallow speculative-decoding setting also lost goodput. We closed both tested branches instead of treating a lower counter or working feature as an improvement. A proxy can suggest a question; promotion requires the complete workload to improve useful output while meeting latency and answer-quality checks. These negative results narrowed the recipe and remain part of the evidence.

## Slide 16 — The retained recipe survives performance and quality checks

We close with three lessons. First, choose the phase split and backend for the target hardware; an H100 setting is not automatically an H200 setting. Second, retain full, repeated gains and reject short-test improvements that do not survive the useful-gain gate. Third, verify deployment and answer quality separately from performance. The accepted portable run reached about 3,052 good output tokens per second. On the same sixteen H200s and 12,032 MMLU-Pro questions, the optimised service answered 9,452 correctly against 9,460 for the stock FP8 reference: 99.9154 percent retention, above our local 99 percent point gate. This is a local full-set check, not BTC certification. I hand over to OpenFOAM.

## Backup 19 — Backup · full-set accuracy verification

If asked for detail: both deployments saw the same 12,032 questions once. The reference scored 78.6237 percent and the candidate 78.5572 percent, eight fewer correct answers in net. Invalid parsed answers and answers capped at 2,048 tokens stayed in the denominator. The 99.9154 percent figure is the candidate score divided by the reference score; it is not the fraction answered correctly. This is one complete local comparison, not statistical equivalence for future workloads or an organiser certificate. Replaying saved answers reproduced the counts.

## Backup 20 — Backup · request-scoped descriptor construction

The source comparison is about scope: the old path enumerated the reserved pool while a request uses only its own pages. The key correctness condition is that the new address-range list covers exactly the same required bytes, with the same transfer and notification meaning. The retained CPU geometry cases check this invariant. The 403.8-million pool-source entries per rank and 188 request ranges are useful scale illustrations only; they are not a speed ratio. No bandwidth, layout or scheduling alternative was disproved.

## Backup 21 — Backup · what the KV recovery run actually proves

The historical unpatched job 22271 timed out before scoring. Patched job 22294 completed real prefill/decode requests and the full N32 benchmark with zero scored errors. The run demonstrates that the changed path became usable. Because the unpatched path has no successful scored control and there is no isolated setup timer, descriptor-only speedup and root-cause attribution remain unknown.

## Backup 31 — Backup · real failures led to a complete portable acceptance

The exact package first failed readiness because the router responded before model registration completed. The bounded readiness repair waited for a valid model list and live workers. Accepted job 28197 then completed on sixteen H200s, passed P/D serving, client result reading, performance gates and cleanup, and measured 3,051.518 good output tokens per second. Historical full N64 runs averaged 3,044.40; a native run measured 3,045.50; an earlier valid replay at 2,830.92 remains unexplained. These are separate observations, not a matched optimisation comparison. The accepted job had no matched control and changed no serving recipe.

## Optional Q&A detail

Nine late H200 runs were reviewed. The fresh control scored 3,038.02; FA3 decode scored 2,999.25. The H100-derived full recipe scored 2,721.82. HPC-Ops prefill at chunks 6,144 and 8,192 scored 2,821.88 and 2,900.61. Decode-only and prefill-only inference-mode variants were slightly positive against their control, but each stayed below the one-percent usefulness gate. None displaced the retained recipe. See FULL_RESULTS.md (source: `FULL_RESULTS.md`, retained outside this compact package) and [MOCK_QA_EVIDENCE.md](<MOCK_QA_EVIDENCE.md>) for methods, evidence and limits. No live mock timing is claimed.
