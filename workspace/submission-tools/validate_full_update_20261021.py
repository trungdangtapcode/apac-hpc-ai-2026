"""Validate the clean English-only winning submission and its portable job."""
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from pptx import Presentation

ROOT=Path('/home/apacsc42/workspace/submission-review/full-update-2026-10-21/VNUHCM - TripleU')
SCRIPTS=ROOT/'AI_Task/job_scripts'
EXP=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
checks=[]
def check(name,condition,detail):
    if not condition:raise AssertionError(name+': '+str(detail))
    checks.append({'check':name,'passed':True,'detail':detail})

check('requested_top_level_format',{p.name for p in ROOT.iterdir()}=={'Presentation','AI_Task','HPC_Task'},'Exactly the three requested directories.')
check('presentation_only_pptx',{p.name for p in (ROOT/'Presentation').iterdir()}=={'TripleU_APAC2026_Presentation.pptx'},'No guides, previews or data files in the presentation directory.')
check('one_slurm_entry',len(list(SCRIPTS.rglob('*.sbatch')))==1,'One primary submit.sbatch; frozen historical scripts are evidence only.')
for f in SCRIPTS.iterdir():
    if f.suffix in ('.sh','.sbatch'):subprocess.run(['bash','-n',str(f)],check=True)
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=SCRIPTS,check=True,capture_output=True,text=True)
config=json.loads((SCRIPTS/'config.json').read_text());meta=json.loads((SCRIPTS/'patch-metadata.json').read_text())
check('winning_primary_config',config['id']=='P8-TP4_D8-TP8-EP8' and config['declared_concurrency']==62 and config['transport_patch']=='hetero-tp-request-descriptors-v1',config['id'])
check('exact_measured_patch',hashlib.sha256((SCRIPTS/'nixl-conn.py').read_bytes()).hexdigest()==meta['patched_sha256']=='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f','Source is byte-identical to measured job 22415.')
for name in ('worker.sh','warm-topology.py','placement.tsv'):
    check('measured_component_'+name,(SCRIPTS/name).read_bytes()==(EXP/'runs/24915/submitted'/name).read_bytes(),'Exact winning-job component.')
placement=[line.split() for line in (SCRIPTS/'placement.tsv').read_text().splitlines()]
check('three_workers_sixteen_gpus',[(r[0],int(r[1]),int(r[2])) for r in placement]==[('prefill-0',0,4),('prefill-1',0,4),('decode-0',1,8)],'Two TP4 prefill workers plus one TP8/EP8 decode worker on two nodes.')
def args(text):
    command=re.search(r'(?m)^\s*aiperf profile \\\n(.*?--ui simple)',text,re.S).group(0)
    return shlex.split(command.replace('\\\n',' '))
expected=args((ROOT.parent/'qwen-rules.md').read_text())
check('exact_current_official_command',args((SCRIPTS/'official-benchmark.sh').read_text())==expected,'Verified against current official repository commit; no extra flags.')
for job,n in (('22197',32),('22219',40),('22415',48),('22809',32)):
    target=ROOT/'AI_Task/logs/measured'/job/'confirm'/f'n{n}'/'artifacts/profile_export_aiperf.json'
    source=EXP/'runs'/job/'confirm'/f'n{n}'/'artifacts/profile_export_aiperf.json'
    check('raw_export_'+job,target.read_bytes()==source.read_bytes(),'Raw canonical export unchanged.')

