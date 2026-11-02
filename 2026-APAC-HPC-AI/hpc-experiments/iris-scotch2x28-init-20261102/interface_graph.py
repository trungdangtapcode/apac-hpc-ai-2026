"""Compare processor-boundary interfaces across the observed 28-rank package groups."""
from pathlib import Path
import collections, hashlib, json, re, sys

def graph(case, label):
    root = Path(case)
    files = {}
    edges = collections.Counter()
    patch_counts, cells = [], []
    decomp = (root / 'logFiles/decomposePar.log').read_text(errors='replace')
    cells = [int(v) for v in re.findall(r'(?m)^\s*Number of cells\s*=\s*(\d+)\s*$', decomp)]
    assert len(cells) == 56 and sum(cells) == 65_334_765 and min(cells) > 0
    for rank in range(56):
        path = root / f'processor{rank}/constant/polyMesh/boundary'
        raw = path.read_bytes(); files[str(path.relative_to(root))] = hashlib.sha256(raw).hexdigest()
        text = raw.decode(errors='strict'); count = 0
        for block in re.findall(r'\{([^{}]*)\}', text, re.S):
            if not re.search(r'\bneighbProcNo\b', block):
                continue
            count += 1
            def entry(name):
                m = re.search(r'\b' + name + r'\s+(\d+)\s*;', block)
                assert m, (path, name)
                return int(m[1])
            assert re.search(r'\btype\s+processor\w*\s*;', block)
            assert entry('myProcNo') == rank
            neighbor, faces = entry('neighbProcNo'), entry('nFaces')
            assert 0 <= neighbor < 56 and neighbor != rank and faces > 0
            edges[(rank, neighbor)] += faces
        assert count == len(re.findall(r'\bneighbProcNo\b', text)), rank
        patch_counts.append(count)
    for (a, b), count in edges.items():
        assert edges[(b, a)] == count, (a, b, count, edges[(b, a)])
    unique = [(a, b, n) for (a, b), n in edges.items() if a < b]
    total = sum(n for _, _, n in unique)
    cross = sum(n for a, b, n in unique if a // 28 != b // 28)
    per_rank = [sum(n for (a, _), n in edges.items() if a == rank) for rank in range(56)]
    mean = sum(cells) / 56
    return {'label': label, 'ranks': 56, 'cells_total': sum(cells),
        'max_cell_excess_over_mean_percent': 100 * (max(cells) / mean - 1),
        'unique_interface_faces': total, 'cross_package_interface_faces_logical_rank28': cross,
        'within_package_interface_faces': total - cross,
        'max_rank_interface_faces': max(per_rank), 'max_rank_neighbor_patches': max(patch_counts),
        'boundary_file_sha256': files,
        'interpretation': 'Graph faces and rank//28 groups only; not traffic, bytes, measured NUMA placement, latency, bandwidth, or solver speed.'}

def compare(control, candidate):
    ratios = {
        'cross_package_reduction_percent': 100 * (1 - candidate['cross_package_interface_faces_logical_rank28'] / control['cross_package_interface_faces_logical_rank28']),
        'total_interface_change_percent': 100 * (candidate['unique_interface_faces'] / control['unique_interface_faces'] - 1),
        'max_rank_faces_change_percent': 100 * (candidate['max_rank_interface_faces'] / control['max_rank_interface_faces'] - 1),
        'max_rank_neighbor_patch_change': candidate['max_rank_neighbor_patches'] - control['max_rank_neighbor_patches']}
    gates = {
        'cross_package_reduction_at_least_5_percent': ratios['cross_package_reduction_percent'] >= 5,
        'max_cell_excess_at_most_3_percent': candidate['max_cell_excess_over_mean_percent'] <= 3,
        'total_interfaces_rise_at_most_10_percent': ratios['total_interface_change_percent'] <= 10,
        'worst_rank_faces_rise_at_most_10_percent': ratios['max_rank_faces_change_percent'] <= 10,
        'worst_rank_neighbor_patches_rise_at_most_2': ratios['max_rank_neighbor_patch_change'] <= 2}
    return {'control': control, 'candidate': candidate, 'changes': ratios, 'triage_gates': gates,
        'promote_to_mandatory_initialization': all(gates.values()),
        'scope': 'Predeclared experiment triage thresholds; not contest score, accuracy threshold, measured NUMA cost, or solver-speed prediction.'}

if __name__ == '__main__':
    c = graph(sys.argv[1], 'accepted-default-scotch')
    x = graph(sys.argv[2], 'candidate-scotch-2x28-weight-1x0.1')
    r = compare(c, x)
    Path(sys.argv[3]).write_text(json.dumps(r, indent=2) + '\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ('control','candidate')}, indent=2))
    sys.exit(0 if r['promote_to_mandatory_initialization'] else 10)
