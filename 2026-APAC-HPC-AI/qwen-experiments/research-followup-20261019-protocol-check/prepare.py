"""Freeze an instrumented control and a global prefill protocol diagnostic."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tarfile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';source='h100-hpc-both-n54-repeat-39';src=P/source
assert json.loads((R/'research-followup-20261019-1200/221827.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
pilots=[];hashes={}
common='  export NCCL_DEBUG=INFO\n  export NCCL_DEBUG_SUBSYS=INIT,ENV,TUNING\n  echo "PREFILL_NCCL_PROTO=${NCCL_PROTO:-unset}"\n'
for name,candidate in [('h100-hpc-n54-env-control-46',False),('h100-hpc-prefill-simple-global-47',True)]:
 dst=P/name;assert not dst.exists();shutil.copytree(src,dst)
 s=(src/'worker.sh').read_text();needle='if [[ $role == prefill ]]; then\n';extra=('  export NCCL_PROTO=Simple\n' if candidate else '')+common;assert s.count(needle)==1;s=s.replace(needle,needle+extra,1)
 check="print('HPC_OPS_PREFLIGHT_PASSED', torch.cuda.get_device_name(), flush=True)";version="print('TORCH_NCCL_VERSION', torch.cuda.nccl.version(), flush=True)\n";assert s.count(check)==2;s=s.replace(check,version+check,1)
 assert s.replace(extra,'',1).replace(version,'',1)==(src/'worker.sh').read_text();assert s.split('\nelse\n',1)[1]==(src/'worker.sh').read_text().split('\nelse\n',1)[1];(dst/'worker.sh').write_text(s)
 f=dst/'benchmark.pbs';f.write_text(f.read_text().replace(source,name).replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE=1'))
 c=json.loads((src/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job='221827.pbs111',replication_source_job='221827.pbs111',control_experiment='h100-hpc-n54-env-control-46',fresh_control_job=None,diagnostic_profile=True,accuracy_verified=False,purpose='Matched instrumented N54 control for protocol activation diagnosis' if not candidate else 'Replace the unverified function-scoped protocol selector with NCCL_PROTO=Simple in prefill only; compare identical instrumented default-protocol control and require actual kernel/communicator proof.',prefill_environment={'NCCL_DEBUG':'INFO','NCCL_DEBUG_SUBSYS':'INIT,ENV,TUNING',**({'NCCL_PROTO':'Simple'} if candidate else {})},changed_factor={'kind':'global_prefill_protocol' if candidate else 'instrumented_control'},profile_position='Separate post-score N48 diagnostic; ranked workload unchanged');(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in {'.sh','.pbs'}:subprocess.run(['bash','-n',str(f)],check=True)
  if f.is_file() and f.name not in {'worker.sh','benchmark.pbs','config.json','SHA256SUMS'}:assert f.read_bytes()==(src/f.name).read_bytes()
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));hashes[name]=h
 pilots.append(dict(id=name,bundle=str(dst),platform='H100',state='PLANNED',planned_ns=[54],minutes=45,max_su=1536,replication_source_job='221827.pbs111',diagnostic_profile=True,purpose=c['purpose'],payload_sha256=h))
a=(P/pilots[0]['id']/'worker.sh').read_text();b=(P/pilots[1]['id']/'worker.sh').read_text();assert b.replace('  export NCCL_PROTO=Simple\n','',1)==a
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as tar:
 for p in pilots:tar.add(p['bundle'],arcname=p['id'])
(O/'pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,pair_workers_differ_only_by_global_prefill_proto=True,decode_unchanged=True,ranked_client_model_precision_transport_quality_unchanged=True,payloads=hashes),indent=2)+'\n')
print('Two instrumented fixed-N54 trials frozen, not submitted.')
