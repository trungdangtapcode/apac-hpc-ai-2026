#!/usr/bin/env python3
"""Refresh prepared S106 derivation and pin metadata; never run after submission."""
from pathlib import Path
import datetime,hashlib,json
D=Path(__file__).resolve().parent;Q=D.parent
B=Q/'serving-tuning-11/s106-h200-prefill-cpp-cache'
P=Q/'runs/27376/submitted-payload'
assert not (D/'submission-receipt.json').exists(),'Never mutate an admitted payload'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
changed=[];unchanged=[]
parent_files={p.relative_to(P).as_posix():p for p in P.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS'}
for rel,p in sorted(parent_files.items()):
    t=B/rel
    assert t.is_file() and not t.is_symlink(),rel
    if sha(p)==sha(t):unchanged.append(rel)
    else:changed.append({'path':rel,'state':'changed','parent_sha256':sha(p),'candidate_sha256':sha(t)})
new=sorted(p.relative_to(B).as_posix() for p in B.rglob('*') if p.is_file()
           and '__pycache__' not in p.parts and p.name not in ('SHA256SUMS','DERIVATION_REVIEW.json')
           and p.relative_to(B).as_posix() not in parent_files)
out={'parent_payload':'runs/27376/submitted-payload','parent_job':27376,
     'changed_parent_files':changed,'unchanged_parent_file_count':len(unchanged),
     'unchanged_parent_files':unchanged,'unchanged_parent_files_sha256_checked':True,
     'new_files':new,'single_runtime_treatment':'P-only SGLANG_EXPERIMENTAL_CPP_RADIX_TREE=1; no other serving option changed',
     'note':'Current hashes refreshed after root guard/import fixes and replacement of the misleading inherited PLAN. Candidate SHA256SUMS and this derivation report are excluded from the parent comparison to avoid recursive hashing. Original ancestor derive.py remains historical, not an S106 generator.'}
(B/'DERIVATION_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
files=sorted(p for p in B.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts)
(B/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(B).as_posix()}\n' for p in files))
root=json.loads((D/'ROOT_REVIEW.json').read_text())
root['manifest_sha256']=sha(B/'SHA256SUMS')
root['documentation_and_provenance_correction']='Replaced inherited stale PLAN and refreshed changed-file hashes after pre-admission guard fixes. Historical ancestor script explicitly labelled.'
root['reviewed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(D/'ROOT_REVIEW.json').write_text(json.dumps(root,indent=2)+'\n')
print(json.dumps({'changed_parent_files':[r['path'] for r in changed],'unchanged_parent_files':len(unchanged),'manifest_sha256':sha(B/'SHA256SUMS')}))
