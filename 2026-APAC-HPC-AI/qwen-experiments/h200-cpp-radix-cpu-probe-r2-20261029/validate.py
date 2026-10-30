#!/usr/bin/env python3
"""CPU stdlib fixtures for the prepared launcher, not C++ runtime acceptance."""
from pathlib import Path
import ast,datetime,hashlib,json,os,subprocess,sys,tempfile,time
D=Path(__file__).resolve().parent;old=D.parent/'h200-cpp-radix-cpu-probe-20261029'
assert not (D/'submission-receipt.json').exists(),'Do not regenerate validation after admission'
assert (D/'probe.py').read_bytes()==(old/'probe.py').read_bytes()
m=json.loads((D/'SOURCE_MANIFEST.json').read_text())
for item in m['files']:
 p=D/item['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
for p in D.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for name in ('job.sbatch','native-container.sh'):
 subprocess.run(['bash','-n',str(D/name)],check=True)
job=(D/'job.sbatch').read_text()
for flag in ('--cpus-per-task=4','--mem=16G','--gres=gpu:0','--time=00:06:00'):
 assert flag in job
assert 'timeout --signal' not in job and 'deadline=$((job_start + 300))' in job
rows=[]
with tempfile.TemporaryDirectory(prefix='ap42-cpp-r2-test-') as tmp:
 t=Path(tmp);fake=t/'fake.sqsh';fake.write_text('not an image; dry-run only')
 env={**os.environ,'SLURM_JOB_ID':'fixture','SLURM_STEP_ID':'0','SLURM_CPUS_PER_TASK':'4',
      'APAC_NATIVE_DRY_RUN':'1','CUDA_VISIBLE_DEVICES':'0,1','SLURM_STEP_GPUS':''}
 cp=subprocess.run(['bash',str(D/'native-container.sh'),str(fake),f'{D}:/work:ro','true'],env=env,capture_output=True,text=True)
 assert cp.returncode==0,cp.stderr
 r=json.loads(cp.stdout);assert r['runtime_visible_gpu_ids']=='void' and r['cuda_mask']==''
 rows.append('zero_gpu_dry_run_masks_inherited_cuda')
 for name,changes,mount in [('reject_wrong_cpu_allocation',{'SLURM_CPUS_PER_TASK':'2'},f'{D}:/work:ro'),
                             ('reject_invalid_mount_mode',{},f'{D}:/work:bad')]:
  cp=subprocess.run(['bash',str(D/'native-container.sh'),str(fake),mount,'true'],env={**env,**changes},capture_output=True,text=True)
  assert cp.returncode!=0,name
  rows.append(name)
 def run_fixture(name,body,seconds,expected):
  p=t/f'{name}.py';p.write_text(body);result=t/f'{name}.json'
  e={**os.environ,'APAC_CPP_RADIX_RESULT':str(result),'APAC_CPP_RADIX_PROCESS_DEADLINE_EPOCH':str(int(time.time())+seconds)}
  cp=subprocess.run([sys.executable,'-B',str(D/'deadline_runner.py'),str(p)],env=e,capture_output=True,text=True,timeout=8)
  assert cp.returncode==expected,(name,cp.stdout,cp.stderr)
  receipt=json.loads((t/'deadline-supervisor.json').read_text())
  return receipt,result
 r,_=run_fixture('normal_exit','raise SystemExit(0)\n',5,0);assert r['state']=='CHILD_EXITED' and r['child_exit_code']==0
 rows.append('inner_supervisor_normal_exit')
 r,_=run_fixture('nonzero_exit','raise SystemExit(7)\n',5,7);assert r['child_exit_code']==7
 rows.append('inner_supervisor_preserves_failure')
 r,p=run_fixture('expired_before_launch','raise RuntimeError("must not run")\n',-1,124)
 assert r['state']=='FAIL_NO_TIME_REMAINING' and json.loads(p.read_text())['state']=='FAIL_PROCESS_DEADLINE'
 rows.append('inner_supervisor_expired_before_launch')
 r,p=run_fixture('deadline_kills_child','import time\ntime.sleep(30)\n',1,124)
 assert r['state']=='CHILD_REAPED_AFTER_TERM' and json.loads(p.read_text())['state']=='FAIL_PROCESS_DEADLINE'
 rows.append('inner_supervisor_deadline_reaps_child')
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'PASS_OFFLINE_LAUNCHER_FIXTURES_ONLY',
     'fixtures':rows,'source_files_verified':len(m['files']),'probe_identical_to_27387':True,
     'no_Torch_or_model_import':True,'no_scheduler_or_GPU_runtime':True,
     'limits':'Synthetic stdlib launcher tests only; not actual C++ build, cleanup of a real container or full-model correctness.'}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
