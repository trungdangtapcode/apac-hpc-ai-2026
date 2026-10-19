"""Record this batch and profile evidence in active notes and run ledgers."""
from pathlib import Path
import datetime,json,shutil,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;W=Path('/home/apacsc42/workspace');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
slurm=json.loads((O/'slurm-receipts.json').read_text());pbs=json.loads((O/'pbs-receipts.json').read_text());assert len(slurm)==4 and len(pbs)==2
jobs=[x['job'] for x in slurm];output=subprocess.check_output(['squeue','-u','apacsc42','-o','%.18i %.12P %.32j %.8T %.10M %.6D %R'],text=True);(O/'slurm-latest.txt').write_text(output)
cmd=['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch','bash -lc \'qstat -u apacsc42; qstat -f '+ ' '.join(x['job'] for x in pbs) +'\''];result=subprocess.run(cmd,capture_output=True,text=True,timeout=40);(O/'pbs-latest.txt').write_text(result.stdout);(O/'pbs-latest.stderr').write_text(result.stderr);assert result.returncode==0
profile=json.loads((O/'h100-both-phase-profile.json').read_text());assert profile['trace_count']==16 and profile['successful_requests']==profile['requests']==376
report='''# Submitted followups and H100 profile — 19 October 2026

The user requested continued optimisation. The [plan](PLAN.md) explains each hypothesis, comparison, acceptance rule and resource bound. All six returned job IDs were recorded immediately, and the two PBS jobs have a verified serial dependency. No background AI or automatic retry was enabled.

| Platform | Job | Trial | Requested maximum allocation |
|---|---|---|---|
| H200 | 24721 | Fresh DeepGEMM prefill chunk 8192, auto decode, N58 control | 16 GPUs / 17 min |
| H200 | 24722 | Same serving configuration, N60 | 16 GPUs / 17 min |
| H200 | 24723 | Same N58 control with prefill chunk 12288 | 16 GPUs / 17 min |
| H200 | 24724 | Same N58 chunk 8192 control with HPC-Ops decode | 16 GPUs / 17 min |
| H100 | 221589.pbs111 | Independent both-phase HPC-Ops N52 repeat | 16 GPUs / 45 min |
| H100 | 221590.pbs111 | Same serving configuration, N54; afterany 221589 | 16 GPUs / 45 min |

At submission verification, H200 jobs were pending Resources (later Priority); PBS 221589 was queued and 221590 dependency-held. These are waiting states, not benchmark results. Preserve their queue positions. Maximum new PBS reserve is 3072 SU; the last freshly queried ledger reports Used 27199.147, Balance 36800.853 and In Doubt 0 as of 19 October 12:00:01 SGT. Internal operating headroom after the new reservation is 20728.853 SU under the unchanged 51000-SU operating bound, with a 13000-SU buffer. Those limits are internal planning, not organiser quotas or actual charges for this batch.

Corrected a bookkeeping inconsistency before reserving: the previous status turn reconciled the three old jobs in `jobs` and the ledger, but left their entries in `pending_reservations` as pending. Fresh terminal accounting and the unchanged Used total verify they are already charged. Their pending reservation states are now also RECONCILED_IN_LEDGER, preventing a duplicate conservative deduction. This correction does not increase the research budget.

## What the recovered profile establishes

Job 221346 supplies a separate post-score N48 diagnostic, with four prefill steps and 32 decode steps. All 16 expected ranks have nonzero kernel events and sealed hashes; all 376 diagnostic requests succeeded. It is not the scored N50 traffic and does not measure N52/N54 performance.

| Role | Named HPC-Ops grouped FP8 GEMM share | Other leading kernels |
|---|---:|---|
| prefill-0 | 33.812% | One NCCL Ring BF16 all-reduce kernel 22.784%; FlashAttention kernel 7.344%; HPC-Ops reduction 6.874% |
| prefill-1 | 33.259% | One NCCL Ring BF16 all-reduce kernel 24.007%; FlashAttention kernel 7.232%; HPC-Ops reduction 6.759% |
| decode-0 | 22.888% | FlashInfer paged attention 16.172%; two MNNVL collectives 11.566% and 11.176%; per-token quantisation 9.993% |

These percentages divide summed event durations across ranks by summed kernel durations in that role. They are not elapsed critical-path shares. Do not sum them into an end-to-end speed prediction or attribute every quantisation kernel to MoE. Named HPC-Ops activation/reduction kernels are present too; grouped GEMM alone is not the complete MoE share. Actual names and per-rank hashes are retained in `h100-both-phase-profile.json`.

The trace motivates investigating prefill communication after the current trials. NVIDIA documents that `NCCL_ALGO` can select Ring or Tree, defaults to automatic selection and supports per-collective selection from NCCL 2.24. Restricting algorithms can fail when none is valid. [NVIDIA NCCL environment variable reference](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html#nccl-algo).

A possible next hypothesis is changing only prefill all-reduce selection while preserving decode MNNVL. This is not yet a submitted experiment: first establish the exact NCCL version and that SGLang's active prefill communicator honours the setting, check earlier trials for duplication, and define a same-platform control. A kernel share on H100 does not establish an H200 gain, and automatic algorithm selection may already be better. No new PBS credit is committed to this branch.

## Next review

Review each completed run independently; do not wait for unrelated pending jobs. Compare 24722/24723/24724 with 24721, and 221590 with the N52 repeat 221589. Require full terminal seals, exact submitted payloads, unchanged full-duration protocol, correct runtime and rank coverage, zero request errors/cancellations, the joint latency gate, short nonregression and all 12 long retrieval checks. No automatic higher load or unchanged backend/output-failure retry. Useful gains need independent confirmation before promotion.

The source measurements remain 2780.483 good tokens/s on H200 24647 (original peak 2786.696) and 2398.728 on H100 221341. The new jobs have no score yet. Full organiser accuracy remains unverified: the rules require at least 99% of the organiser's unmodified FP8 reference benchmark score, not matching output text or passing these synthetic diagnostics. Establish the actual organiser evaluation tasks, harness settings and reference before claiming accuracy or scheduling a surrogate full-set check. No slide, official submission package, HPC task or organiser upload changed.
'''
(O/'RESULTS.md').write_text(report)
# Keep the previous handoff, then make CURRENT concise and unambiguous.
archive=W/'notes/archive';archive.mkdir(exist_ok=True);old=archive/'CURRENT-20261019-0400.md'
if not old.exists():shutil.copyfile(W/'notes/CURRENT.md',old)
current='''# Current APAC handoff — 19 October 2026

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
'''
(W/'notes/CURRENT.md').write_text(current)
notice='''## Manual continuation — 19 October 2026

Four H200 trials 24721–24724 and two serial PBS trials 221589→221590 were explicitly submitted after user continuation, source review and live queue/credit checks. New maximum reserve 3072 SU, internal headroom 20728.853 SU; no budget increase. No new score yet. Latest report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0412/RESULTS.md. This supersedes scheduler/access/budget snapshots below; standing safety and acceptance rules continue. Autopilot remains OFF and no background watcher was started.

'''
p=W/'research-autopilot/POLICY.md';p.write_text(notice+p.read_text());(W/'research-autopilot/LATEST.md').write_text(notice+current)
for path in [W/'research-autopilot/HISTORY.md',W/'notes/TIMELINE.md',W/'notes/DECISIONS.md']:
 with path.open('a') as f:f.write('\n'+notice)
