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

ROOT=Path('/home/apacsc42/workspace/submission-staging/VNUHCM - TripleU')
SCRIPTS=ROOT/'AI_Task/job_scripts'
EXP=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
checks=[]
def check(name,condition,detail):
    if not condition:raise AssertionError(name+': '+str(detail))
    checks.append({'check':name,'passed':True,'detail':detail})

check('requested_top_level_format',{p.name for p in ROOT.iterdir()}=={'Presentation','AI_Task','HPC_Task'},'Exactly the three requested directories.')
check('presentation_only_pptx',{p.name for p in (ROOT/'Presentation').iterdir()}=={'TripleU_APAC2026_Presentation.pptx'},'No guides, previews or data files in the presentation directory.')
check('one_slurm_entry',len(list(ROOT.rglob('*.sbatch')))==1,'One primary submit.sbatch; no old topology submission scripts.')
for f in SCRIPTS.iterdir():
    if f.suffix in ('.sh','.sbatch'):subprocess.run(['bash','-n',str(f)],check=True)
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=SCRIPTS,check=True,capture_output=True,text=True)
config=json.loads((SCRIPTS/'config.json').read_text());meta=json.loads((SCRIPTS/'patch-metadata.json').read_text())
check('winning_primary_config',config['id']=='P8-TP4_D8-TP8-EP8' and config['declared_concurrency']==48 and config['transport_patch']=='hetero-tp-request-descriptors-v1',config['id'])
check('exact_measured_patch',hashlib.sha256((SCRIPTS/'nixl-conn.py').read_bytes()).hexdigest()==meta['patched_sha256']=='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f','Source is byte-identical to measured job 22415.')
for name in ('worker.sh','warm-topology.py','placement.tsv','summarize.py'):
    check('measured_component_'+name,(SCRIPTS/name).read_bytes()==(EXP/'runs/22415/submitted'/name).read_bytes(),'Exact winning-job component.')
placement=[line.split() for line in (SCRIPTS/'placement.tsv').read_text().splitlines()]
check('three_workers_sixteen_gpus',[(r[0],int(r[1]),int(r[2])) for r in placement]==[('prefill-0',0,4),('prefill-1',0,4),('decode-0',1,8)],'Two TP4 prefill workers plus one TP8/EP8 decode worker on two nodes.')
def args(text):
    command=re.search(r'(?m)^\s*aiperf profile \\\n(.*?--ui simple)',text,re.S).group(0)
    return shlex.split(command.replace('\\\n',' '))
expected=args(Path('/tmp/apac42-current-qwen-rules.md').read_text())
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
import hashlib,json,os,sys,time
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
elif name=='aiperf':event('aiperf');Path('artifacts').mkdir();print('Mock only; no performance result')
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
    resolved=[x.replace('${HOST}','192.0.2.1:8000').replace('${MODEL}','qwen').replace('${N}','48') for x in expected[1:]]
    check('executed_official_n48_arguments',actual==resolved,'Actual primary script executes the complete locked command at N48.')
    order=[c['kind'] for c in calls]
    check('deploy_then_benchmark_same_job',order.index('pair_setup')<order.index('official_client')<order.index('aiperf'),order)

deck=Presentation(ROOT/'Presentation/TripleU_APAC2026_Presentation.pptx')
check('nineteen_slides',len(deck.slides)==19,'Editable presentation.')
vietnamese=re.compile('[đĐăĂưƯơƠấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựỵỷỹ]')
texts=[]
for slide in deck.slides:
    texts.extend(s.text for s in slide.shapes if s.has_text_frame)
    texts.append(slide.notes_slide.notes_text_frame.text)
check('english_slides_and_notes',not any(vietnamese.search(t) for t in texts),'All 19 notes and slide text are English.')
for p in ROOT.rglob('*'):
    if not p.is_file() or 'hf-cache' in p.parts or 'measured' in p.parts:continue
    if p.suffix in ('.md','.txt','.sh','.sbatch','.py'):
        check('english_file_'+str(p.relative_to(ROOT)),not vietnamese.search(p.read_text()),'No Vietnamese prose.')
check('declared_winner_slide',any('The primary job deploys the winning stack' in t for t in texts) and not any('still replays unpatched' in t for t in texts),'Slides agree with the updated N48 entry.')
check('no_team_paths_in_primary_scripts',all('/home/apacsc42' not in (SCRIPTS/name).read_text() for name in ('submit.sbatch','deploy-and-benchmark.sh','official-benchmark.sh','worker.sh')),'Portable across accounts.')
check('no_fabricated_hpc',not list((ROOT/'HPC_Task').rglob('*.sbatch')),'HPC directories only state missing evidence.')
report={'passed':True,'checks':checks,'gpu_execution_performed':False,
        'mock_scope':'Verifies shell flow, portable paths, patch mount/hash, layout flags and exact client arguments; not GPU inference or accuracy.'}
(ROOT/'AI_Task/logs/package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'checks_passed':len(checks),'declared':'P8-TP4_D8-TP8-EP8','N':48,'english_only':True},indent=2))
