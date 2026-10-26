# Current H100 control and equal-TP EAGLE functional pass

Recorded 2026-10-26T14:38:08.713215+00:00. The independent raw review finds 225227 F/0 in 15:38 at 2399.186728 good output tokens/s, 98.015873% joint SLA, 1512 profiling requests, no errors/cancellations, smoke 7/8 without regression and retrieval 12/12. This is 0.347131% below accepted 222551, so no unchanged repeat or improvement claim.

225228 F/0 in 6:39 proves eight disjoint H100s, pinned actual native sources, eight metadata receipts and one successful semantic response. Correct equal-TP send_kvcache and send_aux each have four start/return markers without exceptions. It repairs the missing observer evidence from 224560 without retroactively inventing its absent markers. Handles alone are not async completion; the separately validated response establishes this one request succeeded.

Next question: full N24 performance of this same-node eight-GPU EAGLE unit before a possible two-unit 16-GPU experiment. The 16-GPU N54 baseline is a different topology/resource count, not a matched EAGLE treatment. A one-unit result cannot be multiplied into a claimed aggregate score. A necessary 3% headroom feasibility threshold is 2399.186728*1.03/2=1235.581165 good tokens/s per unit; any actual aggregate improvement still needs a full two-unit measurement and quality gates.

[Independent review, per-run inspection, raw outputs and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-review-225227-225228-20261026/REVIEW.md). Official full-set accuracy remains UNKNOWN. All maximum SU reservations remain pending a fresh locked accounting review.
