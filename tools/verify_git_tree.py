#!/usr/bin/env python3
"""Check every captured inline file against actual Git blobs, not only the worktree."""
import argparse,collections,datetime,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);a=p.parse_args();rows=[json.loads(x) for x in (ROOT/'backup/manifest.jsonl').read_text().splitlines()];entries={}
 tree=subprocess.check_output(['git','ls-tree','-r','-z','HEAD'],cwd=ROOT)
 for record in tree.split(b'\0'):
  if not record:continue
  meta,name=record.split(b'\t',1);mode,kind,oid=meta.decode().split();entries[name.decode()]=(kind,oid)
 objects={};errors=[]
 for r in rows:
  if r['storage']!='git':continue
  entry=entries.get(r['path'])
  if not entry or entry[0]!='blob':errors.append(dict(path=r['path'],error='Missing tracked Git blob'));continue
  expected=(r['sha256'],r['bytes']);prior=objects.get(entry[1])
  if prior and prior!=expected:errors.append(dict(path=r['path'],error='Conflicting content for one Git blob'))
  objects[entry[1]]=expected
 proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 for oid,(expected,size) in objects.items():
  proc.stdin.write((oid+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().decode().strip().split();assert header[:2]==[oid,'blob'];remaining=int(header[2]);n=remaining;h=hashlib.sha256()
  while remaining:
   b=proc.stdout.read(min(4*1024*1024,remaining));assert b;h.update(b);remaining-=len(b)
  assert proc.stdout.read(1)==b'\n'
  if n!=size or h.hexdigest()!=expected:errors.append(dict(blob=oid,error='Git content differs from captured source'))
 proc.stdin.close();assert proc.wait()==0
 integrity=subprocess.run(['git','fsck','--full'],cwd=ROOT,capture_output=True,text=True);status=subprocess.check_output(['git','status','--porcelain=v1','-z'],cwd=ROOT);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();count=int(subprocess.check_output(['git','rev-list','--count','HEAD'],cwd=ROOT,text=True));records=subprocess.check_output(['git','log','--format=%H%x09%aI%x09%cI%x09%s'],cwd=ROOT,text=True).splitlines();dates=[dict(zip(['commit','author_date','committer_date','subject'],x.split('\t',3))) for x in records]
 result=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),head=head,commits=count,tracked_paths=len(entries),captured_inline_paths=sum(r['storage']=='git' for r in rows),unique_captured_blobs_checked=len(objects),source_hashes_match=not errors,git_fsck_passed=integrity.returncode==0,worktree_clean=not status,commit_metadata=dates,errors=errors,passed=not errors and integrity.returncode==0 and not status);a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='commit_metadata'}));raise SystemExit(0 if result['passed'] else 1)
if __name__=='__main__':main()
