"""Seal the delivered files, validate checksums, and make the upload archive."""
import hashlib,json,subprocess,zipfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path('/home/apacsc42/workspace/VNUHCM - TripleU')
SCRIPTS=ROOT/'AI_Task/job_scripts'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

files=[p for p in sorted(SCRIPTS.iterdir()) if p.is_file() and p.name!='SHA256SUMS']
files += [p for p in sorted((SCRIPTS/'hf-cache').rglob('*')) if p.is_file()]
(SCRIPTS/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(SCRIPTS)}\n' for p in files))
result=subprocess.run(['bash','setup.sh','--check'],cwd=SCRIPTS,capture_output=True,text=True,check=True)
(ROOT/'AI_Task/logs/setup-check.log').write_text(result.stdout+result.stderr)

manifest=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p.name in ('FILE_MANIFEST.json','SHA256SUMS') and p.parent==ROOT:continue
    if p.is_symlink():raise RuntimeError('Unexpected symlink in package: '+str(p))
    manifest.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)})
(ROOT/'FILE_MANIFEST.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),
  'excludes_self_and_root_checksums':True,'files':manifest},indent=2,ensure_ascii=False)+'\n')
files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=ROOT/'SHA256SUMS']
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n' for p in files))
check=subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=ROOT,capture_output=True,text=True,check=True)
archive=ROOT.parent/(ROOT.name+'.zip')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    z.write(ROOT,ROOT.name+'/')
    for p in sorted(ROOT.rglob('*')):z.write(p,str(p.relative_to(ROOT.parent)))
with zipfile.ZipFile(archive) as z:
    damaged=z.testzip()
    if damaged:raise RuntimeError('ZIP integrity failed: '+damaged)
    archived={i.filename for i in z.infolist() if not i.is_dir()}
    expected={str(p.relative_to(ROOT.parent)) for p in ROOT.rglob('*') if p.is_file()}
    if archived!=expected:raise RuntimeError('Archive inventory mismatch')
digest=sha(archive)
archive.with_suffix('.zip.sha256').write_text(f'{digest}  {archive.name}\n')
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest,
  'sealed_files':len(files)+1,'zip_crc_verified':True,'checksums_verified':True,
  'setup_check_passed':True},indent=2))
