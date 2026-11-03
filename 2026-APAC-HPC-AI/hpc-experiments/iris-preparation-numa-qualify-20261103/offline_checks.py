"""Offline parser and payload-shape checks; no cluster or source access."""
import json
from pathlib import Path
import hashlib
import tempfile
from qualification_utils import (parse_hardware_nodes, parse_numactl_show, parse_id_list,
    exact_tree_paths, require_same_policy, supplementary_hashes)
from qualification_utils import validate_manifest_paths

assert parse_id_list('0-3,7') == [0,1,2,3,7]
assert parse_hardware_nodes('available: 2 nodes (0-1)\n') == {'count':2,'node_ids':[0,1]}
assert parse_hardware_nodes('available: 1 nodes (0)\n')['count'] == 1
p=parse_numactl_show('policy: default\npreferred node: current\n')
assert p['policy']=='default'
p=parse_numactl_show('policy: interleave\ninterleave: 0 1\n')
assert p['policy']=='interleave' and p['interleave_nodes']==[0,1]
require_same_policy(parse_numactl_show('policy: default\n'),parse_numactl_show('policy: default\n'))
try:
    require_same_policy(parse_numactl_show('policy: interleave\ninterleave: 0 1\n'),
                        parse_numactl_show('policy: default\n'))
except ValueError: pass
else: raise AssertionError('changed inherited policy was accepted')
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)/'tree'; (root/'system').mkdir(parents=True)
    (root/'system'/'control').write_text('same')
    (root/'constant').mkdir(); (root/'constant'/'polyMesh').symlink_to('/approved/mesh')
    tiny={'files':{'system/control':'irrelevant hash'},'symlinks':{'constant/polyMesh':'/approved/mesh'}}
    ancillary={'files':{'READY':hashlib.sha256(b'ok').hexdigest()},'symlinks':{},'directories':['system','constant']}
    (root/'READY').write_bytes(b'ok')
    combined={'files':{**tiny['files'],**ancillary['files']},'symlinks':tiny['symlinks']}
    assert exact_tree_paths(root,combined,ancillary['directories'])
    assert supplementary_hashes(root,ancillary)['READY']==ancillary['files']['READY']
    assert exact_tree_paths(root,combined,ancillary['directories']), 'fixture baseline should pass before mutation'
    (root/'READY').write_bytes(b'changed')
    try: supplementary_hashes(root,ancillary)
    except ValueError: pass
    else: raise AssertionError('changed supplementary file was accepted')
    (root/'READY').write_bytes(b'ok')
    (root/'unexpected').write_text('extra')
    try: exact_tree_paths(root,combined,ancillary['directories'])
    except ValueError: pass
    else: raise AssertionError('unmanifested root file was accepted')
    (root/'unexpected').unlink(); (root/'processor56').mkdir()
    try: exact_tree_paths(root,combined,ancillary['directories'])
    except ValueError: pass
    else: raise AssertionError('unmanifested processor directory was accepted')
root=Path(__file__).resolve().parent
m=json.loads((root/'accepted-source-manifest.json').read_text())
assert len(m['files'])==1040 and len(m['symlinks'])==1
assert all(len(v)==64 for v in m['files'].values())
supp=json.loads((root/'supplementary-source-manifest.json').read_text())
assert len(supp['files'])==13 and not supp['symlinks'] and supp['total_ancillary_bytes']==50497
assert len(supp['directories'])==len(set(supp['directories']))
assert all(not Path(x).is_absolute() and '..' not in Path(x).parts for x in supp['directories'])
validate_manifest_paths(m,supp)
try: validate_manifest_paths(m,{'files':{'../escape':'0'*64},'symlinks':{},'directories':[]})
except ValueError: pass
else: raise AssertionError('unsafe supplementary path was accepted')
print('offline parser, exact-tree rejection, policy-equivalence and manifest-shape checks passed; no measurement performed')
