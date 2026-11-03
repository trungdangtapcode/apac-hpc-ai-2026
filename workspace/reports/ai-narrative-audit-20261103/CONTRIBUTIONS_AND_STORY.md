# AI contribution and story guide

This guide explains the team's engineering story in beginner-friendly terms. It follows the questions: what did we observe, why was an idea worth trying, what did the team change, what did the evidence show, and what claim can we defend? It is a retrospective explanation based on retained plans, source and results. It does not reproduce private thoughts or invent predictions that were not recorded before a run.

## Story 1: Make a two-node deployment feasible

### What was the problem?

The team had to serve a large Qwen model on sixteen H200 GPUs across two machines. Each request had a long prompt and a shorter generated answer. Prompt processing and answer generation do different work, but the service still had to meet both a first-token deadline and a token-gap limit. A layout that merely fits in GPU memory is not enough: both serving phases and the transfer between them must work.

### What did the team observe?

Seventeen usable topology observations gave evidence about which layouts could load the FP8 model and complete both phases. The observations used different client loads, so they cannot be treated as a controlled ranking of every topology. The team retained two TP4/EP1 prefill workers on one node and one TP8/EP8 decode worker on the other as a practical, compatible layout for subsequent testing. This was an engineering decision supported by feasibility and later repeatable use, not proof of a global optimum.

A separate historical heterogeneous-parallelism branch exposed a setup problem: workers became ready, but the pair did not complete warmup before a 360-second timeout. The benchmark never started. Thus there was no performance score and no evidence that the network bandwidth, KV layout or scheduler was the cause.

### Why try the descriptor idea?

Source inspection showed that a transfer descriptor list was built by enumerating a reserved KV pool, although a request needs only part of that pool. A descriptor is an address-range list; it is not the KV data being sent. This made excess setup metadata a specific hypothesis visible in the code. It was cheap to test byte-range equivalence on CPU before another distributed serving run. Choosing this first did not establish that bandwidth, layout or scheduling were unimportant; those alternatives were not ruled out.

### What did the team change and measure?

The implementation constructs metadata for the current request's KV pages and merges adjacent ranges. The existing NIXL library remains the transfer mechanism. The team's contribution was a bounded, request-scoped metadata change in its local integration, not a new transfer library or a new data format.

All 720 retained CPU geometry cases passed. Patched serving job 22294 completed pair warmup, served real requests and finished its full N32 benchmark without scored errors. That established feasibility of the patched path. There was no successful unpatched scored control and no isolated initialisation timer, so the evidence cannot establish a descriptor-only end-to-end speedup or show that descriptors were the dominant bottleneck.

### What can we defensibly claim?

The team found a concrete setup path worth improving, checked that the new range representation preserved the intended bytes, and showed that the patched service could run. We should not convert a whole-pool source count and a request-level range count into a speedup ratio; they describe different scopes. We also should not say that the patch proved the network transfer was the root cause of the earlier timeout.

## Story 2: Select a backend and operating load

### What did the team observe?

A separate N48 diagnostic recorded GPU kernel durations. GEMM, collective plus normalisation, and attention were visible candidates, but summed kernel time is not total request time because GPU operations may overlap. A separate full N64 run had first-token misses. Without phase timestamps, the team could not assign those misses to queueing, prefill, KV transfer or compute. These observations suggested questions; they did not identify a verified bottleneck.

### Why try another decode implementation?

The backend experiment was a distinct controlled probe, not a fix proven by the profile. Decode implementation was a plausible way to change whole-service performance. The team compared a fresh automatic-decode control with HPC-Ops decode while holding topology, prefill implementation and chunk, workload, attention and transport fixed. This asked whether the tested configuration performed better under the same load. It did not identify which internal kernel or queue caused the difference.

### What did the evidence show?

