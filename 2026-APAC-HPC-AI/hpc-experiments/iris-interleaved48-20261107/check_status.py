"""Read the accepted ABBA trial without changing its frozen payload."""
from pathlib import Path
import json
from deploy_submit import remote
E=Path(__file__).resolve().parent
r=json.loads((E/'submission-receipt.json').read_text())
body='ROOT='+repr(r['root'])+'\nJOB='+repr(r['job_id'])+r'''
from pathlib import Path
import datetime,subprocess,re,json
k=Path(ROOT)/'kit';run=k/'runs'/JOB
result={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':JOB}
for key,args in [('queue',['squeue','-j',JOB,'-h','-o','%i|%T|%M|%C|%N']),('accounting',['sacct','-j',JOB,'-P','-o','JobID,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList'])]:
 p=subprocess.run(args,text=True,capture_output=True,timeout=15);result[key]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
result['recent_phases']=(run/'phases.jsonl').read_text().splitlines()[-6:] if (run/'phases.jsonl').exists() else []
result['arms']={}
for label in ('A1-default48','B1-balanced48','B2-balanced48','A2-default48'):
 p=run/'arms'/label/'simpleFoam.log'
 if p.exists():
  s=p.read_text();ts=re.findall(r'^Time = (\d+)\s*$',s,re.M);result['arms'][label]={'last_started_step':int(ts[-1]) if ts else None,'end_marker':bool(re.search(r'^End\s*$',s,re.M))}
placement=run/'probes'/'balanced48-placement.json'
result['placement_probe']=json.loads(placement.read_text()) if placement.is_file() else None
result['preparation_tails']={label:(run/(label+'-preparation.log')).read_text()[-2500:] for label in ('A1-default48','B1-balanced48','B2-balanced48','A2-default48') if (run/(label+'-preparation.log')).is_file()}
result['stderr_tail']=(k/'runs'/(JOB+'.err')).read_text()[-1500:] if (k/'runs'/(JOB+'.err')).exists() else ''
'''
d=remote(body,timeout=45);(E/'post-submit-status.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
