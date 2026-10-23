"""Verify embedded case/helper bytes and narrowly derived rank/end-time settings."""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def files(root): return {str(p.relative_to(root)):p for p in root.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix != '.pyc' and 'runs' not in p.relative_to(root).parts and p.name != 'bundle-sha256.json'}
def main():
 a=argparse.ArgumentParser();a.add_argument('--root',default=str(ROOT));a.add_argument('--mode',choices=['bundle','case','derive','mesh'],required=True);a.add_argument('--case');a.add_argument('--mesh');a.add_argument('--nodes',type=int,default=4);a.add_argument('--steps',type=int,default=150);x=a.parse_args();root=Path(x.root)
 if x.mode=='bundle':
  m=json.loads((root/'bundle-sha256.json').read_text())['files']; got=files(root); assert set(m)==set(got),(sorted(set(m)-set(got)),sorted(set(got)-set(m))); bad={n:(sha(p),m[n]) for n,p in got.items() if sha(p)!=m[n]}; assert not bad,bad; out={'passed':True,'hashed_files':len(m),'all_match':True}
 elif x.mode=='mesh':
  mesh=Path(x.mesh or '/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc/shared/polyMesh'); data=json.loads((root/'mesh-manifest.json').read_text()); rows=[]
  for n,q in data['members'].items():
   p=mesh/n; assert p.is_file() and p.stat().st_size==q['bytes'] and sha(p)==q['sha256'],n; rows.append(n)
  out={'passed':True,'member_count_checked':len(rows),'archive_md5':data['archive_md5'],'archive_sha256':data['archive_sha256'],'members':rows}
 else:
  case=Path(x.case) if x.case else root/'case'; n=x.nodes*128; assert (x.nodes,x.steps) in ((1,40),(2,80),(4,150)); m=json.loads((root/'source-case-sha256.json').read_text())['files']; got=files(case); assert set(got)==set(m),(sorted(set(got)-set(m)),sorted(set(m)-set(got)))
  changed=[]
  for rel,p in got.items():
   old=m[rel]
   if sha(p)==old: continue
   assert x.mode=='derive' and rel in ('system/include/caseDefinition','system/controlDict'),('unexpected changed file',rel)
   original=(root/'case'/rel).read_bytes(); actual=p.read_bytes()
   if rel.endswith('caseDefinition'): expected=re.sub(rb'(?m)^(\s*nCores\s+)128(\s*;)',lambda m:m.group(1)+str(n).encode()+m.group(2),original,count=1)
   else: expected=re.sub(rb'(?m)^(\s*endTime\s+)40(\s*;)',lambda m:m.group(1)+str(x.steps).encode()+m.group(2),original,count=1)
   assert expected!=original and actual==expected,('only allowed token replacement accepted',rel)
   changed.append(rel)
  if x.mode=='case': assert not changed and x.nodes==1 and x.steps==40
  else:
   expected_changed=set()
   if n!=128: expected_changed.add('system/include/caseDefinition')
   if x.steps!=40: expected_changed.add('system/controlDict')
   assert set(changed)==expected_changed,changed
  cdef=(case/'system/include/caseDefinition').read_text(); ctrl=(case/'system/controlDict').read_text(); assert re.search(r'(?m)^\s*nCores\s+%d\s*;'%n,cdef); assert re.search(r'(?m)^\s*decompositionMethod\s+scotch\s*;',cdef); assert re.search(r'(?m)^\s*endTime\s+%d\s*;'%x.steps,ctrl)
  out={'passed':True,'file_count':len(got),'nodes':x.nodes,'ranks':n,'steps':x.steps,'method':'scotch','changed_files':changed,'canonical_immutable':True}
 print(json.dumps(out,indent=2))
if __name__=='__main__': main()
