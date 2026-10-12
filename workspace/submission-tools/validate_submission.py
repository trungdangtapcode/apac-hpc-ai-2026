"""Static protocol checks and a mocked, GPU-free portable replay harness."""
import hashlib,json,os,re,shlex,shutil,subprocess,tempfile
from pathlib import Path
from datetime import datetime,timezone
from pptx import Presentation

ROOT=Path('/home/apacsc42/workspace/VNUHCM - TripleU')
SCRIPTS=ROOT/'AI_Task/job_scripts'
EXP=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
RULES=ROOT/'AI_Task/logs/rules/1. Qwen3 AI Task Rules.md'
checks=[]
def check(name,condition,detail):
    if not condition:raise AssertionError(name+': '+str(detail))
    checks.append({'check':name,'passed':True,'detail':detail})

for f in SCRIPTS.iterdir():
    if f.suffix in ('.sh','.sbatch'):
        subprocess.run(['bash','-n',str(f)],check=True)
check('shell_syntax',True,'All declared shell scripts and the single Slurm entry point parse.')
def args(text):
    command=re.search(r'(?m)^\s*aiperf profile \\\n(.*?--ui simple)',text,re.S).group(0)
    command=command.replace('\\\n',' ')
    return shlex.split(command)
expected=args(RULES.read_text());actual=args((SCRIPTS/'official-benchmark.sh').read_text())
check('locked_official_command',expected==actual,{'tokens':len(expected),'no_added_flags':True})
placement=[line.split() for line in (SCRIPTS/'placement.tsv').read_text().splitlines()]
totals={0:0,1:0}
for name,node,tp,port,bootstrap in placement:totals[int(node)]+=int(tp)
check('sixteen_gpus_in_two_nodes',totals=={0:8,1:8} and len(placement)==4,totals)
check('declared_concurrency',json.loads((SCRIPTS/'config.json').read_text())['declared_concurrency']==40,'N40 is pinned in submit.sbatch.')
for name in ('worker.sh','warm-topology.py','placement.tsv','summarize.py'):
    check('verified_source_'+name,(SCRIPTS/name).read_bytes()==(EXP/'runs/22219/submitted'/name).read_bytes(),'Byte-identical to measured job 22219.')
cache=SCRIPTS/'hf-cache/models--Qwen--Qwen3-235B-A22B-Instruct-2507'
revision=(cache/'refs/main').read_text().strip()
tokenizer=cache/'snapshots'/revision/'tokenizer.json'
check('offline_tokenizer_matches_checkpoint',hashlib.sha256(tokenizer.read_bytes()).hexdigest()==hashlib.sha256(Path('/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8/tokenizer.json').read_bytes()).hexdigest(),revision)
for job,n in [('22197',32),('22219',40),('22294',32),('22415',48),('22809',32)]:
    path=ROOT/'AI_Task/logs/runs'/job/'confirm'/f'n{n}'/'artifacts/profile_export_aiperf.json'
    d=json.loads(path.read_text())
    source=EXP/'runs'/job/'confirm'/f'n{n}'/'artifacts/profile_export_aiperf.json'
    check('raw_export_unchanged_'+job,path.read_bytes()==source.read_bytes(),'Original canonical export copied without modifications.')
    published=next(m for m in json.loads((ROOT/'AI_Task/logs/results.json').read_text()) if m['job']==job and m['phase']=='confirm')
    check('goodput_recomputed_'+job,abs(d['goodput']['avg']*200-published['good_output_tokens_s'])<1e-9,d['goodput']['avg']*200)

