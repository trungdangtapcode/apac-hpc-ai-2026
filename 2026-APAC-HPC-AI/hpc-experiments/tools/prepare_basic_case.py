"""Prepare only permitted Basic text settings from the recovered pinned case.

No mesh, solver execution, allocation or account-specific job script is created.
"""
import argparse,hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'case-recovery-20261021/case'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--platform',choices=['gadi','aspire2a'],required=True)
parser.add_argument('--nodes',type=int,choices=[1,2,4],required=True)
parser.add_argument('--method',choices=['hierarchical','scotch'],required=True)
parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args();out=a.output.resolve()
assert not out.exists(),'Refuse to overwrite an existing case'
manifest=json.loads((SOURCE.parent/'manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in manifest['files']:assert sha(SOURCE/row['path'])==row['sha256'],'Frozen source changed'
cores=104 if a.platform=='gadi' else 128
ranks=cores*a.nodes;steps={1:40,2:80,4:150}[a.nodes]
factors={'gadi':{1:[13,4,2],2:[13,8,2],4:[13,8,4]},'aspire2a':{1:[16,4,2],2:[16,8,2],4:[16,8,4]}}[a.platform][a.nodes]
shutil.copytree(SOURCE,out)
def set_entry(path,key,value):
    text=path.read_text()
    text,count=re.subn(r'(?m)^(\s*'+re.escape(key)+r'\s+)[^;]+;',lambda m:m[1]+value+';',text)
    assert count==1,'Ambiguous/missing entry '+key
    path.write_text(text)
case=out/'system/include/caseDefinition'
set_entry(case,'nCores',str(ranks));set_entry(case,'decompositionMethod',a.method)
if a.method=='hierarchical':set_entry(case,'nHierarchical','('+ ' '.join(map(str,factors))+')')
set_entry(out/'system/controlDict.noWrite','endTime',str(steps))
shutil.copyfile(out/'system/controlDict.noWrite',out/'system/controlDict')
shutil.copyfile(out/'system/fvSolution.fixedIter',out/'system/fvSolution')
changed=[]
for row in manifest['files']:
    if sha(out/row['path'])!=row['sha256']:changed.append(row['path'])
assert set(changed)<= {'system/include/caseDefinition','system/controlDict.noWrite','system/controlDict'}
assert sha(out/'Allrun')==sha(SOURCE/'Allrun')
assert sha(out/'system/fvSolution')==sha(SOURCE/'system/fvSolution.fixedIter')
result=dict(platform=a.platform,nodes=a.nodes,mpi_ranks=ranks,method=a.method,endTime=steps,
            hierarchical_factors=factors if a.method=='hierarchical' else None,
            source_revision=manifest['revision'],changed_text_files=changed,
            immutable_input_hashes={r['path']:sha(out/r['path']) for r in manifest['files'] if r['path'] not in changed},
            mesh_included=False,solver_executed=False,job_submitted=False,
            caution='Allrun is preserved source, including its generic arm partition header. Do not sbatch it unchanged; create a correct site job, load v2512 and use bash Allrun or the complete split chain.')
(out/'PREPARATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='immutable_input_hashes'},indent=2))
