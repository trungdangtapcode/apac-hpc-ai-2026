"""Replay all per-rank proof files and exact diagnostic source identities."""
from pathlib import Path
import hashlib,json,sys
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E));from read_rank_proofs import validate_proof_dir
O=E/'completed-2294996';c=json.loads((O/'collection.json').read_text());D=O/'collected';R=D/'runs/2294996'
assert c['terminal_row']==['2294996','COMPLETED','0:0','2','56','iris001']
for name,m in c['files'].items():
 b=(D/name).read_bytes();assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256'],name
m=json.loads((R/'metadata.json').read_text());expected=json.loads((E/'deployment.json').read_text())['files'];assert m['source_hashes_before']==m['source_hashes_after']==c['frozen_hashes']==expected
assert m['all_four_probes_passed'] and not m['solver_invoked'] and not m['stdout_proof_parsing'];assert len(m['modes'])==4
maps=[]
for mode,n in [('M56-socket-core',56),('M48-default',48),('M48-default-repeat',48),('M56-socket-core-repeat',56)]:
 p=validate_proof_dir(R/'proofs'/mode,n);saved=json.loads((R/(mode+'.proof-validation.json')).read_text());assert p==saved
 launch=next(x for x in m['modes'] if x['mode']==mode);assert launch['returncode']==0 and launch['elapsed_seconds']<=30
 maps.append({x['rank']:x['affinity_cpu_ids'] for x in p['proofs']})
assert maps[0]==maps[3] and maps[1]==maps[2]
parent=json.loads((E.parent/'iris-best-recipes40-20261105/completed-2294920/collected/runs/2294920/runtime-before.json').read_text());assert m['mpirun_binary_sha256']==parent['tools']['mpirun']['sha256']
r={'passed':True,'job_id':'2294996','terminal_state':'COMPLETED','exit_code':'0:0','elapsed_seconds':2,'allocated_CPUs':56,'actual_allocated_CPU_hours':2*56/3600,'verified_files':len(c['files']),'all_four_file_probes_passed':True,'mode_order':m['mode_order'],'proof_records_total':208,'same_flags_repeat_affinity_maps_equal':True,'payload_sources_before_after_match':True,'same_mp_run_binary_as_native_parent':True,'protocol_sha256':{n:expected[n] for n in ['probe_writer.py','read_rank_proofs.py']},'limits':['MPI launcher proof transport qualification only; no solver, mesh, speed score or GPU','OS affinity measured before MPI_Init; not solver-thread runtime or page residency','New native bundle must retain the exact qualified protocol bytes and normal native/source/force gates']}
(O/'REVIEW.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
