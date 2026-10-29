#!/usr/bin/env python3
"""Wire source-pinned startup proof before a conditional production benchmark."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent;Q=D.parent
P=Q/'runs/27270/submitted-payload'
H=Q/'h200-decode-compile-startup-20261029'
B=Q/'serving-tuning-11/s105-h200-decode-compile54'
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=P,check=True,stdout=subprocess.DEVNULL)
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=H,check=True,stdout=subprocess.DEVNULL)
shutil.copytree(P,B)
(B/'compile-hooks').mkdir()
for name in ('sitecustomize.py','observer_module.py'):shutil.copy2(H/name,B/'compile-hooks'/name)
shutil.copy2(H/'check_compile_receipts.py',B/'check_compile_receipts.py')
cfg=json.loads((P/'config.json').read_text())
cfg.update(experiment=B.name,label='Decode full CUDA graphs with compile cap54; fail-closed production startup qualification',source_parent_job=27270,source_parent='s101-h200-transfer-poll1',study_arm='decode_compile54_startup_then_conditional_full',decode_enable_torch_compile=True,decode_torch_compile_max_bs=54,prefill_enable_torch_compile=False,matched_control_job=27376,known_reference_job=27270,performance_or_GPU_acceptance='UNKNOWN',matched_pair='Same target-only runtime/workload; enable only decode torch.compile54 plus startup-only observer. Fresh control27376 remains separate.')
(B/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
s=(P/'worker.sh').read_text()
needle='telemetry_flags=()\n';assert s.count(needle)==1
hook='''if [[ $role == decode ]]; then
  extra+=(--enable-torch-compile --torch-compile-max-bs 54)
  export QWEN_TORCH_COMPILE_OBSERVER=1
  export QWEN_TORCH_COMPILE_RECEIPT_DIR="$QWEN_ARTDIR/compile-receipts"
  export PYTHONPATH="$QWEN_BUNDLE/compile-hooks:PYTHONPATH_TAIL"
fi
'''
hook=hook.replace('PYTHONPATH_TAIL','$'+'{PYTHONPATH-}')
s=s.replace(needle,hook+needle)
(B/'worker.sh').write_text(s)
s=(P/'check-fast-runtime.py').read_text()
needle='    for key,wanted in common.items():';assert s.count(needle)==1
s=s.replace(needle,"""    common.update(enable_torch_compile=(role=='decode-0'),
        torch_compile_max_bs=54 if role=='decode-0' else 32,enable_memory_saver=False)
"""+needle)
(B/'check-fast-runtime.py').write_text(s)
s=(P/'topology-job.sh').read_text()
needle='echo "ALL_WORKERS_READY at=$(date +%s)"';assert s.count(needle)==1
gate='''python3 -B "$BUNDLE/check_compile_receipts.py" "$ART/compile-receipts" --world-size 8 --job-id "$SLURM_JOB_ID" --experiment-id "$QWEN_EXPERIMENT_ID" --role decode-0 --json-out "$ART/compile-startup-gate.json"
'''
s=s.replace(needle,gate+needle)
(B/'topology-job.sh').write_text(s)
s=(P/'check-performance.py').read_text()
needle="    token=hashlib.sha256(warm['experiment_id'].encode()).hexdigest()[:32]";assert s.count(needle)==1
added="""    compile_spec=importlib.util.spec_from_file_location('compile_receipts',HERE/'check_compile_receipts.py')
    compile_module=importlib.util.module_from_spec(compile_spec);compile_spec.loader.exec_module(compile_module)
    actual_compile=compile_module.check(art/'compile-receipts',8,str(art.name),warm['experiment_id'],'decode-0')
    assert actual_compile.get('ready_for_aiperf') is True, actual_compile
    assert json.loads((art/'compile-startup-gate.json').read_text())==actual_compile, 'compile startup receipt differs from raw independent replay'
"""
s=s.replace(needle,added+needle)
(B/'check-performance.py').write_text(s)
s=(P/'job.sbatch').read_text().replace('s101-h200-transfer-poll1',B.name).replace('#SBATCH -J ap42-s101-poll1','#SBATCH -J ap42-s105-tc54')
(B/'job.sbatch').write_text(s)
(B/'README.md').write_bytes((D/'PLAN.md').read_bytes())
unchanged=['benchmark.sh','performance_gates.py','native-container.sh','nixl-conn.py','kv_geometry.py','validate_kv_geometry.py','warm-topology.py','warmup_semantic.py','resource-sampler.py','expected-input-config.json','reference-output-smoke.json']
for n in unchanged:assert (B/n).read_bytes()==(P/n).read_bytes(),n
for p in B.rglob('*'):
    if p.suffix=='.py':ast.parse(p.read_text())
    if p.suffix in ('.sh','.sbatch'):subprocess.run(['bash','-n',str(p)],check=True)
files=sorted(p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS')
(B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(B))+'\n' for p in files))
(D/'preparation.json').write_text(json.dumps({'state':'PREPARED_NOT_SUBMITTED','bundle':str(B.relative_to(Q)),'manifest_sha256':hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest(),'source_parent_job':27270,'fresh_control_job':27376,'observer_native_provenance':json.loads((H/'provenance.json').read_text()),'observer_manifest_sha256':hashlib.sha256((H/'SHA256SUMS').read_bytes()).hexdigest(),'unchanged_files':unchanged,'gate_order':'Actual model startup/native ready/compile receipts and existing runtime/KV before semantic warmup and any official AIPerf; same independent replay at review.'},indent=2)+'\n')
print(B)
