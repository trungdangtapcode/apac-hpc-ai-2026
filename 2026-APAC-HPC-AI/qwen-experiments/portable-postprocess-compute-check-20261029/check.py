#!/usr/bin/env python3
"""Reproduce/fix reader behavior on compute-host mount aliases; zero model work."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');D=Path(__file__).resolve().parent;A=Q/'runs'/os.environ['SLURM_JOB_ID'];A.mkdir(parents=True,exist_ok=True)
roots={27136:Q/'submission-replay-20261028/VNUHCM - TripleU/AI_Task/logs/reruns/27136',27145:Q/'portable-replay-r2-20261029/VNUHCM - TripleU/AI_Task/logs/reruns/27145'}
old=Q/'portable-replay-r2-20261029/VNUHCM - TripleU/AI_Task/job_scripts/summarize.py'
repro=subprocess.run([sys.executable,'-B',str(old),str(roots[27145])],capture_output=True,text=True)
result={'vietnam':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),'host':os.uname().nodename,'job':os.environ['SLURM_JOB_ID'],'GPU_requested':0,'model_launched':False,'original_failed_job':27145,'original_summary_returncode':repro.returncode,'original_alias_failure_reproduced':repro.returncode!=0 and 'is not in the subpath' in repro.stderr,'raw':{},'scope':'Postprocessing on real compute-host namespace; no new inference/accuracy/single-allocation end-to-end pass.'}
assert result['original_alias_failure_reproduced'],repro.stderr
for job,root in roots.items():
 gate=subprocess.run([sys.executable,'-B',str(D/'readers/score-gate.py'),str(root),'64'],capture_output=True,text=True);assert gate.returncode==0,gate.stdout+gate.stderr
 summary=subprocess.run([sys.executable,'-B',str(D/'readers/summarize.py'),str(root)],capture_output=True,text=True);assert summary.returncode==0,summary.stderr
 rows=json.loads(summary.stdout);g=json.loads(gate.stdout);assert len(rows)==1 and rows[0]['phase']=='official' and rows[0]['concurrency']==64 and rows[0]['cancelled_requests']==0
 assert rows[0]['good_output_tokens_s']==g['good_output_tokens_s']
 result['raw'][str(job)]={'logical_input_root':str(root),'canonical_input_root':str(root.resolve()),'gate':g,'summary':rows}
(A/'validation.json').write_text(json.dumps(dict(result,state='PASS_COMPUTE_POSTPROCESS_ONLY'),indent=2)+'\n');print('PASS_COMPUTE_POSTPROCESS_ONLY')
