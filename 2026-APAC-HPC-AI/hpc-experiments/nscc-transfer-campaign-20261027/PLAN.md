# NSCC CPU transfer and improvement queue

Prepared 2026-10-27T10:33:22.706355+00:00 after the owner's request to move promising ideas onto the contest CPU machine and measure them until they beat **3.364622070 seconds per step**. The latest request is a plan: every new entry below is **planned, not submitted**. [queue.json](queue.json) is a machine-readable research backlog, not a dispatcher. No scheduler, budget or submission material is changed by writing it.

## Objective and comparison

First obtain a valid new full 150-step observation below the retained own mean **3.364622070 s/step**, then demonstrate the advantage against a comparable fresh control and repeat it on independent allocations. The next external comparison is the organiser full-chain observation **3.210832548 s/step**. It is not our control or a hardware limit. Lower is better.

An isolated record below the target is labelled an observed target hit. A stronger claim requires both directions of a matched comparison and independent full repeats. Gains below 1% merit extra repetition before a reliability claim. Do not discard slow samples, average per-step samples across different configurations, or manufacture confidence intervals by treating serially correlated steps as independent trials. Keep every run visible even after selecting a winner.

## Current access and existing work

The fresh CPU and AI read-only queries at **10:28 UTC on27 October** failed before reaching SSH because the VPN helper found no live session. Current PBS queues and posted credit are therefore **unknown**. No authentication was attempted and no VPN state was altered. [Retained safe access result](access-check.json).

The 07:48 CPU snapshot had four queued shared-account jobs 26023372/26023373/26023382/26023383. Their payloads, submitter provenance and reservations remain unreconciled here. Do not cancel them, assume ownership, import them as this campaign's submissions or submit duplicates. Inspect safe submission paths and receipts after access returns. Job 26019383 was seen terminal F then, but its exit status and application-level replay remain unreviewed; terminal does not mean passed. Preserve that frozen payload.

Before each new qsub, check both own CPU and AI PBS queues under CPU-before-AI locks, preserve the existing one-own-CPU-job cap and combined PBS cap 3 including holds, verify selected CPU project 59000042, actual rate and fresh available spending after all commitments. A research backlog can contain many candidates without placing all of them in PBS at once. Missing current data blocks admission, not preparation of the independent native branch.

## Native Basic tests come first

**S 0:** reproduce the retained default Scotch configuration with four exclusive nodes, 512 ranks, native module 2512, FP 64, SRX off and no injection. Record actual build, MPI/provider libraries, launcher options, effective allowlisted runtime settings, physical mapping, node identities and filesystem placement. Compare these with job 25940700 and the organiser recipe rather than claiming exact parity from a few matching flags. Do not repeat transport settings already present as a newly discovered optimization.

**Hxyz versus Hzyx:** transfer the Iris hypothesis, not its files. Make fresh NSCC512-rank hierarchical decompositions using **factors (16 8 4)**, the retained official four-node control. Change only `hierarchicalCoeffs.order` from `xyz` to `zyx`. Iris actually used (7 4 2),56 ranks and a different MPI/build/hardware stack; neither its processor trees nor a21–27% expected gain transfer automatically.

Each decomposition requires its own complete mandatory preparation. The original global mesh/fields and numerical rules match between methods; their decomposed and initialized field trees are not expected to be bit-identical to one another. Within repeated arms of the same method, clone one verified initialized state into isolated writable case trees and verify byte identity and nonaliasing. Keep initialization artifacts and seals.

Run full 150-step xyz and zyx arms on one allocation, then reverse their order in another allocation if the first valid result gives a target hit or a clear matched advantage. If preparation/copy/validation cannot fit the time guard, stop safely and preserve the incomplete result; do not reduce solver work to manufacture a completion. If neither hierarchy configuration improves the objective, continue the distinct Scotch-placement branch. The PMPI adapter is **not** a prerequisite for these native Basic tests.

## Placement and combinations

