"""Persist this live status check, reconciled credit and reviewed measurements."""
from pathlib import Path
import datetime,fcntl,json
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;W=Path('/home/apacsc42/workspace');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
slurm=json.loads((O/'slurm-reviews.json').read_text());pbs={j:json.loads((O/(j+'.pbs111-review.json')).read_text()) for j in ['221340','221341','221346']}
assert all(v['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS' for v in slurm.values());assert all(v['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS' for v in pbs.values())
new=slurm['24647']['point'];control=slurm['24589']['point'];gain=100*(new['metrics']['good_tokens_s']/control['metrics']['good_tokens_s']-1)
for role,a in new['server_args'].items():
 b=control['server_args'][role];delta={k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)};allowed={'random_seed'}
 if role.startswith('prefill'):
  allowed|={'chunked_prefill_size','cuda_graph_config'};assert a['chunked_prefill_size']=='8192' and b['chunked_prefill_size']=='4096';assert a['cuda_graph_config'].split(', prefill=PhaseConfig(')[0]==b['cuda_graph_config'].split(', prefill=PhaseConfig(')[0]
 assert not delta-allowed,(role,delta)
ledger=R/'nscc-pbs/nscc-budget.json'
with (R/'nscc-pbs/budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);d=json.loads(ledger.read_text());old=d['ledger'];wall={'221340.pbs111':'00:14:43','221341.pbs111':'00:11:35','221346.pbs111':'00:13:19'}
 cost=sum(sum(int(t)*m for t,m in zip(s.split(':'),[3600,60,1]))*16*128/3600 for s in wall.values());assert abs((27199.147-old['used_su'])-cost)<.002
 for row in d['jobs']:
  if row.get('job_id') in wall:row.update(state='F',exit_status=0,observed_walltime=wall[row['job_id']],included_in_ledger_used=True,accounting_pending=False,last_checked_utc=now,state_fresh=True)
 d['ledger'].update(as_of='19/10/2026-12:00:01',grant_su=64000.0,used_su=27199.147,balance_su=36800.853,in_doubt_su=0.0,source=str(O/'pbs-status-credit.txt'),queried_utc=now,freshness_note='New Used delta matches all three recovered terminal jobs at 128 SU per GPU-hour within rounding; no own active PBS jobs.')
 d.update(updated_utc=now,active_pbs_jobs=[],active_pbs_jobs_verified=True,unallocated_commissioning_su=23800.853,campaign_headroom_after_reserved_su=23800.853,reconciliation_note='Recovered terminal 221340/221341/221346; Used delta 1352.249 SU matches their measured walltimes. No outstanding allocation reservations; no new qsub.')
 d['latest_access_check']=dict(checked_utc=now,state='VPN_AND_SSH_RESTORED_AT_USER_REQUEST',pbs_and_credit_refreshed=True,qsub_attempted=False)
 d['evidence'].append(str(O/'pbs-status-credit.txt'));ledger.write_text(json.dumps(d,indent=2)+'\n')
lines=['# Live queue, recovered access and completed results — 19 October 2026','',f'Checked UTC: {now}. Scheduler and accounting evidence is stored beside this report.','',
'Both own queues are empty. All five H200 allocations and the three recovered PBS allocations finished with exit status zero. This is a dated observation, not a promise about future queue state. No new GPU allocation was submitted during this status/login request.','',
'## H200 results','',
'All five measurements pass the unchanged raw protocol, joint latency/error gate, frozen submitted payload hashes, short-output nonregression and all 12 long retrieval checks. Actual logs retain BF16 KV, speculation disabled, all decode NIXL/MNNVL/attention ranks and HPC-Ops preflight where requested. The independent repeat 24647 has only intended prefill chunk/graph geometry differences versus fresh control 24589, apart from random seeds. The 360-second whole-client guard did not fire; it contains a stall rather than proving its underlying cause is repaired.','',
'| Job | Configuration | Good tokens/s | Joint SLA (%) | TTFT mean (ms) | ITL mean (ms) |','|---|---|---:|---:|---:|---:|']
labels={'24589':'DeepGEMM prefill, chunk 4096, auto decode, N58 control','24639':'DeepGEMM prefill, chunk 4096, HPC-Ops decode, N58','24640':'HPC-Ops prefill, chunk 6144, auto decode, N56','24641':'HPC-Ops prefill and decode, chunk 4096, N56','24647':'DeepGEMM prefill, chunk 8192, auto decode, N58 bounded repeat'}
for j,v in slurm.items():
 m=v['point']['metrics'];lines.append(f"|{j}|{labels[j]}|{m['good_tokens_s']:.3f}|{100*m['sla_fraction']:.4f}|{m['ttft_ms']:.3f}|{m['itl_ms']:.3f}|")
lines+=['',f'24647 reproduces the useful chunk-8192 result at **2780.483 good tokens/s**, **+{gain:.4f}%** versus fresh same-load control 24589 (2718.797). Original 24544 was 2786.696; the two completed observations have descriptive mean {(2786.696+2780.4826483016136)/2:.3f}. Retain failed warmup attempt 24588 as a failed attempt, not a score. No statistical confidence claim. Official full-set accuracy remains unverified.','',
'24639 adds only +0.2117% versus the same-load auto-decode control, while raising TTFT. 24640 does not improve the better separate chunk/runner observations; do not assume additive gains. 24641 is a useful 2742.207 observation but remains below the chunk-8192 N58 result and needs its own repeat before promotion.','',
'## H100 results recovered after VPN restoration','',
'VPN was restored at 04:01:09 UTC through the existing tmux-owned IPsec/TCPT client, keeping the private cache. Only the old dead terminal was removed. SSH password authentication then succeeded on a2ap-login01. The initial batch-only SSH rejection was an SSH authentication failure after the VPN was already connected. No additional MFA code was requested by this client; phone-side DUO behaviour was not observed. The tunnel was detached from the tool terminal and left running. No credentials or session material are part of this report.','',
'All three recovered allocations pass terminal accounting, collected evidence hashes, frozen planned payload, full protocol, joint latency/error, short output, long retrieval and intended resolved runtime checks.','',
'| Job | Configuration | Good tokens/s | Joint SLA (%) | TTFT mean (ms) | ITL mean (ms) |','|---|---|---:|---:|---:|---:|']
for j,label in [('221340','Auto prefill, HPC-Ops decode, N50 fresh control'),('221341','HPC-Ops prefill and decode, N52'),('221346','HPC-Ops prefill and decode, N50; separate post-score profile')]:
 m=pbs[j]['point'];lines.append(f"|{j}|{label}|{m['good_output_tokens_s']:.3f}|{100*m['sla_fraction']:.4f}|{m['ttft_avg_ms']:.3f}|{m['itl_avg_ms']:.3f}|")
lines+=['','New H100 highest observation is **221341: 2398.728 good tokens/s**, +1.1285% versus prior N50 peak 221315 (2371.961). That comparison changes concurrency and is not an isolated backend effect or an independently repeated N52 result. Job 221346 provides another both-phase N50 observation at 2375.807, +3.1962% versus fresh N50 decode-only control 221340. Its GPU profile files were recovered but kernel classification was not performed in this status turn. H100 and H200 scores remain separate measured platforms.','',
'## Credit and evidence limits','',
'Fresh project ledger as of 19 October 12:00:01 SGT: grant 64000.000 SU, Used 27199.147 SU, Balance **36800.853 SU**, In Doubt 0.000 SU. Used increased 1352.249 SU, matching 16 GPUs at 128 SU/GPU-hour for the three recovered walltimes (14:43, 11:35, 13:19), within ledger rounding. Reconciled their reservations under budget.lock. Internal operating headroom under the unchanged 51000-SU bound is 23800.853 SU, with the separate 13000-SU planning buffer. These planning bounds are not organiser quotas.','',
'Good tokens/s is the qualifying request rate multiplied by the prescribed 200 output tokens. Each qualifying request must satisfy TTFT ≤ 3000 ms and mean ITL ≤ 20 ms; at least 90% of all requests must pass jointly. Mean latency values alone do not establish this gate. Synthetic short/long checks are research safeguards, not the official 99%-of-reference accuracy evaluation. Raw artifacts and failures remain preserved.','',
'Autopilot remains disabled. No background AI, new job, slide, official package or organiser upload was created.']
(O/'RESULTS.md').write_text('\n'.join(lines)+'\n')
p=W/'notes/CURRENT.md';text=p.read_text();text=text.replace('# Current APAC handoff — 18 October 2026, 19:25 UTC','# Current APAC handoff — 19 October 2026, status and login check')
start=text.index('## Foreground task');end=text.index('## Standing instructions')
text=text[:start]+'''## Latest live check — 19 October 2026, 04:00–04:06 UTC

The user requested live Slurm status and a PBS/DUO login attempt. Both own queues are empty. All five H200 jobs and all three recovered H100 jobs finished successfully and pass local protocol/SLA/output checks. Full report and raw evidence: [19 October results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0400/RESULTS.md).

H200 24647 independently repeats chunk 8192 N58 at **2780.483 good tokens/s**, +2.2688% versus fresh same-load control 24589 (2718.797); original peak 24544 remains 2786.696. H100 new highest observation is **221341, both-phase HPC-Ops N52, 2398.728**; N52 repeat remains outstanding. H100 N50 221346 scores 2375.807 versus fresh decode-only control 221340 at 2302.223. Full official accuracy remains unverified.

VPN restored at 04:01:09 UTC and SSH on a2ap-login01 succeeded; tmux tunnel remains running, private cache preserved. Client requested no extra MFA code; phone-side DUO was not observed. Fresh ledger 19 October 12:00:01 SGT: Used 27199.147 SU, Balance 36800.853 SU, In Doubt 0. Reconciled all three terminal jobs; no outstanding reserves, internal headroom 23800.853 SU. No new job, slide, organiser upload or AI schedule this turn. Older queue/VPN/credit statements below are historical.

## Local preservation and active workspaces

Work in `/home/apacsc42/2026-APAC-HPC-AI` and `/home/apacsc42/workspace`; archive into `/home/apacsc42/apac-hpc-ai-research` with sibling `apac-hpc-ai-research-artifacts`. AGENTS.md records explicit milestone capture and commit, not an automatic mirror. Preserve history and large-object hashes; exclude secrets. GitHub CLI and upload remain deferred. The initial 47-commit snapshot is historical; later captures use actual dates. Both local directories remain on this machine, so off-host recovery is not yet assured.

'''+text[end:]
text=text.replace('## Latest failure and live queue — supersedes older queue snapshots','## Historical 18 October failure and queue — superseded by the live check above').replace('## H100 access and historical verified results','## Historical H100 access and results — superseded above')
p.write_text(text)
for p,entry in [(W/'notes/TIMELINE.md','## 19 October 2026 — live queues, restored PBS access and recovered results'),(W/'notes/DECISIONS.md','## 19 October 2026 — requested status and VPN login')]:
 with p.open('a') as f:f.write('\n'+entry+'\n\nBoth own queues are empty. At the user’s explicit request, restored the existing tmux VPN and authenticated SSH without exposing or changing the private cache. No client MFA code requested; phone-side DUO unknown. H200 24647 passes at 2780.483 good tokens/s, +2.2688% versus fresh 24589. Recovered H100 221341 N52 passes at 2398.728, independent N52 repeat outstanding. N50 221346 passes at 2375.807. Fresh balance 36800.853 SU; reconciled three completed PBS jobs. No new submission or AI schedule. Full source-linked report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0400/RESULTS.md. Archive capture is a separate explicit local operation; no GitHub upload.\n')
