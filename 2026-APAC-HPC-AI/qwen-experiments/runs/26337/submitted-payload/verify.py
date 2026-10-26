#!/usr/bin/env python3
"""CPU checks of the fanout plan and strict result gates, not GPU evidence."""
from pathlib import Path
import ast,hashlib,importlib.util,json,subprocess,tempfile
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('probe',H/'probe.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for p in H.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in [H/'job.sbatch',H/'entry.sh']:subprocess.run(['bash','-n',str(p)],check=True)
assert len({(r,p) for r in range(8) for p in m.peers(r)})==16
rows=[]
for rank in range(16):
 phases=[]
 for i,phase in enumerate(m.PHASES):
  targets=m.peers(rank) if rank in m.senders(phase) else []
  phases.append({'phase':phase,'sent':[{'sender':rank,'receiver':p,'state':'DONE','bytes':m.REGIONS*m.WRITE_BYTES} for p in targets],'received_bytes_and_sentinels_verified':rank>=8,'received_sha256':hashlib.sha256(m.expected_receive(rank,i)).hexdigest() if rank>=8 else None})
 rows.append({'rank':rank,'state':'PASS_COMPONENT_ONLY','host':'prefill-host' if rank<8 else 'decode-host','gpu_uuid':'CPU_FIXTURE_'+str(rank),'agent_name':'CPU_AGENT_'+str(rank),'peer_ranks':m.peers(rank),'regions':m.REGIONS,'phases':phases})
checks=[]
with tempfile.TemporaryDirectory(prefix='nixl-fanout-cpu-') as t:
 art=Path(t)
 def write():
  for row in rows:(art/f"rank-{row['rank']}.json").write_text(json.dumps(row))
 def reject(label):
  try:m.check(art)
  except (AssertionError,FileNotFoundError):checks.append(label)
  else:raise AssertionError('Gate incorrectly accepted '+label)
 write();assert m.check(art)['write_handles']==32
 original=rows[0]['gpu_uuid'];rows[0]['gpu_uuid']=rows[1]['gpu_uuid'];write();reject('duplicate physical GPU');rows[0]['gpu_uuid']=original
 original=rows[0]['phases'][0]['sent'][0]['receiver'];rows[0]['phases'][0]['sent'][0]['receiver']=9;write();reject('wrong peer');rows[0]['phases'][0]['sent'][0]['receiver']=original
 original=rows[8]['phases'][0]['received_sha256'];rows[8]['phases'][0]['received_sha256']='0'*64;write();reject('wrong received bytes or sentinel hash');rows[8]['phases'][0]['received_sha256']=original
 write();(art/'rank-15.json').unlink();reject('missing rank')
report={'state':'PASS_CPU_FIXTURES_ONLY','expected_write_handles':32,'expected_bytes':32*m.REGIONS*m.WRITE_BYTES,'negative_cases_rejected':checks,'limits':'No native imports, CUDA registration, NIXL transfer, GPU result or inference measured by these CPU fixtures.'}
(H/'CPU-VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
