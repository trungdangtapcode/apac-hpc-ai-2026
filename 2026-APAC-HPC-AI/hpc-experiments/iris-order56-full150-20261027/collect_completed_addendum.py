"""Collect native timing and force-coefficient function-object tables omitted by v1."""
from pathlib import Path
import base64,datetime,hashlib,io,json,sys,tarfile
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json
OUT=E/'completed-2294234'/'collected-addendum'
assert not OUT.exists(),f'Preserve existing addendum: {OUT}'
root=json.loads((E/'deployment.json').read_text())['root']
body='ROOT='+repr(root)+r'''
from pathlib import Path
import base64,datetime,hashlib,io,json,tarfile
r=Path(ROOT);files={};stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for rel in ['cases/zyx/postProcessing/wallClockTimeStatistics/0/wallClockTime.dat',
             'cases/zyx/postProcessing/forceCoeffsAll/0/coefficient.dat',
             'cases/xyz/postProcessing/wallClockTimeStatistics/0/wallClockTime.dat',
             'cases/xyz/postProcessing/forceCoeffsAll/0/coefficient.dat']:
  p=r/rel;raw=p.read_bytes();files[rel]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
  info=tarfile.TarInfo(rel);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
raw=stream.getvalue();result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'archive_bytes':len(raw),'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_base64':base64.b64encode(raw).decode()}
'''
d=run_json(body,timeout=55);raw=base64.b64decode(d.pop('archive_base64'),validate=True)
assert len(raw)==d['archive_bytes'] and hashlib.sha256(raw).hexdigest()==d['archive_sha256']
OUT.mkdir();(OUT/'raw-evidence.tar.gz').write_bytes(raw);(OUT/'collection.json').write_text(json.dumps(d,indent=2)+'\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for m in tar.getmembers():
  assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  data=tar.extractfile(m).read();meta=d['files'][m.name]
  assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256']
  p=E/'completed-2294234'/'collected'/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
print(json.dumps({'files':d['files'],'archive_bytes':len(raw),'archive_sha256':d['archive_sha256']}))
