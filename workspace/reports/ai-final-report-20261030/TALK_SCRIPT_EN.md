# AI speaking script — English

Speaking version for the existing sixteen main AI slides, aligned with the revised Vietnamese script. Each paragraph develops one spoken idea. Values are rounded for delivery. Study notes at the end are not part of the talk. The AI target is twelve to thirteen minutes; this revision has not been delivered and timed in a live rehearsal.

## Slide 1 — Fast tokens count only when requests meet both latency limits

Our question is not simply how fast the model generates tokens. We must serve Qwen3-235B on two nodes with eight H200 GPUs each, using 4,000 input and 200 output tokens. A request qualifies only if its first token arrives within three seconds and average later-token gaps stay within twenty milliseconds. At least ninety percent of all requests, including errors, must meet both limits. So raw speed matters only when enough requests also meet the service conditions.

## Slide 2 — Three investigations support three different kinds of claim

Our work has three types of contribution.

First, the architecture decision: how should sixteen GPUs be divided between prompt processing and token generation? We explored different layouts, checked whether they could run, and retained a suitable configuration for further optimisation.

Second, a code change in the integration path of NIXL, an existing data-transfer library. We changed how transfer address lists were prepared: for the individual request, rather than by enumerating the reserved KV pool.

Third, integration and experiments with backend choices and client load. We used existing projects, including SGLang, NIXL, DeepGEMM, FlashInfer and HPC-Ops. Our contribution was checking compatibility, designing comparisons and selecting configurations based on measured results.

## Slide 3 — Replica count and parallel width compete for the same 16 GPUs

The first design question was how to use sixteen GPUs when prefill and decode both need resources.

More prefill workers can process more prompts independently. Giving decode more GPUs may help token generation. But both phases share the same sixteen-GPU budget, so giving more resources to one leaves fewer for the other.

We explored seventeen topology configurations to identify workable ways to divide the GPUs. These results helped narrow our choice for further investigation. They were not an exhaustive search of every possible configuration under the same load.

## Slide 4 — Two TP4 prefills feed one TP8 decode within the two-node budget

We retained two prefill workers and one decode worker. This arrangement fits the two nodes and completed both phases in later full benchmarks.

The first node runs two prefill workers, each using four GPUs to process long prompts. TP4 means four GPUs share the tensor computations of one worker. The second node runs one eight-GPU decode worker with TP8 and EP8. The same eight GPUs share tensor computations and distribute the model's experts.

This keeps each tensor-parallel group within one node. In exchange, after processing a prompt, prefill must send its KV attention state to the decode node so generation can continue. We therefore checked both connection setup and correct transfer.

## Slide 5 — Ready workers still failed before the first usable benchmark

While checking that transfer path, we encountered a historical branch where the workers loaded the model and reported ready, but a warmup request through prefill and decode did not finish within three hundred and sixty seconds. The benchmark had not started, so that attempt had no score.

Reading the source, we found that descriptor construction prepared address information for the reserved KV pool, although a request used only part of it. Descriptors list memory addresses and lengths; they are not the KV data itself.

We therefore tested reducing setup work by describing only the KV pages belonging to the request. The next slide explains the change and its correctness check.

## Slide 6 — Request-scoped descriptors remove work unrelated to the request

The patch has two steps. First, it creates descriptors only for KV pages belonging to the current request. Then it merges adjacent memory ranges into larger ranges to shorten the descriptor list.

For example, three consecutive ranges of one hundred bytes each can be described by one three-hundred-byte descriptor. The list becomes shorter, but the required bytes stay the same. If there is a gap between ranges, the merge must not include that gap.

We checked correctness with seven hundred and twenty CPU cases, comparing the byte ranges described by the old and new methods. All cases passed. The next step was testing the patch on the actual GPU serving path.

## Slide 7 — The patched path became usable; descriptor-only speedup is unknown

After changing descriptor construction, the prefill–decode pair completed warmup and a full benchmark with zero scored request errors.

The branch that had previously timed out had become a usable serving path. We retained the patch and continued performance experiments on that working end-to-end deployment.

## Slide 8 — Profiles identify candidates for investigation, not a proven time budget

Once serving worked, the next question was which computation paths were worth investigating.

A separate profile at forty-eight concurrent requests highlighted matrix multiplication, communication and attention work. These are operations visible in the profile. Kernel execution can overlap, so this chart does not divide the entire waiting time of one request into separate parts.

