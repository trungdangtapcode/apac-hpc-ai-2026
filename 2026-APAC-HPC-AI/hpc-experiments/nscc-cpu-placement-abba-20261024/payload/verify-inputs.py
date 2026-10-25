"""Verify frozen source bytes, permitted case derivation, and known shared mesh."""
from pathlib import Path
import argparse, hashlib, json, re, sys

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 return h.hexdigest()
def verify_bundle(root):
 root=Path(root); base=root/'payload'; manifest=json.loads((root/'payload-sha256.json').read_text())['files']
 actual={str(p.relative_to(root)) for p in base.rglob('*') if p.is_file()}
 assert actual==set(manifest),(sorted(actual-set(manifest)),sorted(set(manifest)-actual))
 bad={n:(sha(root/n),h) for n,h in manifest.items() if sha(root/n)!=h}
 assert not bad,bad
 return {'passed':True,'entries':len(manifest),'payload_sha256':'all_match'}
def verify_case(root, casepath, check_derived=True):
 root=Path(root); case=Path(casepath); accepted=json.loads((root/'payload/accepted-source-manifest.json').read_text())
 allowed=set(accepted['allowed_delta_files'])
 expected=set(accepted['files']); actual={str(p.relative_to(case)) for p in case.rglob('*') if p.is_file() and not p.is_symlink()}
 if check_derived:
  assert actual==expected,(sorted(actual-expected),sorted(expected-actual))
  for rel,h in accepted['files'].items():
   if rel not in allowed: assert sha(case/rel)==h,(rel,sha(case/rel),h)
  cdef=(case/'system/include/caseDefinition').read_text(); ctrl=(case/'system/controlDict').read_text()
  assert re.search(r'(?m)^\s*nCores\s+512\s*;',cdef)
  assert re.search(r'(?m)^\s*decompositionMethod\s+scotch\s*;',cdef)
  assert re.search(r'(?m)^\s*endTime\s+150\s*;',ctrl)
 return {'passed':True,'file_count':len(actual),'allowed_delta_files':sorted(allowed),'ranks':512,'method':'scotch','endTime':150}
def verify_against_source(root, source):
 root=Path(root); source=Path(source); case=root/'payload/case'
 accepted=json.loads((root/'payload/accepted-source-manifest.json').read_text())
 original={str(p.relative_to(source)):p for p in source.rglob('*') if p.is_file()}
 current={str(p.relative_to(case)):p for p in case.rglob('*') if p.is_file()}
 assert set(original)==set(current)==set(accepted['files'])
 changed=[]
 for rel,src in original.items():
  before=src.read_bytes(); after=current[rel].read_bytes()
  assert hashlib.sha256(before).hexdigest()==accepted['files'][rel],('canonical source hash mismatch',rel)
  if before==after: continue
  changed.append(rel)
  if rel=='system/include/caseDefinition':
   a=re.sub(rb'(?m)^(\s*nCores\s+)128(\s*;)',rb'\g<1>512\g<2>',before)
   assert a==after,rel
  elif rel=='system/controlDict':
   a=re.sub(rb'(?m)^(\s*endTime\s+)40(\s*;)',rb'\g<1>150\g<2>',before)
   assert a==after,rel
  else: raise AssertionError('Unexpected source edit: '+rel)
 assert set(changed)==set(accepted['allowed_delta_files']),changed
 return {'passed':True,'canonical_source':str(source),'changed_files':changed,'only_authorized_edits':True}
def verify_mesh(root, meshpath):
 root=Path(root); mesh=Path(meshpath); prior=json.loads((root/'payload/mesh-identity.json').read_text())
 assert prior['archive_md5']=='50393a15d84f53255fda85ac702390e9'
 assert prior['archive_sha256']=='ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376'
 expected={x['file']:x for x in prior['unpacked_members_match_archive']}
 assert len(expected)==8
 found=[]
 for rel,item in expected.items():
  p=mesh/rel; assert p.is_file() and p.stat().st_size==item['bytes'],(str(p),item)
  actual=sha(p); assert actual==item['sha256'],(rel,actual,item['sha256'])
  found.append({'file':rel,'bytes':item['bytes'],'sha256':actual})
 return {'passed':True,'recorded_archive_md5':prior['archive_md5'],'recorded_archive_sha256':prior['archive_sha256'],'mesh_directory':str(mesh),'member_count_checked':len(found),'members':found,'scope':'Compares reused unpacked files with the prior CPU preparation manifest; does not re-read or download the large archive.'}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1])); ap.add_argument('--mode',choices=['bundle','case','mesh','all'],default='all'); ap.add_argument('--case'); ap.add_argument('--mesh',default='/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc/shared/polyMesh'); ap.add_argument('--source-case'); a=ap.parse_args(); out={}
 if a.mode in ('bundle','all'): out['bundle']=verify_bundle(a.root)
 if a.mode in ('case','all'):
  cp=a.case or str(Path(a.root)/'payload/case'); out['case']=verify_case(a.root,cp)
 if a.source_case: out['canonical_source_comparison']=verify_against_source(a.root,a.source_case)
 if a.mode in ('mesh','all'): out['mesh']=verify_mesh(a.root,a.mesh)
 print(json.dumps(out,indent=2))
if __name__=='__main__': main()
