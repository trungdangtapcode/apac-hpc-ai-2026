"""Offline checks for treatment separation and fixed native solver controls."""
from pathlib import Path
import json
from qualification_utils import (parse_numactl_show, policy_signature,
    validate_manifest_paths, require_same_policy)
import run

root=Path(__file__).resolve().parent
assert run.ARMS==['A1-inherited-prep','B1-interleaved-prep','B2-interleaved-prep','A2-inherited-prep']
assert run.TREATMENTS=={'A1-inherited-prep':'inherited','B1-interleaved-prep':'interleave-all',
                        'B2-interleaved-prep':'interleave-all','A2-inherited-prep':'inherited'}
default=parse_numactl_show('policy: default\ninterleavemask: 0\n')
interleave=parse_numactl_show('policy: interleave\ninterleavemask: 0-1\n')
assert policy_signature(default)!=policy_signature(interleave)
assert policy_signature(default)==policy_signature(parse_numactl_show('policy: default\ninterleavemask: 0\n'))
require_same_policy(default,parse_numactl_show('policy: default\ninterleavemask: 0\n'))
try: require_same_policy(interleave,default)
except ValueError: pass
else: raise AssertionError('inherited-policy arm accepted interleave treatment')
observed=parse_numactl_show((root/'observed-numactl-interleave.txt').read_text())
assert observed['policy']=='interleave' and observed['interleave_nodes']==[0,1] and observed['membind_nodes']==[0,1]
commands=[run.solver_launch(label) for label in run.ARMS]
assert all(command==commands[0] for command in commands), 'treatment must not alter native solver command'
worker=['python3','copy_phase.py']
assert run.preparation_launch('A1-inherited-prep',worker,'/bin/numactl')==worker
assert run.preparation_launch('B1-interleaved-prep',worker,'/bin/numactl')==['/bin/numactl','--interleave=all',*worker]
assert run.sys.executable
assert run.SOLVER_CAP==1500 and run.COPY_CAP==50 and run.PREP_CAP==60 and run.INTERNAL_SECONDS==6800
assert run.complete_sequence_seconds(4)==6420
assert 4*(run.SOLVER_CAP+run.PREP_CAP)+run.FINALIZE_RESERVE==6420
assert run.INTERNAL_SECONDS>=run.complete_sequence_seconds(4)
run.require_complete_sequence_window(6420,4)
try: run.require_complete_sequence_window(6419,4)
except RuntimeError: pass
else: raise AssertionError('overlong preflight should reject before arm 1')
assert run.complete_sequence_seconds(4,include_current_prep=False)==6360
run.require_complete_sequence_window(6435-70,4,include_current_prep=False)
source= (root/'run.py').read_text()
assert "WM_PROJECT_VERSION')=='v2512'" in source and "WM_PRECISION_OPTION')=='DP'" in source
assert run.solver_launch(run.ARMS[0])==['mpirun','-np','56','--report-bindings','--display-map','--','simpleFoam','-parallel']
core=json.loads((root/'accepted-source-manifest.json').read_text())
extra=json.loads((root/'supplementary-source-manifest.json').read_text())
validate_manifest_paths(core,extra)
assert len(core['files'])==1040 and len(extra['files'])==13 and extra['total_ancillary_bytes']==50497
job=(root/'job.sbatch').read_text()
for required in ('--exclusive','--qos=low','--ntasks=56','--gpus=0','--time=02:00:00','7190s python3'):
    assert required in job, required
print('native treatment, fixed solver controls, source manifest and resource-envelope checks passed; no measurement performed')
