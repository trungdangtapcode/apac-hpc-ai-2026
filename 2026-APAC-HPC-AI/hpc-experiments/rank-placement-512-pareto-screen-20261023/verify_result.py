#!/usr/bin/env python3
"""Recompute the chosen placement and reproduce search in isolated outputs."""
from pathlib import Path
from collections import Counter
import contextlib
import hashlib
import importlib.util
import io
import json
import tempfile

HERE = Path(__file__).resolve().parent
R = HERE.parent


def main():
    graph_path = R / 'rank-placement-512-screen-20261023/graph.json'
    numa_path = R / 'rank-placement-512-numa-screen-20261023/screen.json'
    graph = json.loads(graph_path.read_text())
    numa = json.loads(numa_path.read_text())
    screen_path = HERE / 'screen.json'
    before = screen_path.read_bytes()
    data = json.loads(before)
    assert data['input_hashes']['rank_graph_sha256'] == hashlib.sha256(graph_path.read_bytes()).hexdigest()
    assert data['input_hashes']['fixed_host_numa_screen_sha256'] == hashlib.sha256(numa_path.read_bytes()).hexdigest()
    candidate = data['best_feasible']
    hosts = candidate['rank_to_host']
    domains = candidate['rank_to_logical_numa_group_within_host']
    assert len(hosts) == len(domains) == 512 and Counter(hosts) == {i: 128 for i in range(4)}
    groups = [[tuple(i for i in range(512) if hosts[i] == h and domains[i] == n)
               for n in range(8)] for h in range(4)]
    assert all(len(g) == 16 for host in groups for g in host)
    old_groups = numa['optimized_fixed_host_mapping']['numa_group_members_by_host']
    assert {frozenset(g) for host in old_groups for g in host} == {frozenset(g) for host in groups for g in host}
    permutation = candidate['full_rank_permutation_host_numa_group_major']
    assert sorted(permutation) == list(range(512)) and permutation[0] == 0
    assert permutation == [r for host in groups for group in host for r in group]
    totals = [0, 0, 0]
    external = [0] * 4
    for edge in graph['edges']:
        a, b, faces = edge['a'], edge['b'], edge['faces']
        category = 0 if hosts[a] != hosts[b] else (1 if domains[a] != domains[b] else 2)
        totals[category] += faces
        if category == 0:
            external[hosts[a]] += faces
            external[hosts[b]] += faces
    assert totals == [283819, 710003, 1933200] and sum(totals) == 2927022
    assert external == candidate['host_metrics']['external_interface_faces_by_host']
    assert 283741 <= totals[0] <= 337324 and totals[1] <= 710081
    cells = [sum(graph['cells_by_rank'][i] for i in range(512) if hosts[i] == h) for h in range(4)]
    assert cells == candidate['host_metrics']['cell_totals_by_host'] and sum(cells) == 65334765
    spec = importlib.util.spec_from_file_location('pareto_search', HERE / 'screen.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='pareto-replay-') as td:
        temp = Path(td)
        module.OUTPUT_PATH = temp / 'screen.json'
        module.QUALIFICATION_PATH = temp / 'qualification.json'
        with contextlib.redirect_stdout(io.StringIO()):
            module.main()
        replay = json.loads(module.OUTPUT_PATH.read_text())
        assert replay['best_feasible'] == candidate, 'Bounded replay did not reproduce chosen mapping'
    assert screen_path.read_bytes() == before, 'Original accepted screen changed'
    result = dict(passed=True, input_screen_sha256=hashlib.sha256(before).hexdigest(),
        independent_category_faces=totals, fixed_32_group_memberships_preserved=True,
        ranks_per_host=128, ranks_per_logical_numa_group=16,
        host_external_face_totals=external, host_cell_totals=cells,
        host_cut_reduction_vs_original_percent=(1 - totals[0] / 337324) * 100,
        same_host_numa_cut_reduction_vs_original_faces=710081 - totals[1],
        same_host_numa_cut_reduction_vs_original_percent=(1 - totals[1] / 710081) * 100,
        isolated_replay_selected_mapping_identical=True, original_accepted_screen_unchanged=True,
        limits='Two face-category proxies only; cell balance is worse than original. No physical NUMA, traffic, or solver speedup proof.')
    (HERE / 'root-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