The matched full N60 comparison improved good output throughput by about 5.30%. Mean time to first token worsened by about 125 milliseconds, while mean inter-token latency improved by about 1.64 milliseconds. An independent treatment repeat was within 0.033% of the first treatment. The team retained this setting for further operating-point work while keeping the first-token tradeoff visible. This is a repeatable, configuration-level result under the measured workload; it is not a universal backend ranking.

The next question was client concurrency. More requests in flight might help overlap work, but it could also increase waiting. Full N62/N64 measurements and an independent N64 repeat supported N64: the measured gain was about 1.08%, and the repeat was nearly unchanged. Full N68 improved only about 0.08%, below the team's 1% usefulness gate. The team kept N64 and closed that N68 branch. In a separate full N64 request-level view, every latency miss was a first-token miss; that identifies the service symptom, not its internal cause.

### What can we defensibly claim?

The controlled comparison supports retaining the tested HPC-Ops decode configuration for the measured setup, with its latency tradeoff. The repeat supports the N64 operating point. We cannot claim that the profile percentages predicted the backend win, that a specific kernel caused it, or that increasing concurrency always improves serving.

## Story 3: Check robustness and answer quality

### What question remained?

A configuration can score well in a research run and still fail as a portable package, transfer poorly to another GPU generation, or change answer quality. The team therefore treated package completion, direct H200 checks and quality retention as separate gates.

### What did the team observe and test?

The accepted portable entry, job 28197, completed deployment, inference, scoring and cleanup on the retained sixteen-H200 recipe at 3,051.52 good output tokens per second. This is package acceptance and a performance observation, not a matched optimisation comparison.

The team tested selected H100-derived settings directly on H200 against fresh controls. The full transferred recipe lost. Matching the prefill chunk recovered part of that branch, but it remained 4.52% below the H200 incumbent. Some phase-mode variants were positive by less than 0.14%; no tested alternative cleared the team's 1% useful-gain gate. This supported keeping the H200-specific recipe; it does not mean those libraries are universally slower.

Other experiments improved a proxy without improving the service. Sparse graph capture reduced logged capture memory while goodput fell slightly. A shallow speculative-decoding setting also lost goodput. The team closed those tested settings rather than promoting a resource counter or working feature by itself.

Finally, the complete local quality comparison used the same official FP8 checkpoint, the same sixteen H200 GPUs and the same 12,032 MMLU-Pro questions for stock reference and optimised candidate. The stock deployment answered 9,460 correctly; the candidate answered 9,452. The candidate retained 99.9154% of the reference score and passed the local 99% point gate. This is a local full-set check, not BTC certification or proof of statistical equivalence on future workloads.

### What are the three decisions?

1. Retain the practical two-node serving split and its bounded request-scoped transfer metadata change, with no isolated descriptor speedup claim.
2. Retain the matched backend and N64 operating choices within the tested workload and latency evidence; do not call them universal optima.
3. Retain the portable recipe after its performance and local quality checks, while keeping package acceptance, performance and answer quality as distinct claims.

### What is the team's contribution?

The defensible contribution is engineering: integrating existing serving components for the local two-node setup, making a bounded request-scoped metadata change to an existing NIXL transfer path, and selecting a configuration through compatibility checks, controlled comparisons, repeats and quality validation. The team did not invent SGLang, NIXL, DeepGEMM, FlashInfer or HPC-Ops. This guide makes no first-in-the-world claim.

## Suggested spoken transitions

- “The first result was a feasibility observation, so we asked what blocked a usable request before looking for a score.”
- “The profile gave us candidates, but it did not prove a cause; the next slide is a separate controlled test.”
- “That backend result changed the conditions, so we retested client load rather than assuming the previous operating point still applied.”
- “A package run, a performance score and an answer-quality result answer different questions; we keep those claims separate.”

For exact run reviews and limitations, see [the final report](../ai-final-report-20261030/REPORT.md), [the reasoning guide](../teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md), and [the full-set quality result](../ai-quality-verification-20261103/FULL_RESULTS.md).
