"""Replay native initialization and transfer checks; no solver claim."""
from pathlib import Path
import hashlib,importlib.util,json,re
E=Path(__file__).resolve().parent;O=E/'completed-2294915';d=json.loads((O/'collection.json').read_text())
for name,row in d['files'].items():
 raw=(O/'collected'/name).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
spec=importlib.util.spec_from_file_location('init_checks',E/'verify-init.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
runs=O/'collected/init-runs';stage=module.check_stage_logs(runs,'2294915');assert stage['passed']
accounting=[line.split('|') for line in d['accounting']['stdout'].splitlines()];row=next(row for row in accounting if row[0]=='2294915')
assert row[1:6]==['COMPLETED','0:0','111','56','iris001']
source=[json.loads((runs/('2294915-source-'+phase+'.json')).read_text()) for phase in ['before','after']]
assert all(s['passed'] and s['pinned_files']==41 for s in source)
assert source[0]['input_hashes']==source[1]['input_hashes']
manifest=json.loads((E/'payload-sha256.json').read_text())['files']
for phase in ['before','after']:
 lines=(runs/('2294915-kit-source-'+phase+'.txt')).read_text().splitlines()
 assert set(lines)=={name+': OK' for name in manifest}
fields=[json.loads((runs/('2294915-fields-'+phase+'.json')).read_text()) for phase in ['before','after']]
assert all(f['passed'] and f['field_count']==288 and len(f['fields'])==288 for f in fields)
assert set(fields[0]['fields'])==set(fields[1]['fields'])
changed=sum(fields[0]['fields'][name]['sha256']!=fields[1]['fields'][name]['sha256'] for name in fields[0]['fields'])
resources={}
for stage_name in ['renumberMesh','potentialFoam','applyBoundaryLayer']:
 text=(runs/('2294915-'+stage_name+'.resource.txt')).read_text();assert 'Exit status: 0' in text
 resources[stage_name]={'peak_RSS_KiB_as_reported_by_GNU_time':int(re.search(r'Maximum resident set size \(kbytes\): (\d+)',text).group(1))}
r={'passed':True,'job_id':'2294915','terminal_state':'COMPLETED','exit_code':'0:0','allocation_wall_seconds':111,'allocated_CPUs':56,'estimated_allocated_CPU_hours':56*111/3600,'SU_charge':None,'stages':stage,'pinned_kit_files':len(manifest),'pinned_case_files':41,'initial_field_files_before_and_after':288,'fields_changed_by_required_initialization':changed,'resource_observations':resources,'transfer_verified_files':len(d['files']),'limits':['No solver timing or Cd result','GNU time peak RSS is not aggregate 48-rank resident memory or bandwidth','Changed initialized field hashes are expected, not an error','Original reviewed cut payload and group input were not changed']}
(E/'completed-review.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

assert (O/"collected/artifacts/cut-N48-scotch/READY").read_text().startswith("N=48\nmethod=scotch\n")
