"""Render the refined NUMA mapping against actual identity-run host/core slots."""
import argparse
import json
from pathlib import Path
from mapping_common import (DOMAINS_PER_HOST, HOSTS, RANKS, RANKS_PER_DOMAIN,
                            normalize_host, read_assignment, read_nodefile,
                            read_probe, validate_probe)


def render(identity_path, nodefile_path, assignment_path):
    assignment = read_assignment(assignment_path)
    _, node_counts = read_nodefile(nodefile_path)
    identity, identity_summary = validate_probe(identity_path, node_counts)

    first_host = normalize_host(identity[0]['processor_name'])
    min_rank = {}
    for rank, row in identity.items():
        host = normalize_host(row['processor_name'])
        min_rank[host] = min(rank, min_rank.get(host, rank))
    host_order = [first_host] + sorted((host for host in min_rank if host != first_host),
                                       key=lambda host: (min_rank[host], host))
    assert len(host_order) == HOSTS and len(set(host_order)) == HOSTS

    actual_domains = {}
    for host in host_order:
        actual_domains[host] = sorted(set(row['numa_node'] for row in identity.values()
                                           if normalize_host(row['processor_name']) == host))
        assert len(actual_domains[host]) == DOMAINS_PER_HOST
    domain_order = {}
    for host_index, host in enumerate(host_order):
        domains = actual_domains[host]
        if host_index == 0:
            rank_zero_domain = identity[0]['numa_node']
            domain_order[host] = [rank_zero_domain] + [x for x in domains if x != rank_zero_domain]
        else:
            domain_order[host] = domains[:]

    groups = assignment['mapping']['numa_group_members_by_host']
    candidate_order = [None] * RANKS
    expected_by_rank = [None] * RANKS
    rank_to_logical = assignment['mapping']['rank_to_host']
    rank_to_group = assignment['mapping']['rank_to_logical_numa_group_within_host']
    for host_group, host in enumerate(host_order):
        for logical_domain, actual_domain in enumerate(domain_order[host]):
            slots = sorted(rank for rank, row in identity.items()
                           if normalize_host(row['processor_name']) == host and row['numa_node'] == actual_domain)
            candidate_ranks = sorted(groups[host_group][logical_domain])
            assert len(slots) == RANKS_PER_DOMAIN and len(candidate_ranks) == RANKS_PER_DOMAIN, \
                ('slot/group size mismatch', host_group, logical_domain, len(slots), len(candidate_ranks))
            for slot, candidate_rank in zip(slots, candidate_ranks):
                assert candidate_order[slot] is None
                assert rank_to_logical[candidate_rank] == host_group
                assert rank_to_group[candidate_rank] == logical_domain
                candidate_order[slot] = candidate_rank
                control = identity[slot]
                expected_by_rank[candidate_rank] = {
                    'candidate_rank': candidate_rank,
                    'control_slot_index': slot,
                    'host': normalize_host(control['processor_name']),
                    'affinity_cpus': control['affinity_cpus'],
                    'physical_package_id': control['physical_package_id'],
                    'physical_core_id': control['physical_core_id'],
                    'numa_node': control['numa_node'],
                    'logical_host_group': host_group,
                    'logical_numa_group': logical_domain}
    assert all(x is not None for x in candidate_order)
    assert sorted(candidate_order) == list(range(RANKS))
    assert candidate_order[0] == 0, 'candidate rank zero must stay in first slot'
    assert expected_by_rank[0]['control_slot_index'] == 0

    plan = {'passed': True, 'candidate_order_file_sequence': candidate_order,
            'rank_zero_first': True, 'identity_host_order': host_order,
            'physical_numa_domain_order_by_identity_host': domain_order,
            'expected_mapping_by_candidate_rank': expected_by_rank,
            'identity_validation': identity_summary,
            'mapping_rule': 'candidate rank r occupies control identity slot order-file position s where candidate_order_file_sequence[s] == r'}
    return candidate_order, plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('identity')
    ap.add_argument('nodefile')
    ap.add_argument('assignment')
    ap.add_argument('--order-file', required=True)
    ap.add_argument('--expected-file', required=True)
    args = ap.parse_args()
    order, plan = render(args.identity, args.nodefile, args.assignment)
    Path(args.order_file).write_text(','.join(str(x) for x in order) + '\n')
    Path(args.expected_file).write_text(json.dumps(plan, indent=2) + '\n')
    print(json.dumps({'passed': True, 'order_entries': len(order), 'rank_zero_first': order[0] == 0,
                      'hosts': plan['identity_host_order'], 'domain_map': plan['physical_numa_domain_order_by_identity_host']}, indent=2))


if __name__ == '__main__':
    main()
