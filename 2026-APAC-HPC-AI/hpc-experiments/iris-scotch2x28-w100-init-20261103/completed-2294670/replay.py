from pathlib import Path
import fcntl,hashlib,json,math,re,sys,datetime
E=Path(__file__).resolve().parents[1];B=E.parent;out=E/'completed-2294670';sys.path.insert(0,str(E))
from interface_graph import graph,compare
from init import expected_config
c=json.loads((out/'collection.json').read_text());assert c['scheduler']['State']=='COMPLETED' and c['scheduler']['ExitCode']=='0:0' and c['scheduler']['AllocCPUS']=='56';R=out/'collected';run=R/'runs/2294670'
for rel,meta in c['files'].items():
 raw=(R/rel).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256']
control=graph(R/'control','accepted-default-scotch');candidate=graph(R/'candidate','candidate-scotch-2x28-weight-1x0.01');saved=json.loads((run/'interface-graph-review.json').read_text());assert compare(control,candidate)==saved
accepted=json.loads((E/'accepted-control-manifest.json').read_text());assert all(accepted['files'][k]==v for k,v in control['boundary_file_sha256'].items())
for case,g in [('control',control),('candidate',candidate)]:
 log=(R/case/'logFiles/decomposePar.log').read_text();assert re.search(r'^End\s*$',log,re.M) and 'scalar=64' in log and 'version=v2512' in log
 total=re.search(r'^Number of processor faces = (\d+)',log,re.M);assert total and int(total[1])==g['unique_interface_faces']
 assert not re.search(r'FOAM FATAL|MPI_ABORT|FATAL ERROR',log,re.I)
for rel in json.loads((E/'source-pins.json').read_text())['files']:
 if rel.startswith('system/'):
  expected=expected_config(rel) if rel in ['system/include/caseDefinition','system/decomposeParDict'] else (E/'payload-case'/rel).read_bytes();assert (R/'candidate'/rel).read_bytes()==expected
for label in ['serial-mesh-check','native-decomposePar','native-restore0Dir','native-cut-validator']:assert json.loads((run/(label+'.status.json')).read_text())['returncode']==0
assert json.loads((run/'candidate-input-check.json').read_text())['passed'];mesh=json.loads((run/'mesh-check.json').read_text());assert mesh['passed'] and mesh['members']==json.loads((E/'expected-mesh.json').read_text())['unpacked_members_match_archive']
cut=json.loads((run/'native-cut.json').read_text());assert cut['passed'] and cut['mesh_cells']==65334765 and cut['restored_zero_fields']==336
terminal=json.loads((run/'terminal-screen.json').read_text());assert terminal['state']=='GRAPH_FILTER_REJECTED_NO_READY_NO_INITIALIZATION' and not c['candidate_READY_present'] and not saved['promote_to_mandatory_initialization']
assert not any((run/('native-'+stage+'.log')).exists() for stage in ['renumberMesh','potentialFoam','applyBoundaryLayer'])
review={'passed':True,'job_id':'2294670','scheduler':c['scheduler'],'transfer_files':len(c['files']),'all_transfer_hashes_verified':True,'native_cut_offline_replay_passed':True,'original_mesh_members':8,'cells':65334765,'ranks':56,'native_restored_field_presence_validated_on_compute':336,'binary_processor_fields_retained':False,'boundary_files_replayed':112,'accepted_control_hashes_verified':56,'graph':saved,'initialized':False,'READY':False,'solver_measured':False,'scope':'Completed native cut/restore and graph rejection; not a completed solver benchmark or speedup.','limits':['Synthetic 100:1 costs; logical rank//28 face counts, not measured traffic/latency/bandwidth.','Binary processor fields and mesh are not retained; runtime validation confirms field presence, not offline full-field byte recovery.','Hardware telemetry not collected beyond job hardware record and GNU-time stage resources.']};(out/'REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({"passed":True,"job_id":"2294670","graph_changes":saved["changes"],"read_only_ledger":True}))
