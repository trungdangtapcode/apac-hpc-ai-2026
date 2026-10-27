#!/usr/bin/env python3
"""Freeze an entrypoint repair and bounded cleanup in three full chunk arms."""
import ast,hashlib,json,shutil,subprocess
from pathlib import Path
Q=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent
arms=[('s84-h200-native-r2-chunk8192','s87-h200-native-r3-chunk8192',8192),('s85-h200-native-r2-chunk10240','s88-h200-native-r3-chunk10240',10240),('s86-h200-native-r2-chunk12288','s89-h200-native-r3-chunk12288',12288)]
checks=[]
for old,new,chunk in arms:
 src=Q/'serving-tuning-11'/old;dst=Q/'serving-tuning-11'/new
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=src,check=True,stdout=subprocess.DEVNULL)
 shutil.copytree(src,dst)
 for name in ['native-container.sh','exec.rc','cleanup-node.py']:shutil.copy2(D/name,dst/name)
 cfg=json.loads((dst/'config.json').read_text());cfg.update(experiment=new,label=new,prerequisite_job=26764,source_parent=old,source_failed_jobs=[26579,26581,26583],runtime_repair='Explicit Enroot exec rc; remove only owned terminal native roots before startup and current disposable roots after step termination.',matched_pair='Three same-runtime full N64 chunks 8192/10240/12288; no useful new performance observation yet.',study_arm='prefill_chunk_interaction')
 (dst/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 s=(dst/'job.sbatch').read_text().replace(old,new).replace('#SBATCH -J ap42-s'+old[1:3]+'-r2','#SBATCH -J ap42-s'+new[1:3]+'-r3')
 s=s.replace("runs/26574/split-proof.json","runs/26764/runtime-proof.json").replace("r.get('state')=='NATIVE_SPLIT_EIGHT_GPU_PASS' and r.get('unique_gpu_count')==8","r.get('state')=='AIPERF_ENTRYPOINT_AND_TERMINAL_ROOT_CLEANUP_PASS'")
 s=s.replace('Actual split8 CUDA prerequisite missing; no model may start','Actual R3 entrypoint/cleanup prerequisite missing; no model may start')
 # Preserve the independently proven split GPU prerequisite, in addition to the new probe.
 s=s.replace("r=json.loads(p.read_text())", "g=json.loads(Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/26574/split-proof.json').read_text())\nassert g['state']=='NATIVE_SPLIT_EIGHT_GPU_PASS' and len(set(g['role0_uuids'])|set(g['role1_uuids']))==8\nr=json.loads(p.read_text())")
 (dst/'job.sbatch').write_text(s)
 s=(dst/'topology-job.sh').read_text()
 start='''# Reclaim only this user's disposable native roots with verified terminal job state.
srun --exact -N2 -n2 --ntasks-per-node=1 --gres=gpu:0 --cpus-per-task=1 \\
  python3 "$BUNDLE/cleanup-node.py" >"$ART/native-cleanup-before.jsonl" 2>&1
'''
 s=s.replace('trap cleanup EXIT\n','trap cleanup EXIT\n'+start)
 oldline='  wait || :\n'
 newlines='''  wait || :
  # A killed Slurm step cannot finish an in-step EXIT trap. Clean from a new step
  # only after all launched step clients have terminated, within the same walltime.
  local reclaim_remaining=$((HARD_STOP-$(date +%s)-5))
  if (( reclaim_remaining > 0 )); then
    (( reclaim_remaining > 30 )) && reclaim_remaining=30
    timeout --signal=TERM --kill-after=2s "$reclaim_remaining" \\
      srun --overlap -N2 -n2 --ntasks-per-node=1 --gres=gpu:0 --cpus-per-task=1 \\
      python3 "$BUNDLE/cleanup-node.py" --include-current >"$ART/native-cleanup-after.jsonl" 2>&1 || result=1
  else
    echo 'FATAL: no bounded native cleanup budget remains' >&2; result=1
  fi
'''
 assert s.count(oldline)==1;s=s.replace(oldline,newlines)
 # Cleanup time has its own hard bound, so don't apply the preceding worker-stop deadline to it.
 s=s.replace('  if (( $(date +%s) > cleanup_deadline )); then echo \'FATAL: bounded teardown deadline exceeded\' >&2; result=1; fi\n','')
 (dst/'topology-job.sh').write_text(s)
 (dst/'R3_PARENT.json').write_text(json.dumps({'parent':str(src.relative_to(Q)),'parent_manifest_sha256':hashlib.sha256((src/'SHA256SUMS').read_bytes()).hexdigest(),'deriver':str(Path(__file__).relative_to(Q)),'probe':26764,'chunk':chunk},indent=2)+'\n')
 (dst/'README.md').write_text(f'''# Full N64 chunk {chunk}, native runtime R3

This derives {old}. Previous job 26579 reached workers and semantic routes but the AIPerf image entrypoint interpreted the intended env command as an AIPerf subcommand. Jobs 26581/26583 hit the local rootfs capacity guard. R3 explicitly executes the intended argv with Enroot --rc and reclaims only this user's disposable native roots from terminal jobs. A new batch-level cleanup covers steps killed before their EXIT trap completes. All cleanup remains inside the existing 17-minute allocation. Raw failed evidence is retained.

Both actual split-eight CUDA proof 26574 and actual entrypoint/cleanup proof 26764 are mandatory. The model, source pins, read-only patched mounts, precision, GPU layout, full 60/120/30-second N64 workload and strict raw SLA/output gates remain. Across these three arms only prefill chunk differs. Official quality remains UNKNOWN. No gain is claimed before a qualified same-runtime comparison, then independent confirmation for a useful gain above 1%.
''')
 for name in ['worker.sh','benchmark.sh','expected-input-config.json','check-performance.py','performance_gates.py','check-fast-runtime.py','nixl-conn.py','kv_geometry.py']:
  assert (dst/name).read_bytes()==(src/name).read_bytes(),name
 assert cfg['prefill_chunked_prefill_size']==chunk
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in {'.sh','.sbatch'}:subprocess.run(['bash','-n',str(f)],check=True)
 files=sorted(p for p in dst.iterdir() if p.is_file() and p.name!='SHA256SUMS')
 (dst/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=dst,check=True,stdout=subprocess.DEVNULL)
 checks.append({'bundle':str(dst.relative_to(Q)),'chunk':chunk,'syntax':'PASS','retained_model_client_gate_identity':'PASS','manifest':'PASS'})
(D/'preparation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
