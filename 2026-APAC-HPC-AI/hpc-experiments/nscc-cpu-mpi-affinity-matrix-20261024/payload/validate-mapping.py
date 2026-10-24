"""Validate actual MPI mappings against identity slots and the refined logical groups."""
import argparse
import json
from pathlib import Path
from mapping_common import (RANKS, read_assignment, read_nodefile,
                            validate_probe, normalize_host)


def validate(identity_path, candidate_path, nodefile_path, assignment_path, expected_path):
    assignment = read_assignment(assignment_path)
    _, node_counts = read_nodefile(nodefile_path)
    identity, identity_summary = validate_probe(identity_path, node_counts)
    candidate, candidate_summary = validate_probe(candidate_path, node_counts)
    expected = json.loads(Path(expected_path).read_text())
    assert expected['passed'] is True
    by_rank = expected['expected_mapping_by_candidate_rank']
    assert len(by_rank) == RANKS
    order = expected['candidate_order_file_sequence']
    assert sorted(order) == list(range(RANKS)) and order[0] == 0
    assert sorted(row['control_slot_index'] for row in by_rank) == list(range(RANKS))
    rank_to_host = assignment['mapping']['rank_to_host']
    rank_to_domain = assignment['mapping']['rank_to_logical_numa_group_within_host']
    mismatched_pmi = 0
    rows = []
    for rank in range(RANKS):
        actual = candidate[rank]
        want = by_rank[rank]
        slot = want['control_slot_index']
        assert want['candidate_rank'] == rank and order[slot] == rank
        control = identity[slot]
        assert (want['host'], want['affinity_cpus'], want['physical_package_id'],
                want['physical_core_id'], want['numa_node']) == (
                    normalize_host(control['processor_name']), control['affinity_cpus'],
                    control['physical_package_id'], control['physical_core_id'], control['numa_node']), \
                ('expected mapping differs from original identity slot', rank, slot)
        observed = {'host': normalize_host(actual['processor_name']),
                    'affinity_cpus': actual['affinity_cpus'],
                    'physical_package_id': actual['physical_package_id'],
                    'physical_core_id': actual['physical_core_id'],
                    'numa_node': actual['numa_node']}
        target = {'host': want['host'], 'affinity_cpus': want['affinity_cpus'],
                  'physical_package_id': want['physical_package_id'],
                  'physical_core_id': want['physical_core_id'], 'numa_node': want['numa_node']}
        assert observed == target, ('candidate MPI rank does not match intended identity slot', rank, observed, target)
        assert rank_to_host[rank] == want['logical_host_group']
        assert rank_to_domain[rank] == want['logical_numa_group']
        pmi = actual.get('pmi_rank')
        if pmi is not None and pmi != str(rank):
            mismatched_pmi += 1
        rows.append({'mpi_world_rank': rank, 'control_slot_index': want['control_slot_index'],
                     'host': observed['host'], 'logical_cpu': observed['affinity_cpus'][0],
                     'physical_package_id': observed['physical_package_id'],
                     'physical_core_id': observed['physical_core_id'], 'numa_node': observed['numa_node'],
                     'logical_host_group': want['logical_host_group'],
                     'logical_numa_group': want['logical_numa_group']})
    assert rows[0]['mpi_world_rank'] == 0 and rows[0]['control_slot_index'] == 0
    for host_group in range(4):
        group_rows = [row for row in rows if row['logical_host_group'] == host_group]
        assert len({row['host'] for row in group_rows}) == 1
        for domain in range(8):
            domain_rows = [row for row in group_rows if row['logical_numa_group'] == domain]
            assert len(domain_rows) == 16 and len({row['numa_node'] for row in domain_rows}) == 1
    return {'passed': True, 'world_size': RANKS, 'host_count': len(node_counts),
            'identity_validation': identity_summary, 'candidate_validation': candidate_summary,
            'candidate_rank_zero_first': True, 'pmi_mismatch_count_diagnostic_only': mismatched_pmi,
            'mapping_rule': expected['mapping_rule'], 'intended_and_observed_by_mpi_rank': rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('identity')
    ap.add_argument('candidate')
    ap.add_argument('nodefile')
    ap.add_argument('assignment')
    ap.add_argument('expected')
    ap.add_argument('--output')
    args = ap.parse_args()
    result = validate(args.identity, args.candidate, args.nodefile, args.assignment, args.expected)
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
