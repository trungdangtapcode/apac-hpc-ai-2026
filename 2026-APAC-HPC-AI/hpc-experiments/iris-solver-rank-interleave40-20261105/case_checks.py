from pathlib import Path
import json,re
import native_checks as checks
KIT=Path(__file__).resolve().parent
def source_check(case,order):
 pins=json.loads((KIT/'source-pins.json').read_text())['files'];assert len(pins)==41
 for name,digest in pins.items():
  original=KIT/'payload-case'/name;assert checks.sha256(original)==digest
  target=case/name
  if name=='Allrun':assert not target.exists() and not target.is_symlink();continue
  expected=original.read_bytes()
  if name=='system/include/caseDefinition':
   text=expected.decode();text,n=re.subn(r'(?m)^nCores .*$', 'nCores              56;',text);assert n==1
   text,n=re.subn(r'(?m)^nHierarchical .*$', 'nHierarchical       (7 4 2);',text);assert n==1;expected=text.encode()
  elif name=='system/decomposeParDict':
   text,n=re.subn(r'(?m)^([ \t]+order[ \t]+)xyz;',r'\g<1>'+order+';',expected.decode());assert n==1;expected=text.encode()
  assert target.is_file() and not target.is_symlink() and target.read_bytes()==expected,name
 return {'passed':True,'pinned_input_files':41,'order':order,'factors':[7,4,2]}
