## Manual optimisation — 2026-10-19T06:04:59.145550+00:00

H200 24724 passes at 2938.628 good tokens/s, +5.6907% versus fresh same-N58 control 24721. Chunk-12288 job 24723 passes but loses 2.3789%; close it. Submitted H200 24736/24737/24738 for fresh control, independent interaction repeat and N60. Existing 24732 running, 24733 pending. Submitted one source-checked H100 N54 prefill Tree trial 221669 after 221646, preserving 221645→221646→221669 serial chain. Total PBS max reserve 4608 SU; ledger Balance 36024.320 SU, internal headroom 18416.320 SU, no budget increase. Full local gates and actual Tree trace activation required. Report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md. No official accuracy claim, slides, organiser upload or AI schedule; autopilot OFF. Supersedes older snapshots below.

# Current APAC handoff — 19 October 2026

## Current research — 19 October 2026, 06:00–06:05 UTC

The user requested continued optimisation. Latest full review, source inspection, plan and actual receipts: [chunk/decode interaction and prefill communication](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md). Check live schedulers again for any later status claim.

**H200 24724 = 2938.628 good tokens/s**, +5.6907% versus fresh same-N58 auto-decode control 24721 = 2780.403. DeepGEMM prefill chunk 8192 plus HPC-Ops decode passes every local protocol/runtime/short/12-long gate. This is one observation, not a reproduced gain. New jobs: **24736** fresh auto-decode N58 control, **24737** interaction N58 repeat, **24738** interaction N60. Compare 24738 with 24737 for load and 24732 for runner. Five active H200 jobs: **24732** auto N60 repeat is running; **24733** auto N62 and **24736–24738** pending. Preserve positions; each 16 GPUs / 17 minutes.

**24723 chunk 12288 loses 2.3789%** versus control, despite local correctness/SLA pass. Close that branch without an unchanged retry or larger chunk. Original N60 auto-decode 24722 = 2839.532 remains a useful earlier point. No automatic higher load or promotion from a single result; whole-client timeout is failure, not a passing measurement.

H100 peak still **221590 N54 = 2430.891** (prior N52 repeat 221589 = 2411.304). PBS chain **221645 N54 repeat → 221646 N56 → 221669 N54 prefill-Tree** is verified serial, at most one 16-GPU allocation running. All three are queued/dependency-held at this check. New fixed-N54 candidate changes only prefill NCCL algorithm selection; decode retained. The existing separate post-score N48 profile must prove actual Tree execution. Log env alone is insufficient. No new PBS score yet.

Runtime logs and exact image header establish NCCL 2.28.9. Sealed H100 profile shows Ring all-reduce share 22.784%/24.007% of summed prefill kernel durations; not elapsed bottleneck shares or speed predictions. Exact image source shows PyNccl version/all-reduce calls and SGLang dispatch; actual GPU activation still required. NVIDIA 2.28 documentation and source hashes are linked in the latest report. Local extraction option/destination mistakes are preserved and corrected; no GPU used for inspection.

VPN/SSH remain usable without restart or authentication. Ledger as of 19 October 13:40:01 SGT: Used 27975.680 SU, Balance **36024.320 SU**, In Doubt 0. Terminal 221590 charge reconciled in Used. Total three-job PBS maximum reserve **4608 SU**, conservative internal headroom **18416.320 SU**, unchanged 51000-SU bound and 13000-SU buffer. Budget reconciled under lock; no increase or double prepayment deduction. Never retry uncertain submissions.

## Private Git archive

The private GitHub repo is https://github.com/trungdangtapcode/apac-hpc-ai-research. The 60-commit history correction was verified at 906ae52; new milestones use actual dates and ordinary pushes. Preserve provenance/history-rewrite-20261019.json. GitHub stores Git, not the sibling external object store; those bytes remain local. Edit active sources once, then explicit safe capture, verify, commit and push; no automatic mirror.

## Accepted local measurements and evidence limits

Latest complete review: [interaction result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md). Older source measurements below remain historical context. All listed observations pass full local protocol, SLA/error, frozen payload, runtime and short/12-long checks. These do not establish official full-set accuracy at 99% of the organiser reference score.

- H200 chunk 8192 N58: **24647 = 2780.483 good tokens/s**, +2.2688% versus fresh 24589 = 2718.797. Original 24544 = 2786.696; two-observation descriptive mean 2783.589. Failed warmup 24588 remains failure evidence, not a score or proven root-cause repair.
- H200 24639 = 2724.552 (DeepGEMM prefill/HPC-Ops decode N58), 24640 = 2714.903 (HPC-Ops prefill chunk 6144 N56), 24641 = 2742.207 (both HPC-Ops N56). Do not assume additive gains. The winning chunk-8192 configuration is the current comparison source.
- Historical H100 N52 source **221341 = 2398.728**, now independently repeated by 221589 = 2411.304; the new highest observation is N54 above. N50 221346 = 2375.807 versus fresh decode-only 221340 = 2302.223 (+3.1962%). Prior both-phase N50 221315/221339 = 2371.961/2371.341. Keep H100/H200 results separate.

## Profile findings and future research

Recovered H100 221346 has 16 sealed nonzero-rank traces and 376/376 successful separate diagnostic requests at N48. Named HPC grouped GEMM shares: prefill 33.812%/33.259%, decode 22.888%. Leading prefill NCCL Ring all-reduce shares 22.784%/24.007%. These are summed kernel durations, not wall-time or speed predictions. Actual-name analysis and NVIDIA source references are in the latest report.

Prefill Tree trial is now explicitly submitted as 221669 after source/version/profile review. Its activation and performance still require GPU evidence; compare with 221645 N54 default-algorithm repeat. H100 auto-prefill chunk 8192 and graph-off losing branches remain closed; invalid equal-TP8/EP2 24375 stays quarantined. Do not infer correctness from CPU geometry tests. Establish organiser accuracy tasks/harness/reference before claiming full accuracy.

## Standing workflow

Vietnamese chat only; all new work artifacts in readable English. Qwen only; keep HPC_Task empty. Preserve raw failures and corrected interpretations. No slide, official script promotion or organiser upload without relevant authorisation. Keep queue bounds: at most five active H200 jobs, three active PBS jobs and one running PBS 16-GPU allocation.

Codex autopilot stays OFF. No background Codex, replacement schedules or automatic chat notifications. No background Slurm watcher is running; this batch was submitted explicitly under locks.

Work once in `/home/apacsc42/2026-APAC-HPC-AI` and `/home/apacsc42/workspace`. Capture completed milestones into `/home/apacsc42/apac-hpc-ai-research` with sibling artifact store, scan/verify and commit. AGENTS.md records this manual workflow; no automatic mirror. GitHub publication is now authorised and the private remote stores Git. The sibling artifact store still has no configured off-host copy, so the GitHub clone is not complete evidence/runtime recovery. Historical handoff snapshots are in notes/archive and Git; they are not live scheduler state.
