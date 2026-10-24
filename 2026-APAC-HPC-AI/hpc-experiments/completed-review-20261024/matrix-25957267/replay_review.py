"""Independently replay retained control and partial-shim observations."""
from pathlib import Path
import collections,hashlib,json
E=Path(__file__).resolve().parent;D=E/'collected';m=json.loads((D/'collection.json').read_text())
for rel,item in m['files'].items():
 data=(D/rel).read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
p=D/'25957267/runs/25957267/logs'
def rows(name,stream,marker):
 return [json.loads(x.split(marker,1)[1]) for x in (p/(name+'.'+stream+'.txt')).read_text().splitlines() if marker in x]
review=json.loads((E/'review.json').read_text())
for name in ['method0_cli','method3_pals_env']:
 data=rows(name,'stdout','TOPOLOGY_JSON\t');assert len(data)==512 and {x['rank'] for x in data}==set(range(512))
 assert all(len(x['pre_init_cpus'])==1 for x in data)
 assert sum(x['post_init_cpus']==list(range(256)) for x in data)==review['controls'][name]['post_init_256CPU']
 assert sum(len(x['post_init_cpus'])==1 for x in data)==review['controls'][name]['post_init_singleton']
data=rows('mpi_identity','stderr','APAC_AFFINITY_JSON ');assert len(data)==512 and {x['rank'] for x in data}==set(range(512))
assert sum(x['success'] for x in data)==review['shim_restored_success']==253
assert all(x['restore_set_status']==-1 and x['pre_init_truncated'] for x in data if not x['success'])
rc=json.loads((p.parent/'command-return-codes.json').read_text());assert not any(x['stage']=='mpi_candidate' for x in rc)
assert rc[-1]=={'stage':'mpi_identity','return_code':255}
assert review['source_after']['passed']
print('All retained matrix counts, source seal and failure-stage observations replayed')
