"""Verify the official archive and reused unpacked mesh on allocated CPUs."""
from pathlib import Path
import hashlib,tarfile,json,datetime
archive=Path('/scratch/users/industry/hpcadvisorycouncil/pengzhi/public/2026-apac-hpc-ai/openfoam/polyMesh_65M.tar.gz')
mesh=Path('/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc/shared/polyMesh')
md5=hashlib.md5();sha=hashlib.sha256()
with archive.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):md5.update(b);sha.update(b)
assert md5.hexdigest()=='50393a15d84f53255fda85ac702390e9'
rows=[]
with tarfile.open(str(archive),'r|gz') as t:
 for m in t:
  if m.isdir():continue
  assert m.isfile() and '..' not in Path(m.name).parts and not m.name.startswith('/')
  parts=Path(m.name).parts;assert 'polyMesh' in parts
  relative=Path(*parts[parts.index('polyMesh')+1:]);p=mesh/relative
  assert p.is_file() and p.stat().st_size==m.size
  a=hashlib.sha256();b=hashlib.sha256()
  with t.extractfile(m) as src:
   for chunk in iter(lambda:src.read(1024*1024),b''):a.update(chunk)
  with p.open('rb') as src:
   for chunk in iter(lambda:src.read(1024*1024),b''):b.update(chunk)
  assert a.hexdigest()==b.hexdigest(),str(relative)
  rows.append({'file':str(relative),'bytes':m.size,'sha256':a.hexdigest()})
assert {'points','faces','owner','neighbour','boundary'}.issubset(set(x['file'] for x in rows))
Path('mesh-identity.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive_md5':md5.hexdigest(),'archive_sha256':sha.hexdigest(),'unpacked_members_match_archive':rows},indent=2)+'\n')
