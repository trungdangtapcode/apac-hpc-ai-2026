"""Freeze observer overhead controls and a decode-only native receive-poll candidate on each platform."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tarfile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;T=R/'resource-telemetry-20261020';D=R/'serving-tuning-10';P=R/'nscc-pbs'
assert json.loads((T/'validation.json').read_text())['passed']
assert json.loads((R/'research-followup-20261020-0132/24913-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
assert json.loads((R/'research-followup-20261020-0132/222027.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
fixed=(R/'profile-http-fix-20261020/profile-serving.py').read_text();node=next(x for x in ast.parse(fixed).body if isinstance(x,ast.FunctionDef) and x.name=='post');fixed_post=ast.get_source_segment(fixed,node)
pilots=[]
for platform,source,n,names in [('H200',R/'runs/24913/submitted',60,['s19-hpc-n60-observer-off','s19-hpc-n60-observer-on','s19-hpc-n60-recv2']),('H100',P/'h100-hpc-n54-attention-control-55',54,['h100-hpc-n54-observer-off-57','h100-hpc-n54-observer-on-58','h100-hpc-n54-recv2-59'])]:
 subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=source,capture_output=True,check=True)
 old=json.loads((source/'config.json').read_text())['experiment'];group=[]
 for ix,name in enumerate(names):
  monitor=ix>0;recv=2 if ix==2 else 1;dst=(D if platform=='H200' else P)/name;assert not dst.exists();shutil.copytree(source,dst)
  for fname in ['resource-sampler.py','phase-marker.py']:shutil.copyfile(T/fname,dst/fname)
  launch=dst/('job.sbatch' if platform=='H200' else 'benchmark.pbs');s=launch.read_text().replace(old,name)
  if platform=='H200':s=s.replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE=1')
  s=s.replace('set -euo pipefail','set -euo pipefail\nexport QWEN_RESOURCE_MONITOR='+str(int(monitor))+'\nexport QWEN_TELEMETRY_MAX_S='+('1100' if platform=='H200' else '2800'),1);launch.write_text(s)
  p=dst/'topology-job.sh';s=p.read_text();assert 'ART=$ROOT/runs/$SLURM_JOB_ID' in s;s=s.replace('ART=$ROOT/runs/$SLURM_JOB_ID','ART=$ROOT/runs/$SLURM_JOB_ID\nexport QWEN_ARTDIR="$ART"',1);p.write_text(s)
  p=dst/'worker.sh';s=p.read_text();needle='exec python3 -m sglang.launch_server';assert s.count(needle)==1
  addon='''telemetry_flags=()
if [[ ${QWEN_RESOURCE_MONITOR:-0} == 1 ]]; then
  telemetry_flags=(--enable-metrics)
  mkdir -p "$QWEN_ARTDIR/resource-telemetry"
  python3 "$QWEN_BUNDLE/resource-sampler.py" --out "$QWEN_ARTDIR/resource-telemetry" \\
    --role "$name" --port "$port" --parent "$$" --gpus "${CUDA_VISIBLE_DEVICES:-}" \\
    --interval 5 --duration "$QWEN_TELEMETRY_MAX_S" \\
    >"$QWEN_ARTDIR/resource-telemetry/$name-sampler.log" 2>&1 &
fi
'''
  s=s.replace(needle,addon+needle,1);s=s.replace('"${extra[@]}" "$@"','"${telemetry_flags[@]}" "${extra[@]}" "$@"')
  if recv==2:
   needle='extra=(--cuda-graph-max-bs-decode 64';assert s.count(needle)==1;s=s.replace(needle,'extra=(--scheduler-recv-interval 2 --cuda-graph-max-bs-decode 64',1)
  p.write_text(s)
  p=dst/'benchmark.sh';s=p.read_text();needle='  timeout --signal=TERM --kill-after=15s 360s aiperf profile' if platform=='H200' else '  aiperf profile';assert s.count(needle)==1;s=s.replace(needle,'  python3 "$QWEN_BUNDLE/phase-marker.py" "$ART" benchmark_start "$PHASE" "$N"\n'+needle,1)
  needle='  echo "DONE $PHASE N=$N at $(date -Iseconds)"';assert s.count(needle)==1;s=s.replace(needle,'  python3 "$QWEN_BUNDLE/phase-marker.py" "$ART" benchmark_end "$PHASE" "$N"\n'+needle,1);p.write_text(s)
  p=dst/'profile-serving.py';s=p.read_text();oldnode=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='post');s=s.replace(ast.get_source_segment(s,oldnode),fixed_post,1);s=s.replace("post(url+'/start_profile', request, timeout=60)","post(url+'/start_profile', request, timeout=60, expect_json=False)").replace("post(url+'/stop_profile', {}, timeout=60)","post(url+'/stop_profile', {}, timeout=60, expect_json=False)");p.write_text(s)
  c=json.loads((source/'config.json').read_text());c.update(experiment=name,source_experiment=old,source_job='24913' if platform=='H200' else '222027.pbs111',control_experiment=names[1],diagnostic_profile=True,resource_monitor=monitor,scheduler_recv_interval_decode=recv,purpose=['Observer-off reference; common phase markers and post-score profiler HTTP fix','Observer-on interval-1 control; quantify monitoring overhead','Observer-on decode-only native polling interval 2; compare equally observed control'][ix],changed_factor={'resource_monitor':monitor,'scheduler_recv_interval_decode':recv},accuracy_verified=False)
  if platform=='H200':c.update(replication_source_job='24913',concurrency=[60])
  (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
  for f in dst.iterdir():
   if f.suffix=='.py':ast.parse(f.read_text())
   if f.suffix in {'.sh','.sbatch','.pbs'}:subprocess.run(['bash','-n',str(f)],check=True)
  allowed={'benchmark.pbs','job.sbatch','topology-job.sh','worker.sh','benchmark.sh','profile-serving.py','config.json','SHA256SUMS','resource-sampler.py','phase-marker.py'}
  for f in source.iterdir():
   if f.is_file() and f.name not in allowed:assert f.read_bytes()==(dst/f.name).read_bytes(),f.name
  hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in hashes.items()))
  pilot=dict(platform=platform,id=name,bundle=str(dst),planned_ns=[n],state='PREPARED_NOT_SUBMITTED',minutes=17 if platform=='H200' else 45,max_su=None if platform=='H200' else 1536,payload_sha256=hashes,resource_monitor=monitor,scheduler_recv_interval_decode=recv,diagnostic_profile=True,purpose=c['purpose'],accuracy_verified=False)
  if platform=='H200':pilot.update(wave=10,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=False,traces=[],attempts=[])
  pilots.append(pilot);group.append(dst)
 assert (group[0]/'worker.sh').read_bytes()==(group[1]/'worker.sh').read_bytes()
 assert (group[2]/'worker.sh').read_text().replace('--scheduler-recv-interval 2 ','')==(group[1]/'worker.sh').read_text()
 for fname in ['benchmark.sh','topology-job.sh','profile-serving.py','resource-sampler.py','phase-marker.py']:assert len({(x/fname).read_bytes() for x in group})==1
(O/'pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,candidate_vs_monitored_control_worker_only_poll_interval_diff=True,off_on_worker_identical_env_toggle=True,workload_outputs_precision_transport_numerical_kernels_unchanged=True,syntax_checked=True,sampler_and_native_selector_local_fixture_pass=True,monitoring_gpu_execution_and_overhead_unverified=True),indent=2)+'\n')
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as archive:
 for pilot in pilots:
  if pilot['platform']=='H100':archive.add(pilot['bundle'],arcname=pilot['id'])
print('Prepared three matched runs on each platform; all syntax and inverse-diff checks passed')
