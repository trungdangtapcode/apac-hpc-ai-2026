"""Check real native record compatibility, C grammar and synthetic rejection gates."""
from pathlib import Path
import ast,hashlib,importlib.util,json,subprocess,tarfile,tempfile
E=Path(__file__).resolve().parent;R=E.parent
for p in E.rglob('*.py'):ast.parse(p.read_text(),filename=str(p),feature_version=(3,9))
for name in ['worker.sh','rank-exec.sh','nscc-cpu-pstream-latepin.pbs']:
 subprocess.run(['bash','-n',str(E/'payload'/name)],check=True)
for name in ['mpi-init-probe.c','latepin-pmpi-adapter.c']:
 subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-pthread','-fsyntax-only','-I',str(E/'payload/offline/include'),str(E/'payload'/name)],check=True)
subprocess.run(['python3',str(E/'payload/offline/fixtures.py')],check=True,stdout=subprocess.DEVNULL)
spec=importlib.util.spec_from_file_location('pstream_review',E/'review.py');review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
parent=R/'nscc-cpu-postinit-pin-20261027/completed-26016270';meta=json.loads((parent/'collection.json').read_text());arc=parent/'raw-records.tar.gz'
assert hashlib.sha256(arc.read_bytes()).hexdigest()==meta['archive_sha256']
with tempfile.TemporaryDirectory() as temporary:
 run=Path(temporary);(run/'logs').mkdir();(run/'logs/arm-no-adapter.stdout.txt').write_text('MPI_SUMMARY_JSON {"world_size":512,"ranks_with_capture_or_identity_errors":0}\n')
 count=0
 with tarfile.open(arc) as tar:
  for m in tar.getmembers():
   prefix='runs/26016270/arms/baseline/native/'
   if not m.isfile() or not m.name.startswith(prefix) or not m.name.endswith('.json'):continue
   raw=tar.extractfile(m).read();assert hashlib.sha256(raw).hexdigest()==meta['files'][m.name]['sha256']
   p=run/'arms/no-adapter/native'/m.name[len(prefix):];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);count+=1
 assert count==1024 and len(review.native_arm(run,'no-adapter'))==512
 post=sorted((run/'arms/no-adapter/native').glob('rank-*.json'));a=json.loads(post[0].read_text());b=json.loads(post[1].read_text());b['pmi_rank']=a['pmi_rank'];post[1].write_text(json.dumps(b)+'\n')
 try:review.native_arm(run,'no-adapter')
 except review.ReviewError:pass
 else:raise AssertionError('duplicate PMI crosswalk accepted')
result={'passed':True,'scope':'Offline only; no real MPI ABI build, launch or OpenFOAM runtime qualification','Python_3_9_grammar':True,'shell_syntax':True,'C_syntax_warning_checks_with_declaration_only_MPI_header':True,'synthetic_positive_and_six_rejection_cases':True,'real_parent_native_record_compatibility':{'archive_sha256':meta['archive_sha256'],'actual_record_count':1024,'positive':True,'duplicate_PMI_negative':True,'correction':'Unchanged native C records have no world_size field; world size and errors are verified in the real MPI summary plus complete record sets.'}}
(E/'offline-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
