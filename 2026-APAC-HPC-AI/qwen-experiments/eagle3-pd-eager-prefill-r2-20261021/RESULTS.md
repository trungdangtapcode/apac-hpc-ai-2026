# Full PD EAGLE3 eager-prefill correctness repair

Submitted 2026-10-21T14:19:52.505863+00:00 as **223053.pbs111**. The first live check in this continuation shows R; see [dated snapshot](live-initial.json). This is a diagnostic, not a ranked performance result.

The reviewed isolated TP4 prefill probe 223005 passed native readiness, BF16 KV initialization and all four NIXL ranks after uniform prefill graph disable. The full 222780 candidate had decode readiness but divergent prefill graph initialization. This new frozen bundle combines those supported results: both TP4/EP1 prefills disable native prefill graphs; TP8/EP8 decode arguments and graph choices are unchanged. Target FP8 weights, BF16/unquant draft, pinned draft revision, NIXL patch, placement and 1600-ID exact comparison stay fixed. [Plan](PLAN.md).

Readiness is capped at 1200 seconds, with an immutable allocation deadline and a bounded warmup that preserves time for actual output checks. Five shell deadline fixtures and nine adversarial semantic fixtures pass. These checks do not establish runtime success.

The definite receipt reserves 16 H100 for at most 30 minutes, **1024 SU maximum**. Fresh locked project ledger before submission: Used **45633.701 SU**, Balance **18366.299 SU**, In Doubt **0 SU**. The uniquely posted **57.742-SU** delta reconciles probe 223005 (allocation estimate 57.742222 SU); its maximum reservation is released. Conservative internal headroom after the new maximum is **4342.299 SU**, with the existing 51000-SU cap and 13000-SU reserve unchanged. Balance already excludes published In Doubt. [Receipt](pbs-receipt.json), [reconciliation](reconciliation.json).

Own GPU queue was empty before submission. The submitter retains one conservative external CPU slot allowance under the other worker's documented one-job cap; it does not connect to or assert live state of the HPC cluster. The abandoned first preparation was never uploaded, reserved or submitted. Revision 2 removes its unnecessary cross-track query dependency and makes configuration metadata match runtime flags.

Next: seal terminal artifacts, verify payload hashes, all-role runtime/transport and resource coverage, and the actual 1600 output IDs. Full-PD success is required before a separately funded matched-capacity N54 short screen. No speedup, complete output equivalence, official accuracy or global optimality is claimed. H200 and H100 scores remain separate. The five H200 queue positions are preserved; see [snapshot](h200-queue.txt).

Terminal update: **F/exit127**, 507 seconds; all roles and router ready, then warmup launcher failed before execution. See [complete failure review](REVIEW.md). Earlier R observations are historical.
