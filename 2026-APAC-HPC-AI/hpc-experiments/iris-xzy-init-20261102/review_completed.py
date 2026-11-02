"""Independently replay xzy initialization logs and source/field provenance."""
from pathlib import Path
import hashlib,json,re
import native_checks as checks
E=Path(__file__).resolve().parent;receipt=json.loads((E/'submission-receipt.json').read_text());job=receipt['stdout'].strip().split(';')[0];out=E/('completed-'+job);c=json.loads((out/'collection.json').read_text());assert c['scheduler']['State']=='COMPLETED' and c['scheduler']['ExitCode']=='0:0' and c['scheduler']['AllocCPUS']=='56'
root=out/'collected';run=root/'runs'/job
for name,meta in c['files'].items():
 raw=(root/name).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256']
for name in ['xzy-original-input.json','xzy-source-before.json','xzy-source-after.json']:
 d=json.loads((run/name).read_text());assert d['passed'] and d['pinned_input_files']==41 and d['order']=='xzy' and d['factors']==[7,4,2]
mesh=json.loads((E/'expected-mesh.json').read_text())['unpacked_members_match_archive']
for phase in ['before','after']:
 d=json.loads((run/f'mesh-{phase}.json').read_text());assert d['passed'] and d['members']==mesh
source=root/'initialized/order-xzy';snapshots=[json.loads((source/n).read_text()) for n in ['source-before.json','source-after-copy.json','source-after-init.json']];assert snapshots[0]==snapshots[1]==snapshots[2]
checks.check_probe(run,job)
stages=[]
for label,args in [('renumberMesh',['renumberMesh','-constant','-overwrite','-parallel']),('potentialFoam',['potentialFoam','-initialiseUBCs','-parallel']),('applyBoundaryLayer',['applyBoundaryLayer','-ybl','0.0450244','-parallel'])]:
 s=(run/f'xzy-{label}.log').read_text();status=json.loads((run/f'xzy-{label}.status.json').read_text());assert status['returncode']==0 and 'INIT_STAGE_RETURN_CODE=0' in s
 actual=re.search(r'^Exec\s*:\s*(.+)$',s,re.M);assert actual and [Path(actual[1].split()[0]).name,*actual[1].split()[1:]]==args
 assert 'OPENFOAM=2512' in s and 'scalar=64' in s and re.search(r'^nProcs\s*:\s*56\s*$',s,re.M) and re.search(r'^End\s*$',s,re.M) and not checks.FATAL.search(s)
 stages.append({'stage':label,'returncode':0,'elapsed_seconds':status['elapsed_seconds']})
manifest=json.loads((run/'accepted-xzy-source-manifest.json').read_text());fields=json.loads((run/'xzy-fields-after.json').read_text());assert fields['passed'] and fields['field_count']==336
for name,data in fields['fields'].items():assert manifest['files'][name]==data['sha256']
complete=json.loads((run/'xzy-complete.json').read_text());assert complete['passed'] and complete['order']=='xzy' and complete['raw_cut_preserved'] and complete['solver_result'] is None and complete['initialized_case']==receipt['root']+'/initialized/order-xzy'
ready=(source/'READY').read_bytes();assert hashlib.sha256(ready).hexdigest()==complete['READY_sha256'] and b'N=56' in ready and b'method=hierarchical' in ready
result={'passed':True,'job_id':job,'scheduler':c['scheduler'],'all_transfer_hashes_verified':True,'all_native_initialization_gates_passed':True,'canonical_input_pins':41,'serial_mesh_members':len(mesh),'initialized_field_seals':336,'accepted_manifest_files':len(manifest['files']),'accepted_manifest_sha256':hashlib.sha256((run/'accepted-xzy-source-manifest.json').read_bytes()).hexdigest(),'source_unchanged_and_copy_independent':True,'stages':stages,'initialized_source':complete['initialized_case'],'solver_measured':False,'Gadi_result':False,'limits':['Initialization only, no solver speedup or full scored result.','No hardware bandwidth/cycles, sustained frequency or solver telemetry collected.','Iris allocated CPU-hours are local planning, not billed SU.']}
(out/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