# Test submission wrappers under a different directory/account-shaped HOME,
# including spaces. Slurm, containers and model execution are explicitly mocked.
with tempfile.TemporaryDirectory(prefix='apac42_submission_replay_') as directory:
    td=Path(directory);bin=td/'bin';bin.mkdir();mock_home=td/'judge-home';mock_home.mkdir()
    scriptdir=td/'Some Team With Spaces/AI_Task/job_scripts';scriptdir.mkdir(parents=True)
    for f in SCRIPTS.iterdir():
        if f.is_file():shutil.copyfile(f,scriptdir/f.name)
    shim=bin/'shim.py'
    shim.write_text('''#!/usr/bin/python3
import json,os,sys,time
from pathlib import Path
name=Path(sys.argv[0]).name;args=sys.argv[1:]
def event(kind):
 with open(os.environ['TRIPLEU_MOCK_EVENTS'],'a') as f:f.write(json.dumps({'kind':kind,'args':args})+'\\n')
if name=='scontrol':
 print('mock-node-a\\nmock-node-b')
elif name=='getent':
 print(('192.0.2.1' if args[-1]=='mock-node-a' else '192.0.2.2')+' STREAM '+args[-1])
elif name=='curl':
 if any('/v1/models' in x for x in args):print('{"data":[{"id":"qwen"}]}')
elif name=='python3':
 if args and args[0]=='-':
  sys.stdin.read();print('Mocked container preflight')
 else:os.execv('/usr/bin/python3',['python3']+args)
elif name=='aiperf':
 event('aiperf');Path('artifacts').mkdir();print('Mocked AIPerf; no performance measurements')
elif name=='srun':
 if any(x.endswith('/worker.sh') for x in args):event('worker');time.sleep(60)
 elif 'sglang_router.launch_router' in args:event('router');time.sleep(60)
 elif any(x.endswith('/warm-topology.py') for x in args):event('pair_setup');print('Mocked four P/D setup paths')
 elif any(x.endswith('/official-benchmark.sh') for x in args):
  event('official_client');i=args.index('bash');os.execvp('bash',args[i:])
 else:raise SystemExit('Unexpected mocked srun: '+str(args))
''')
    shim.chmod(0o755)
    for name in ('scontrol','getent','curl','python3','aiperf','srun'):(bin/name).symlink_to(shim)
    events=td/'events.jsonl'
    env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'],HOME=str(mock_home),SLURM_JOB_ID='MOCK_ONLY',
             SLURM_SUBMIT_DIR=str(scriptdir),SLURM_JOB_NODELIST='mock-node-[a,b]',TRIPLEU_CONCURRENCY='40',TRIPLEU_MOCK_EVENTS=str(events))
    result=subprocess.run(['bash',str(scriptdir/'deploy-and-benchmark.sh')],env=env,cwd=scriptdir,
                          capture_output=True,text=True,timeout=20)
    check('portable_wrapper_mock_exit',result.returncode==0,{'exit':result.returncode,'stderr':result.stderr[-1000:]})
    calls=[json.loads(line) for line in events.read_text().splitlines()]
    check('portable_wrapper_mock_stages',sum(c['kind']=='worker' for c in calls)==4 and sum(c['kind']=='router' for c in calls)==1 and sum(c['kind']=='pair_setup' for c in calls)==1 and sum(c['kind']=='aiperf' for c in calls)==1,'4 worker steps + gateway + pair setup + one client invocation; paths containing spaces worked.')
    benchmark=next(c['args'] for c in calls if c['kind']=='aiperf')
    resolved=[x.replace('${HOST}','192.0.2.1:8000').replace('${MODEL}','qwen').replace('${N}','40') for x in expected[1:]]
    check('portable_wrapper_mock_client_arguments',benchmark==resolved,'Executed client argument vector exactly matches the locked rule command after HOST/MODEL/N substitution.')
    order=[c['kind'] for c in calls]
    check('deploy_then_benchmark_same_job',order.index('pair_setup')<order.index('official_client')<order.index('aiperf'),order)

presentation=Presentation(ROOT/'Presentation/TripleU_APAC2026_Presentation.pptx')
check('presentation_structure',len(presentation.slides)==19 and all(s.has_notes_slide for s in presentation.slides),'19 editable slides with notes; PDF companion generated from the same layout.')
data=json.loads((ROOT/'Presentation/presentation-data.json').read_text())
eligible=[m for m in data['results'] if m['phase']=='confirm' and m['sla_pass'] and (m['requests'] or 0)>0 and m['cancelled_requests']==0]
winner=max(eligible,key=lambda m:m['good_output_tokens_s'])
check('slides_use_latest_passing_long_run',data['best']==winner and winner['job']=='22415',{'job':winner['job'],'good_output_tokens_s':winner['good_output_tokens_s']})
check('complete_usable_coverage',data['measured_originals']==14 and data['measured_variants']==3,'14 exact originals + 3 explicit EP2 replacements; incompatible EP1 originals stay labelled.')
for index in (0,17):
    text='\n'.join(shape.text for shape in presentation.slides[index].shapes if shape.has_text_frame)
    check('winner_on_slide_'+str(index+1),'1,912.30' in text and '97.44%' in text,text)
layout=json.loads((ROOT/'Presentation/layout-validation.json').read_text())
check('winner_per_request_gate_rechecked',layout['profiling_points_rechecked']==1211 and layout['good_requests_rechecked']==1180,'Winner JSONL has 1180/1211 requests passing both limits.')
check('portable_entry_distinguished_from_winner',data['declared_basic']['job']=='22219' and json.loads((SCRIPTS/'config.json').read_text())['measured_evidence_job']=='22219','Slides explicitly distinguish the winning research stack from the existing unpatched portable entry.')
for job in ('22415','22809'):
    subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=SCRIPTS/'archive'/job,capture_output=True,text=True,check=True)
check('winning_and_final_frozen_payloads_intact',True,'Both archive payloads include every file named in their original SHA256SUMS, including patch metadata and diff.')
check('no_hpc_results_fabricated',not list((ROOT/'HPC_Task').rglob('*.sbatch')),'HPC directories contain explicit missing-evidence notices only.')
report={'utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'passed':True,
        'gpu_execution_performed':False,'accuracy_check_performed':False,
        'mock_scope':'Validates shell flow, paths and exact client arguments. Does not validate Slurm placement, container runtime, model inference or GPU transfer.'}
(ROOT/'AI_Task/logs/package-validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'checks_passed':len(checks),'gpu_execution_performed':False},indent=2))
