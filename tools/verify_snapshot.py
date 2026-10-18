#!/usr/bin/env python3
"""Verify exact captured bytes; deep mode decompresses each unique object once."""
import argparse,hashlib,json,subprocess,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest_stream(stream):
 h=hashlib.sha256();n=0
 while True:
  b=stream.read(4*1024*1024)
  if not b:break
  h.update(b);n+=len(b)
 return h.hexdigest(),n
def main():
 p=argparse.ArgumentParser();p.add_argument('--store',type=Path,default=ROOT.with_name(ROOT.name+'-artifacts'));p.add_argument('--deep',action='store_true');p.add_argument('--report',type=Path,default=ROOT/'backup/verification.json');a=p.parse_args();rows=[json.loads(x) for x in (ROOT/'backup/manifest.jsonl').read_text().splitlines()];errors=[];unique={};inline=0
 for r in rows:
  if r['storage']=='git':
   f=ROOT/r['path']
   try:
    with f.open('rb') as stream:h,n=digest_stream(stream)
    if (h,n)!=(r['sha256'],r['bytes']):errors.append(dict(path=r['path'],error='Inline checksum/size mismatch'))
   except OSError as e:errors.append(dict(path=r['path'],error=type(e).__name__))
   inline+=1
  else:unique.setdefault(r['sha256'],r)
 for i,r in enumerate(unique.values(),1):
  f=a.store/r['object']
  if not f.is_file():errors.append(dict(path=r['object'],error='Object missing'));continue
  if a.deep:
   process=subprocess.Popen(['zstd','-q','-d','-c',str(f)],stdout=subprocess.PIPE);h,n=digest_stream(process.stdout)
   if process.wait() or (h,n)!=(r['sha256'],r['bytes']):errors.append(dict(path=r['object'],error='Decompressed checksum/size mismatch'))
  if i%50==0:print(json.dumps(dict(objects_checked=i,total=len(unique))),flush=True)
 d=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),mode='deep' if a.deep else 'inline_hashes_and_object_presence',manifest_files=len(rows),inline_files_checked=inline,unique_objects_checked=len(unique),passed=not errors,errors=errors);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d));raise SystemExit(0 if not errors else 1)
if __name__=='__main__':main()
