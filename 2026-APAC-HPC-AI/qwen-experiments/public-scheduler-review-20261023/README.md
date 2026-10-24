# Public retained Slurm accounting, 23 October

At **19:29:47 UTC on 23 October**, retained `hpcai` allocation records since 1 September contain **370 records for apacsc01** and **175 for apacsc42**. Their scheduler states include **196 and 142 COMPLETED**, respectively. The raw user-specific accounting, queue snapshot and exact counts are preserved beside this report.

These are public scheduler allocation records. They are not counts of distinct valid benchmarks, independent research hypotheses, all-time submissions or leaderboard scores. Cancelled and failed allocations remain in the totals. The separate H100/PBS history is absent, so do not treat this as a comparison of the teams' total work. We accessed no private competitor script, model output or run log, and do not know their score from this evidence.

Public job labels suggest leads involving different prefill/decode splits, DP, expert counts and FP8 KV. Labels alone cannot establish their implementation or explain a performance advantage. The useful response is to qualify those mechanisms independently against the pinned source. The resulting [DP/EP feasibility review](../dp-attention-ep-feasibility-20261024/README.md) separates arithmetic and documented implementation paths from unproved routing, kernel and memory behavior. A subsequent one-GPU replica primitive tests one of those specific uncertainties.

The owner's concern about an empty research queue remains valid regardless of these counts. During active authorised research, use completed evidence to select and submit the next distinct feasible hypothesis while preserving acceptance gates and budgets. Do not submit unchanged jobs solely to imitate queue occupancy.
