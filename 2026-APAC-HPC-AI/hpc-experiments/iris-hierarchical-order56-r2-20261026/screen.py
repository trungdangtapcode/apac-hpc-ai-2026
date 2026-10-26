"""Produce a fresh control and three native hierarchical cuts; no initialization or solver score."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time
KIT=Path(__file__).resolve().parent;WORK=KIT.parent
MESH=Path('/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/occDrivAer/polyMesh')
RUN=None
DEADLINE=time.monotonic()+2160

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(2*1024*1024),b''):
   assert time.monotonic()<DEADLINE,'internal deadline while hashing'
   h.update(chunk)
 return h.hexdigest()

def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def kit_check():
 files=json.loads((KIT/'payload-sha256.json').read_text())['files']
 assert all((KIT/n).is_file() and not(KIT/n).is_symlink() and digest(KIT/n)==v for n,v in files.items())
 return {'passed':True,'files':len(files)}
def mesh_check():
 checks=[]
 for expected in json.loads((KIT/'expected-mesh.json').read_text())['unpacked_members_match_archive']:
  p=MESH/expected['file'];assert p.is_file()
  got={'file':expected['file'],'bytes':p.stat().st_size,'sha256':digest(p)};assert got==expected,got['file'];checks.append(got)
 assert len(checks)==8
 return {'passed':True,'members':checks}

def native_summary(case,order):
 log=(case/'logs/decomposePar.log').read_text(errors='replace')
 assert 'OPENFOAM=2512' in log and 'scalar=64' in log and re.search(r'(?m)^End\s*$',log)
 assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal',log,re.I)
 cells=[int(x) for x in re.findall(r'(?m)^[ \t]+Number of cells\s*=\s*(\d+)\s*$',log)]
 faces=[int(x) for x in re.findall(r'(?m)^[ \t]+Number of processor faces\s*=\s*(\d+)\s*$',log)]
 unique=int(re.search(r'(?m)^Number of processor faces = (\d+)',log)[1]);neighbors=int(re.search(r'(?m)^Max number of processor patches = (\d+)',log)[1])
 assert len(cells)==len(faces)==56 and sum(cells)==65334765 and sum(faces)==2*unique
 assert {p.name for p in case.glob('processor*') if p.is_dir()}=={'processor'+str(i) for i in range(56)}
 assert all((case/('processor'+str(i))/'constant/polyMesh/boundary').is_file() for i in range(56))
 assert re.search(r'(?m)^\s*order\s+'+order+r'\s*;', (case/'system/decomposeParDict').read_text())
 assert all(not(case/('processor'+str(i))).is_symlink() and all((case/('processor'+str(i))/'0'/field).is_file() for field in ['U','p','k','omega','nut','nuTilda']) for i in range(56))
 return {'passed':True,'order':order,'method':'hierarchical','factors':[7,4,2],'ranks':56,'mesh_cells':sum(cells),'cells_by_rank':cells,'unique_interface_faces':unique,'maximum_interface_faces_per_rank':max(faces),'maximum_neighbor_patches':neighbors,'maximum_cells_above_mean_percent':100*(max(cells)/(sum(cells)/56)-1),'restored_initial_fields':336,'initialization_complete':False,'solver_result':None}

def execute(case,label,args,cap):
 remaining=int(DEADLINE-time.monotonic())-30;assert remaining>0,'deadline before '+label
 seconds=min(cap,remaining);logs=case/'logs';start=time.monotonic()
 command=['/usr/bin/time','-v','-o',str(logs/(label+'.resource.txt')),'timeout','--signal=TERM','--kill-after=10s',str(seconds)+'s',*args]
 with (logs/(label+'.log')).open('w') as out:
  p=subprocess.run(command,cwd=str(case),stdout=out,stderr=subprocess.STDOUT,timeout=seconds+20)
 save(logs/(label+'.status.json'),{'returncode':p.returncode,'elapsed_seconds':time.monotonic()-start,'cap_seconds':seconds})
 assert p.returncode==0,(label,p.returncode)

def render_inputs(case,order):
 assert order in ['xyz','xzy','yxz','zyx']
 p=case/'system/include/caseDefinition';text=p.read_text()
 text,n=re.subn(r'(?m)^nCores .*$', 'nCores              56;',text);assert n==1
 text,n=re.subn(r'(?m)^nHierarchical .*$', 'nHierarchical       (7 4 2);',text);assert n==1;p.write_text(text)
 p=case/'system/decomposeParDict';text,n=re.subn(r'(?m)^([ \t]+order[ \t]+)xyz;',r'\g<1>'+order+';',p.read_text());assert n==1;p.write_text(text)

def arm(order):
 case=WORK/'cases'/('order-'+order);case.parent.mkdir(parents=True,exist_ok=True);assert not case.exists()
 shutil.copytree(KIT/'payload-case',case);(case/'Allrun').unlink();(case/'logs').mkdir()
 render_inputs(case,order)
 assert not(case/'constant/polyMesh').exists();(case/'constant/polyMesh').symlink_to(MESH)
 for relative in [p.relative_to(KIT/'payload-case') for p in (KIT/'payload-case').rglob('*') if p.is_file()]:
  if str(relative) in ['Allrun','system/include/caseDefinition','system/decomposeParDict']:continue
  assert digest(case/relative)==digest(KIT/'payload-case'/relative),str(relative)
 save(case/'changes.json',{'order':order,'nCores':56,'factors':[7,4,2],'method':'hierarchical','allowed_source_edits':['nCores','nHierarchical','hierarchicalCoeffs/order'],'all_other_input_bytes_match':True})
 execute(case,'decomposePar',['decomposePar','-constant'],500)
 execute(case,'restore0Dir',['bash','-ec','. "$WM_PROJECT_DIR/bin/tools/RunFunctions"; restore0Dir -processor'],90)
 result=native_summary(case,order);save(RUN/('order-'+order+'.json'),result);return result

if __name__=='__main__':
 RUN=WORK/'runs'/os.environ['SLURM_JOB_ID'];RUN.mkdir(parents=True,exist_ok=False)
 save(RUN/'source-before.json',kit_check());save(RUN/'mesh-before.json',mesh_check())
 available={line.split(':',1)[0]:int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')}.get('MemAvailable')
 workers=3 if available is not None and available>=128*1024**2 else 1
 save(RUN/'memory-admission.json',{'MemAvailable_KiB':available,'parallel_workers':workers,'minimum_parallel_available_GiB':128,'prior_serial_decomposition_peak_KiB':33323056,'scope':'Unranked native cuts; concurrent cut durations are not a solver performance comparison.'})
 results=[]
 with ThreadPoolExecutor(max_workers=workers) as pool:
  futures={pool.submit(arm,o):o for o in ['xyz','xzy','yxz','zyx']}
  for future in as_completed(futures):
   order=futures[future]
   try:result=future.result()
   except Exception as error:result={'passed':False,'order':order,'error_type':type(error).__name__,'error':str(error)}
   results.append(result);save(RUN/'results.json',{'arms':results,'all_complete':len(results)==4})
 save(RUN/'mesh-after.json',mesh_check());save(RUN/'source-after.json',kit_check())
 assert len(results)==4 and all(r['passed'] for r in results),results
 print('FOUR_HIERARCHICAL_ORDER_CUTS_PASS')
