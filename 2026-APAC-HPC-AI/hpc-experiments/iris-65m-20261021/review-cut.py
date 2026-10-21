"""Review the sealed 65M decomposition; this is not solver acceptance."""
from pathlib import Path
import json, hashlib, re, statistics, datetime

r = Path(__file__).resolve().parent
d = r / 'collected/2293752'
a = d / 'artifacts/ready-N56-h742'
for relative, digest in json.loads((d / 'evidence-sha256.json').read_text()).items():
    assert hashlib.sha256((d / relative).read_bytes()).hexdigest() == digest
c = json.loads((d / 'collection.json').read_text())
assert sorted(c['processors']) == sorted('processor' + str(i) for i in range(56))
assert '2293752|COMPLETED|0:0|161|56|1|iris031' in c['accounting']
t = (a / 'logFiles/decomposePar.log').read_text()
assert re.search(r'^End\s*$', t, re.M)
assert 'FOAM FATAL' not in t and 'scalar=64' in t and 'OPENFOAM=2512' in t
assert 'hierarchical [56]' in t
# Indented records are per-rank; the unindented summary counts each cut once.
cells = [int(v) for v in re.findall(r'^    Number of cells\s*=\s*(\d+)', t, re.M)]
faces = [int(v) for v in re.findall(r'^    Number of processor faces\s*=\s*(\d+)', t, re.M)]
neighbors = [int(v) for v in re.findall(r'^    Number of processor patches\s*=\s*(\d+)', t, re.M)]
cut_faces = int(re.search(r'^Number of processor faces\s*=\s*(\d+)', t, re.M)[1])
assert len(cells) == len(faces) == len(neighbors) == 56
assert sum(cells) == 65334765 and sum(faces) == 2 * cut_faces
expected = {'U', 'k', 'nuTilda', 'nut', 'omega', 'p'}
assert len(c['zero_fields']) == 56
assert all(expected.issubset(set(v)) for v in c['zero_fields'].values())
for current, source in [('system/fvSolution', 'system/fvSolution.fixedIter'),
                        ('system/controlDict', 'system/controlDict.noWrite'),
                        ('system/decomposeParDict', 'system/decomposeParDict')]:
    assert (a / current).read_bytes() == (r / 'shared-case' / source).read_bytes()
b = (a / 'system/include/caseDefinition').read_text()
orig = (r / 'shared-case/system/include/caseDefinition').read_text()
def normalize(text):
    return re.sub(r'^(nCores|nHierarchical)\s+.*$', r'\1 ALLOWED;', text, flags=re.M)
assert normalize(b) == normalize(orig)
assert re.search(r'^nCores\s+56;', b, re.M)
assert re.search(r'^nHierarchical\s+\(7 4 2\);', b, re.M)
assert '03.1-cut-65M-N56: PASS' in (d / 'runs/2293752.out').read_text()
assert not (d / 'runs/2293752.err').read_text().strip()
assert 'Restore 0/' in (a / 'logFiles/restore0Dir.log').read_text()
out = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           job='2293752', state='DECOMPOSITION_AND_RESTORE_PASS', elapsed_seconds=161,
           allocated_cpus=56, nodes=1, node='iris031', serial_tasks=1,
           total_cells=sum(cells), processor_count=len(cells),
           cell_min=min(cells), cell_max=max(cells),
           cell_max_over_mean_percent=100 * (max(cells) / statistics.mean(cells) - 1),
           processor_faces_max=max(faces), processor_faces_sum=sum(faces),
           unique_cut_faces=cut_faces, max_neighbor_patches=max(neighbors),
           max_rss_KiB_reported=32011392, max_rss_GiB=32011392 / 1024**2,
           total_cpu_time_reported='00:02:37.720', verified_full_initialization=False,
           score=None,
           limits='Decomposition only; no solver/Cd. All ranks are on one node; graph cut is not off-node traffic. NUMA/bandwidth/hardware counters not collected; billed SU unknown.')
(r / 'cut-review.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
