"""Verify frozen native-wave source and narrowly authorized decomposition variants."""
from pathlib import Path
import argparse, hashlib, json, re

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def verify_bundle(root):
 root=Path(root); manifest=json.loads((root/'payload-sha256.json').read_text())['files']
 files={str(p.relative_to(root)) for p in (root/'payload').rglob('*') if p.is_file()}
 assert files==set(manifest),(sorted(files-set(manifest)),sorted(set(manifest)-files))
 bad={n:(sha(root/n),h) for n,h in manifest.items() if sha(root/n)!=h}
 assert not bad,bad
 return {'passed':True,'entries':len(files),'payload_sha256':'all_match'}

def verify_mesh(root, mesh):
 prior=json.loads((Path(root)/'payload/mesh-identity.json').read_text())
 assert prior['archive_md5']=='50393a15d84f53255fda85ac702390e9'
 assert prior['archive_sha256']=='ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376'
 expected={x['file']:x for x in prior['unpacked_members_match_archive']}; assert len(expected)==8
 found=[]
 for rel,item in expected.items():
  p=Path(mesh)/rel; assert p.is_file() and p.stat().st_size==item['bytes'],(str(p),item)
  actual=sha(p); assert actual==item['sha256'],(rel,actual,item['sha256']); found.append({'file':rel,'bytes':item['bytes'],'sha256':actual})
 return {'passed':True,'mesh_directory':str(mesh),'member_count_checked':len(found),'members':found}

def verify_against_canonical(root, source, case, method):
 root=Path(root); source=Path(source); case=Path(case)
 accepted=json.loads((root/'payload/accepted-source-manifest.json').read_text())
 original={str(p.relative_to(source)):p for p in source.rglob('*') if p.is_file()}
 current={str(p.relative_to(case)):p for p in case.rglob('*') if p.is_file() and not p.is_symlink()}
 assert set(original)==set(current)==set(accepted['files'])
 changed=[]
 for rel,src in original.items():
  before=src.read_bytes(); after=current[rel].read_bytes()
  assert hashlib.sha256(before).hexdigest()==accepted['files'][rel],('canonical source hash mismatch',rel)
  if before==after: continue
  changed.append(rel)
  if rel=='system/include/caseDefinition':
   expected,n=re.subn(rb'(?m)^(\s*nCores\s+)128(\s*;)',rb'\g<1>512\g<2>',before); assert n==1
   if method!='S0':
    expected,n=re.subn(rb'(?m)^(\s*decompositionMethod\s+)scotch(\s*;)',rb'\g<1>hierarchical\g<2>',expected); assert n==1
    expected,n=re.subn(rb'(?m)^(\s*nHierarchical\s+)\(16 4 2\)(\s*;)',rb'\g<1>(16 8 4)\g<2>',expected); assert n==1
   assert after==expected,rel
  elif rel=='system/controlDict':
   expected,n=re.subn(rb'(?m)^(\s*endTime\s+)40(\s*;)',rb'\g<1>150\g<2>',before); assert n==1 and after==expected,rel
  elif rel=='system/decomposeParDict' and method=='Hzyx':
   expected,n=re.subn(rb'(?m)^(\s*order\s+)xyz(\s*;)',rb'\g<1>zyx\g<2>',before); assert n==1 and after==expected,rel
  else: raise AssertionError('Unexpected source edit: '+rel)
 allowed={'system/include/caseDefinition','system/controlDict'}
 if method=='Hzyx': allowed.add('system/decomposeParDict')
 assert set(changed)==allowed,changed
 return {'passed':True,'method':method,'canonical_source':str(source),'changed_files':changed,'only_authorized_edits':True}

def transform(template, method):
 b=Path(template).read_bytes()
 def sub(pattern,repl,buf, count=1):
  out,n=re.subn(pattern,repl,buf,count=count,flags=re.M); assert n==count,(pattern,n); return out
 if method=='S0':
  return b
 order={'Hxyz':'xyz','Hzyx':'zyx'}[method]
 b=sub(rb'^(decompositionMethod\s+)scotch(\s*;)',rb'\g<1>hierarchical\g<2>',b)
 b=sub(rb'^(nHierarchical\s+)\([^)]*\)(\s*;)',rb'\g<1>(16 8 4)\g<2>',b)
 return b

