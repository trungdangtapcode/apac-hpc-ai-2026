# 23 October: use existing H100 access and reconcile the last component probe

**Question and prior evidence.** The 22 October handoff recorded authentication failure and stale PBS credit. Existing authenticated SSH state is now present; check it read-only before considering another GPU expense, without starting VPN or DUO.

**Observation and correction.** Existing transport reaches a2ap-login01. The first non-login command lacked PBS PATH, and older history records later proved purged; neither means authentication failure. The successful selected-project check shows no AI 59010042 jobs. No CPU-project queue/ledger or authentication state was touched. Restoration time/method and negotiated lifetime remain unknown.

**Cost evidence.** Fresh published Used 46404.261 SU / Balance 17595.739 SU / In Doubt 0.000 SU. Terminal 223132 ran two GPUs for 315 seconds, 22.4 SU; that exactly matches the only unposted charge. The locked reconciliation releases its 42.666667 SU maximum only, marks the job included in Used, and leaves 4595.739 SU internal headroom under the unchanged 51000 cap / 13000 reserve. No new reservation or submission. [Raw selected evidence and reconciliation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-access-credit-20261023/REVIEW.md).

**Next decision.** Reuse existing access for a separately justified inexpensive diagnostic where it answers a remaining production-runtime question, with new locked cost/queue gates. H200 reference repair 25585 continues separately. Never infer a full EAGLE3 transfer/output or serving gain from a small registration probe, asset identity or mere access.

**Preservation.** Capture safe selected AI accounting, updated GPU ledger, new explanations and historical correction. Exclude live sockets, private caches, credentials and all CPU-project state.
