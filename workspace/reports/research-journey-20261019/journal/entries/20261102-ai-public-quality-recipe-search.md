# Locate the quality evaluator rather than confuse it with performance jobs

**Question.** The owner expected an accuracy evaluation to have been submitted and then asked whether the public competition repository supplies the recipe. This review checks the source independently rather than asking the owner to locate public information.

**Evidence and method.** Current public main is b4df5290. The recursive tree has 412 blobs and is not truncated. Read the Q1 quality requirement, two AI application notes, common baselines and all sample AI scripts/READMEs (20 files). Public issues returned zero records. Search and content review found no full-set accuracy harness or numerical FP8 reference. Reference deployment/performance scores are not quality denominators. Primary-source snapshots and hashes are retained in the linked report.

**Local readiness.** Recovered the prepared 24 October MMLU-Pro screen. Independently verified the retained full test/validation Parquet hashes and exact 128-question corpus identity. It has no completed response summaries. The prepared client and sample comparator are not an official full-set evaluator; tokenizer prompt fitting and inference remain unperformed.

**Assessment and decision.** Quality >=99% means a ratio against the organisers' actual unchanged FP8 reference on the same checks. Neither AIPerf goodput nor the request-latency success fraction gives that score. A separately qualified local control/candidate test could provide internal regression evidence; it must not be called official certification. No new GPU job, budget reservation, auth, message, upload or release change. This source-search milestone does not reopen broad performance research.

**Sources and preservation.** [Full report](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-evaluation-access-review-20261102/REPORT.md), retained source-review metadata, public AI file manifest and local protocol inventory. Capture these safe findings, preserve raw sources and push a small research checkpoint. No credentials or runtime state are captured.
