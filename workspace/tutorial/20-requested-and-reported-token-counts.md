# Requested lengths, reported token counts and the official score

Recorded 29 October 2026, Vietnam time (UTC+7). These are three different quantities. Keeping them separate avoids a misleading explanation in the presentation.

**Requested workload.** Our official AIPerf recipe asks for synthetic input mean 4000 with zero configured deviation and output mean 200 with zero configured deviation. The actual endpoint command also requests min_tokens=max_tokens=200, ignore_eos=true and temperature=0.0. These settings describe what the benchmark requests.

**Client-reported counts.** In the pinned AIPerf 0.12 configuration, server token counting is not enabled. The client instead tokenizes the text extracted from its request payload and the returned response text. This is like counting words again after receiving a printed page: the count is a measurement of the text, not a saved list of the tokens the server actually generated. Synthetic prompt generation itself samples token IDs and decodes them to text before the later recount. The source has a separate server-usage path, but that optional path was not enabled in these frozen jobs.

For example, actual control 27270 reports input counts 3986 or 3987. Its output count is 200 in 1898 requests and 199 in four. Interval 2 run 27272 reports 200 in 1887 requests and 199 in five. The older control 26949 also has two reported-199 requests. Those observations do not prove the model stopped early. We did not retain the actual generated token IDs or authoritative per-request server usage needed to establish the exact per-row cause. Do not turn the possible effect of text re-encoding into a proven explanation for these particular differences.

**Official score.** The organiser explicitly says to read exported AIPerf Goodput in requests/s and multiply by the fixed 200. Keep that formula even if a client text count differs slightly. A Goodput of 15.19526693 requests/s gives 3039.053386 good output tokens/s. Do not substitute the locally recounted mean, and do not multiply Goodput by the good-request fraction a second time.

A good request must satisfy both TTFT ≤3000 ms and request-mean ITL ≤20 ms. The run also needs at least 90% good requests, with errors in the denominator. Passing this latency gate says nothing about full model accuracy, whose separate official threshold remains unverified in our work.

The original fixed-workload configuration and raw latency gates still pass. A new diagnostic asking whether every reported output count is exactly 200 fails and is preserved explicitly. It was not an original prospective gate; the later inspection does not silently rewrite old acceptance criteria. No frozen job or official scoring command was changed. Future diagnostic use of authoritative token IDs or server usage would need its own declared scope and must not replace the official recipe without permission from the rules.

[Exact pinned client source, hashes and run evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/aiperf-token-accounting-20261029/REPORT.md). [Retained organiser clarification](../notes/official-goodput-clarification-20261020.md). [Full paired review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-transfer-poll-study-20261029/PARTIAL_RESULTS.md).
