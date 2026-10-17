from pathlib import Path
import json,statistics,hashlib,re,shutil,subprocess,datetime
R=Path(__file__).resolve().parents[2];D=R/'serving-tuning-10';O=Path(__file__).parent;run=R/'runs/24263';now=datetime.datetime.now(datetime.timezone.utc).isoformat();rows=json.loads((run/'diagnostic-profile/kernel-summary.json').read_text())['traces'];assert len(rows)==16
roles={}
for role,count in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:
 a=[x for x in rows if '/'+role+'/' in x['trace']];ranks={int(re.search(r'-TP-(\d+)(?:-EP-|\.trace)',x['trace']).group(1)) for x in a};assert len(a)==count and ranks==set(range(count)) and all(x['kernels']>0 for x in a)
 roles[role]={'ranks':sorted(ranks),'mean_moe_fraction':statistics.mean(x['moe_fraction_of_summed_kernel_time'] for x in a),'mean_collective_fraction':statistics.mean(x['collective_fraction_of_summed_kernel_time'] for x in a)}
req=json.loads((run/'diagnostic-profile/requests.json').read_text());assert all(x.get('ok') is True and 'error' not in x for x in req)
(O/'profile-review.json').write_text(json.dumps({'reviewed_utc':now,'roles':roles,'diagnostic_concurrency':48,'successful_requests':len(req),'control_warnings':json.loads((run/'diagnostic-profile/profile-control.json').read_text()),'status':'Usable traces with control warnings; summed kernels are not walltime'},indent=2)+'\n')
(O/'RESULTS.md').write_text('''# Job 24263: benchmark and profile review

The full N56 benchmark reached **2,667.46 good tokens/s**, SLA **98.80%**, zero
errors/cancellations, and 12/12 long checks. This confirms the existing performance
range; it is not a new gain.

## Diagnostic evidence

The profile ran after scoring with **48 concurrent requests**. Earlier notes
calling it a 52-request profile are historical; protocol.json records the actual
load. All 16 rank traces contain kernels, and all 415 diagnostic requests succeeded.

| Role | Mean MoE fraction | Mean collective fraction |
|---|---:|---:|
| Prefill 0 | 42.84% | 23.48% |
| Prefill 1 | 42.77% | 23.64% |
| Decode | 27.99% | 23.89% |

These are per-rank means of classifier fractions of summed kernel durations,
not fractions of job wall time or predicted speedups. Prefill/decode captured
4/32 steps respectively, so their absolute sums are not comparable phase times.

Start-profile returned HTTP200 but the client failed to parse its response as
JSON. Later explicit stops returned HTTP500: the server said profiling was no
longer running. Keep these control warnings. Valid traces exist for every rank;
no extra GPU rerun is justified merely to remove these warnings.

## Next trial: DeepGEMM for prefill only

The profile motivates testing the prefill MoE implementation. The earlier
DeepGEMM experiment changed **decode** and lost performance; that result does not
establish whether DeepGEMM helps the much larger prefill batches. It may still
lose here. Do not assume that a large kernel fraction proves a bottleneck.

Keep both prefill workers TP4/EP1 and decode TP8/EP8 with MNNVL+FlashInfer. Change
only prefill `--moe-runner-backend deep_gemm`. Exact image source snapshots under
source/ expose this backend and its standard-layout path for unsplit experts.
This is source compatibility evidence, not GPU validation.

One initial N56 allocation, 16H200/17min; official FP8, BF16KV, RR/NIXL and full
60/120/30 protocol unchanged, followed by the same short/12long checks. Compare
against 24263's benchmark before profiling and 24190/24235. Require runtime backend
proof, SLA>=90%, zero errors/cancel, short nonregression and long pass. Any useful
gain needs an independent repeat. No automatic repeat, new load, H100 spending,
or organiser accuracy claim.
''')
name='s10-prefill-deepgemm-n56';src=D/'s10-combo-repeat-n56';dst=D/name;assert not dst.exists();shutil.copytree(src,dst);dst.chmod(0o755)
for f in dst.iterdir():
 if f.is_file():f.chmod(0o644)
f=dst/'job.sbatch';f.write_text(f.read_text().replace('s10-combo-repeat-n56',name));f=dst/'worker.sh';s=f.read_text();assert s.count('extra=(--chunked-prefill-size 4096)')==1;f.write_text(s.replace('extra=(--chunked-prefill-size 4096)','extra=(--chunked-prefill-size 4096 --moe-runner-backend deep_gemm)'))
f=dst/'config.json';c=json.loads(f.read_text());c.update(experiment=name,source_job='24263',purpose='Profile-guided prefill-only DeepGEMM trial; decode unchanged',prefill_extra_flags=['--chunked-prefill-size','4096','--moe-runner-backend','deep_gemm']);f.write_text(json.dumps(c,indent=2)+'\n')
for f in src.iterdir():
 if f.name not in ['job.sbatch','worker.sh','config.json','SHA256SUMS']:assert f.read_bytes()==(dst/f.name).read_bytes()
for f in list(dst.glob('*.sh'))+[dst/'job.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()))
with (D/'PLAN.md').open('a') as f:f.write('\n## Prefill-only DeepGEMM — '+now+'\n\n[Evidence and bounded plan](profile-review-24263/RESULTS.md). One N56 trial,\n16H200/17min, full protocol and quality checks. This changes prefill, whereas\nthe previous rejected DeepGEMM trial changed decode. No automatic repeat.\n')
q=subprocess.run(['squeue','-h','-u','apacsc42','-o','%i'],capture_output=True,text=True,check=True);assert len(q.stdout.splitlines())<5
f=D/'prepared-pilots.json';plan=json.loads(f.read_text());plan['pilots'].append(dict(id=name,bundle=str(dst),planned_ns=[56],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[56],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24263'));plan.update(state='ACTIVE',updated_utc=now);tmp=f.with_suffix('.moe.tmp');tmp.write_text(json.dumps(plan,indent=2)+'\n');tmp.replace(f)
(O/'pilot-validation.json').write_text(json.dumps({'shell_syntax_pass':True,'only_execution_change':'prefill-only --moe-runner-backend deep_gemm','payload_sha256':h,'GPU_validated':False},indent=2)+'\n');print('Reviewed profile; armed one prefill-only DeepGEMM N56 trial')
