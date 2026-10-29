#!/usr/bin/env python3
"""Preserve the actual full-model compile incompatibility without assigning a score."""
from pathlib import Path
import collections,datetime,hashlib,json,re,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;job=27383;a=Q/f'runs/{job}'
account=subprocess.check_output(['sacct','-X','-j',str(job),'-P',
    '--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'],text=True)
rows=[line.split('|') for line in account.splitlines()]
states=[dict(zip(rows[0],r)) for r in rows[1:] if r[0]==str(job)]
assert len(states)==1 and states[0]['State']=='FAILED' and states[0]['ExitCode']=='1:0'
assert str(job) not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=a/'submitted-payload',stdout=subprocess.DEVNULL,check=True)
text=(a/'decode-0.log').read_text(errors='replace')
error='AssertionError: fused_set_kv_buffer_arg is not supported for native implementation'
assert error in text
assert 'torch_dynamo_resume_in_forward_prepare_native_at_591' in text
assert 'rotary_embedding/base.py", line 244, in forward_native' in text
assert not list(a.rglob('profile_export_aiperf.json'))
out=(Q/f'runs/{job}.out').read_text(errors='replace')
assert 'ALL_WORKERS_READY' not in out
receipts=[]
for p in sorted(a.rglob('rank-*-pid-*.json')):
    r=json.loads(p.read_text())
    assert str(r['job_id'])==str(job) and r['role']=='decode-0' and r['world_size']==8
    receipts.append({'path':str(p.relative_to(a)),'rank':r['rank'],'state':r['state'],
        'experiment_id':r['experiment_id'],'distributed_initialized_at_hook':r.get('distributed_initialized_at_hook'),
        'native_source_sha256':r.get('native_source_sha256'),'module_source_sha256':r.get('module_source_sha256'),
        'shapes':r.get('shapes',{})})
assert len(receipts)==8 and sorted(r['rank'] for r in receipts)==list(range(8))
cleanup={}
for role in ['prefill-0','prefill-1','decode-0']:
    t=(a/f'{role}.log').read_text(errors='replace')
    cleanup[role]={'native_remove_end':t.count('NATIVE_REMOVE_END'),
                   'traceback_markers':t.count('Traceback (most recent call last)'),
                   'native_ready_markers':t.count('The server is fired up and ready to roll!')}
(a/'scheduler-accounting.psv').write_text(account)
manifest=a/'artifact-manifest.json';assert not manifest.exists()
files=[]
for p in sorted(a.rglob('*'))+[Q/f'runs/{job}.out',Q/f'runs/{job}.err']:
    if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p==manifest:continue
    before=p.stat();digest=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat()
    assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':digest})
manifest.write_text(json.dumps({'job':job,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                               'terminal_accounting':account,'files':files},indent=2)+'\n')
result={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':job,
    'state':'FAILED_NATIVE_QWEN_COMPILE_ROPE_KV_INTERFACE_BEFORE_AIPERF','scheduler':states[0],
    'good_output_tokens_s':None,'benchmark_started':False,'official_accuracy':'UNKNOWN',
    'actual_error':error,'observed_trace_path':'First enabled compiled shape54: qwen3_moe.forward_prepare_native -> apply_qk_norm_rope -> rotary_embedding.forward_native asserts fused_set_kv_buffer_arg is None.',
    'source_causal_scope':'Native trace proves unsupported interface during actual Qwen compile; exact source-supported remedy requires separate review. It is not evidence of a compiler timeout or full-model numeric acceptance.',
    'current_rank_receipts':receipts,'role_cleanup':cleanup,
    'actual_allocation_GPU_hours':16*int(states[0]['ElapsedRaw'])/3600,
    'maximum_reservation_GPU_hours':16*17/60,'PBS_SU':0,
    'observability':'Inspected traceback, current rank/shape/compiler/capture receipts, startup/cleanup logs, absence of raw AIPerf exports and terminal accounting. Hardware collectors contain startup samples only and were not treated as ranked phase health/performance data. No request tail, error fraction or goodput exists.',
    'decision':'Close unchanged S105 and block unchanged sparse S108 compile. Fewer graph buckets do not fix this fused-KV/native interface assertion. Independent compile-off sparse control remains distinct and may proceed after review. Source-supported compile remedy and appropriate matched control require fresh qualification.'}
(D/'failure-review-27383.json').write_text(json.dumps(result,indent=2)+'\n')
(D/'FAILURE-27383.md').write_text(f"""# Actual Qwen compile failed before measurement

Reviewed 29 October 2026, Vietnam time (UTC+7). Actual job 27383 ended **FAILED 1:0 after 3:35** on g1/g4, 16 H200. **No AIPerf measurement or score exists.** Preserve the failure; do not count it as a completed performance trial.

The candidate enabled native decode torch.compile up to batch 54, retaining the original 1..64 graph list. The first compiled shape, 54, reached Qwen3 attention. The actual traceback enters qwen3_moe.forward_prepare_native, apply_qk_norm_rope and rotary_embedding/base.py forward_native, then raises:

    {error}

This is a native interface incompatibility, not an exhausted 600-second startup deadline. Eight current distributed decode receipts bind the actual job, experiment and native source. They retain successful ordinary capture evidence for larger noncompiled shapes and incomplete evidence at the first enabled compile shape; the full all-shape compile gate never passed. The independent one-GPU tiny fixture 27340 proved its own small-module interface only and did not establish Qwen compatibility. That prior limit is now concretely demonstrated.

The controller never reached ALL_WORKERS_READY, and no profile_export_aiperf.json exists. Local smoke/retrieval and official accuracy are unmeasured here. Startup hardware samples are retained but are not ranked-phase performance or hardware-health proof. Raw trace, every receipt, worker cleanup and terminal accounting are sealed in runs/27383/artifact-manifest.json. Observed occupancy is {result['actual_allocation_GPU_hours']:.6f} GPU-hours versus maximum 4.533334; zero PBS SU.

Decision: close unchanged S105 and block unchanged sparse-graph compile S108. Reducing graph bucket count cannot repair this interface assertion. Continue the independent compile-off sparse graph trial after its own source/fixture review; its startup and padding question remains valid. Investigate a source-supported fusion/compile compatibility setting before considering any new compiled Qwen trial, with a matching control if that setting changes serving behavior. No frozen submitted source was changed, no old queue position cancelled, and no submission or HPC payload was updated.
""")
print(json.dumps({'job':job,'state':result['state'],'GPU_hours':result['actual_allocation_GPU_hours']}))
