# Current compute-alias correction — 29 October 2026

Second real run **27145** completed the official GPU client and both semantic routes, then ended **FAILED 1:0** in summary. The namespace resolver returned canonical `/scratch/home/...` paths while the summary used lexical `/home/...` paths. Canonicalizing the input root fixes that mismatch; absolute and relative alias regression assertions now pass locally, along with both real retained datasets. The original failure remains unchanged.

Its recovered raw observation is **3055.330517 good output tokens/s**, **1881/1907 good requests (98.636602%)**, zero errors/cancellations. Mean/p95 TTFT are 1096.029421/1254.518145 ms; request-mean ITL 15.010794/15.154927 ms. This is about 0.323% above separate native 26766, not a proven optimization. No separate smoke/retrieval/hardware series and official accuracy UNKNOWN remain.

The team folder/ZIP now include both reader fixes. All 265 HPC files/modes/ZIP attributes and full PPTX bytes remain unchanged. Current ZIP is 78,619,450 bytes, SHA256 `99422f42a3f2f59453dc3d89d673160c494df1bf80661a598bbc290a8f748f3b`. Actual zero-GPU compute-host regression **27152** is submitted/PENDING to reproduce the old alias error and execute the fixed exact postprocessor tail on both completed raw runs. Local tests are not an observed compute pass or a single-allocation end-to-end success. No further full GPU allocation is bought merely to test this reader.

[Second correction validation](../submission-review/ai-compute-alias-fix-20261029/publication-validation.json), [retained alias failure/correction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-artifact-path-fix-20261029/ALIAS_CORRECTION.md). `patch_ai_compute_alias_20261029.py` is the later correction publisher; the preparation builder reads the current canonical source so it includes both fixes.

## Historical first namespace correction

# AI submission reader repair — 29 October 2026

The published team folder and ZIP now include the corrected AIPerf result readers. All 265 HPC files, their modes and ZIP attributes are unchanged. The complete presentation file is also unchanged, including its eight HPC slides. This update changes AI postprocessing only; it does not change the GPU configuration or the official benchmark command.

Actual portable job **27136** initialized the three workers, passed both semantic prefill/decode routes and completed the official N64 benchmark. It then ended **FAILED 1:0** because the local checker looked for exports directly under `artifacts/`. AIPerf 0.12 instead placed them in `artifacts/qwen-openai-chat-concurrency64/`. The original failure, empty summary and raw output remain intact.

The new readers accept exactly one complete export pair at the artifact root or one immediate child. They reject missing, incomplete, ambiguous and symlink namespaces, and avoid recursively picking a warmup/profiling phase export. The summary also reads phase-completion evidence from the actual run directory. Eight regression tests and the repaired gate on retained real raw data pass. Earlier 591-check reports describe the historical 28 October build; this correction has its own targeted validation.

| Recovered observation from 27136 | Value |
|---|---:|
| Good output throughput | 3050.225487 tokens/s |
| Goodput read from AIPerf | 15.251127435 requests/s |
| Requests meeting both latency limits | 1880 / 1906, or 98.635887% |
| Profiling errors / cancellations | 0 / 0 |
| Mean / p95 TTFT | 1102.185717 / 1297.447714 ms |
| Mean / p95 request-mean ITL | 15.011058 / 15.165369 ms |

This is a recovered full-protocol observation, about 0.155% above the separate native 26766 result. It does not demonstrate a new optimization, and repairing a reader does not change the original scheduler failure. No separate smoke/retrieval suite or hardware time series was collected in this portable allocation. Official full-set accuracy remains UNKNOWN.

A separate frozen confirmation **27145** was accepted and is running at the latest dated observation. It changes only the two readers, their new path helper and hashes. Model, worker, semantic routes, entry script and official client bytes are identical to the first replay. Its eventual end-to-end status must be checked independently; no success is claimed here.

The updated ZIP is 78,616,964 bytes with SHA-256 `6f380eaeb0e8a635a78f90c86a7657c3b97b5f67031abea52511921c2a02b563`. The presentation SHA-256 remains `31f8e4cb925ed1655c6888f7f5589decf60a87b5f6b7ea76df71fe9a79b11e33`. No organiser upload was performed.

For future rebuilding, `submission-tools/prepare_ai_update_20261028.py` now copies the canonical corrected readers from the active research source before generating hashes. The bounded publisher `submission-tools/patch_ai_artifact_paths_20261029.py` holds the shared submission lock, saves prior files/ZIP, verifies all HPC bytes/modes and presentation bytes, rebuilds global manifests and checks the resulting archive. The original publication review is historical; do not run an obsolete staged payload over a newer delivery.

[Publication validation](../submission-review/ai-artifact-path-fix-20261029/publication-validation.json), [actual failure and recovered evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-artifact-path-fix-20261029/REPLAY_REVIEW.md), [frozen confirmation plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-replay-r2-20261029/PLAN.md). The private Git archive retains safe code, notes, checksums and object metadata; large external object bytes still need a separate off-host copy.
