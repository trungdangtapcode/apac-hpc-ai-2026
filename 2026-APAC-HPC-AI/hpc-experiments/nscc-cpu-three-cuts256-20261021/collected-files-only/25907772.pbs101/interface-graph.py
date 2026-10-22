"""Inspect actual processor-boundary graph on allocated compute, never time a solve."""
from pathlib import Path
import json,re,collections,hashlib,sys
root=Path.cwd()
controls=json.loads(Path('graph-inputs.json').read_text())
summary={}
for label,path in controls.items():
 case=Path(path);ready=json.loads((case/'CUT_READY.json').read_text());assert ready['ranks']==256 and ready['total_cells']==65334765
 edges=collections.Counter();patches=[];seals={}
 for rank in range(256):
  p=case/('processor'+str(rank))/'constant/polyMesh/boundary';raw=p.read_bytes();text=raw.decode();seals[str(p.relative_to(case))]=hashlib.sha256(raw).hexdigest()
  count=0
  for block in re.findall(r'\{([^{}]*)\}',text,re.S):
   if not re.search(r'\bneighbProcNo\b',block):continue
   count+=1
   def entry(name):
    m=re.search(r'\b'+name+r'\s+(\d+)\s*;',block);assert m,name;return int(m[1])
   assert re.search(r'\btype\s+processor\w*\s*;',block)
   assert entry('myProcNo')==rank
   neighbor=entry('neighbProcNo');faces=entry('nFaces');assert 0<=neighbor<256 and neighbor!=rank and faces>0
   edges[(rank,neighbor)]+=faces
  assert count==len(re.findall(r'\bneighbProcNo\b',text)),rank
  patches.append(count)
 for (a,b),faces in edges.items():assert edges[(b,a)]==faces,(a,b)
 unique=[dict(a=a,b=b,faces=n,cross_group=(a//128!=b//128)) for (a,b),n in sorted(edges.items()) if a<b]
 total=sum(x['faces'] for x in unique);cross=sum(x['faces'] for x in unique if x['cross_group']);assert total>0
 per_rank=[sum(n for (a,b),n in edges.items() if a==i) for i in range(256)]
 result=dict(label=label,case=str(case),ranks=256,grouping='logical rank//128, physical node only when a matching placement probe passes',unique_interface_faces=total,unique_cross_group_interface_faces=cross,unique_within_group_interface_faces=total-cross,max_rank_interface_faces=max(per_rank),max_rank_processor_patches=max(patches),weighted_objective_10_to_1=10*cross+(total-cross),edges=unique,boundary_sha256=seals,limitations='Face graph, not measured traffic, message time, page residency or critical path. Scalar synthetic weights are not hardware performance ratios.')
 Path('graph-'+label+'.json').write_text(json.dumps(result,indent=2)+'\n')
 summary[label]={k:v for k,v in result.items() if k not in ['edges','boundary_sha256']}
Path('interface-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
