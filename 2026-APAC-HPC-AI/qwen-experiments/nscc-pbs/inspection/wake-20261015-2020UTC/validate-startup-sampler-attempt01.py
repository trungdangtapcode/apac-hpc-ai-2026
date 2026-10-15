from pathlib import Path
import importlib.util,json,os,subprocess,sys,time
root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('sampler',root/'startup-sampler.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
code='''import os,subprocess,sys,tempfile
with tempfile.TemporaryFile() as f:
 child=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"])
 try:
  print(child.pid,flush=True)
  sys.stdin.readline()
  f.write(b"x"*(4*1024*1024)); f.flush(); os.fsync(f.fileno())
  print("done",flush=True)
  sys.stdin.readline()
 finally:
  child.terminate();child.wait()
'''
p=subprocess.Popen([sys.executable,'-c',code],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
try:
 grandchild=int(p.stdout.readline())
 first=m.snapshot(p.pid,{})
 first_by={(r['pid'],r['start_ticks']):r for r in first['processes']}
 assert {p.pid,grandchild}=={r['pid'] for r in first['processes']}
 p.stdin.write('go\n');p.stdin.flush();assert p.stdout.readline().strip()=='done'
 second=m.snapshot(p.pid,first_by)
 writer=next(r for r in second['processes'] if r['pid']==p.pid)
 assert writer['delta']['write_bytes']>=4*1024*1024
 assert writer['delta']['wchar']>=4*1024*1024
 assert writer['delta']['minor_faults']>=0 and writer['threads']>=1
 assert writer['Cpus_allowed_list'] and writer['Mems_allowed_list']
 assert all(r['start_ticks']>0 and r['rss_bytes']>0 for r in second['processes'])
 assert os.getpid() not in {r['pid'] for r in m.snapshot(os.getpid(),{})['processes']}
 assert m.snapshot(2147483647,{})['processes']==[]
 env=os.environ.copy();env.pop('PBS_JOBID',None)
 refusal=subprocess.run([sys.executable,str(root/'startup-sampler.py'),'--root-pid',str(p.pid),'--out','/nonexistent/unused.jsonl'],env=env,capture_output=True,text=True)
 assert refusal.returncode==2 and 'existing PBS compute allocation' in refusal.stderr
 result=dict(passed=True,scope='Controlled CPU own-child/grandchild validation only',gpu_executed=False,remote_validated=False,descendants_verified=True,pid_identity_verified=True,write_bytes_delta=writer['delta']['write_bytes'],cli_outside_pbs_refused=True,raw_samples=[first,second])
 (Path(__file__).parent/'startup-sampler-validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='raw_samples'}))
finally:
 p.stdin.write('end\n');p.stdin.flush();p.wait(timeout=5)
