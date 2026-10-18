#!/usr/bin/env python3
"""Restore manifest paths, verify bytes and refuse unexpected overwrites."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--store',type=Path,default=ROOT.with_name(ROOT.name+'-artifacts'));p.add_argument('--destination',type=Path,required=True);p.add_argument('--path',action='append',help='Restore this exact manifest path; repeat to select several');p.add_argument('--overwrite',action='store_true');a=p.parse_args();dest=a.destination.resolve();rows=[json.loads(x) for x in (ROOT/'backup/manifest.jsonl').read_text().splitlines()];selected=set(a.path or []);matched=set();restored=0
 if not selected and (ROOT/'backup/directories.json').exists():
  for entry in json.loads((ROOT/'backup/directories.json').read_text()):
   relative=Path(entry)
   if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe directory path')
   directory=dest/relative
   if dest not in directory.resolve().parents and directory.resolve()!=dest:raise ValueError('Directory traverses a symlink')
   directory.mkdir(parents=True,exist_ok=True)
 for r in rows:
  if selected and r['path'] not in selected:continue
  matched.add(r['path']);rel=Path(r['path'])
  if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe manifest path')
  target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
  if dest not in target.parent.resolve().parents and target.parent.resolve()!=dest:raise ValueError('Destination traverses a symlink')
  if target.exists() and not a.overwrite:
   h=hashlib.sha256()
   with target.open('rb') as f:
    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
   if h.hexdigest()==r['sha256']:continue
   raise FileExistsError('Refusing different existing content: '+str(target))
  fd,tmp=tempfile.mkstemp(prefix='.restore-',dir=target.parent);tmp=Path(tmp)
  try:
   with os.fdopen(fd,'wb') as output:
    if r['storage']=='git':
     with (ROOT/r['path']).open('rb') as source:shutil.copyfileobj(source,output,4*1024*1024)
    else:subprocess.run(['zstd','-q','-d','-c',str(a.store/r['object'])],stdout=output,check=True)
   h=hashlib.sha256()
   with tmp.open('rb') as f:
    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
   if tmp.stat().st_size!=r['bytes'] or h.hexdigest()!=r['sha256']:raise ValueError('Restored checksum mismatch: '+r['path'])
   os.chmod(tmp,r['mode']);os.utime(tmp,ns=(r['mtime_ns'],r['mtime_ns']));tmp.replace(target);restored+=1
  finally:
   if tmp.exists():tmp.unlink()
 if selected-matched:raise ValueError('Requested paths missing from manifest: '+str(sorted(selected-matched)))
 print(json.dumps(dict(restored=restored,selected_paths=len(matched),destination=str(dest),checksums_verified=True)))
if __name__=='__main__':main()
