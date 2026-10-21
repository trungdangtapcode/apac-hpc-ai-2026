"""Recover the exact public case commit after the committee GitLab migration."""
import concurrent.futures,datetime,hashlib,json,urllib.request,urllib.parse
from pathlib import Path
O=Path(__file__).resolve().parent
API='https://gitlab.com/api/v4/projects/83806040/repository/'
REV='84c262431117f5c921db8335e368a12d0e9fa3f0'
CASE='incompressible/simpleFoam/occDrivAerStaticMesh'
def get(url):return urllib.request.urlopen(url,timeout=30).read()
commit=json.loads(get(API+'commits/'+REV));assert commit['id']==REV
(O/'commit.json').write_text(json.dumps({k:commit[k] for k in ['id','title','committed_date','web_url']},indent=2)+'\n')
response=urllib.request.urlopen(API+'tree?path='+urllib.parse.quote(CASE)+'&ref='+REV+'&recursive=true&per_page=100',timeout=30)
assert not response.headers.get('X-Next-Page'),'Unexpected pagination; do not freeze incomplete tree'
tree=json.load(response);(O/'tree.json').write_text(json.dumps(tree,indent=2)+'\n')
# Plots are unnecessary for reconstruction; retain every text input and the figures licence.
selected=[r for r in tree if r['type']=='blob' and not r['path'].lower().endswith(('.png','.jpg','.pdf'))]
def fetch(row):
    relative=Path(row['path']).relative_to(CASE);url=API+'files/'+urllib.parse.quote(row['path'],safe='')+'/raw?ref='+REV
    path=O/'case'/relative;path.parent.mkdir(parents=True,exist_ok=True)
    data=path.read_bytes() if path.exists() else get(url)
    assert b'<!DOCTYPE html' not in data[:200], 'HTML is not case source'
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['id']
    path.write_bytes(data);path.chmod(int(row['mode'],8) & 0o777)
    return dict(mode=row['mode'],path=str(relative),url=url,git_blob=row['id'],sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(fetch,selected))
manifest=dict(retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repository='https://gitlab.com/openfoam/community/hpc',revision=REV,files=files,mesh_included=False,plots_omitted=True,our_measurement=False)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(text_files=len(files),bytes=sum(r['bytes'] for r in files),revision=REV,mesh_included=False)))
