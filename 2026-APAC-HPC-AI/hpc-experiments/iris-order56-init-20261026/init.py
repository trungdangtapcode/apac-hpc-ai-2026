"""Clone and initialize fresh xyz/zyx cuts, retaining the uninitialized sources."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
import native_checks as checks
KIT=Path(__file__).resolve().parent;WORK=KIT.parent
CUT=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-orders56-20261026T130521Z')
RUN=None
DEADLINE=time.monotonic()+2160

def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def command(label,args,cwd,cap):
 left=int(DEADLINE-time.monotonic())-30;assert left>0,'deadline before '+label
 seconds=min(left,cap);out=RUN/(label+'.log');resource=RUN/(label+'.resource.txt');start=time.monotonic()
 with out.open('w') as stream:p=subprocess.run(['/usr/bin/time','-v','-o',str(resource),'timeout','--signal=TERM','--kill-after=10s',str(seconds)+'s',*args],cwd=str(cwd),stdout=stream,stderr=subprocess.STDOUT,timeout=seconds+20)
 save(RUN/(label+'.status.json'),{'returncode':p.returncode,'elapsed_seconds':time.monotonic()-start,'cap_seconds':seconds});assert p.returncode==0,(label,p.returncode)
 return out

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

def mesh_check():
 records=[]
 root=CUT/'cases/order-xyz/constant/polyMesh'
 for expected in json.loads((KIT/'expected-mesh.json').read_text())['unpacked_members_match_archive']:
  path=root/expected['file'];row={'file':expected['file'],'bytes':path.stat().st_size,'sha256':checks.sha256(path)}
  assert row==expected;records.append(row)
 assert len(records)==8
 return {'passed':True,'members':records}

def main():
 global RUN
 RUN=WORK/'runs'/os.environ['SLURM_JOB_ID'];RUN.mkdir(parents=True,exist_ok=False)
 # Pinned kit and terminal cut evidence precede all case mutation.
 save(RUN/'mesh-before.json',mesh_check())
 command('kit-before',['sha256sum','-c','payload-sha256.txt'],KIT,30)
 accounting=subprocess.check_output(['sacct','-j','2294097','-n','-P','-o','JobIDRaw,State,ExitCode,AllocCPUS'],universal_newlines=True,timeout=15)
 assert [r.split('|') for r in accounting.splitlines() if r.startswith('2294097|')]==[['2294097','COMPLETED','0:0','56']]
 summary=json.loads((CUT/'runs/2294097/results.json').read_text());assert summary['all_complete'] and len(summary['arms'])==4 and all(r['passed'] for r in summary['arms'])
 for phase in ['before','after']:
  assert json.loads((CUT/('runs/2294097/source-'+phase+'.json')).read_text())['passed']
  assert json.loads((CUT/('runs/2294097/mesh-'+phase+'.json')).read_text())['passed']
 probe=command(os.environ['SLURM_JOB_ID']+'-mpi-hostnames',['mpirun','--display-map','--report-bindings','-np','56','--','python3','-c','import os,socket;print("INIT_PROBE"+chr(9)+os.environ["OMPI_COMM_WORLD_RANK"]+chr(9)+socket.getfqdn(),flush=True)'],KIT,60)
 with probe.open('a') as f:f.write('\nINIT_PROBE_RETURN_CODE=0\n')
 save(RUN/'mpi-probe-review.json',checks.check_probe(RUN,os.environ['SLURM_JOB_ID']))
 for order in ['xyz','zyx']:
  assert int(DEADLINE-time.monotonic())>900,'insufficient budget for next initialization'
  src=CUT/'cases'/('order-'+order);dest=WORK/'initialized'/('order-'+order)
  assert src.is_dir() and not(src/'READY').exists() and not dest.exists();save(RUN/(order+'-original-input.json'),source_check(src,order))
  dest.mkdir(parents=True);command(order+'-original-before',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'source-before.json'),'--source-only'],KIT,180)
  command(order+'-clone',['python3','-c','import shutil,sys;shutil.copytree(sys.argv[1],sys.argv[2],symlinks=True,dirs_exist_ok=True)',str(src),str(dest)],KIT,300)
  command(order+'-clone-check',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'source-after-copy.json'),'--compare-copy'],KIT,180)
  save(RUN/(order+'-source-before.json'),source_check(dest,order));save(RUN/(order+'-fields-before.json'),checks.field_snapshot(dest))
  for stage,args in [('renumberMesh',['renumberMesh','-constant','-overwrite','-parallel']),('potentialFoam',['potentialFoam','-initialiseUBCs','-parallel']),('applyBoundaryLayer',['applyBoundaryLayer','-ybl','0.0450244','-parallel'])]:
   log=command(order+'-'+stage,['mpirun','--display-map','--report-bindings','-np','56','--',*args],dest,210)
   with log.open('a') as f:f.write('\nINIT_STAGE_RETURN_CODE=0\n')
   text=log.read_text(errors='replace');actual=re.search(r'(?m)^Exec\s*:\s*(.+)$',text);assert actual and [Path(actual[1].split()[0]).name,*actual[1].split()[1:]]==args
   assert 'OPENFOAM=2512' in text and 'scalar=64' in text and re.search(r'(?m)^nProcs\s*:\s*56\s*$',text) and re.search(r'(?m)^End\s*$',text) and not checks.FATAL.search(text)
  save(RUN/(order+'-source-after.json'),source_check(dest,order));save(RUN/(order+'-fields-after.json'),checks.field_snapshot(dest))
  command(order+'-original-after',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'source-after-init.json'),'--source-only','--compare-source-snapshot'],KIT,180)
  with (dest/'READY').open('x') as f:f.write('N=56\nmethod=hierarchical\nnHierarchical=(7 4 2)\nmesh=occDrivAer-65M\nstages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer\n')
  save(RUN/(order+'-complete.json'),{'passed':True,'order':order,'initialized_case':str(dest),'source_cut':str(src),'raw_cut_preserved':True,'solver_result':None})
 save(RUN/'mesh-after.json',mesh_check())
 command('kit-after',['sha256sum','-c','payload-sha256.txt'],KIT,30)
 print('FRESH_XYZ_ZYX_INITIALIZATION_PASS')

if __name__=='__main__':main()
