"""Prepare a source-supported attention trial; do not upload, reserve or submit."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs'
source='h100-hpc-both-n54-repeat-39';name='h100-hpc-prefill-flashinfer-n54-45';src=P/source;dst=P/name
assert not dst.exists();shutil.copytree(src,dst)
f=dst/'worker.sh';s=f.read_text();needle='--chunked-prefill-size 4096';patch=needle+' --prefill-attention-backend flashinfer';assert s.count(needle)==1;s=s.replace(needle,patch,1);f.write_text(s)
assert s.replace(patch,needle,1)==(src/'worker.sh').read_text()
assert s.split('\nelse\n',1)[1]==(src/'worker.sh').read_text().split('\nelse\n',1)[1]
f=dst/'benchmark.pbs';s=f.read_text().replace(source,name).replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE=1');f.write_text(s)
c=json.loads((src/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job='221645.pbs111',replication_source_job='221645.pbs111',control_experiment='h100-hpc-n54-control-profile-42',fresh_control_job='221827.pbs111',purpose='Dense FlashInfer prefill backend at fixed N54, both-phase HPC-Ops and chunk4096; compare the fresh default-FA3 prefill control. Exact retained container supports the per-phase flag and registered backend. No performance prediction; verify actual kernels and output checks.',diagnostic_profile=True,accuracy_verified=False,changed_factor={'phase':'prefill','attention_backend':'flashinfer'})
c['prefill_extra_flags']+=['--prefill-attention-backend','flashinfer'];(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
for f in dst.iterdir():
 if f.suffix=='.py':ast.parse(f.read_text())
 if f.suffix in {'.pbs','.sh'}:subprocess.run(['bash','-n',str(f)],check=True)
 if f.is_file() and f.name not in {'worker.sh','benchmark.pbs','config.json','SHA256SUMS'}:assert f.read_bytes()==(src/f.name).read_bytes()
h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()))
(O/'standby-pilot.json').write_text(json.dumps(dict(id=name,bundle=str(dst),platform='H100',state='PREPARED_NOT_SUBMITTED_QUEUE_CAP',planned_ns=[54],max_su=1536,minutes=45,source_job='221645.pbs111',fresh_control_job='221827.pbs111',payload_sha256=h,budget_reserved=False,diagnostic_profile=True,submission_condition='Review earliest new completion and live queue/credit first. Submit if still a useful distinct comparison and fewer than three active PBS jobs. Select a dependency preserving one running allocation. Never resubmit an uncertain receipt.'),indent=2)+'\n')
print('One attention standby frozen; not submitted or reserved.')
