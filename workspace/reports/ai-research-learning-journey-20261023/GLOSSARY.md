# Quick glossary

- **AIPerf:** The benchmark client used to generate requests and measure latency and goodput.
- **CUDA graph:** A captured sequence of GPU operations that can be replayed with less CPU launch work. A graph batch-size range is not the same as client concurrency.
- **Collective / all-reduce:** Work that combines partial tensor results across GPUs. This differs from sending a request’s KV cache between prefill and decode workers.
- **Decode:** The repeated step that generates output tokens after prompt processing.
- **EP (expert parallelism):** Splits a mixture-of-experts model's experts across GPUs.
- **Goodput:** Requests per second that satisfy both TTFT and ITL limits. The contest expresses the same ranking value as good output tokens/s by multiplying by 200.
- **H100 / H200:** Different GPU platforms. Their measurements are kept separate because hardware and system conditions differ.
- **ITL (inter-token latency):** Average time between output tokens within one request. Here the limit is 20 ms.
- **KV cache:** Key/value tensors created while processing the prompt and reused during token generation.
- **N (concurrency):** Number of client requests in flight. It is not the same as a GPU batch at every moment.
- **NIXL:** A library/runtime path used here to move KV data between serving workers.
- **Prefill:** Processing the input prompt before output generation; it strongly influences TTFT.
- **SLA pass fraction:** Share of all requests that jointly meet the latency limits. Errors remain in the denominator.
- **TP (tensor parallelism):** Splits each model layer's matrix operations across several GPUs.
- **TTFT:** Time from sending a request until its first output token. Here the limit is 3,000 ms.

- **Token:** A unit of text used by the tokenizer. A token is not necessarily a word; performance lengths and score units count tokens.
- **MoE (mixture of experts):** A model with many expert neural networks, with a subset selected for each token. Expert placement and kernel choice affect serving cost.
- **FP8 / BF16:** Numeric formats used by the runtime. The official target uses the FP8 checkpoint; BF16 activations/KV and an unquantized BF16 draft are separate settings. Matching formats does not by itself prove output quality.
- **DeepGEMM / HPC-Ops:** GPU kernel implementations used for matrix/MoE work in our measured stack. The useful choice depended on prefill versus decode and hardware. HPC-Ops here is a GPU library, not the separate OpenFOAM competition task.
- **FlashInfer:** GPU attention and communication operations used by the serving runtime. A backend change needs a measured control and output checks.
- **MNNVL path:** The selected fused GPU all-reduce/normalization implementation. Its trace time includes fused work, so it is not pure network time.
- **EAGLE3 / speculative decoding:** A smaller draft proposes tokens and the main model verifies them. Acceptance length counts output tokens per verification step; it is not tokens/s or measured speedup.
- **Control / candidate:** The reference serving setup and one tested alternative. A useful comparison keeps workload, hardware and observation settings matched.
- **Repeat:** A new deployment/measurement of the same point. It checks whether a gain persists; one number is not its own replication.
- **Short screen / full run:** A cheaper exploratory test versus the full retained 60-second warmup, 120-second measurement and 30-second grace protocol. Their scores must not be ranked interchangeably.
- **p95 / p99:** Latency percentiles: approximately 95% / 99% of observed request latencies are at or below those values. A good mean can hide a slow tail.
- **Receipt / semantic gate:** A saved result and a checker that replays its actual contents. Scheduler exit or a printed success message alone does not prove correct model output or transfer.
- **SU (service unit):** The H100 project's accounting unit. Our GPU rate is 128 SU per allocated GPU-hour: four GPUs for 20 minutes reserve at most 170.667 SU. Actual charges are reconciled separately; reservations are not spent cost.

## Three different kinds of stored data

**Model weights** are trained parameters loaded when workers start; this project optimizes serving rather than training new weights. They live in the staged shared storage outside Git. **KV cache** is request-dependent attention state held by workers, usually in GPU memory. Mounting shared files does not transfer that GPU cache; the serving system's NIXL path handles the relevant transfers. **Run evidence** is the job script, API/benchmark exports, logs, hashes and review retained to explain what happened. A Git commit backs up reviewed source and selected evidence; it does not itself submit a GPU job.

The synthetic performance workload measures serving latency and goodput. Local short-answer and long-retrieval checks inspect selected outputs. The organizer's separate full-set accuracy evaluation compares benchmark scores with its unchanged official FP8 reference. Those are different tests, so passing one cannot stand in for all three.
