# Speaker notes — the Qwen AI research journey

*Designed for a five-to-eight-minute English presentation. The README is the visual route; these notes are the spoken story.*

## Opening: what are we trying to improve?

We are serving Qwen3-235B on multiple GPUs. The official workload gives the model fixed four-thousand-token inputs and asks for two hundred output tokens. A request counts only if its first token arrives within three seconds and its average gap between output tokens is no more than twenty milliseconds. At least ninety percent of all requests must pass both limits. The organizer clarified that the score is good requests per second multiplied by two hundred output tokens.

That means this is not just a “make the GPU busy” exercise. A request that is fast enough contributes; a request that misses either latency limit does not. Errors remain in the denominator. Separately, the contest has a ninety-nine-percent-of-reference accuracy condition, which our local checks have not yet established.

## Why the first experiments were about plumbing

The GPU clusters are scheduled systems. Slurm is used on the H200 side, and PBS on H100. We cannot treat a login shell as a permanent GPU machine. Each candidate is a complete serving setup: roles, GPU split, runtime settings, concurrency and benchmark protocol.

The first topology runs surfaced real systems issues. Prefill builds the key/value cache from the prompt; decode uses that cache to generate tokens. Moving it between workers involves NIXL. Some layouts failed before a valid benchmark because of tensor shape constraints or remote-transfer failures. Those failed jobs taught us that “the server started” and “the benchmark completed correctly” are different milestones.

## How we raised the H200 result

Once there was a stable topology, we tuned prefill and decode separately. The early operating points moved from roughly nineteen hundred at concurrency 48 to about twenty-one hundred at concurrency 52, as configuration and load both changed. This is the historical progression; individual graph and chunking conclusions came from matched controls. Then controlled backend trials showed that the MNNVL collective and FlashInfer attention worked well in the current pipeline. A combined configuration reached about 2,939 at concurrency 58, and repeated deployments confirmed that result was not a one-off. A later concurrency-60 point reached about 2,990. Some early measurements used different cache handling, so we keep their protocols attached and do not present the entire history as one normalized speedup curve.

We did not assume these improvements would add together. They interact through batching, queueing and latency. Some changes that sounded promising lost against controls, so we stopped repeating them. That is useful progress too: a failed hypothesis narrows what deserves more GPU time.

## Why N64 is the current local choice

A short screening result favored N64, so we checked it in full runs against N62. The first full comparison was about 1.083 percent better at N64. Two independent full N64 runs then reproduced the result. Across three full points the mean is about 3,044.4 good output tokens per second. The latest N64 run had zero request errors or cancellations and passed all twelve long retrieval checks; about 98.63 percent of requests met both latency limits.

N68 scored only 0.083 percent higher than a fresh N64 control. Its latency pass fraction and first-token latency were worse. Our planned threshold for a useful gain was one percent, so we closed that branch rather than spending another run to chase a near-tie. The H100 result, about 2,433 at N54, remains separate; a GPU generation and system change makes a direct merged ranking misleading.

## Correctness before speculative decoding

EAGLE3 uses a draft model to propose tokens that the main model verifies. It may save decode work, but only if its output matches the normal model and its extra coordination does not erase the gain.

We first repaired the H200 exact-output reference. The accepted reference produced eight responses and retained all 1,600 generated token IDs, with repeated greedy outputs matching exactly. A correctness-only EAGLE3 H200 job was then submitted. It must match those token IDs and pass runtime checks before we compare speed.

A separate H100 geometry probe also shows why validators matter. The actual model reached readiness and recorded before/after geometry for all four ranks: 190 KV regions and ten auxiliary buffers per rank, one local and four total KV heads, and page size one. Our strict checker rejected an empty layer-ID list. The runtime's geometry was stable; the checker's assumption was too strong. That run is therefore not called an accepted geometry pass. A narrowly corrected gate now replays the captured metadata while preserving the original failed job. We do not need another GPU allocation just to change this unsupported metadata assumption. It says nothing about EAGLE3 speed.

## Closing

Our honest claim is a reproducible local H200 result around 3,044 good output tokens per second on N64, alongside a separate H100 result around 2,433. We have improved the measured serving system through matched controls and repeats. We have not yet proven the official accuracy threshold, and we have not claimed an EAGLE3 speedup. The next step is to validate exact output equivalence first, then run a matched performance comparison only if correctness passes.

## Likely questions

**Is 3,044 the official contest score?**  
No. It is a local full-benchmark result expressed in the official good-output-token unit. The official ranking and separate accuracy evaluation have not been claimed here.

**Why not pick the single highest number, N68?**  
It was only 0.083 percent above the fresh N64 result, below the planned one-percent repeat threshold, and its TTFT and joint pass fraction were worse. N64 has three full observations.

**What does N64 mean?**  
It is the client concurrency: up to sixty-four simultaneous in-flight requests. It does not mean each GPU always computes a batch of sixty-four.

**Why keep H100 and H200 separate?**  
The GPU hardware and cluster environment differ. The numbers describe local results on each platform; we have no validated conversion that makes them one directly comparable ranking.

**Did EAGLE3 improve speed?**  
Not established. The H200 correctness job must first prove its generated IDs match the accepted reference. Then a separate matched benchmark can measure speed.

**Does zero error mean every request passed?**  
No. Errors are only one failure mode. A request can complete successfully but miss TTFT or ITL; the score requires both limits jointly.

**Does the 99% rule mean 99% of answers must be correct?**  
It means at least 99% of the organizer's reference benchmark score, not an absolute 99% accuracy. For an illustrative accuracy score, if a reference scored 70%, 99% of that would be 69.3%. These are example numbers, not our measured reference. Our official full-set accuracy requirement remains unverified.

**Does a CUDA graph replay a saved answer?**  
No. It replays a sequence of GPU operations on the current tensors. Prefix/KV cache reuse is a separate mechanism; the official performance workload uses cache busting, while the second pass of our N1 exact-output diagnostic may reuse its prompt cache and is not a speed benchmark.

**Why record a failed test in a presentation?**  
It explains a decision. A transport failure narrowed the next question to actual memory geometry; a cheap four-GPU probe then exposed a validator assumption before we submitted the larger H200 candidate. We preserve the failure and the useful evidence separately.

**Did the unusual KV list split prove a code bug?**  
No. We followed the complete source chain and checked the final mapping with independent labels. For our one-pipeline-stage configuration, the split and recombination preserve the original list. This is a source-level negative result, not proof that GPU memory transfers or model outputs are correct.
