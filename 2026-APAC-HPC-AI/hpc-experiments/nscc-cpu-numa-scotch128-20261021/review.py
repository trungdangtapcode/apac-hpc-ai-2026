"""Review a native NUMA partition prep and its preregistered graph filter."""
from pathlib import Path
import hashlib,json,re,statistics,datetime
r=Path(__file__).resolve().parent;job=json.loads((r/'submission.json').read_text())['stdout'].strip();d=r/'collected'/job
for f,h in json.loads((d/'evidence-sha256.json').read_text()).items():assert hashlib.sha256((d/f).read_bytes()).hexdigest()==h
j=json.loads((r/'terminal-accounting.json').read_text())['jobs'][job];assert j['job_state']=='F' and j['Exit_status']==0
assert j['Resource_List']['ncpus']==32 and j['Resource_List']['ngpus']==0
for f,h in json.loads((r/'payload-sha256.json').read_text()).items():assert hashlib.sha256((d/f).read_bytes()).hexdigest()==h,f
mesh=json.loads((d/'mesh-identity.json').read_text());assert mesh['archive_md5']=='50393a15d84f53255fda85ac702390e9' and mesh['archive_sha256']=='ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376' and len(mesh['unpacked_members_match_archive'])==8
assert (d/'iris-control-semantic.PASS').read_text().strip()=='PASS' and not (d/'iris-control-semantic.diff').read_text()
a=d/'artifacts/scotch-N128-numa8x16';ready=json.loads((a/'CUT_READY.json').read_text());assert ready['ranks']==128 and ready['method']=='scotch' and ready['total_cells']==65334765 and ready['domains']==[8,16] and ready['domainWeights']==[1,0.1]
t=(a/'logFiles/decomposePar.log').read_text();assert re.search(r'^End\s*$',t,re.M) and 'FOAM FATAL' not in t and 'OPENFOAM=2512' in t and 'scalar=64' in t and 'scotch [128]' in t and '_87ed40d256' in t
cells=[int(v) for v in re.findall(r'^    Number of cells\s*=\s*(\d+)',t,re.M)];faces=[int(v) for v in re.findall(r'^    Number of processor faces\s*=\s*(\d+)',t,re.M)];neighbors=[int(v) for v in re.findall(r'^    Number of processor patches\s*=\s*(\d+)',t,re.M)];assert len(cells)==len(faces)==len(neighbors)==128 and sum(cells)==65334765
for p in (a/'system').rglob('*'):
 if p.is_file():assert p.read_bytes()==(r/'payload/case/system'/p.relative_to(a/'system')).read_bytes()
assert 'Restore 0/' in (a/'logFiles/restore0Dir.log').read_text() and 'CPU_N128_CUT_PASS' in (d/('tu-cpu-numa128.o'+job.split('.')[0])).read_text()
graph=json.loads((d/'interface-summary.json').read_text());g=graph['numa_scotch'];control=graph['default_scotch'];assert g['unique_interface_faces']==sum(faces)//2 and g['max_rank_interface_faces']==max(faces) and g['max_rank_processor_patches']==max(neighbors)
assert control['unique_interface_faces']==1549377 and graph['hierarchical']['unique_interface_faces']==2109346
for label in ['hierarchical','default_scotch','numa_scotch']:
 detail=json.loads((d/('graph-'+label+'.json')).read_text());assert len(detail['boundary_sha256'])==128
 assert sum(e['faces'] for e in detail['edges'])==graph[label]['unique_interface_faces']
 assert sum(e['faces'] for e in detail['edges'] if e['cross_group'])==graph[label]['unique_cross_group_interface_faces']
 assert all(e['cross_group']==(e['a']//16!=e['b']//16) for e in detail['edges'])
imbalance=max(cells)/statistics.mean(cells)-1
criteria=dict(cross_group_faces_reduced_at_least_10_percent=g['unique_cross_group_interface_faces']<=0.9*control['unique_cross_group_interface_faces'],weighted_10_to_1_objective_lower=g['weighted_objective_10_to_1']<control['weighted_objective_10_to_1'],max_cell_excess_at_most_3_percent=imbalance<=0.03,total_faces_at_most_15_percent_higher=g['unique_interface_faces']<=1.15*control['unique_interface_faces'],max_rank_faces_at_most_50_percent_higher=g['max_rank_interface_faces']<=1.5*control['max_rank_interface_faces'])
h,m,sec=map(int,j['resources_used']['walltime'].split(':'));elapsed=h*3600+m*60+sec
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),job=job,state='NATIVE_NUMA_SCOTCH_PREPARATION_PASS',graph_filter='PROMISING_FOR_BUDGETED_SOLVER_SCREEN' if all(criteria.values()) else 'DO_NOT_PROMOTE_UNCHANGED',graph_filter_criteria=criteria,graph_filter_scope='Research triage only, not official accuracy or performance thresholds',graph=graph,max_cell_excess_fraction=imbalance,cell_min=min(cells),cell_max=max(cells),elapsed_seconds=elapsed,estimated_base_SU=elapsed*32/3600,reported_resources=j['resources_used'],native_tree_branch='Requested by validated dictionary; inferred from pinned native source and successful build-matched execution, not direct function tracing',limits='No candidate initialization or solve. Logical rank groups only; future physical grouping needs matching placement probe. No measured speedup, page locality, counters, traffic or power. Weights synthetic 10:1. Individual posted charge not reported.')
(r/'review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
