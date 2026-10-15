"""One foreground observation, bounded to14min; never submits or alters a job."""
from pathlib import Path
from datetime import datetime, timezone
import json, re, shlex, subprocess, time
OUT=Path(__file__).resolve().parent
HELPER='/home/apacsc42/workspace/vpn-rootless/vpn.sh'
REMOTE=r'''
import concurrent.futures,datetime,json,pathlib,re,subprocess,urllib.request
root=pathlib.Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015')
run=root/'runs/220562.pbs111'
r=subprocess.run(['qstat','-xf','220562.pbs111'],capture_output=True,text=True,timeout=10)
def field(name):
 m=re.search(r'^\s*'+re.escape(name)+r'\s*=\s*(.*)$',r.stdout,re.M)
 return m.group(1) if m else None
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def health(row):
 role,url,_=row.split()
 try:
  with opener.open(url+'/health',timeout=2) as h:return {'role':role,'http_status':h.status}
 except Exception as e:return {'role':role,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 endpoints=list(pool.map(health,(run/'endpoints.tsv').read_text().splitlines()))
print(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':'220562.pbs111','state':field('job_state'),'elapsed':field('resources_used.walltime'),'exit_status':field('Exit_status'),'health':endpoints,'exports':[str(p.relative_to(root)) for p in run.glob('*/n*/artifacts/profile_export_aiperf.json')],'output_smoke':(run/'output-smoke.json').exists(),'new_files':[str(p.relative_to(run)) for p in run.iterdir() if p.name not in ('submitted',)]},sort_keys=True))
'''
deadline=time.monotonic()+14*60
with (OUT/'live-observations.jsonl').open('a') as log:
 while time.monotonic()<deadline:
  try:
   result=subprocess.run(['bash',HELPER,'ssh-batch','bash -lc '+shlex.quote('python3 -c '+shlex.quote(REMOTE))],capture_output=True,text=True,timeout=25)
   if result.returncode:
    record={'checked_utc':datetime.now(timezone.utc).isoformat(),'remote_exit':result.returncode,'error':result.stderr[:1000]}
   else:record=json.loads(result.stdout)
  except Exception as e:record={'checked_utc':datetime.now(timezone.utc).isoformat(),'error':str(e)}
  line=json.dumps(record,sort_keys=True)
  log.write(line+'\n');log.flush();print(line,flush=True)
  if record.get('state') in ('F','E') or 'error' in record:break
  time.sleep(min(45,max(0,deadline-time.monotonic())))
