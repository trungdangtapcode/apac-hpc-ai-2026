#!/usr/bin/env python3
"""Independently recompute every face category of the retained mapping."""
from pathlib import Path
from collections import Counter
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'rank-placement-512-screen-20261023'


def main():
    graph = json.loads((PARENT / 'graph.json').read_text())
    parent = json.loads((PARENT / 'screen.json').read_text())
    screen = json.loads((HERE / 'screen.json').read_text())
    final = screen['optimized_fixed_host_mapping']
    hosts = final['rank_to_host']
    domains = final['rank_to_logical_numa_group_within_host']
    parent_hosts = parent['candidate']['rank_to_logical_host']
    assert hosts == parent_hosts
    assert len(hosts) == len(domains) == 512 and Counter(hosts) == {0: 128, 1: 128, 2: 128, 3: 128}
    sorted_domains = [None] * 512
    for host in range(4):
        ranks = [i for i in range(512) if hosts[i] == host]
        assert Counter(domains[i] for i in ranks) == {i: 16 for i in range(8)}
        for slot, rank in enumerate(ranks):
            sorted_domains[rank] = slot // 16
    cases = [
        ('original', [i // 128 for i in range(512)], [(i % 128) // 16 for i in range(512)], (337324, 710081, 1879617)),
        ('parent', parent_hosts, sorted_domains, (261110, 1097554, 1568358)),
        ('refined', hosts, domains, (261110, 732712, 1933200))]
    results = []
    for name, assignment, numa, expected in cases:
        totals = [0, 0, 0]
        for edge in graph['edges']:
            a, b = edge['a'], edge['b']
            category = 0 if assignment[a] != assignment[b] else (1 if numa[a] != numa[b] else 2)
            totals[category] += edge['faces']
        assert tuple(totals) == expected and sum(totals) == 2927022
        results.append(dict(arm=name, cross_host_faces=totals[0],
                            same_host_cross_numa_faces=totals[1], within_host_same_numa_faces=totals[2]))
    permutation = final['full_rank_permutation_host_numa_group_major']
    assert sorted(permutation) == list(range(512)) and permutation[0] == 0
    for host in range(4):
        assert set(permutation[host * 128:(host + 1) * 128]) == {i for i in range(512) if hosts[i] == host}
        for domain in range(8):
            start = host * 128 + domain * 16
            assert set(permutation[start:start + 16]) == {i for i in range(512) if hosts[i] == host and domains[i] == domain}
    result = dict(passed=True, screen_sha256=hashlib.sha256((HERE / 'screen.json').read_bytes()).hexdigest(),
                  full_face_category_recomputations=results, parent_host_membership_preserved=True,
                  rank_zero_first_bijection=True, four_hosts_128_ranks_eight_domains_16_ranks=True,
                  cross_numa_change_vs_original_percent=(732712 / 710081 - 1) * 100,
                  cross_numa_reduction_vs_parent_percent=(1 - 732712 / 1097554) * 100,
                  limits='Graph checks only. Physical topology, memory page placement and solver speedup are unmeasured.')
    (HERE / 'root-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