# Add reviewed source results to the global machine-readable ledger.
path=R/'comparison.json';comparison=json.loads(path.read_text());ids={'24589','24639','24640','24641','24647'};comparison=[x for x in comparison if x['job'] not in ids];state=json.loads((R/'serving-tuning/registry.json').read_text());notes=json.loads((R/'run-notes.json').read_text())
for entry in state['entries']:
 for attempt in entry['attempts']:
  job=attempt['job']
  if job in ids:
   point=json.loads((R/'research-followup-20261019-0400'/(job+'-review.json')).read_text())['point'];smoke=json.loads((R/'runs'/job/'output-smoke.json').read_text());rows=json.loads((R/'runs'/job/'summary.json').read_text());attempt.update(output_smoke={'passed':smoke['passed'],'total':smoke['total']},output_baseline_comparison=point['short_output_comparison'],measurements=rows)
   entry['measurements']=[dict(job=job,experiment=entry['id'],topology='P8-TP4_D8-TP8-EP8',output_smoke=attempt['output_smoke'],output_baseline_comparison=attempt['output_baseline_comparison'],**row) for row in rows];comparison.extend(entry['measurements'])
   notes[job]=dict(topology='P8-TP4_D8-TP8-EP8',purpose=entry['purpose'],finding='Complete terminal measurement; full local protocol/SLA/short/long evidence passes. See research-followup-20261019-0400.',lesson='Use matched same-platform controls; preserve failed attempts separately. Official accuracy unverified.',performance_evidence=True,provenance_note='Frozen submitted payload and post-completion artifact manifest retained.')
for receipt in slurm:
 p=next(x for x in json.loads((O/'pilots.json').read_text()) if x['id']==receipt['id']);notes[receipt['job']]=dict(topology='P8-TP4_D8-TP8-EP8',purpose=p['purpose'],finding='Submitted; no measurement yet. See research-followup-20261019-0412 receipts.',lesson='One changed factor versus fresh control; stop after backend/output failure.',performance_evidence=False,provenance_note='Frozen payload before submission: '+p['bundle'])
(R/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n');(R/'run-notes.json').write_text(json.dumps(notes,indent=2)+'\n');(R/'serving-tuning/registry.json').write_text(json.dumps(state,indent=2)+'\n')
for name in ['RUNS.md','SERVING_TUNING_RESULTS.md']:
 with (R/name).open('a') as f:f.write('\n## 19 October 2026 — recovered measurements and new controlled batch\n\n[Accepted source results](research-followup-20261019-0400/RESULTS.md): H200 24647 repeats 2780.483 good tokens/s; H100 221341 N52 reaches 2398.728, awaiting repeat. All local gates pass; full organiser accuracy remains unverified. [New plan and receipts](research-followup-20261019-0412/RESULTS.md): H200 24721–24724 and PBS 221589→221590 submitted. New jobs have no accepted measurement yet. Preserve all raw runs and use platform-matched controls.\n')
print('Handoff, budgets, run ledgers and profile evidence recorded',now)
