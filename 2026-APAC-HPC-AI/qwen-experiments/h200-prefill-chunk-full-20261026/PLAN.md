# H200 full N64 prefill chunk bracket

## Decision

Prepare one matched pair using the frozen `serving-tuning-11/s72-h200-full-pgraph-breakable-capnative` runtime. The only serving change is `--chunked-prefill-size`: 6144 in s76 and 4096 in s77. Both are full native prefill admission, breakable prefill CUDA graphs, N64, 16 H200 GPUs across two nodes, and a 17-minute wall limit. The workload, model, images, precision, topology, NIXL transport, policies, output checks, warmup, measurement, and quality limitations stay fixed. These are prepared payloads; this record does not claim submission or GPU results.

## Why this branch is still worth one bounded test

The recent full native N64 control (job 26319) produced 2827.996 good output tokens/s, 98.424% joint SLA, 0 errors, 7/8 output smoke, and 12/12 retrieval checks. The matched N62 and N66 brackets (jobs 26436 and 26438) produced 2823.777 and 2826.104 good output tokens/s, respectively. Their range is about 0.15%, with every arm passing the local gates. That closes the immediate load/concurrency question; changing N alone is not a useful next test.

Two earlier H200 chunk-6144 measurements at N56 were positive but below the previously declared 1% useful-gain threshold: job 24528 scored 2737.011 versus fresh chunk-4096 job 24526 at 2715.832 (+0.780%); its independent repeat, job 24573, scored 2737.410 versus fresh chunk-4096 job 24575 at 2714.097 (+0.858%). Both passed local SLA and had zero errors. They are retained as subthreshold history, not treated as a proven win. This N64 bracket is a single new attempt for each exact chunk setting under the newer full breakable-graph/native-admission runtime. It is not a retry under identical runtime conditions.

The N64 telemetry showed asymmetric prefill waiting queues (mean queue about 6.5 on prefill-0 and 0.13 on prefill-1); N62 was about 4.88 and 0.08, and N66 about 8.42 and 0.71. These observations motivate testing prefill chunk geometry but do not establish that chunk size caused the imbalance or that either new value will help. The runtime generates its native graph capture geometry from the chunk setting. The checker requires successful breakable graph capture begin/end on every prefill rank and validates the actual logged chunk against the bundle config; it deliberately does not hard-code graph bucket sizes inferred from another chunk.

## Decision rule

Compare each arm with the frozen N64 control, and compare s76 directly with s77. Keep all original metrics and errors in the run evidence. A result is useful only if the full-workload/local acceptance gates pass and good output throughput improves by more than 1% with no material tail-latency regression. A single result above that threshold warrants an independent confirmation before promotion. If both are subthreshold or fail a gate, close this chunk-size branch. Do not widen the sweep or repeat the same setting without a new hypothesis.

The score is local performance evidence only. The official full-set accuracy requirement remains unknown/unverified; these preparations make no official accuracy claim.

## Preparation and review

Run `python3 derive.py` from this directory only when creating the two payload folders. Run `python3 verify.py` to verify source lineage, fixed workload identity, exact worker-flag differences, Python and shell syntax, checksums, and checker behavior. The fixture test changes only the parsed chunk literal in temporary copies of the N64 runtime logs. It checks parser behavior and is not a GPU run, graph-capture result, or performance result. Submission and all scheduler actions are handled separately.
