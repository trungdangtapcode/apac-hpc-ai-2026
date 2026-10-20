"""Re-evaluate decode attention on the new both-HPC-Ops H100 incumbent."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tarfile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';src=P/'h100-hpc-n54-inference-control-49'
assert json.loads((R/'research-followup-20261020-0028/221923.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
registry=R/'research-followup-20261019-1200/runtime-attention-source/sgl-workspace/sglang/python/sglang/srt/layers/attention/attention_registry.py';text=registry.read_text();assert '@register_attention_backend("fa3")' in text
pilots=[]
for name,backend in [('h100-hpc-n54-attention-control-55','flashinfer'),('h100-hpc-n54-decode-fa3-56','fa3')]:
 dst=P/name;assert not dst.exists();shutil.copytree(src,dst);p=dst/'benchmark.pbs';p.write_text(p.read_text().replace(src.name,name))
 p=dst/'worker.sh';s=p.read_text();needle='--decode-attention-backend flashinfer';assert s.count(needle)==1
 if backend=='fa3':s=s.replace(needle,'--decode-attention-backend fa3',1)
 p.write_text(s);assert s.replace('--decode-attention-backend fa3',needle,1)==(src/'worker.sh').read_text()
 c=json.loads((src/'config.json').read_text());c.update(experiment=name,source_experiment=src.name,source_job='221923.pbs111',control_job=None,control_experiment='h100-hpc-n54-attention-control-55',changed_factor={'phase':'decode','attention_backend':backend},purpose='Fresh matched FlashInfer decode control on both-HPC-Ops N54' if backend=='flashinfer' else 'Re-evaluate dense FA3 decode after the MoE runner/load changes; compare with fresh same-load FlashInfer control',accuracy_verified=False)
 c['decode_extra_flags']=[backend if v=='flashinfer' else v for v in c['decode_extra_flags']];(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for p in dst.iterdir():
  if p.suffix=='.py':ast.parse(p.read_text())
  if p.suffix in {'.sh','.pbs'}:subprocess.run(['bash','-n',str(p)],check=True)
  if p.name not in {'benchmark.pbs','worker.sh','config.json','SHA256SUMS'}:assert p.read_bytes()==(src/p.name).read_bytes()
 h={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dst.iterdir()) if p.is_file() and p.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()))
 pilots.append(dict(platform='H100',id=name,bundle=str(dst),planned_ns=[54],minutes=45,max_su=1536,state='PREPARED_NOT_SUBMITTED',diagnostic_profile=True,payload_sha256=h))
(O/'pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,worker_inverse_patch_pass=True,all_other_operational_files_byte_identical=True,full_workload_precision_transport_output_gates_unchanged=True,pinned_registry_sha256=hashlib.sha256(registry.read_bytes()).hexdigest(),fa3_registered=True,gpu_compatibility_and_effect_unverified=True),indent=2)+'\n')
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as archive:
 for p in pilots:archive.add(p['bundle'],arcname=p['id'])
print('Prepared fresh FlashInfer control and decode-only FA3 candidate')
