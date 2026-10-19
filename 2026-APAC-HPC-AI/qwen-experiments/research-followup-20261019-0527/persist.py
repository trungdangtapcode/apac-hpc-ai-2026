"""Record accepted operating points, actual queues and bounded next submissions."""
from pathlib import Path
import csv,datetime,fcntl,json,shutil,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;W=Path('/home/apacsc42/workspace');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
sj={j:json.loads((O/(j+'-review.json')).read_text()) for j in ['24721','24722']};pj={j:json.loads((O/(j+'.pbs111-review.json')).read_text()) for j in ['221589','221590']};assert all(x['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS' for x in sj.values());assert all(x['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS' for x in pj.values())
queue=subprocess.check_output(['squeue','-u','apacsc42','-o','%.18i %.12P %.32j %.8T %.10M %.6D %R'],text=True);(O/'slurm-latest.txt').write_text(queue)
remote=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch',"bash -lc 'qstat -u apacsc42; qstat -xf 221589.pbs111 221590.pbs111 221645.pbs111 221646.pbs111; myprojects'"],capture_output=True,text=True,timeout=40);(O/'pbs-latest.txt').write_text(remote.stdout);(O/'pbs-latest.stderr').write_text(remote.stderr);assert remote.returncode==0
raw=subprocess.check_output(['sacct','-X','-j','24721,24722,24723,24724,24732,24733','-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True);(O/'slurm-latest-accounting.txt').write_text(raw);statuses={x['JobID']:x for x in csv.DictReader(raw.splitlines(),delimiter='|')}
with (R/'nscc-pbs/budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);p=R/'nscc-pbs/nscc-budget.json';b=json.loads(p.read_text());b['ledger']['freshness_note']='At the pre-submission ledger snapshot, Used delta reconciles 221589. Retain full 1536 SU for terminal 221590 until its charge appears in Used. Newly submitted 221645/221646 are reserved separately. Reported Balance already excludes In Doubt prepayment; do not deduct it twice.';p.write_text(json.dumps(b,indent=2)+'\n')
hg=100*(sj['24722']['point']['metrics']['good_tokens_s']/sj['24721']['point']['metrics']['good_tokens_s']-1);pg=100*(pj['221590']['point']['good_output_tokens_s']/pj['221589']['point']['good_output_tokens_s']-1)
lines=['# New H200 and H100 operating-point observations — 19 October 2026','',f'Checked UTC: {now}. This report follows the user-requested status check during the authorised optimisation work. Full raw snapshots, reviewer code, scheduler receipts and new frozen bundles are retained beside it or in their source-linked run directories.','',
'## Accepted local measurements','',
'| Platform | Job | Configuration | Good tokens/s | Joint SLA (%) | Mean TTFT (ms) | Mean ITL (ms) |','|---|---|---|---:|---:|---:|---:|']
for j,label in [('24721','Fresh DeepGEMM prefill chunk 8192 / auto decode, N58'),('24722','Same serving configuration, N60')]:
 m=sj[j]['point']['metrics'];lines.append(f"| H200 | {j} | {label} | {m['good_tokens_s']:.3f} | {100*m['sla_fraction']:.4f} | {m['ttft_ms']:.3f} | {m['itl_ms']:.3f} |")
for j,label in [('221589','Both-phase HPC-Ops, chunk 4096, N52 independent repeat'),('221590','Same serving configuration, N54')]:
 m=pj[j]['point'];lines.append(f"| H100 | {j} | {label} | {m['good_output_tokens_s']:.3f} | {100*m['sla_fraction']:.4f} | {m['ttft_avg_ms']:.3f} | {m['itl_avg_ms']:.3f} |")
lines += ['',f'**H200 24722 is a new highest observation: 2839.532 good tokens/s, +{hg:.4f}% versus fresh same-platform N58 control 24721.** That control (2780.403) differs from the previous independent N58 repeat 24647 (2780.483) by only about −0.003%. The changed factor is concurrency 58 to 60. The new N60 result still needs its own independent repeat; it is not a reproduced gain or a statistical significance claim.','',f'**H100 221590 is a new highest observation: 2430.891 good tokens/s, +{pg:.4f}% versus the fresh N52 repeat 221589.** Original N52 job 221341 scored 2398.728, and this N52 repeat scores 2411.304. Preserve both observations rather than choosing the lower comparator. The N54 gain is small and requires independent confirmation. Its higher mean TTFT and lower mean ITL are both reported; the joint per-request gate determines acceptance.','',
'All four completed allocations have successful terminal accounting, complete unchanged 60-second warmup / 120-second scoring / 30-second grace, sealed raw exports, frozen payload hashes, zero request errors/cancellations, intended runtime, short-output nonregression and all 12 long retrieval checks. PBS long answers were also checked against the retained response text and expected values, not only their precomputed pass flags. H200 runtime differs from the accepted source only in random seeds; PBS runtime likewise retains both-phase HPC-Ops, BF16 KV, speculation disabled, the intended TP/EP layout and all decode backend ranks. The H200 360-second whole-client guard did not fire.','',
'Good tokens/s is the rate of requests satisfying both TTFT ≤ 3000 ms and request-mean ITL ≤ 20 ms, multiplied by the prescribed 200 output tokens. At least 90% of all requests must pass jointly. Latency table entries are means in milliseconds. Local synthetic output checks do not establish full organiser accuracy at 99% of the reference score.','',
'## Next jobs actually submitted','',
'| Platform | Job | Trial and comparison | Maximum request |','|---|---|---|---|',
'| H200 | 24732 | Independent N60 repeat of 24722 | 16 GPUs / 17 min |',
'| H200 | 24733 | One N62 trial, same serving configuration; compare 24732 | 16 GPUs / 17 min |',
'| H100 | 221645.pbs111 | Independent N54 repeat of 221590 | 16 GPUs / 45 min |',
'| H100 | 221646.pbs111 | One N56 trial, same serving configuration; afterany 221645 | 16 GPUs / 45 min |','',
'The higher-load points are new explicit decisions after the preceding source point passed every local gate. They are not automatic retries or an unchanged continuation of a failed load. The repeated source observations have joint SLA success above 98%, TTFT below 1 second and mean ITL below the 20-ms bound. This motivates one bounded next load test, not a prediction that it passes. Worker, client, precision, quality scripts and transport are byte-identical to the source in every new bundle; only concurrency and identifying metadata differ. No automatic N64 on H200 or N58 on H100. Stop a losing/error/quality branch and retain its data.','',
'H200 24723 (chunk 12288 at N58) and 24724 (HPC-Ops decode with chunk 8192 at N58) retain their original positions. They are independent factors; do not wait for them before reviewing completed load trials. Current exact queue/accounting snapshots are slurm-latest.txt, slurm-latest-accounting.txt and pbs-latest.txt. New jobs have no score yet.','',
'## Credit and preservation','',
f"Pre-submission ledger as of {b['ledger']['as_of']} SGT: Used {b['ledger']['used_su']:.3f} SU, reported Balance {b['ledger']['balance_su']:.3f} SU, In Doubt {b['ledger']['in_doubt_su']:.3f} SU. Only charges reflected in Used were reconciled. Any terminal job awaiting the ledger retains its full maximum reservation. The new two-job PBS reservation is **3072 SU**, not actual expenditure. Internal headroom after all conservative reservations is **{b['campaign_headroom_after_reserved_su']:.3f} SU**, under the unchanged 51000-SU bound and 13000-SU buffer. Balance already excludes prepayment; do not deduct In Doubt twice. The ledger is a dated published snapshot, not a live second-by-second total.", '',
'No VPN restart, reauthentication, background AI, automatic watcher, slide, official submission package or organiser upload occurred. Full source data and failures remain preserved; capture this milestone with actual Git dates and keep the external object store with the archive.']
(O/'RESULTS.md').write_text('\n'.join(lines)+'\n')
(O/'PLAN.md').write_text('''# Bounded load followup after complete source review

The source measurements and exact new IDs are in [RESULTS.md](RESULTS.md). H200 N60 passed at 2839.532 good tokens/s and H100 N54 at 2430.891; neither new load has an independent repeat yet.

Submit one repeat plus one further load step on each platform: H200 N60 repeat then N62, H100 N54 repeat then N56 in a serial PBS chain. Retain all serving/runtime/client/quality payloads unchanged and freeze new metadata hashes. Use each same-platform repeat as the fresh control. Prior H200 chunk/backend jobs keep queue positions. Require all terminal raw protocol/runtime/output gates and preserve failure evidence. No unchanged retry or automatic higher load follows this batch.

The maximum new PBS reservation is 3072 SU under the existing operating budget. Reconcile only terminal charges already reflected in Used; retain any ledger-lag maximum reserve. No new budget, model precision, GPU count, official accuracy claim or background scheduling is authorised by this plan.
''')
# Retain the preceding handoff before updating its current statements.
archive=W/'notes/archive';archive.mkdir(exist_ok=True);backup=archive/'CURRENT-20261019-0412.md'
if not backup.exists():shutil.copyfile(W/'notes/CURRENT.md',backup)
p=W/'notes/CURRENT.md';s=p.read_text();s=s.replace('research-followup-20261019-0412/RESULTS.md','research-followup-20261019-0527/RESULTS.md')
start=s.index('Four H200 jobs');end=s.index('VPN and SSH',start)
s=s[:start]+'''H200 24721 (N58 control) and 24722 (N60) are completed and fully reviewed. **24722 = 2839.532 good tokens/s**, +2.1266% versus 24721 = 2780.403, is the new highest observation; independent N60 repeat **24732** and one N62 trial **24733** are now submitted. Existing **24723** chunk 12288 at N58 is running and **24724** HPC-Ops decode at N58 is pending at this check. Preserve positions. Each requests 16 GPUs / 17 minutes. No automatic N64 or unchanged failure retry.

H100 221589 N52 repeat (2411.304) and 221590 N54 (2430.891) both completed and pass full local checks. **221590 = 2430.891** is the new highest observation, +0.8123% versus the fresh N52 repeat. Independent N54 repeat **221645.pbs111** and one N56 trial **221646.pbs111** were submitted with verified afterany dependency; at most one 16-GPU PBS allocation running. Each requests at most 45 minutes. No automatic H100 N58. New jobs have no score yet.

'''+s[end:]
start=s.index('Freshly queried PBS ledger');end=s.index('## Accepted local measurements',start)
s=s[:start]+f"Pre-submission ledger as of {b['ledger']['as_of']} SGT: Used {b['ledger']['used_su']:.3f} SU, Balance {b['ledger']['balance_su']:.3f} SU, In Doubt {b['ledger']['in_doubt_su']:.3f}. New two-job maximum reserve **3072 SU**; conservative internal headroom **{b['campaign_headroom_after_reserved_su']:.3f} SU** under the unchanged 51000-SU bound and 13000-SU buffer. Retain any terminal-ledger-lag maximum reservation until Used reconciles; do not deduct prepayment twice. Reserve under budget.lock and never retry uncertain qsub. This is a dated published ledger snapshot.\n\n"+s[end:]
s=s.replace('Latest complete source review: [recovered results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0400/RESULTS.md).','Latest complete review: [new operating points](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0527/RESULTS.md). Older source measurements below remain historical context.')
s=s.replace('- H100 highest observation: **221341 = 2398.728**, both-phase HPC-Ops N52; independent repeat now queued.','- Historical H100 N52 source **221341 = 2398.728**, now independently repeated by 221589 = 2411.304; the new highest observation is N54 above.')
p.write_text(s)
notice=f'''## Manual result review and next batch — {now}

H20024722 N60 passes at2839.532goodtokens/s (+2.1266% vs fresh24721); H100221590 N54 passes at2430.891 (+0.8123% vs freshN52 repeat221589). All local terminal/protocol/runtime/short/long gates pass; official accuracy unverified. Submitted H20024732 N60 repeat and24733 N62; PBS221645 N54 repeat→221646 N56, new maximum3072SU. Older24723/24724 keep positions. Conservative internal headroom {b['campaign_headroom_after_reserved_su']:.3f} SU; no budget increase. Full readable report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0527/RESULTS.md. Autopilot remains OFF. This supersedes older queue/measurement/credit snapshots below.

'''
# Keep handoff prose readable even in compact ledger notices.
notice=notice.replace('H20024722','H200 24722').replace('at2839.532goodtokens/s','at 2839.532 good tokens/s').replace('fresh24721','fresh 24721').replace('H100221590','H100 221590').replace('at2430.891','at 2430.891 good tokens/s').replace('freshN52 repeat221589','fresh N52 repeat 221589').replace('H20024732','H200 24732').replace('and24733','and 24733').replace('PBS221645','PBS 221645').replace('repeat→221646','repeat → 221646').replace('maximum3072SU','maximum 3072 SU').replace('Older24723/24724','Older 24723/24724')
policy=W/'research-autopilot/POLICY.md';policy.write_text(notice+policy.read_text());(W/'research-autopilot/LATEST.md').write_text(notice+s)
for path in [W/'notes/DECISIONS.md',W/'notes/TIMELINE.md',W/'research-autopilot/HISTORY.md']:
 with path.open('a') as f:f.write('\n'+notice)
# Update machine-readable ledgers and add a short source-linked run ledger entry.
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);path=R/'serving-tuning/registry.json';state=json.loads(path.read_text());notes=json.loads((R/'run-notes.json').read_text());comparison=[x for x in json.loads((R/'comparison.json').read_text()) if x['job'] not in sj]
 for entry in state['entries']:
  for a in entry['attempts']:
   job=a['job']
   if job in sj:
    point=sj[job]['point'];smoke=json.loads((R/'runs'/job/'output-smoke.json').read_text());a.update(state='COMPLETED',status=statuses[job],measurements=json.loads((R/'runs'/job/'summary.json').read_text()),output_smoke={'passed':smoke['passed'],'total':smoke['total']},output_baseline_comparison=point['short_output_comparison']);entry['measurements']=[dict(job=job,experiment=entry['id'],topology='P8-TP4_D8-TP8-EP8',output_smoke=a['output_smoke'],output_baseline_comparison=a['output_baseline_comparison'],**row) for row in a['measurements']];entry.update(state='MEASURED',benchmark_complete=True,missing_ns=[]);comparison.extend(entry['measurements']);notes[job]=dict(topology='P8-TP4_D8-TP8-EP8',purpose=entry['purpose'],finding='Completed full local protocol/SLA/runtime/output checks; see research-followup-20261019-0527.',lesson='Repeat new highest operating points and use a fresh same-platform control.',performance_evidence=True)
 for receipt in json.loads((O/'slurm-receipts.json').read_text()):
  pilot=next(x for x in json.loads((O/'pilots.json').read_text()) if x['id']==receipt['id']);notes[receipt['job']]=dict(topology='P8-TP4_D8-TP8-EP8',purpose=pilot['purpose'],finding='Submitted; no measurement yet.',lesson='One load step with source gates and a fresh repeat; no automatic higher load.',performance_evidence=False)
 path.write_text(json.dumps(state,indent=2)+'\n');(R/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n');(R/'run-notes.json').write_text(json.dumps(notes,indent=2)+'\n');p=R/'job-status.json';d=json.loads(p.read_text());d.update(statuses);p.write_text(json.dumps(d,indent=2)+'\n')
p=R/'nscc-pbs/continuous-plan.json';plan=json.loads(p.read_text())
for pilot in plan['pilots']:
 j=pilot.get('job_id','').split('.')[0]
 if j in pj:pilot.update(state='F',result_state='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS',review=str(O/(j+'.pbs111-review.json')),accuracy_verified=False)
p.write_text(json.dumps(plan,indent=2)+'\n')
for name in ['RUNS.md','SERVING_TUNING_RESULTS.md']:
 with (R/name).open('a') as f:f.write('\n## 19 October 2026 — new load observations and independent repeats\n\nH200 24722 = 2839.532 good tokens/s, +2.1266% versus fresh N58 control 24721. H100 221590 = 2430.891, +0.8123% versus N52 repeat 221589. All local gates pass; new operating points await independent repeats and official accuracy remains unverified. Submitted H200 24732/24733 and PBS 221645→221646. [Full measurements, units, control mapping and receipts](research-followup-20261019-0527/RESULTS.md).\n')
(O/'checked-utc.txt').write_text(now+'\n');print('Reviewed results, budget caveats and next job IDs persisted',now)