# Run the actual primary script from a path with spaces under a GPU-free mock.
with tempfile.TemporaryDirectory(prefix='tripleu_final_mock_') as directory:
    td=Path(directory);scriptdir=td/'Judge Team With Spaces/AI_Task/job_scripts'
    shutil.copytree(SCRIPTS,scriptdir)
    bin=td/'bin';bin.mkdir();events=td/'events.jsonl'
    shim=bin/'shim.py'
    shim.write_text('''#!/usr/bin/python3
import hashlib,json,os,sys,time,shutil
from pathlib import Path
name=Path(sys.argv[0]).name;args=sys.argv[1:]
def event(kind):
 with open(os.environ['TRIPLEU_MOCK_EVENTS'],'a') as f:
  f.write(json.dumps({'kind':kind,'args':args,'patch_sha':os.environ.get('QWEN_NIXL_PATCH_SHA256')})+'\\n')
if name=='scontrol':print('mock-node-a\\nmock-node-b')
elif name=='getent':print(('192.0.2.1' if args[-1]=='mock-node-a' else '192.0.2.2')+' STREAM '+args[-1])
elif name=='curl':
 if any('/v1/models' in x for x in args):print('{"data":[{"id":"qwen"}]}')
elif name=='python3':
 if args and args[0]=='-':sys.stdin.read();print('Mocked container preflight')
 else:os.execv('/usr/bin/python3',['python3']+args)
elif name=='aiperf':
 event('aiperf');Path('artifacts/logs').mkdir(parents=True)
 source=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24915/confirm/n62')
 for filename in ['profile_export_aiperf.json','profile_export.jsonl']:
  shutil.copyfile(source/'artifacts'/filename,Path('artifacts')/filename)
 shutil.copyfile(source/'artifacts/logs/aiperf.log',Path('artifacts/logs/aiperf.log'))
 print('Mock orchestration only; replayed retained artifacts, not a new measurement')
elif name=='srun':
 if any(x.endswith('/worker.sh') for x in args):
  mounts=next(x.split('=',1)[1] for x in args if x.startswith('--container-mounts='))
  patch=next(x for x in mounts.split(',') if ':/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro' in x)
  assert hashlib.sha256(Path(patch.split(':',1)[0]).read_bytes()).hexdigest()==os.environ['QWEN_NIXL_PATCH_SHA256']
  event('worker');time.sleep(60)
 elif 'sglang_router.launch_router' in args:event('router');time.sleep(60)
 elif any(x.endswith('/warm-topology.py') for x in args):event('pair_setup');print('Mocked two P/D setup paths')
 elif any(x.endswith('/official-benchmark.sh') for x in args):
  event('official_client');i=args.index('bash');os.execvp('bash',args[i:])
 else:raise SystemExit('Unexpected srun: '+str(args))
''')
    shim.chmod(0o755)
    for name in ('scontrol','getent','curl','python3','aiperf','srun'):(bin/name).symlink_to(shim)
    env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'],SLURM_JOB_ID='MOCK_ONLY',
             SLURM_SUBMIT_DIR=str(scriptdir),SLURM_JOB_NODELIST='mock-node-[a,b]',TRIPLEU_MOCK_EVENTS=str(events))
    result=subprocess.run(['bash',str(scriptdir/'submit.sbatch')],cwd=scriptdir,env=env,capture_output=True,text=True,timeout=20)
    check('portable_primary_script_mock',result.returncode==0,{'exit':result.returncode,'stderr':result.stderr[-1000:]})
    calls=[json.loads(line) for line in events.read_text().splitlines()]
    workers=[c for c in calls if c['kind']=='worker']
    check('three_mock_workers_patch_mounted',len(workers)==3 and all(c['patch_sha']==meta['patched_sha256'] for c in workers),'All three worker steps receive and verify the mounted winning patch.')
    observed=[]
    for call in workers:
        a=call['args'];i=next(i for i,x in enumerate(a) if x.endswith('/worker.sh'))
        name,port,model,tp=a[i+1:i+5];flags=a[i+5:]
        assert flags[flags.index('--nccl-port')+1]==str(20000+int(port)-30100)
        if name.startswith('decode-'):assert flags[flags.index('--ep-size')+1]=='8'
        observed.append((name,int(tp)))
    check('actual_worker_arguments',sorted(observed)==[('decode-0',8),('prefill-0',4),('prefill-1',4)],observed)
    check('one_router_setup_client',sum(c['kind']=='router' for c in calls)==1 and sum(c['kind']=='pair_setup' for c in calls)==1 and sum(c['kind']=='aiperf' for c in calls)==1,'No sweep; one official AIPerf invocation.')
    actual=next(c['args'] for c in calls if c['kind']=='aiperf')
    resolved=[x.replace('${HOST}','192.0.2.1:8000').replace('${MODEL}','qwen').replace('${N}','62') for x in expected[1:]]
    check('executed_official_n62_arguments',actual==resolved,'Actual primary script executes the complete locked command at N62.')
    order=[c['kind'] for c in calls]
    check('deploy_then_benchmark_same_job',order.index('pair_setup')<order.index('official_client')<order.index('aiperf'),order)


# The real post-client gate must be reached by the primary job.
    gate=json.loads((scriptdir.parent/'logs/reruns/MOCK_ONLY/performance-gate.json').read_text())
    check('executed_semantic_gate',gate['passed'] and gate['requests']==1884 and gate['good_requests']==1860,'Replayed measured artifacts, not a new GPU result.')
    # Fail closed on missing artifacts and a corrupted raw request.
    missing=subprocess.run(['/usr/bin/python3',str(scriptdir/'score-gate.py'),str(td/'missing'),'62'],capture_output=True,text=True)
    check('reject_missing_artifacts',missing.returncode!=0,'Scheduler/client exit alone cannot pass.')
    raw=scriptdir.parent/'logs/reruns/MOCK_ONLY/official/n62/artifacts/profile_export.jsonl'
    lines=raw.read_text().splitlines()
    for i,line in enumerate(lines):
        row=json.loads(line)
        if row['metadata'].get('phase_kind')=='profiling':
            row['error']={'message':'validation-only injected request failure'};lines[i]=json.dumps(row);break
    raw.write_text('\n'.join(lines)+'\n')
    failed=subprocess.run(['/usr/bin/python3',str(scriptdir/'score-gate.py'),str(scriptdir.parent/'logs/reruns/MOCK_ONLY'),'62'],capture_output=True,text=True)
    check('reject_injected_request_failure',failed.returncode!=0,'Failure injection only in temporary mock copy.')

check('no_team_paths_in_primary_scripts',all('/home/apacsc42' not in (SCRIPTS/name).read_text() for name in ('submit.sbatch','deploy-and-benchmark.sh','official-benchmark.sh','worker.sh')),'Portable across accounts.')
check('hpc_empty',not any(p.is_file() for p in (ROOT/'HPC_Task').rglob('*')),'Empty by owner scope.')
check('n62_no_speculation',not config['speculative_decoding'] and config['concurrency']==[62],'Declared N62 Basic deployment.')
check('round_robin',(SCRIPTS/'deploy-and-benchmark.sh').read_text().count('--prefill-policy round_robin')==1,'Matches source job.')
provenance=json.loads((ROOT/'AI_Task/logs/source-provenance.json').read_text())
for relative,entry in provenance['files'].items():
    check('raw_hash_'+relative,hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==entry['sha256'],'Unchanged source bytes.')
report={'passed':True,'checks':checks,'gpu_execution_performed':False,
        'mock_scope':'Actual shell orchestration and post-client gate with measured artifacts replayed in a temporary mock; no new GPU inference, accuracy or performance measurement.'}
(ROOT/'AI_Task/logs/package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'checks_passed':len(checks),'declared':'P8-TP4_D8-TP8-EP8','N':62},indent=2))
