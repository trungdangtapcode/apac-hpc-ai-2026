"""Check real adapter GPU mapping and retain the official client byte-for-byte."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

DIR=Path(__file__).resolve().parent;ROOT=DIR.parent;bundle=DIR/'baseline-n32';cases=[]
with tempfile.TemporaryDirectory(prefix='ap42-pbs-map-') as temp:
    nodefile=Path(temp)/'nodes';nodefile.write_text('n0\nn1\n')
    env=dict(os.environ,PBS_NODEFILE=str(nodefile),QWEN_BUNDLE=str(bundle),APAC_PBS_DRY_RUN='1')
    for role,node,tp,expected in [('prefill-0',0,4,[0,1,2,3]),('prefill-1',0,4,[4,5,6,7]),('decode-0',1,8,list(range(8)))]:
        args=['bash','-c','source "$1";shift;srun "$@"','_',str(bundle/'pbs-shim.sh'),'--exact','-N1','-n1','-w',f'n{node}',
              f'--gres=gpu:{tp}',f'--cpus-per-task={tp*8}','--container-image=/images/sglang.sqsh',
              '--container-mounts=/scratch:/scratch','bash','/art/worker.sh',role,'30100','/model',str(tp)]
        result=json.loads(subprocess.check_output(args,env=env,text=True))
        assert result['node']==node and result['gpu_indices']==expected and result['cpus']==tp*8
        cases.append(result)
    args=['bash','-c','source "$1";shift;srun "$@"','_',str(bundle/'pbs-shim.sh'),'--overlap','-N1','-n1','-w','n0',
          '--gres=gpu:0','--cpus-per-task=4','--container-image=/images/client.sqsh','--container-mounts=/scratch:/scratch',
          'bash','/art/benchmark.sh','n0:8000','/model','/art']
    result=json.loads(subprocess.check_output(args,env=env,text=True));assert result['node']==0 and result['gpu_indices']==[]
    cases.append(result)
source=ROOT/'serving-tuning/s5-rr-repeat-n52'
for name in ('benchmark.sh','worker.sh','placement.tsv','nixl-conn.py','output-smoke.py'):
    assert (source/name).read_bytes()==(bundle/name).read_bytes(),name
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True,capture_output=True)
report=dict(passed=True,scope='CPU PBS launch adaptation and immutable source checks; full Qwen runtime untested on NSCC',
            gpu_mapping_cases=cases,official_client_worker_router_patch_preserved=True,
            client_sha256=hashlib.sha256((bundle/'benchmark.sh').read_bytes()).hexdigest())
(DIR/'port-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PBS GPU placement and frozen-source validation passed')