We also considered the difference between phases. Prefill processes many tokens together, while decode generates tokens sequentially, so the phases may benefit from different backends. We tested DeepGEMM for prefill with decode fixed, then used whole-service measurements to guide the decision. After improving prefill, we moved on to the decode choice.

## Slide 9 — Test the decode implementation while holding the serving setup fixed

Here, we compared two choices for the MoE computation in decode: letting SGLang select the backend automatically, and explicitly selecting HPC-Ops. HPC-Ops is an existing GPU operator library from Tencent.

Both used the same sixteen H200 GPUs, DeepGEMM prefill with a chunk size of eight thousand one hundred and ninety-two, and sixty concurrent requests. We kept GPU placement, workload, attention and transport unchanged to assess the effect of changing the decode backend.

The next slide presents the results.

## Slide 10 — Higher goodput came with slower first tokens and faster streaming

Compared with SGLang's automatic decode-backend selection, HPC-Ops increased goodput by about five point three percent under the same setup.

The tradeoff was that the first token arrived about one hundred and twenty-five milliseconds later on average, while the average gap between subsequent tokens fell by about one point six milliseconds. Requests started answering a little later, but then generated tokens faster, and the service produced more output from qualifying requests overall.

An independent run produced almost the same result. We therefore retained HPC-Ops for decode and continued tuning the number of concurrent requests.

## Slide 11 — N64 survives a full repeat; N68 loses its short-test advantage

When increasing concurrency, we needed to balance throughput against latency. More requests can keep the GPUs busy, but they can also increase waiting and push requests beyond the first-token limit.

Moving from sixty-two to sixty-four concurrent requests increased goodput by about one point one percent, and an independent run reproduced the result. Increasing to sixty-eight looked promising in a short test, but the full measurement improved by only about zero point zero eight percent over N64, below our one-percent usefulness threshold.

We therefore retained N64: it gave a clear improvement, while increasing load further brought little additional benefit. N64 means sixty-four concurrent client requests, not the number of GPUs or the decode batch size.

## Slide 12 — The remaining latency failures are first-token tails

After selecting N64, we wanted to understand what went wrong for requests that missed the SLA, rather than looking only at total goodput.

Each point in this chart is one request. The horizontal axis is time to first token, and the vertical axis is the average gap between tokens, both in milliseconds. The red lines mark the three-second and twenty-millisecond limits. A qualifying request must lie in the lower-left region, including the boundaries.

About ninety-eight point six percent of requests met both conditions. The blue-grey points are qualifying requests. The orange points are all to the right of the first-token boundary but still below the inter-token limit. These requests started answering late, but once they started, they generated tokens fast enough. There were twenty-seven such requests and no request errors.

Further improvement would therefore focus on investigating why some requests waited longer for their first token.

## Slide 13 — A complete portable run reproduces the retained operating level

The final package also had to become ready, serve real requests, pass the client result reader and clean up correctly. The first readiness check saw a healthy router before the model was registered, so it failed before a benchmark. We tightened readiness to wait for the model list and live workers, then ran accepted job 28197 on the retained recipe. It completed the deployment-to-client-to-cleanup chain and measured about three thousand and fifty-two good output tokens per second. With no matched control and no serving-recipe change, this is portable acceptance evidence, not an optimisation claim.

## Slide 14 — Direct H200 tests decide which H100 ideas transfer

We tested selected H100-derived ideas directly against fresh controls on sixteen H200s. The full transferred recipe lost, while changing its chunk recovered part of that branch: the matched chunk trial improved about 6.6 percent over its own 4096 control, yet remained about 4.5 percent below the H200 incumbent. Some phase-mode variants were positive, but by less than 0.14 percent; none of the tested alternatives cleared the one-percent usefulness gate. We kept the H200-specific recipe. These tests reject promotion under the measured conditions, not the libraries universally.

## Slide 15 — Better proxy metrics did not always improve qualifying throughput

Sparse graph capture reduced a logged memory proxy but slightly lowered goodput. A shallow speculative-decoding setting also lost goodput. We closed both tested branches instead of treating a lower counter or working feature as an improvement. A proxy can suggest a question; promotion requires the complete workload to improve useful output while meeting latency and answer-quality checks. These negative results narrowed the recipe and remain part of the evidence.

## Slide 16 — The retained recipe survives performance and quality checks

