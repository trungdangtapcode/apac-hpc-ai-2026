# Review the prefill experiments

These tools read retained artifacts. They do not submit jobs or modify a GPU run.
Run them from the qwen-experiments directory after a terminal seal appears.

| Job | Intended change | Reviewer |
|---|---|---|
|24281|One request per prefill batch|Already reviewed; see24281_RESULT.md. Close this branch.|
|24282|One TP8 prefill worker instead of two TP4 workers|review-tp8.py|
|24291|DeepGEMM for prefill only|review-two-worker.py24291|

```bash
python3 serving-tuning-10/prefill-pilot-reviews/review-tp8.py
python3 serving-tuning-10/prefill-pilot-reviews/review-two-worker.py 24291 \
  --out serving-tuning-10/prefill-pilot-reviews/24291.json
```

The TP8 reviewer requires the sealed one-worker placement, correct TP/EP and
BF16/NIXL runtime, one initialized warmup path, unchanged decode backends, full
raw client protocol and output checks. Unexpected differences require manual
review; do not relax checks simply to produce a pass.

The shared reviewer preserves its two-worker default. CPU regression checks on
real24263 data passed, including rejection of a falsely requested one-worker
layout. The single-worker terminal path is not yet validated against real24282
data. Pending status is not a benchmark result.
