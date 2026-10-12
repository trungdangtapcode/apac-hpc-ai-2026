"""Seal and atomically promote the clean final package; preserve prior snapshots."""
import hashlib
import json
import os
import subprocess
import zipfile
from datetime import datetime,timezone
from pathlib import Path

WORKSPACE=Path('/home/apacsc42/workspace')
STAGE=WORKSPACE/'submission-staging/VNUHCM - TripleU'
TARGET=WORKSPACE/'VNUHCM - TripleU'
LOGS=STAGE/'AI_Task/logs'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

assert json.loads((LOGS/'package-validation.json').read_text())['passed']
result=subprocess.run(['bash','setup.sh','--check'],cwd=STAGE/'AI_Task/job_scripts',capture_output=True,text=True,check=True)
(LOGS/'setup-check.log').write_text(result.stdout+result.stderr)
files=[p for p in sorted(STAGE.rglob('*')) if p.is_file() and p not in (LOGS/'FILE_MANIFEST.json',LOGS/'SHA256SUMS')]
assert not any(p.is_symlink() for p in STAGE.rglob('*'))
manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'paths_relative_to_team_directory':True,
    'files':[{'path':str(p.relative_to(STAGE)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
(LOGS/'FILE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=[p for p in sorted(STAGE.rglob('*')) if p.is_file() and p!=LOGS/'SHA256SUMS']
(LOGS/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {os.path.relpath(p,LOGS)}\n' for p in files))
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=LOGS,capture_output=True,text=True,check=True)
temp=WORKSPACE/'submission-staging/final-submission.zip.tmp'
with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    z.write(STAGE,STAGE.name+'/')
    for p in sorted(STAGE.rglob('*')):z.write(p,str(Path(STAGE.name)/p.relative_to(STAGE)))
with zipfile.ZipFile(temp) as z:
    assert z.testzip() is None,'ZIP CRC failure'
    expected={str(Path(STAGE.name)/p.relative_to(STAGE)) for p in STAGE.rglob('*') if p.is_file()}
    assert {i.filename for i in z.infolist() if not i.is_dir()}==expected
    assert {Path(i.filename).parts[1] for i in z.infolist() if len(Path(i.filename).parts)>1}=={'Presentation','AI_Task','HPC_Task'}
digest=sha(temp)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
archive=WORKSPACE/'submission-archive'/stamp;archive.mkdir(parents=True)
if TARGET.exists():TARGET.rename(archive/TARGET.name)
zip_target=WORKSPACE/'VNUHCM - TripleU.zip'
if zip_target.exists():zip_target.rename(archive/zip_target.name)
old_sha=zip_target.with_suffix('.zip.sha256')
if old_sha.exists():old_sha.rename(archive/old_sha.name)
STAGE.rename(TARGET)
temp.replace(zip_target)
zip_target.with_suffix('.zip.sha256').write_text(f'{digest}  {zip_target.name}\n')
print(json.dumps({'folder':str(TARGET),'zip':str(zip_target),'bytes':zip_target.stat().st_size,
    'sha256':digest,'files':len(expected),'english_only':True,'primary_config':'P8-TP4_D8-TP8-EP8',
    'N':48,'previous_snapshot_preserved':str(archive),'zip_crc_verified':True,'all_checksums_verified':True},indent=2))
