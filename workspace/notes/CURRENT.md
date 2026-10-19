# Current APAC handoff — 19 October 2026

## Active batch and live checks

The user requested continued optimisation. Latest plan, receipts, source measurements and profile analysis: [19 October followups](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0412/RESULTS.md). Check actual schedulers again before reporting a later live state.

Four H200 jobs are pending: **24721** fresh best control (DeepGEMM prefill chunk 8192, auto decode, N58), **24722** N60, **24723** chunk 12288 at N58, **24724** HPC-Ops decode with chunk 8192 at N58. Each requests 16 GPUs / 17 minutes. Only one factor changes versus 24721. Existing 360-second whole-client guard is identical across all four. Any guard timeout is failure; no unchanged retry or automatic N62/larger chunk.

Two PBS jobs are submitted: **221589.pbs111** independent both-phase HPC-Ops N52 repeat, then **221590.pbs111** N54 via verified afterany dependency. Each requests 16 GPUs / 45 minutes; at most one runs at a time. At verification the first was queued and second dependency-held. No new measurement yet. Preserve queue positions; review completions without waiting for the whole batch.

VPN and SSH were restored at the user's request at 04:01 UTC and remain in use through the tmux client. Private cache preserved; client requested no extra MFA code, phone-side DUO unknown. Do not restart a live tunnel. Use workspace/vpn-rootless/vpn.sh ssh-batch. A batch SSH auth failure alone does not establish VPN loss.

Freshly queried PBS ledger as of 19 October 12:00:01 SGT: Used 27199.147 SU, Balance 36800.853 SU, In Doubt 0. New two-job maximum reserve **3072 SU**; internal headroom **20728.853 SU** under the unchanged 51000-SU operating bound, retaining a separate 13000-SU buffer. No budget increase. Corrected old terminal entries in pending_reservations to RECONCILED_IN_LEDGER after live accounting, matching prior jobs/ledger reconciliation. Reserve under budget.lock; never retry uncertain qsub.

## Accepted local measurements and evidence limits

Latest complete source review: [recovered results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0400/RESULTS.md). All listed observations pass full local protocol, SLA/error, frozen payload, runtime and short/12-long checks. These do not establish official full-set accuracy at 99% of the organiser reference score.

- H200 chunk 8192 N58: **24647 = 2780.483 good tokens/s**, +2.2688% versus fresh 24589 = 2718.797. Original 24544 = 2786.696; two-observation descriptive mean 2783.589. Failed warmup 24588 remains failure evidence, not a score or proven root-cause repair.
- H200 24639 = 2724.552 (DeepGEMM prefill/HPC-Ops decode N58), 24640 = 2714.903 (HPC-Ops prefill chunk 6144 N56), 24641 = 2742.207 (both HPC-Ops N56). Do not assume additive gains. The winning chunk-8192 configuration is the current comparison source.
- H100 highest observation: **221341 = 2398.728**, both-phase HPC-Ops N52; independent repeat now queued. N50 221346 = 2375.807 versus fresh decode-only 221340 = 2302.223 (+3.1962%). Prior both-phase N50 221315/221339 = 2371.961/2371.341. Keep H100/H200 results separate.

## Profile findings and future research

Recovered H100 221346 has 16 sealed nonzero-rank traces and 376/376 successful separate diagnostic requests at N48. Named HPC grouped GEMM shares: prefill 33.812%/33.259%, decode 22.888%. Leading prefill NCCL Ring all-reduce shares 22.784%/24.007%. These are summed kernel durations, not wall-time or speed predictions. Actual-name analysis and NVIDIA source references are in the latest report.

Potential future prefill communication trial needs exact NCCL version/active-communicator validation and a same-platform control before submission. No new credit reserved for it. H100 auto-prefill chunk 8192 and graph-off losing branches remain closed; invalid equal-TP8/EP2 24375 stays quarantined. Do not infer correctness from CPU geometry tests. Establish organiser accuracy tasks/harness/reference before claiming full accuracy.

## Standing workflow

Vietnamese chat only; all new work artifacts in readable English. Qwen only; keep HPC_Task empty. Preserve raw failures and corrected interpretations. No slide, official script promotion or organiser upload without relevant authorisation. Keep queue bounds: at most five active H200 jobs, three active PBS jobs and one running PBS 16-GPU allocation.

Codex autopilot stays OFF. No background Codex, replacement schedules or automatic chat notifications. No background Slurm watcher is running; this batch was submitted explicitly under locks.

Work once in `/home/apacsc42/2026-APAC-HPC-AI` and `/home/apacsc42/workspace`. Capture completed milestones into `/home/apacsc42/apac-hpc-ai-research` with sibling artifact store, scan/verify and commit. AGENTS.md records this manual workflow; no automatic mirror. GitHub CLI/upload remain deferred. A same-machine archive is not yet an off-host backup. Historical handoff snapshots are in notes/archive and Git; they are not live scheduler state.
