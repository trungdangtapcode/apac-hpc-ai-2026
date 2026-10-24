# Deferred H100 cache-precision control

**Prepared, not submitted.** Admission is disabled in `ROOT_REVIEW.json`. The intended fresh BF16 control uses 16 H100 GPUs, N54, fixed 4,000/200 tokens, seed 2026 and the full 60/120/30-second protocol. A later FP8 candidate would need to change only KV precision. The maximum reservation would be 1,024 SU for 30 minutes; no reservation or spending was made for this prepared branch.

The newly completed H200 comparison, 25920 versus 25863, loses 3.52239% with FP8 KV. Its sampled decode KV token occupancy is at most 12% for BF16 and 6% for FP8. That does not establish the result on H100, whose hardware and prefill runner differ, but it lowers the immediate value of an isolated new control. Defer this branch while qualifying five-rank topology and preparing EAGLE performance feasibility. Resume only with a distinct hardware-specific hypothesis and a reviewed candidate, not to fill a queue.

The preserved draft derives the existing H100 HPC-Ops P/D baseline and actual 222048 client protocol. It adds explicit BF16 query/cache selection, exact per-rank cache checks and independent raw SLA/error/smoke/retrieval replay. Corrected non-login PBS adapters avoid the separately reproduced logout failure. It has CPU syntax/source checks only; no new GPU result, output-quality result or score exists.