**Spin:** after independently reviewing actual Pstream/checkMesh integration, compare native Scotch to post-init identity main-thread pinning. Use A 1–B 1–B 2–A 2, all 150-step solves, unchanged partition and fixed work. Capture actual solver entry/final affinity and source/runtime hashes. The native probe qualifies a main-thread mechanism, not helper threads or page residency. The old ABBA draft's entry-mask shim and graph permutation must not be deployed wholesale.

**Sbalanced:** keep Scotch partitions fixed and test the balanced logical assignment only after actual world/PMI/host/core mapping qualifies on a fresh allocation. Its 15.86% host-face reduction is a proxy, not a speed prediction. Identity and candidate must share the same required launcher/adapter mechanism.

**Saggressive:** separately qualify and test the aggressive mapping if its lower host cut versus worse NUMA proxy remains a useful trade-off. The balanced branch winning is not a prerequisite; both derive from the same unchanged partition but make distinct trade-offs. Preserve losses.

**Hzyx plus pin:** combine only after both standalone results justify the interaction. Control is the exact same hierarchy without pinning. Do not apply a graph assignment constructed for Scotch to a different hierarchical partition. A graph combination would need a new graph, hypothesis and qualification.

If these branches do not provide a repeatable win, use the last bounded fallback stage to test hierarchy factors (8 8 8) and(16 4 8), one at a time, against the selected hierarchy shape with the same order and all other settings fixed. These are new hypotheses, not previously measured winners. After that, review timing and available hardware evidence before any distinct next wave; do not repeat unchanged losers just to occupy PBS.

## Basic versus Bonus matters

Pinned official rules classify `hierarchical`/`scotch` coefficients and runtime MPI settings as Basic, but **LD_PRELOAD/code injection as Bonus**. Thus the native hierarchy branch can improve the Basic result directly. The PMPI pin/map/combinations as currently proposed are Bonus candidates and must retain their own pre-change controls. They cannot silently replace the Basic package.

A promising four-node Bonus result needs complete F 3 self-proof at 1 node/40 steps,2 nodes/80 steps and 4 nodes/150 steps against the same pre-change configuration with the injection removed. Cd must be identical or within the stated±0.5% band at each endpoint. Retain all force trajectories; do not apply that Bonus band as an invented universal Basic gate. Basic decomposition changes use the published sanity check.

## Proposed finite queue and request ceilings

All full four-node scoring observations use 150 steps and 149 timed samples. Qualifiers run no contest solver. Times below are **request caps**, not expected duration, guaranteed completion or exact charges.

| Queue item | Work | Request cap | Maximum SU |
|---|---|---|---:|
| Q00 | Restore verified access; reconcile existing jobs and receipts; review 26019383 and storage | 1 × 0 min / 0 CPUs | 0.000 |
| Q01 | Fresh full native Scotch reference and exact recipe/environment comparison | 1 × 40 min / 512 CPUs | 341.333 |
| Q02 | Matched full native hierarchy xyz then zyx; fresh required preparation per decomposition | 1 × 70 min / 512 CPUs | 597.333 |
| Q03 | Reverse full pair zyx then xyz if Q02 gives a valid target hit or meaningful matched advantage | 1 × 70 min / 512 CPUs | 597.333 |
| Q04 | Review submitted integration; allow at most two log-derived tiny repair tests if needed | 2 × 10 min / 512 CPUs | 170.667 |
| Q05 | Full native Scotch versus identity pin in A-B-B-A order | 1 × 90 min / 512 CPUs | 768.000 |
| Q06 | Fresh balanced-map qualification then full matched identity/candidate A-B-B-A | 10 + 90 min / 512 CPUs, separate jobs | 853.333 |
| Q07 | Fresh aggressive-map qualification then matched A-B-B-A if trade-off remains informative | 10 + 90 min / 512 CPUs, separate jobs | 853.333 |
| Q08 | Combine measured useful hierarchy and pin findings, compare matched unpinned hierarchy | 1 × 90 min / 512 CPUs | 768.000 |
| Q09 | Only if needed: two bounded matched hierarchy-factor trials, reviewed sequentially | 2 × 70 min / 512 CPUs | 1194.667 |
| Q10 | Two independent full winner repeats on fresh allocations | 2 × 40 min / 512 CPUs | 682.667 |
| Q11 | If Bonus selected: paired pre-change/change at one node40 steps and two nodes80 steps | 1 × 60 min / 128 CPUs | 128.000 |
| Q12 | Two-node Bonus self-proof pair, 80 steps each | 1 × 70 min / 256 CPUs | 298.667 |