def verify_case(case, method, template=None, allow_run_output=False):
 case=Path(case)
 cdef=case/'system/include/caseDefinition'; ctrl=case/'system/controlDict'; dpd=case/'system/decomposeParDict'
 txt=cdef.read_text(); ct=ctrl.read_text(); dt=dpd.read_text()
 assert re.search(r'(?m)^\s*nCores\s+512\s*;',txt)
 assert re.search(r'(?m)^\s*endTime\s+150\s*;',ct)
 assert re.search(r'(?m)^\s*numberOfSubdomains\s+\$nCores\s*;',dt)
 want='scotch' if method=='S0' else 'hierarchical'
 assert re.search(r'(?m)^\s*decompositionMethod\s+'+want+r'\s*;',txt)
 if method!='S0':
  assert re.search(r'(?m)^\s*nHierarchical\s+\(16 8 4\)\s*;',txt)
  assert re.search(r'(?m)^\s*order\s+'+('xyz' if method=='Hxyz' else 'zyx')+r'\s*;',dt)
 if template:
  template=Path(template)
  expected={str(p.relative_to(template)) for p in template.rglob('*') if p.is_file()}
  actual={str(p.relative_to(case)) for p in case.rglob('*') if p.is_file() and not p.is_symlink()}
  extras=actual-expected
  if allow_run_output:
   generated=lambda rel: bool(re.fullmatch(r'processor\d+',rel.split('/',1)[0])) or rel.split('/',1)[0] in {'logFiles','postProcessing','dynamicCode'} or bool(re.fullmatch(r'\d+(?:\.\d+)?',rel.split('/',1)[0]))
   assert all(generated(rel) for rel in extras),sorted(extras)
   assert expected<=actual,sorted(expected-actual)
  else: assert actual==expected,(sorted(actual-expected),sorted(expected-actual))
  changed=[]
  for rel in sorted(expected):
   before=(template/rel).read_bytes(); after=(case/rel).read_bytes()
   if before==after: continue
   changed.append(rel)
   if rel=='system/include/caseDefinition':
    expected_bytes=before
    if method!='S0':
     expected_bytes=re.sub(rb'(?m)^(decompositionMethod\s+)scotch(\s*;)',rb'\g<1>hierarchical\g<2>',expected_bytes)
     expected_bytes=re.sub(rb'(?m)^(nHierarchical\s+)\([^)]*\)(\s*;)',rb'\g<1>(16 8 4)\g<2>',expected_bytes)
    assert after==expected_bytes,(rel,'unexpected caseDefinition edit')
   elif rel=='system/decomposeParDict':
    expected_bytes=before if method=='S0' else re.sub(rb'(?m)^(\s*order\s+)xyz(\s*;)',rb'\g<1>'+('xyz' if method=='Hxyz' else 'zyx').encode()+rb'\g<2>',before)
    assert after==expected_bytes,(rel,'unexpected decomposeParDict edit')
   else: raise AssertionError('Unexpected source edit: '+rel)
  if method=='S0': assert not changed,changed
  elif method=='Hxyz': assert set(changed)=={'system/include/caseDefinition'},changed
  else: assert set(changed)=={'system/include/caseDefinition','system/decomposeParDict'},changed
 return {'passed':True,'method':method,'ranks':512,'endTime':150}

def main():
 p=argparse.ArgumentParser(); p.add_argument('mode',choices=['bundle','case','mesh']); p.add_argument('--root',default=str(Path(__file__).resolve().parents[1])); p.add_argument('--case'); p.add_argument('--template'); p.add_argument('--source-case'); p.add_argument('--mesh',default='/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc/shared/polyMesh'); p.add_argument('--method',choices=['S0','Hxyz','Hzyx']); p.add_argument('--allow-run-output',action='store_true'); a=p.parse_args()
 if a.mode=='bundle': out=verify_bundle(a.root)
 elif a.mode=='mesh': out=verify_mesh(a.root,a.mesh)
 else:
  out=verify_case(a.case,a.method,a.template,a.allow_run_output)
  if a.source_case: out['canonical_source']=verify_against_canonical(a.root,a.source_case,a.case,a.method)
 print(json.dumps(out,indent=2))
if __name__=='__main__': main()
