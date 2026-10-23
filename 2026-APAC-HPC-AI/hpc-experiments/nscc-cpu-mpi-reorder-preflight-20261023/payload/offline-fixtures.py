"""Run synthetic positive and negative validator fixtures; launches no MPI ranks."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PAYLOAD = Path(__file__).resolve().parent
VALIDATOR = PAYLOAD / 'validate-probe.py'


def run(identity, candidate, nodefile, root):
    return subprocess.run([sys.executable, str(VALIDATOR), str(identity), str(candidate), str(nodefile),
                           '--sysfs-root', '/sys', '--output', str(root / 'validated.json')],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


def write_rows(path, rows):
    path.write_text(''.join('PROBE_JSON\t' + json.dumps(x, sort_keys=True) + '\n' for x in rows))


def available_cores():
    selected = []
    for cpu in sorted(os.sched_getaffinity(0)):
        topology = Path('/sys/devices/system/cpu/cpu%d/topology' % cpu)
        key = (int((topology / 'physical_package_id').read_text()),
               int((topology / 'core_id').read_text()))
        if key not in [x[1] for x in selected]:
            selected.append((cpu, key))
        if len(selected) == 4:
            return [x[0] for x in selected]
    raise AssertionError('four accessible unique physical cores unavailable for fixture')


def records(rank_cpus):
    return [{'rank': rank, 'world_size': 4, 'processor_name': 'fixture-host.local',
             # Deliberately arbitrary: PMI metadata is diagnostic, never rank authority.
             'pmi_rank': 'diagnostic-%d' % (3-rank), 'affinity_cpus': [rank_cpus[rank]]}
            for rank in range(4)]


def main():
    order = [0, 2, 1, 3]
    inverse = {rank: slot for slot, rank in enumerate(order)}
    cpus = available_cores()
    identity_cpus = {rank: cpus[rank] for rank in range(4)}
    candidate_cpus = {rank: cpus[inverse[rank]] for rank in range(4)}
    summary = {'fixture_type': 'synthetic MPI records; no MPI launch or site inference',
               'cpu_topology_source': '/sys on the local validation host',
               'pmi_rank_is_authoritative': False, 'positive': [], 'negative': []}
    with tempfile.TemporaryDirectory(prefix='.offline-fixtures-', dir=str(PAYLOAD)) as td:
        root = Path(td)
        nodefile = root / 'nodefile'; nodefile.write_text('fixture-host\n' * 4)
        identity = root / 'identity.jsonl'; candidate = root / 'candidate.jsonl'
        write_rows(identity, records(identity_cpus)); write_rows(candidate, records(candidate_cpus))
        result = run(identity, candidate, nodefile, root)
        assert result.returncode == 0, result.stderr
        summary['positive'].append({'name': 'identity control and requested nonidentity candidate', 'passed': True,
                                    'validator_output': json.loads((root / 'validated.json').read_text())})

        write_rows(candidate, records(identity_cpus))
        result = run(identity, candidate, nodefile, root)
        assert result.returncode != 0
        summary['negative'].append({'name': 'candidate left at identity mapping', 'rejected': True})

        duplicate_cpus = dict(identity_cpus); duplicate_cpus[3] = duplicate_cpus[2]
        write_rows(identity, records(duplicate_cpus))
        result = run(identity, candidate, nodefile, root)
        assert result.returncode != 0
        summary['negative'].append({'name': 'duplicate physical core in identity arm', 'rejected': True})

        write_rows(identity, records(identity_cpus))
        duplicate_rank = records(candidate_cpus); duplicate_rank[3]['rank'] = 2
        write_rows(candidate, duplicate_rank)
        result = run(identity, candidate, nodefile, root)
        assert result.returncode != 0
        summary['negative'].append({'name': 'duplicate MPI_COMM_WORLD rank record', 'rejected': True})

        write_rows(candidate, records(candidate_cpus)); nodefile.write_text('fixture-host\n' * 3)
        result = run(identity, candidate, nodefile, root)
        assert result.returncode != 0
        summary['negative'].append({'name': 'PBS nodefile has only three slots', 'rejected': True})
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
