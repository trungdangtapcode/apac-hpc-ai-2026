# Current APAC handoff — 19 October 2026

## Foreground repository publication — 19 October 2026

Private GitHub repository: https://github.com/trungdangtapcode/apac-hpc-ai-research. GitHub CLI is authenticated as trungdangtapcode. The first 50 commits were successfully uploaded. The owner then requested at least 60 commits and descriptive conventional subjects, with reconstructed record committer dates aligned to existing metadata-based author dates. All 57 rewritten per-commit trees are byte-identical; the mapping and date policy are retained in provenance/history-rewrite-20261019.json. Publication documentation and this handoff complete the requested minimum. Verify remote main against local HEAD for the current exact revision.

The Git history and inline files are uploaded; the sibling object store remains local. GitHub authentication is excluded. No scheduler, VPN, new GPU result or budget was checked or changed during this repository task. The research states below remain their earlier dated snapshots.

## Research snapshot — last checked in the linked review

The user requested continued optimisation. Latest plan, receipts, source measurements and profile analysis: [19 October followups](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0527/RESULTS.md). Check actual schedulers again before reporting a later live state.

H200 24721 (N58 control) and 24722 (N60) are completed and fully reviewed. **24722 = 2839.532 good tokens/s**, +2.1266% versus 24721 = 2780.403, is the new highest observation; independent N60 repeat **24732** and one N62 trial **24733** are now submitted. Existing **24723** chunk 12288 at N58 is running and **24724** HPC-Ops decode at N58 is pending at this check. Preserve positions. Each requests 16 GPUs / 17 minutes. No automatic N64 or unchanged failure retry.

H100 221589 N52 repeat (2411.304) and 221590 N54 (2430.891) both completed and pass full local checks. **221590 = 2430.891** is the new highest observation, +0.8123% versus the fresh N52 repeat. Independent N54 repeat **221645.pbs111** and one N56 trial **221646.pbs111** were submitted with verified afterany dependency; at most one 16-GPU PBS allocation running. Each requests at most 45 minutes. No automatic H100 N58. New jobs have no score yet.

VPN and SSH were restored at the user's request at 04:01 UTC and remain in use through the tmux client. Private cache preserved; client requested no extra MFA code, phone-side DUO unknown. Do not restart a live tunnel. Use workspace/vpn-rootless/vpn.sh ssh-batch. A batch SSH auth failure alone does not establish VPN loss.

Pre-submission ledger as of 19/10/2026-13:20:02 SGT: Used 27577.458 SU, Balance 34886.542 SU, In Doubt 1536.000. New two-job maximum reserve **3072 SU**; conservative internal headroom **18814.542 SU** under the unchanged 51000-SU bound and 13000-SU buffer. Retain any terminal-ledger-lag maximum reservation until Used reconciles; do not deduct prepayment twice. Reserve under budget.lock and never retry uncertain qsub. This is a dated published ledger snapshot.

## Accepted local measurements and evidence limits

Latest complete review: [new operating points](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0527/RESULTS.md). Older source measurements below remain historical context. All listed observations pass full local protocol, SLA/error, frozen payload, runtime and short/12-long checks. These do not establish official full-set accuracy at 99% of the organiser reference score.

- H200 chunk 8192 N58: **24647 = 2780.483 good tokens/s**, +2.2688% versus fresh 24589 = 2718.797. Original 24544 = 2786.696; two-observation descriptive mean 2783.589. Failed warmup 24588 remains failure evidence, not a score or proven root-cause repair.
- H200 24639 = 2724.552 (DeepGEMM prefill/HPC-Ops decode N58), 24640 = 2714.903 (HPC-Ops prefill chunk 6144 N56), 24641 = 2742.207 (both HPC-Ops N56). Do not assume additive gains. The winning chunk-8192 configuration is the current comparison source.
- Historical H100 N52 source **221341 = 2398.728**, now independently repeated by 221589 = 2411.304; the new highest observation is N54 above. N50 221346 = 2375.807 versus fresh decode-only 221340 = 2302.223 (+3.1962%). Prior both-phase N50 221315/221339 = 2371.961/2371.341. Keep H100/H200 results separate.

## Profile findings and future research

Recovered H100 221346 has 16 sealed nonzero-rank traces and 376/376 successful separate diagnostic requests at N48. Named HPC grouped GEMM shares: prefill 33.812%/33.259%, decode 22.888%. Leading prefill NCCL Ring all-reduce shares 22.784%/24.007%. These are summed kernel durations, not wall-time or speed predictions. Actual-name analysis and NVIDIA source references are in the latest report.

Potential future prefill communication trial needs exact NCCL version/active-communicator validation and a same-platform control before submission. No new credit reserved for it. H100 auto-prefill chunk 8192 and graph-off losing branches remain closed; invalid equal-TP8/EP2 24375 stays quarantined. Do not infer correctness from CPU geometry tests. Establish organiser accuracy tasks/harness/reference before claiming full accuracy.

## Standing workflow

Vietnamese chat only; all new work artifacts in readable English. Qwen only; keep HPC_Task empty. Preserve raw failures and corrected interpretations. No slide, official script promotion or organiser upload without relevant authorisation. Keep queue bounds: at most five active H200 jobs, three active PBS jobs and one running PBS 16-GPU allocation.

Codex autopilot stays OFF. No background Codex, replacement schedules or automatic chat notifications. No background Slurm watcher is running; this batch was submitted explicitly under locks.

Work once in `/home/apacsc42/2026-APAC-HPC-AI` and `/home/apacsc42/workspace`. Capture completed milestones into `/home/apacsc42/apac-hpc-ai-research` with sibling artifact store, scan/verify and commit. AGENTS.md records this manual workflow; no automatic mirror. GitHub publication is now authorised and the private remote stores Git. The sibling artifact store still has no configured off-host copy, so the GitHub clone is not complete evidence/runtime recovery. Historical handoff snapshots are in notes/archive and Git; they are not live scheduler state.
