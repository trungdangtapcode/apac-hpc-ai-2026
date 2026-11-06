"""Read accepted initialization state through the interactive Iris bridge."""
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json
r=json.loads((E/'submission-receipt.json').read_text())
body='ROOT='+repr(r['root'])+'\nJOB='+repr(r['job_id'])+r'''
from pathlib import Path
import subprocess,datetime
r=Path(ROOT);runs=r/'init-runs';a=r/'artifacts/cut-N40-scotch'
result={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':JOB}
for key,args in [('queue',['squeue','-j',JOB,'-h','-o','%i|%T|%M|%C|%N']),('accounting',['sacct','-j',JOB,'-P','-o','JobID,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList'])]:
 p=subprocess.run(args,text=True,capture_output=True,timeout=15);result[key]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
result['ready']=(a/'READY').read_text() if (a/'READY').is_file() else None
result['in_progress']=(a/'.INIT_IN_PROGRESS').exists()
result['files']=[p.name for p in runs.glob(JOB+'*') if p.is_file()]
result['stderr_tail']=(runs/(JOB+'.sbatch.err')).read_text()[-1500:] if (runs/(JOB+'.sbatch.err')).exists() else ''
'''
d=run_json("print(\"\\n\", flush=True)\n"+body,timeout=45)
(E/'post-submit-status.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d,indent=2))
