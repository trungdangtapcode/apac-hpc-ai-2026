"""Offline positive and negative checks; never seals or contacts the cluster."""
from pathlib import Path
import importlib.util, tempfile, shutil, sys, hashlib
E=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reverse_run',E/'run.py'); run=importlib.util.module_from_spec(spec);sys.modules[spec.name]=run;spec.loader.exec_module(run)
spec=importlib.util.spec_from_file_location('reverse_deploy',E/'deploy_submit.py'); dep=importlib.util.module_from_spec(spec);sys.modules[spec.name]=dep;spec.loader.exec_module(dep)
# Arm association follows names even when data arrives in the actual reverse order.
zyx={'order':'zyx','mean_seconds_per_step':23.8};xyz={'order':'xyz','mean_seconds_per_step':32.6}
a,b=run.select_arms_by_order([zyx,xyz]);assert a is zyx and b is xyz
for rows in ([zyx], [zyx,zyx], [dict(order='other'),xyz]):
    try:run.select_arms_by_order(rows)
    except (AssertionError,KeyError):pass
    else:raise AssertionError('invalid arm set accepted')
# Seal/hash check accepts the original fixture and rejects byte changes and missing files.
with tempfile.TemporaryDirectory(prefix='iris-reverse-seal-') as td:
    root=Path(td); files=[]
    for name,body in [('run.py',b'runner'),('payload-case/a',b'case')]:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body);files.append(p)
    manifest=dep.compute_files(files);assert len(manifest)==2
    assert all(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest for name,digest in manifest.items())
    (root/'payload-case/a').write_bytes(b'changed')
    current=dep.compute_files(files);assert current!=manifest
    files.pop();assert set(dep.compute_files(files))!=set(manifest)
# Parent native parser already has fixtures; validate checked-in fixtures and negative paths.
review=E/'offline_review.py'
assert review.is_file() and len(dep.expected_paths())==49
print('PASS: order-keyed arm selection positive/negative; payload hash seal positive/tamper/missing-file negatives; 49-file runtime boundary.')

# Enforce one own queued/running allocation, including unrelated own job names.
dep.require_no_own_jobs('2290000|other-user-job|RUNNING\n')
for queue in ['2294100|tu-existing|RUNNING\n','2294100|tu-other|PENDING\n']:
    try:dep.require_no_own_jobs(queue)
    except AssertionError:pass
    else:raise AssertionError('own active job accepted')
assert run.ARM_ORDER==('zyx','xyz') and run.SOLVER_CAP==1150 and run.ARM_START_RESERVE==1270
with tempfile.TemporaryDirectory(prefix='iris-node-snapshot-') as td:
    import json
    root=Path(td);run.node_snapshot('fixture',root);snap=json.loads((root/'fixture-node-snapshot.json').read_text())
    assert snap['collection_elapsed_ms']>=0 and all(name in snap or name+'_error' in snap for name in ['meminfo','vmstat','pressure/memory'])
print('PASS: one-own-job queue guard, deadline constants and bounded snapshot interface.')