We close with three lessons. First, choose the phase split and backend for the target hardware; an H100 setting is not automatically an H200 setting. Second, retain full, repeated gains and reject short-test improvements that do not survive the useful-gain gate. Third, verify deployment and answer quality separately from performance. The accepted portable run reached about 3,052 good output tokens per second. On the same sixteen H200s and 12,032 MMLU-Pro questions, the optimised service answered 9,452 correctly against 9,460 for the stock FP8 reference: about 99.92 percent retention, above our local 99 percent point gate. This is a local full-set check, not BTC certification. I hand over to OpenFOAM.

## Backup 19 — Backup · full-set accuracy verification

If asked for detail: both deployments saw the same 12,032 questions once. The reference scored 78.6237 percent and the candidate 78.5572 percent, eight fewer correct answers in net. Invalid parsed answers and answers capped at 2,048 tokens stayed in the denominator. The 99.9154 percent figure is the candidate score divided by the reference score; it is not the fraction answered correctly. This is one complete local comparison, not statistical equivalence for future workloads or an organiser certificate. Replaying saved answers reproduced the counts.

## Backup 20 — Backup · request-scoped descriptor construction

The source comparison is about scope: the old path enumerated the reserved pool while a request uses only its own pages. The key correctness condition is that the new address-range list covers exactly the same required bytes, with the same transfer and notification meaning. The retained CPU geometry cases check this invariant. The 403.8-million pool-source entries per rank and 188 request ranges are useful scale illustrations only; they are not a speed ratio. No bandwidth, layout or scheduling alternative was disproved.

## Backup 21 — Backup · what the KV recovery run actually proves

The historical unpatched job 22271 timed out before scoring. Patched job 22294 completed real prefill/decode requests and the full N32 benchmark with zero scored errors. The run demonstrates that the changed path became usable. Because the unpatched path has no successful scored control and there is no isolated setup timer, descriptor-only speedup and root-cause attribution remain unknown.

## Backup 31 — Backup · real failures led to a complete portable acceptance

The exact package first failed readiness because the router responded before model registration completed. The bounded readiness repair waited for a valid model list and live workers. Accepted job 28197 then completed on sixteen H200s, passed P/D serving, client result reading, performance gates and cleanup, and measured 3,051.518 good output tokens per second. Historical full N64 runs averaged 3,044.40; a native run measured 3,045.50; an earlier valid replay at 2,830.92 remains unexplained. These are separate observations, not a matched optimisation comparison. The accepted job had no matched control and changed no serving recipe.

## Optional Q&A detail

Nine late H200 runs were reviewed. The fresh control scored 3,038.02; FA3 decode scored 2,999.25. The H100-derived full recipe scored 2,721.82. HPC-Ops prefill at chunks 6,144 and 8,192 scored 2,821.88 and 2,900.61. Decode-only and prefill-only inference-mode variants were slightly positive against their control, but each stayed below the one-percent usefulness gate. None displaced the retained recipe. See [FULL_RESULTS.md](../ai-quality-verification-20261103/FULL_RESULTS.md) and [MOCK_QA_EVIDENCE.md](MOCK_QA_EVIDENCE.md) for methods, evidence and limits. No live mock timing is claimed.

## Study notes for slide 8 — not spoken

- Prefill-only DeepGEMM test: job 24291 on sixteen H200 GPUs at N56 reached about 2,716 good output tokens/s, +1.81% against control 24263; approximately 98.82% of requests met the SLA. This is the prefill result, separate from the +5.3% decode comparison on slide 10.
- A later H200 HPC-Ops prefill test with the same chunk size of 8192 was about 4.52% below the DeepGEMM configuration. This is supporting evidence, not a trial that preceded the decode choice in the spoken sequence.
- A separate H100 Triton kernel screen found no useful gain in the tested cases. It is not a whole-model serving benchmark on H200.
- SGLang is the serving framework; NIXL handles data transfer; DeepGEMM and HPC-Ops supply computational implementations; FlashInfer supplies attention in the retained configuration. These projects are not interchangeable clients.
- Slide 8 shows profiling rather than a prefill comparison table. These additional figures are for study and Q&A. Slide 9 explains the decode comparison setup; slide 10 presents the decode outcome.

## Study notes for slide 7 — not spoken

The patch was retained because the changed path completed warmup and benchmarking. There is no successful unpatched scored run or isolated descriptor-construction timer to quantify a descriptor-only speedup. Do not assign the entire effect to a single cause. Supporting detail remains in the backup sections.
