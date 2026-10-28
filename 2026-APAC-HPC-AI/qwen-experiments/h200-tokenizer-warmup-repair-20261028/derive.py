#!/usr/bin/env python3
"""Separate a fixed semantic deadline from native rootfs extraction/removal."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;checks=[]
for old,new in [('s90-h200-tokenizer-off','s93-h200-tokenizer-off-warmfix'),('s91-h200-tokenizer-200us','s94-h200-tokenizer-200us-warmfix'),('s92-h200-tokenizer-2ms','s95-h200-tokenizer-2ms-warmfix')]:
 src=Q/'serving-tuning-11'/old;dst=Q/'serving-tuning-11'/new
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=src,check=True,stdout=subprocess.DEVNULL);shutil.copytree(src,dst)
 cfg=json.loads((src/'config.json').read_text());cfg.update(experiment=new,label=new,source_parent=old,runtime_repair='Preserve semantic Python deadline120s and global warmup deadlineT0+720; bound native setup/cleanup by remaining global warmup envelope, with lifecycle timestamps.',source_failed_jobs=[26849,26851,26853]);(dst/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 s=(src/'native-container.sh').read_text()
 s=s.replace('  enroot remove --force rootfs >/dev/null 2>&1 || :','''  printf 'NATIVE_REMOVE_BEGIN epoch=%s result=%s data=%s\\n' "$(date +%s)" "$result" "$ENROOT_DATA_PATH"
  enroot remove --force rootfs >/dev/null 2>&1 || :
  printf 'NATIVE_REMOVE_END epoch=%s data=%s\\n' "$(date +%s)" "$ENROOT_DATA_PATH"''')
 s=s.replace('enroot create --name rootfs "$image"','''printf 'NATIVE_CREATE_BEGIN epoch=%s\\n' "$(date +%s)"
enroot create --name rootfs "$image"
printf 'NATIVE_CREATE_END epoch=%s\\n' "$(date +%s)"''')
 s=s.replace('wait "$child"','''set +e
wait "$child"
command_status=$?
set -e
printf 'NATIVE_COMMAND_EXIT epoch=%s status=%s data=%s\\n' "$(date +%s)" "$command_status" "$ENROOT_DATA_PATH"
exit "$command_status"''')
 (dst/'native-container.sh').write_text(s)
 s=(src/'topology-job.sh').read_text();oldtime='timeout --signal=TERM --kill-after=5s 120 srun --overlap';assert s.count(oldtime)==1
 s=s.replace(oldtime,'''warm_step_remaining=$((WARMUP_DEADLINE-$(date +%s)))
(( warm_step_remaining > 0 )) || { echo 'FATAL: no global warmup budget remains' >&2; exit 1; }
timeout --signal=TERM --kill-after=5s "$warm_step_remaining" srun --overlap''')
 oldcommand='    python3 -B "$BUNDLE/warm-topology.py"';assert s.count(oldcommand)==1
 s=s.replace(oldcommand,'    timeout --signal=TERM --kill-after=5s 120 python3 -B "$BUNDLE/warm-topology.py"')
 (dst/'topology-job.sh').write_text(s)
 (dst/'job.sbatch').write_text((src/'job.sbatch').read_text().replace(old,new).replace('#SBATCH -J ap42-'+old[:3]+'-tok','#SBATCH -J ap42-'+new[:3]+'-warm'))
 (dst/'WARMFIX_PARENT.json').write_text(json.dumps({'parent':str(src.relative_to(Q)),'manifest_sha256':hashlib.sha256((src/'SHA256SUMS').read_bytes()).hexdigest(),'changed_files':['native-container.sh','topology-job.sh','config.json','job.sbatch','README.md','WARMFIX_PARENT.json'],'semantic_deadline_seconds':120,'absolute_global_warmup_seconds':720,'full_job_hard_stop_seconds':1020,'semantic_logic_changed':False,'model_client_protocol_changed':False},indent=2)+'\n')
 (dst/'README.md').write_text('''# Full tokenizer trial with bounded native warmup lifecycle

The previous three arms all reached actual source/runtime/KV readiness and wrote both valid semantic P/D receipts, then their outer 120-second Slurm/container step timed out. This prevented AIPerf; no valid throughput or tokenizer benefit exists. The exact location after semantic success was not instrumented, so slow container removal versus process shutdown remains an open distinction.

This derived arm keeps the original semantic Python logic and its 120-second budget, plus the original absolute T0+720 warmup deadline. The outer native step now uses the time remaining until that existing absolute deadline. Its extraction and removal therefore no longer consume the command's separate 120-second timeout. The full 17-minute job hard stop and full 60/120/30 benchmark remain. Lifecycle markers distinguish create, command return and removal boundaries without changing model math. Every semantic receipt, source/runtime/precision/KV/workload/SLA/output gate remains. The same repair is applied to the fresh control and both original prefill-only tokenizer waits; decode is unchanged. No new performance or official accuracy claim.
''')
 for name in ['worker.sh','benchmark.sh','expected-input-config.json','check-performance.py','performance_gates.py','check-fast-runtime.py','warm-topology.py','warmup_semantic.py','nixl-conn.py','kv_geometry.py','validate_kv_geometry.py','cleanup-node.py','exec.rc']:
  assert (src/name).read_bytes()==(dst/name).read_bytes(),name
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in {'.sh','.sbatch'}:subprocess.run(['bash','-n',str(f)],check=True)
 files=sorted(p for p in dst.iterdir() if p.is_file() and p.name!='SHA256SUMS');(dst/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files));subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=dst,check=True,stdout=subprocess.DEVNULL)
 checks.append({'bundle':new,'semantic_model_benchmark_gate_identity':'PASS','syntax':'PASS','manifest':'PASS'})
(D/'preparation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
