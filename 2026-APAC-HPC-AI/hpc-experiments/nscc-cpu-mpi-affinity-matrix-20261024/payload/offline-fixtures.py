"""Exercise slot rendering and guard failures with synthetic four-host records only."""
import json
import copy
from pathlib import Path
import random
import subprocess
import sys
import tempfile
from mapping_common import RANKS, read_assignment

PAYLOAD = Path(__file__).resolve().parent
ASSIGNMENT = PAYLOAD / 'assignment.json'
RENDERER = PAYLOAD / 'render-candidate.py'
VALIDATOR = PAYLOAD / 'validate-mapping.py'


def write_rows(path, rows):
    path.write_text(''.join('MAP_JSON\t' + json.dumps(row, sort_keys=True) + '\n' for row in rows))


def command(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


def make_records():
    slots = []
    for host in range(4):
        for numa in range(8):
            for core in range(16):
                slots.append({'processor_name': 'synthetic-host-%d' % host,
                              'affinity_cpus': [numa * 16 + core],
                              'physical_package_id': 0,
                              'physical_core_id': numa * 16 + core,
                              'numa_node': numa})
    random.Random(24061).shuffle(slots)
    rows = []
    for rank, slot in enumerate(slots):
        row = dict(slot)
        row.update({'rank': rank, 'world_size': RANKS,
                    # This is intentionally not equal to MPI_COMM_WORLD rank.
                    'pmi_rank': str((rank + 73) % RANKS)})
        rows.append(row)
    return rows


def main():
    assignment = read_assignment(ASSIGNMENT)
    rank_host = assignment['mapping']['rank_to_host']
    report = {'fixture_type': 'synthetic MPI records only; no MPI runtime or ASPIRE topology claim',
              'randomized_identity_control_slots': True,
              'identity_rank_order_is_not_assumed_to_match_contiguous_hosts': True,
              'pmi_rank_is_authoritative': False,
              'positive': [], 'negative': []}
    with tempfile.TemporaryDirectory(prefix='.placement512-fixtures-', dir=str(PAYLOAD)) as td:
        root = Path(td)
        nodefile = root / 'nodefile'
        nodefile.write_text(''.join(('synthetic-host-%d\n' % host) * 128 for host in range(4)))
        identity_path = root / 'identity.jsonl'
        candidate_path = root / 'candidate.jsonl'
        order_path = root / 'rank-order.txt'
        expected_path = root / 'expected.json'
        identity = make_records()
        assert [row['processor_name'] for row in identity] != \
               ['synthetic-host-%d' % (rank // 128) for rank in range(RANKS)]
        assert all(sum(row['processor_name'] == 'synthetic-host-%d' % host for row in identity) == 128
                   for host in range(4))
        write_rows(identity_path, identity)
        result = command([sys.executable, str(RENDERER), str(identity_path), str(nodefile), str(ASSIGNMENT),
                          '--order-file', str(order_path), '--expected-file', str(expected_path)])
        assert result.returncode == 0, result.stderr
        order = [int(x) for x in order_path.read_text().strip().split(',')]
        assert len(order) == RANKS and sorted(order) == list(range(RANKS)) and order[0] == 0
        identity_by_slot = {row['rank']: row for row in identity}
        candidate = [None] * RANKS
        for slot, rank in enumerate(order):
            row = dict(identity_by_slot[slot])
            row['rank'] = rank
            row['pmi_rank'] = str(slot)
            candidate[rank] = row
        write_rows(candidate_path, candidate)
        result = command([sys.executable, str(VALIDATOR), str(identity_path), str(candidate_path),
                          str(nodefile), str(ASSIGNMENT), str(expected_path)])
        assert result.returncode == 0, result.stderr
        report['positive'].append({'name': 'randomized identity slots render and validate exact refined mapping',
                                   'passed': True, 'rank_order_entries': len(order),
                                   'rank_zero_first': order[0] == 0,
                                   'identity_host_sequence_is_interleaved': True,
                                   'validator_world_size': json.loads(result.stdout)['world_size']})

        valid_expected = json.loads(expected_path.read_text())
        broken_expected = copy.deepcopy(valid_expected)
        targets = broken_expected['expected_mapping_by_candidate_rank']
        targets[1]['control_slot_index'], targets[2]['control_slot_index'] = \
            targets[2]['control_slot_index'], targets[1]['control_slot_index']
        expected_path.write_text(json.dumps(broken_expected))
        result = command([sys.executable, str(VALIDATOR), str(identity_path), str(candidate_path),
                          str(nodefile), str(ASSIGNMENT), str(expected_path)])
        assert result.returncode != 0
        report['negative'].append({'name': 'expected slot metadata differs from original identity', 'rejected': True})

        # Keep a physically valid one-rank-per-core permutation, but break the
        # selected logical host membership. Comparing only to an expected file
        # would miss this; the validator must check group co-location itself.
        first = 1
        second = next(rank for rank in range(2, RANKS) if rank_host[rank] != rank_host[first])
        broken_expected = copy.deepcopy(valid_expected)
        targets = broken_expected['expected_mapping_by_candidate_rank']
        slot_a = targets[first]['control_slot_index']
        slot_b = targets[second]['control_slot_index']
        bad_order = broken_expected['candidate_order_file_sequence']
        bad_order[slot_a], bad_order[slot_b] = bad_order[slot_b], bad_order[slot_a]
        broken = copy.deepcopy(candidate)
        for rank, slot in ((first, slot_b), (second, slot_a)):
            control = identity_by_slot[slot]
            broken[rank] = dict(control, rank=rank, pmi_rank=str(slot))
            targets[rank].update(control_slot_index=slot,
                host=control['processor_name'], affinity_cpus=control['affinity_cpus'],
                physical_package_id=control['physical_package_id'],
                physical_core_id=control['physical_core_id'], numa_node=control['numa_node'])
        expected_path.write_text(json.dumps(broken_expected))
        write_rows(candidate_path, broken)
        result = command([sys.executable, str(VALIDATOR), str(identity_path), str(candidate_path),
                          str(nodefile), str(ASSIGNMENT), str(expected_path)])
        assert result.returncode != 0
        report['negative'].append({'name': 'physically valid permutation breaks selected logical host group', 'rejected': True})
        expected_path.write_text(json.dumps(valid_expected))
        write_rows(candidate_path, candidate)

        wrong_identity = [dict(row) for row in identity]
        wrong_identity[0]['numa_node'] = (wrong_identity[0]['numa_node'] + 1) % 8
        write_rows(identity_path, wrong_identity)
        result = command([sys.executable, str(RENDERER), str(identity_path), str(nodefile), str(ASSIGNMENT),
                          '--order-file', str(order_path), '--expected-file', str(expected_path)])
        assert result.returncode != 0
        report['negative'].append({'name': 'identity NUMA count differs from eight domains by sixteen', 'rejected': True})
        write_rows(identity_path, identity)

        broken = [dict(row) for row in candidate]; broken[511]['rank'] = broken[510]['rank']
        write_rows(candidate_path, broken)
        result = command([sys.executable, str(VALIDATOR), str(identity_path), str(candidate_path),
                          str(nodefile), str(ASSIGNMENT), str(expected_path)])
        assert result.returncode != 0
        report['negative'].append({'name': 'duplicate or missing MPI world rank', 'rejected': True})

        for field, value, name in (
                ('physical_core_id', 99999, 'candidate reports a wrong physical core'),
                ('processor_name', 'synthetic-host-3', 'candidate rank is on the wrong host'),
                ('numa_node', 7, 'candidate rank is on the wrong NUMA domain')):
            broken = [dict(row) for row in candidate]
            if field == 'physical_core_id':
                broken[1][field] = value
            elif field == 'processor_name':
                current_host = int(broken[1][field].rsplit('-', 1)[1])
                broken[1][field] = 'synthetic-host-%d' % ((current_host + 1) % 4)
            else:
                broken[1][field] = (broken[1][field] + 1) % 8
            write_rows(candidate_path, broken)
            result = command([sys.executable, str(VALIDATOR), str(identity_path), str(candidate_path),
                              str(nodefile), str(ASSIGNMENT), str(expected_path)])
            assert result.returncode != 0, name
            report['negative'].append({'name': name, 'rejected': True})
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
