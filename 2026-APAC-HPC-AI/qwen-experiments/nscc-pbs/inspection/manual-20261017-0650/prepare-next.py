from pathlib import Path
import json,shutil,hashlib,subprocess,datetime,fcntl
R=Path.cwd();P=R/'nscc-pbs';O=P/'inspection/manual-20261017-0650';D=R/'serving-tuning-10';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def clone(src,dst,old,new,oldload,newload,ns,pbs):
 assert not dst.exists();shutil.copytree(src,dst);dst.chmod(0o755)
 for f in dst.iterdir():
  if f.is_file():f.chmod(0o644)
 launch=dst/('benchmark.pbs' if pbs else 'job.sbatch');launch.write_text(launch.read_text().replace(old,new).replace(oldload,newload))
 p=dst/'config.json';c=json.loads(p.read_text());c.update(experiment=new,concurrency=ns,source_job='221021.pbs111' if pbs else '24190',purpose='Bounded measured frontier continuation; preserve all failed SLA points and quality diagnostics');p.write_text(json.dumps(c,indent=2)+'\n')
 for f in src.iterdir():
  if f.name not in ['config.json','SHA256SUMS','job.sbatch','benchmark.pbs']:assert f.read_bytes()==(dst/f.name).read_bytes()
 for f in list(dst.glob('*.sh'))+[launch]:subprocess.run(['bash','-n',str(f)],check=True)
 hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in hashes.items()));return hashes
report={'created_utc':now,'pbs':{},'slurm':{}}
for name,source,ns in [('h100-mnnvl-midpoint-13','h100-mnnvl-frontier-repeat-11',[47]),('h100-combo-load-14','h100-combo-frontier-repeat-12',[48,50,52])]:
 report['pbs'][name]=clone(P/source,P/name,source,name,'46 48',' '.join(map(str,ns)),ns,True)
new=[]
for name,n in [('s10-combo-repeat-n56',56),('s10-combo-probe-n58',58)]:
 h=clone(D/'s10-combo-probe-n56',D/name,'s10-combo-probe-n56',name,'QWEN_TUNE_NS=56','QWEN_TUNE_NS='+str(n),[n],False);report['slurm'][name]=h
 new.append(dict(id=name,bundle=str(D/name),planned_ns=[n],state='PLANNED',wave=10,purpose='Confirm N56 or modest N58 probe after full passing N56; noN60 or promotion',diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24190'))
text='''# Bounded continuation — '''+now+'''

User asks continue within existingbudget; noCodexautopilot. All source jobs now
terminalexit0. H200sealedfullprotocol/runtime/short/long passes:24189N54=2658.547,
24190N56=2671.109,SLA98.800%,TTFT847.849ms,ITL16.287ms,long12/12. ModestN56gain
is provisional. Send exactlyoneN56repeat andoneN58probe16H200/17min; this amends
previousnoN58basedonnewN56evidence. Sameexecutionexceptload/metadata;noN60.

H100repeat221021comboN48=2190.538/SLA98.759%,versusprior2209992204.528/98.766%.
MNNVLaloneN48againfailsSLA64.211%;N46passes2182.281. ComboN46slower2143.069,
so no universal speedupclaim. Bothlonglogs12/12;fullsealed review mustpassbeforeqsub.
Two useful nextpoints: MNNVLN47 midpoint (between repeated46pass/48fail), and
combo48anchor/50/52capacitysweep,stopfirstfailedSLA/error. Sameexecution/quality.
Do not promote or claimaccuracy99%; no automaticrepeat orN54H100.

EachH100allocation16GPU45minmax1536SU;strictafteranychain,max1running,cap3.
Used12487.681SU,remaining3896.319;newmaxreserve3072leaves824.319SU. Preserveproject
13000SU. Reconcile old1889.280SUcharges andfreshqueue/credit underbudget.lock.
No further45minH100jobfits afterreserves withoutactualcostreconciliation.
'''
(O/'PLAN.md').write_text(text)
with (D/'PLAN.md').open('a') as f:f.write('\n'+text)
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);q=subprocess.run(['squeue','-h','-u','apacsc42','-o','%i'],capture_output=True,text=True,check=True);assert len(q.stdout.splitlines())+2<=5
 p=D/'prepared-pilots.json';d=json.loads(p.read_text());d['pilots'].extend(new);d.update(state='ACTIVE',updated_utc=now);p.write_text(json.dumps(d,indent=2)+'\n')
 with (R/'serving-tuning/watcher.log').open('a') as f:proc=subprocess.Popen(['python3','-u',str(R/'watch-serving-tuning.py'),'--run'],cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 (R/'serving-tuning/watcher.pid').write_text(str(proc.pid)+'\n');report['watcher_pid']=proc.pid
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Armed2H200; prepared2H100; watcher',proc.pid)
