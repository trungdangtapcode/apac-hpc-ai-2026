> 29 October 2026 update: the portable GPU/model/client replay completed, but job27136 failed in postprocessing because of an unhandled AIPerf output namespace. Readers are corrected and actual raw performance rechecks pass. See artifact-path-fix-20261029.md and portable-replay-27136-20261029.json. Full end-to-end repeat and official quality remain unverified.

# Latest AI results and submission point

Updated 28 October 2026, Vietnam time. Primary submission is one N64 point on two H200 nodes: two TP4 prefill workers and one TP8/EP8 decode worker. The official FP8 checkpoint uses BF16 activation and KV dtype auto, resolved to BF16 in measured job 26766, DeepGEMM prefill with chunk8192 and breakable prefill graphs, HPC-Ops/FlashInfer/MNNVL decode with full graphs 1–64, round-robin routing, and no EAGLE or dynamic tokenization. The deployment remains a conventional Slurm/Pyxis job.

| Evidence | Good output throughput (tokens/s) | Joint SLA pass | Requests | Errors/cancellations | Interpretation |
|---|---:|---:|---:|---:|---|
|25366, N64|3044.489701|98.633018%|1902; 1876 good|0 / 0|Historical full observation|
|25373, N64|3044.074628|98.632299%|1901; 1875 good|0 / 0|Historical full observation|
|25487, N64|3044.637094|98.632299%|1901; 1875 good|0 / 0|Historical full observation|
|Historical mean|3044.400475|—|—|—|Three-run mean; local reference only|
|26766, N64|3045.501509|98.580442%|1902; 1875 good|0 / 0|New native-runtime full pass; reproduces historical level, not a matched speedup|
|26768, chunk10240|3034.088251|98.523985%|1897; 1869 good|0 / 0|Valid full run; slower than chunk8192|
|26770, chunk12288|3020.943099|98.310454%|1894; 1862 good|0 / 0|Valid full run; slower and higher p95 TTFT|

All full profiles used closed-loop N64, 60 s warmup, 120 s measurement, 30 s grace, 4000 input tokens, 200 output tokens, seed 2026, and cold prefixes. Output throughput equals AIPerf Goodput requests/s × 200 output tokens. The selected 26766 run passed the local full protocol, smoke 7/8 with no regression and retrieval 12/12. The three newer chunk arms had 24 per-role hardware/server samples; selected resource metrics and limitations are described in the retained review. Missing telemetry is not inferred as zero.

Jobs 26849/26851/26853 failed during outer warmup before AIPerf; they have no performance measurements and are not candidates. Jobs 26947/26949/26951/26953 remain queued/uncertain per the dated handoff and are not represented as results.

The official full-set accuracy check against at least 99% of the organizer reference remains UNKNOWN. Local smoke/retrieval results do not certify it. H100 225227 scored 2399.186728 good output tokens/s; retained H100 222048 scored 2433.019859. These are separate-platform results and are not mixed into the H200 comparison.

See the H200 and H100 review files and per-job compact artifacts under `measured/` for exact metrics, raw exports, input configuration, runtime logs and provenance.

Generated inputs.json dataset exports are omitted from the compact submission with exact byte sizes and SHA-256 hashes in ../omitted-artifacts-20261028.json. The fixed official AIPerf command regenerates the synthetic workload. Raw profiling requests, input configuration, performance exports and the retained research originals are preserved.
