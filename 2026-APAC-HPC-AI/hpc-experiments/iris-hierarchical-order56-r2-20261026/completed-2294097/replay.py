"""Verify the retained four-cut archive and native summaries without cluster access."""
from pathlib import Path
import hashlib,json,re,tarfile
E=Path(__file__).resolve().parent;meta=json.loads((E/'collection.json').read_text());archive=E/'raw-evidence.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['archive_sha256']
with tarfile.open(archive) as tar:
 rows={m.name:tar.extractfile(m).read() for m in tar.getmembers()}
assert set(rows)==set(meta['files'])
for name,raw in rows.items():assert len(raw)==meta['files'][name]['bytes'] and hashlib.sha256(raw).hexdigest()==meta['files'][name]['sha256']
run='runs/2294097/';result=json.loads(rows[run+'results.json']);assert result['all_complete'] and len(result['arms'])==4
assert rows[run+'mesh-before.json']==rows[run+'mesh-after.json']
for phase in ['before','after']:
 assert json.loads(rows[run+'source-'+phase+'.json'])['passed']
 assert json.loads(rows[run+'mesh-'+phase+'.json'])['passed']
for arm in result['arms']:
 order=arm['order'];log=rows['cases/order-'+order+'/logs/decomposePar.log'].decode()
 cells=[int(v) for v in re.findall(r'(?m)^[ \t]+Number of cells = (\d+)',log)];faces=[int(v) for v in re.findall(r'(?m)^[ \t]+Number of processor faces = (\d+)',log)]
 assert arm['passed'] and arm['restored_initial_fields']==336 and len(cells)==len(faces)==56 and sum(cells)==65334765
 assert cells==arm['cells_by_rank'] and sum(faces)==2*arm['unique_interface_faces'] and re.search(r'(?m)^End\s*$',log)
assert '2294097|COMPLETED|0:0|00:06:03|56|iris005|' in meta['accounting']
print('PASS: 51 retained artifacts, four native cuts and source/mesh seals. No initialization or solver claim.')
