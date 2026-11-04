"""Offline checks for named arms, bounded windows, and in-rank pre-exec gates."""
from pathlib import Path
import json
import tempfile

from qualification_utils import parse_numactl_show
import run

ROOT = Path(__file__).resolve().parent
assert run.ARMS == ['A1-default-solver', 'B1-interleaved-solver',
                    'B2-interleaved-solver', 'A2-default-solver']
assert run.TREATMENTS == {'A1-default-solver':'default',
    'B1-interleaved-solver':'interleave-all', 'B2-interleaved-solver':'interleave-all',
    'A2-default-solver':'default'}
assert run.SOLVER_CAP == 1500 and run.INTERNAL_SECONDS == 6800
assert run.complete_sequence_seconds(4) == 6420
run.require_complete_sequence_window(6800, 4)
try:
    run.require_complete_sequence_window(6419, 4)
except RuntimeError:
    pass
else:
    raise AssertionError('sequence window gate accepted insufficient time')

assert run.preparation_launch(run.ARMS[0], ['python3','copy_phase.py'], '/bin/numactl') == ['python3','copy_phase.py']
assert run.preparation_launch(run.ARMS[1], ['python3','copy_phase.py'], '/bin/numactl') == ['python3','copy_phase.py']
proof = ROOT / 'test-proof'
assert run.solver_launch(run.ARMS[0], proof) == run.LAUNCH + ['--','python3',str(ROOT/'rank_exec.py'),'default',str(proof)]
assert run.solver_launch(run.ARMS[1], proof) == run.LAUNCH + ['--','numactl','--interleave=all','python3',str(ROOT/'rank_exec.py'),'interleave-all',str(proof)]

default = parse_numactl_show('policy: default\ninterleavemask: 0\n')
interleave = parse_numactl_show('policy: interleave\ninterleavemask: 0-1\n')
assert default['policy'] == 'default'
assert interleave['policy'] == 'interleave' and interleave['interleave_nodes'] == [0,1]
with tempfile.TemporaryDirectory() as temp:
    for expected, policy in (('default',default), ('interleave-all',interleave)):
        proof_dir = Path(temp) / expected
        proof_dir.mkdir()
        for rank in range(56):
            (proof_dir / f'rank-{rank:02d}.json').write_text(json.dumps({
                'rank':rank, 'pid':10000+rank, 'expected_policy':expected,
                'observed_policy':policy, 'affinity_cpu_ids':[rank],
                'command_before_exec':['simpleFoam','-parallel']}))
        assert len(run.verify_rank_proofs(proof_dir, expected)) == 56
        wrong = 'interleave-all' if expected == 'default' else 'default'
        try:
            run.verify_rank_proofs(proof_dir, wrong)
        except RuntimeError:
            pass
        else:
            raise AssertionError('proof gate accepted wrong expected policy')
    incomplete = Path(temp) / 'incomplete'
    incomplete.mkdir()
    for rank in range(55):
        (incomplete / f'rank-{rank:02d}.json').write_text(json.dumps({
            'rank':rank, 'pid':10000+rank, 'expected_policy':'default',
            'observed_policy':default, 'affinity_cpu_ids':[rank],
            'command_before_exec':['simpleFoam','-parallel']}))
    try:
        run.verify_rank_proofs(incomplete, 'default')
    except RuntimeError:
        pass
    else:
        raise AssertionError('proof gate accepted a missing rank')
    overlap = Path(temp) / 'overlap'
    overlap.mkdir()
    for rank in range(56):
        (overlap / f'rank-{rank:02d}.json').write_text(json.dumps({
            'rank':rank, 'pid':10000+rank, 'expected_policy':'default',
            'observed_policy':default, 'affinity_cpu_ids':[0],
            'command_before_exec':['simpleFoam','-parallel']}))
    try:
        run.verify_rank_proofs(overlap, 'default')
    except RuntimeError:
        pass
    else:
        raise AssertionError('proof gate accepted overlapping core mappings')

source = (ROOT/'rank_exec.py').read_text()
assert "['numactl', '--show']" in source
assert "os.sched_getaffinity(0)" in source
assert "os.execvp('simpleFoam', ['simpleFoam', '-parallel'])" in source
assert source.index("os.replace(temporary, target)") < source.index("os.execvp('simpleFoam'")
job = (ROOT/'job.sbatch').read_text()
for limit in ('--exclusive','--qos=low','--ntasks=56','--gpus=0','--time=02:00:00','7190s python3'):
    assert limit in job, limit
print('named arm, solver policy, pre-exec proof, core-map, and window gates passed; no measurement performed')
