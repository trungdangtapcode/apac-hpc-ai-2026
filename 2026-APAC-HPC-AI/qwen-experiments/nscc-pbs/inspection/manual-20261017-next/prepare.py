from pathlib import Path
import json,shutil,hashlib,subprocess,datetime,fcntl,importlib.util,re
R=Path.cwd();P=R/'nscc-pbs';O=P/'inspection/manual-20261017-next';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def clone(src,dst,old,new,loadold,loadnew,is_pbs):
 assert not dst.exists();shutil.copytree(src,dst);dst.chmod(0o755)
 for f in dst.iterdir():
  if f.is_file():f.chmod(0o644)
 launch=dst/('benchmark.pbs' if is_pbs else 'job.sbatch');launch.write_text(launch.read_text().replace(old,new).replace(loadold,loadnew))
 c=json.loads((dst/'config.json').read_text());c.update(experiment=new,concurrency=[46,48] if is_pbs else [int(loadnew.split('=')[1])],source_job='220999.pbs111' if is_pbs else '24175',purpose='Bounded independent matched frontier confirmation; preserve failed-SLA points and long checks' if is_pbs else 'Fresh N54 control / bounded N56 capacity probe after independently repeated passing N54 with ITL16.25ms');(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in src.iterdir():
  if f.name not in ['benchmark.pbs','job.sbatch','config.json','SHA256SUMS']:assert f.read_bytes()==(dst/f.name).read_bytes()
 for f in list(dst.glob('*.sh'))+[launch]:subprocess.run(['bash','-n',str(f)],check=True)
 hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in hashes.items()));return hashes
# Read sealed candidate and actual task logs once before arming any PBS work.
d=json.loads((P/'inspection/manual-20261017/review-220999.json').read_text());assert d['terminal_seal_short_payload_pass'] and d['long_diagnostic']['state']=='PASSED'
run=P/'collected/220999.pbs111/20261017T021930446319Z/runs/220999.pbs111';log=next(run.glob('task-decode*.log')).read_text()
assert sorted(set(map(int,re.findall(r'backend=mnnvl, rank=(\d+), world_size=8',log))))==list(range(8))
assert sorted(set(map(int,re.findall(r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3',log))))==list(range(8))
assert 'KV Cache is allocated. dtype: torch.bfloat16' in log
report={'runtime_rank_backend_bf16_pass':True,'pbs':{},'slurm':{},'created_utc':now}
for name,old in [('h100-mnnvl-frontier-repeat-11','h100-mnnvl-capacity-09'),('h100-combo-frontier-repeat-12','h100-mnnvl-flashinfer-10')]:
 report['pbs'][name]=clone(P/old,P/name,old,name,'42 44 46 48','46 48',True)
D=R/'serving-tuning-10';new=[]
for name,n in [('s10-combo-control-n54-v2',54),('s10-combo-probe-n56',56)]:
 hashes=clone(D/'s10-combo-repeat-n54',D/name,'s10-combo-repeat-n54',name,'QWEN_TUNE_NS=54','QWEN_TUNE_NS='+str(n),False);report['slurm'][name]=hashes
 new.append(dict(id=name,bundle=str(D/name),planned_ns=[n],state='PLANNED',wave=10,purpose='N54 control and N56 capacity after two passing N54 measurements; no N58 or automatic promotion',diagnostic_profile=False,expected_profile_ranks={},payload_sha256=hashes,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24175'))
# Explicit plan amendments precede arming, and preserve original submitted bundles.
text='''\n## Bounded continuation — '''+now+'''\n\nUser requests immediate continued submissions. Amend old noN56 restriction based\non two sealed passing comboN54 runs2654.172/2658.195, SLA98.91%, ITL16.25ms,\nshort/runtime passes and both12longpass. Submit freshN54 control and exactlyone\nN56 capacity probe,16H200/17min each,cap5. Same execution/model/backend/long checks;\nonly load and labels change. Compare allN54 controls; report TTFT/ITL/goodput/SLA,\nnot only peak. NoN58, auto retry expansion or promotion; full accuracy unverified.\n\nH100:sealed220999fullprotocol/short/long passes,N48=2204.528/SLA98.766%;\nMNNVLaloneN48failed80.49%,whileN46ties. Actual combo task log confirms MNNVL\nranks0..7,FlashInferattentionranks0..7,BF16KV. Submit matched independent\nMNNVL46/48 thencombo46/48,stoploadincreaseonfail. This confirms frontier\ninteraction instead of assuming causality from one fail/pass. Each16H100/45min,\nstrictafterany,max1running,3072SUmaxreserve;noN50. Budgetused10598.401SU,\nremaining5785.599 before newreserves,projectbalance53401.599,InDoubt0.\nNo new Codex automation; deterministicSlurmwatcher restarted only for this GPUwork.\n'''
(O/'PLAN.md').write_text(text)
with (D/'PLAN.md').open('a') as f:f.write(text)
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 q=subprocess.run(['squeue','-h','-u','apacsc42','-o','%i'],capture_output=True,text=True,check=True);assert len(q.stdout.splitlines())+2<=5
 p=D/'prepared-pilots.json';plan=json.loads(p.read_text());plan['pilots'].extend(new);plan.update(state='ACTIVE',updated_utc=now);p.write_text(json.dumps(plan,indent=2)+'\n')
 with (R/'serving-tuning/watcher.log').open('a') as f:process=subprocess.Popen(['python3','-u',str(R/'watch-serving-tuning.py'),'--run'],cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 (R/'serving-tuning/watcher.pid').write_text(str(process.pid)+'\n');report['watcher_pid']=process.pid
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared and armed2H200, prepared2H100;watcher',process.pid)
