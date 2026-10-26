"""Verify both fresh initialized copies and retained original-cut integrity."""
from pathlib import Path
import hashlib,json,re,tarfile
E=Path(__file__).resolve().parent;meta=json.loads((E/'collection.json').read_text());arc=E/'raw-evidence.tar.gz'
assert hashlib.sha256(arc.read_bytes()).hexdigest()==meta['archive_sha256']
with tarfile.open(arc) as tar:data={m.name:tar.extractfile(m).read() for m in tar.getmembers()}
assert set(data)==set(meta['files'])
for name,raw in data.items():assert len(raw)==meta['files'][name]['bytes'] and hashlib.sha256(raw).hexdigest()==meta['files'][name]['sha256']
r='runs/2294098/';assert data[r+'mesh-before.json']==data[r+'mesh-after.json']
for order in ['xyz','zyx']:
 assert json.loads(data[r+order+'-complete.json'])['passed']
 for phase in ['before','after']:
  assert json.loads(data[r+order+'-source-'+phase+'.json'])['passed']
  fields=json.loads(data[r+order+'-fields-'+phase+'.json']);assert fields['passed'] and fields['field_count']==336
 for stage in ['renumberMesh','potentialFoam','applyBoundaryLayer']:
  log=data[r+order+'-'+stage+'.log'].decode();assert re.search(r'(?m)^End\s*$',log) and 'OPENFOAM=2512' in log and 'scalar=64' in log and re.search(r'(?m)^nProcs\s*:\s*56\s*$',log)
  assert json.loads(data[r+order+'-'+stage+'.status.json'])['returncode']==0
 prefix='initialized/order-'+order+'/'
 assert data[prefix+'source-before.json']==data[prefix+'source-after-copy.json']==data[prefix+'source-after-init.json']
 assert 'method=hierarchical' in data[prefix+'READY'].decode()
assert '2294098|COMPLETED|0:0|00:07:35|56|iris001|' in meta['accounting']
result={'passed':True,'job_id':'2294098','orders':['xyz','zyx'],'allocation_wall_seconds':455,'estimated_allocated_CPU_hours':56*455/3600,'verified_files':len(data),'both_original_cuts_unchanged':True,'both_copies_initialized':True,'solver_result':None,'limits':['No solver comparison yet','Full binary fields remain remote; byte seals and reproducible stages retained','Resource reports do not measure bandwidth or solver-time residency']}
(E/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
