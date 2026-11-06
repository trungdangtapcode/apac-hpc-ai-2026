from pathlib import Path
import json,sys
E=Path('/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch40-init-20261106');sys.path.insert(0,str(E.parent/'tools'));from iris_bridge import run_json
intent=json.loads((E/'deployment-intent.json').read_text());body='ROOT='+repr(intent['root'])+'\nEXPECTED='+repr(intent['files'])+r'''
from pathlib import Path
import hashlib,datetime,json
r=Path(ROOT);k=r/'init-kit';a=r/'artifacts/cut-N40-scotch'
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':ROOT,'kit_exists':k.exists(),'artifact_exists':a.exists(),'ready':(a/'READY').exists(),'in_progress':(a/'.INIT_IN_PROGRESS').exists(),'existing_files':sorted(str(p.relative_to(k)) for p in k.rglob('*') if p.is_file()) if k.exists() else []}
result['matching_files']={n:hashlib.sha256((k/n).read_bytes()).hexdigest()==v for n,v in EXPECTED.items() if (k/n).is_file()}
result['submission_intent_exists']=(r/'init-submission-intent.json').exists()
'''
d=run_json(body,timeout=45);(E/'deployment-reconciliation.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
if d['kit_exists'] and len(d['matching_files'])==len(intent['files']) and all(d['matching_files'].values()):
 assert not d['submission_intent_exists'] and not d['ready'] and not d['in_progress']
 result={'root':intent['root'],'kit':intent['root']+'/init-kit','files':intent['files'],'state':'DEPLOYED_NOT_SUBMITTED','reconciled_after_transport_timeout':True}
 with (E/'deployment.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
