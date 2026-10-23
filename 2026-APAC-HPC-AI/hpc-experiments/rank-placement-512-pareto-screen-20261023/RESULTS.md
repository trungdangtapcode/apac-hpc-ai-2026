# Whole-group host assignment on the two-cut frontier

## Result

Reassigning the 32 fixed 16-rank logical NUMA groups as whole groups found a balanced four-host assignment that matches or improves the original contiguous control on both graph proxies:

| Assignment | Cross-host faces | Same-host cross-NUMA faces | Within-host same-NUMA faces |
|---|---:|---:|---:|
| Original control: `rank // 128`, `(rank % 128) // 16` | 337,324 | 710,081 | 1,879,617 |
| Aggressive parent assignment, groups held intact | 261,110 | 732,712 | 1,933,200 |
| New feasible whole-group assignment | **283,819** | **710,003** | **1,933,200** |

The new assignment lowers cross-host faces by **53,505** versus the original control and lowers same-host cross-NUMA faces by **78**. It sits only **78 faces above** the feasible interval's lower boundary, which would exactly match the control's same-host cross-NUMA subtotal. Its cross-host cut remains below the control's upper bound. This assignment therefore removes the remaining NUMA-cut regression in the aggressive mapping while retaining most of that mapping's cross-host cut reduction. These are graph counts, not measurements of communication or runtime.

## Feasibility and search

The 32 fixed supernodes contain **993,822 cross-NUMA faces** in total. For any assignment of these intact groups, `same-host cross-NUMA faces = 993,822 - cross-host faces`. Matching the control's two cut categories requires `283,741 <= cross-host faces <= 337,324`. This interval uses no physical weights.

The search first checked all **384** inter-host single-supernode swaps from the aggressive assignment; **179 assignments** were feasible, with 178 distinct cross-host cut values. The best feasible single swap had a 285,765-face host cut. Seeded search (seed **2026**) then completed **500,000** balanced whole-group swap proposals and found the 283,819-face assignment. Total local elapsed time was **1.41 seconds**, within the 20-second bound. The retained sampled nondominated set contains **1,098 distinct feasible cut values**, from 283,819 through 337,315. Because the two cut proxies sum to a fixed 993,822, every distinct feasible host-cut value has a distinct opposing NUMA-cut value and is nondominated. This is only the sampled frontier, not an exhaustive enumeration or global-optimum proof.

The selected mapping uses eight intact groups per host, 128 ranks per host, all 512 ranks exactly once, and a rank-zero-first full permutation. Its host assignment and permutation are pinned in [screen.json](screen.json). The script validates all 128 incremental superedge swap deltas against full recomputation and independently reproduces the selected cut from the original 512-rank graph.

## External-face and cell-balance proxies

The maximum cross-host external-face total on one logical host is **214,160** for the original control, **140,111** for the aggressive mapping, and **149,331** for the new feasible assignment. New assignment per-host external totals are **140,111; 138,144; 149,331; and 140,052**. This diagnostic counts graph faces incident to a logical host; it is not measured node traffic.

Host cell totals for the new assignment are **16,393,858; 16,330,513; 16,291,414; and 16,318,980**, with a range of **102,444 cells** (0.627% of the mean). The original control range is 35,108 cells (0.215%); the aggressive assignment range is 114,711 cells (0.702%). Host counts remain balanced by assigning eight 16-rank groups to each host. The assignment changes which host receives each fixed group, so cell totals are recomputed from native per-rank cell counts rather than assumed equal.

## Provenance, qualification and limits

The screen pins the validated rank graph and the exact preceding four-host and fixed-host NUMA screen files by SHA256. Aggregating the 512-rank edge list into the 32 fixed groups conserves all **2,927,022** interface faces: **1,933,200** lie inside the intact groups and **993,822** cross between groups. All three assignments are checked against the full rank graph.

[qualification.json](qualification.json) records structural checks only. Eight NUMA domains per host remain an unverified historical-topology assumption. No fresh four-node physical NUMA topology, MPI rank-to-host/core mapping, or page placement was measured. Face counts do not measure bytes, network traffic, MPI wait, memory locality, latency, solver critical path or speedup. The new mapping is offline only; no runnable rank-order file, MPI/solver run, SSH, scheduler, or budget action was created.

The next evidence gate remains the separate four-rank MPI reorder-interface preflight. Even a pass would verify only a small MPI-world rank-order path; it would not establish the 512-rank mapping or current four-node NUMA placement.

## Root review and runtime status

Independent full-edge checks reproduce 283,819 crossing-host, 710,003 same-host crossing-NUMA and 1,933,200 within-group faces. All 32 original 16-rank groups are unchanged, the four hosts contain 128 ranks each, and the complete 512-rank permutation keeps rank 0 first. An isolated replay of all 500,000 proposals reproduced the selected mapping exactly while leaving the accepted source JSON unchanged; see [root-review.json](root-review.json) and [verify_result.py](verify_result.py).

The 78-face NUMA difference is only 0.010985% of the original category. Its purpose is a no-regression constraint, not a claim of a material memory-speed benefit. This candidate is better on two face-count proxies; its host cell-balance range remains worse than the original. It is not dominance over every performance metric.

The already queued 512-rank qualification 25947168 contains the older aggressive mapping and stays frozen. It must not be retargeted in place. A successful run would demonstrate the mechanism for that exact mapping/allocation, not prove this new assignment. The new balanced mapping remains unsubmitted, and any later derived bundle requires fresh graph and actual MPI placement checks. No additional SU or queue slot was reserved for this offline search.