Q 06 andQ 07 each include one 10-minute mapping qualifier plus one 90-minute ABBA job; these are separate admissions, not one 100-minute payload. Q 04 has no automatic retry: inspect each actual failure and permit at most two distinct log-derived fixes before closing that adapter version. Q 09 is two sequentially reviewed factor trials, not an automatic two-job sweep. Q 11/Q 12 run only if a Bonus winner needs official self-proof.

Sum of every conditional request maximum is **7253.333 SU**, within a proposed **8000-SU bounded wave**. The initial S 0 plus forward/reverse hierarchy comparisons total 1536 SU maximum. These planning envelopes create **no reservation** and do not raise the existing CPU research ceiling. The dated ledger reported 4857.2 SU commitment and 24920.646667 SU headroom, but outstanding shared-account jobs and fresh site credit must be reconciled first. AI credit is separate.

The retained one-run measurements were 419.14 s serial decomposition,549.16 s solver and 1133.66 s wrapper. Four solver arms alone imply about 2196.64 s; complete initialized clones, hashing and guards are additional and unmeasured. Never reuse the earlier 43-file source-copy timing as a full clone bound. Begin with bounded space/inode/copy checks, use existing own verified data only, and derive longer caps only if evidence and the same budget justify them. Longer requests can wait longer in PBS; no start-time ETA is promised.

## Per-run gates and feedback loop

1. Freeze reviewed source/config/launcher/runtime before submission; write a durable intent before qsub and preserve the definite receipt. Never retry an uncertain qsub blindly.
2. Preserve the official 65334765-cell mesh, native v 2512 FP 64, all function objects and log output, fixed Ux/Uy/Uz 15,p 12,k/omega 8 iterations, prescribed preparation and ybl 0.0450244.
3. Require all stages to return zero,150 ordered solver steps,149 positive timing rows for Times 2–150, exact native-log/time-file arithmetic, finite force rows, expected resources/ranks/hosts, source/field seals and actual terminal evidence. A failure or timeout is not a completed timing result.
4. Inspect mean, median,p 95,max/slow-step times, native sampling warning, Cd, runtime/transport errors and allocation cost. Use bounded matched phase/resource/CPU telemetry; unavailable bandwidth, memory residency or MPI waiting remains unknown. Keep heavy profiles outside scored runs.
5. Record the hypothesis, exact control/change, IDs and hashes, observations, interpretation and next choice. Capture/verify/commit/push each completed checkpoint promptly.
6. Advance or close the branch from the reviewed result, then select the next justified ready entry. Reaching one target hit moves the next slots to confirmation; it does not justify stopping all evidence collection or announcing an official score. If all queued hypotheses lose, use their diagnostics for the next distinct hypothesis within the remaining authorised credit and deadline.

PBS `afterok` serializes shell success; it does not verify the scientific gates. Do not submit the whole logical backlog as an unchecked dependency chain. No background Codex, schedule or automatic chat notification is enabled. This plan does not promise self-waking execution.

## Source and recovery routes

- [Pinned official rules](sources/2.%20OpenFOAM%20HPC%20Task%20Rules.md), especially F1–F3; [source hashes/revision](sources/provenance.json).
- [Pinned official ASPIRE notes](sources/4.3%20OpenFOAM%20Application%20Notes%20-%20ASPIRE-2A.md), including four-node factors (16 8 4).
- [Own findings](/home/apacsc42/workspace/reports/hpc-research-journey-20261023/OWN_FINDINGS_THROUGH_20261027.md) and their raw/result links.
- [Current HPC handoff](/home/apacsc42/workspace/notes/HPC_CURRENT.md), CPU ledger and actual new receipts before execution.

No AI payload, queue or budget is modified. No submission slides/scripts are promoted by a planned experiment.
