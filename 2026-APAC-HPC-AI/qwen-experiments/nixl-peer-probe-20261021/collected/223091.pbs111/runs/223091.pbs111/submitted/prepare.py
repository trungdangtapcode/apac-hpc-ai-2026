"""Freeze the no-model probe and its source/API evidence before any GPU action."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,shutil,subprocess,tarfile
O=Path(__file__).resolve().parent;R=O.parent;assert not (O/'SHA256SUMS').exists(),'Never rewrite a frozen payload'
C=R/'eagle3-pd-eager-prefill-r3-20261021';review=json.loads((C/'REVIEW.json').read_text());assert review['state']=='ALL_ROLES_READY_PD_TRANSPORT_FAILED' and not review['actual_output_ids_collected']
shutil.copyfile(C/'nixl-conn.py',O/'nixl-conn.py');(O/'prerequisite.json').write_text(json.dumps(review,indent=2)+'\n')
api_root=Path('/tmp/nixl-api-read-path').read_text().strip();api=Path(api_root)/'usr/local/lib/python3.12/dist-packages/nixl_cu13/_api.py';assert hashlib.sha256(api.read_bytes()).hexdigest()=='27c3ce3c4fe58480aa3bce5e5c158c7659821a3bf1e84680778645adfdaa1bea'
(O/'source').mkdir(exist_ok=True);shutil.copyfile(api,O/'source/nixl_api.py')
(O/'source/PROVENANCE.md').write_text('''# Pinned API evidence

Selected file extracted on CPU using unsquashfs with two processors from
/scratch/enroot-images/sglang-harbor.sqsh, source member
usr/local/lib/python3.12/dist-packages/nixl_cu13/_api.py.
SHA256: 27c3ce3c4fe58480aa3bce5e5c158c7659821a3bf1e84680778645adfdaa1bea.
Original NVIDIA Apache-2.0 header is preserved. Runtime probes must match it.

The first local extraction commands used unsupported -cat and then an already
existing destination directory; both failed without GPU activity or source
mutation. The successful extraction used a fresh nonexisting child destination.
The current installed API and the pinned SGLang adapter govern the probe;
public main-branch examples are references, not assumed runtime version proof.
''')
result=subprocess.run(['python3',str(O/'CPU-test.py')],capture_output=True,text=True);(O/'cpu-validation.stdout').write_text(result.stdout);(O/'cpu-validation.stderr').write_text(result.stderr);assert result.returncode==0
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(O.glob('*.sh'))+[O/'component.pbs']:subprocess.run(['bash','-n',str(p)],check=True)
validation=dict(passed=True,checked_utc=datetime.now(timezone.utc).isoformat(),cpu_regression_tests=9,scope='Actual helper calls through mocked NIXL plus semantic/deadline/source identity checks; no GPU/network execution',source_api_sha256=hashlib.sha256(api.read_bytes()).hexdigest(),requested_gpus=2,minutes=10,max_su=2*128*10/60,model_loaded=False,raw_peer_metadata_outside_artifact_tree=True,actual_transport_validated=False)
(O/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
files=['component.pbs','node-entry.sh','entry.sh','probe.py','CPU-test.py','prepare.py','nixl-conn.py','PLAN.md','prerequisite.json','validation.json','cpu-validation.stdout','cpu-validation.stderr','source/nixl_api.py','source/PROVENANCE.md']
(O/'SHA256SUMS').write_text(''.join(hashlib.sha256((O/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in files))
with tarfile.open(O/'payload.tar.gz','w:gz') as tar:
 for name in files+['SHA256SUMS']:tar.add(O/name,arcname=O.name+'/'+name)
print('Frozen no-model two-node/2H100/10min transport probe; max42.666667SU, not submitted')
