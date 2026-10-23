#!/usr/bin/env python3
"""Show both face-count proxies, without assigning hardware cost weights."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
R = HERE.parents[2] / '2026-APAC-HPC-AI/hpc-experiments'
OLD = R / 'rank-placement-512-numa-screen-20261023/root-review.json'
NEW = R / 'rank-placement-512-pareto-screen-20261023/root-review.json'


def main():
    old = json.loads(OLD.read_text())
    new = json.loads(NEW.read_text())
    assert old['passed'] and new['passed']
    rows = old['full_face_category_recomputations']
    points = [(r['cross_host_faces'], r['same_host_cross_numa_faces']) for r in rows]
    points.append(tuple(new['independent_category_faces'][:2]))
    assert points == [(337324, 710081), (261110, 1097554), (261110, 732712), (283819, 710003)]
    fig, ax = plt.subplots(figsize=(11.8, 6.9))
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FAFAFA')
    ax.set_xlim(245000, 353000)
    ax.set_ylim(635000, 1140000)
    ax.add_patch(Rectangle((245000, 635000), 337324 - 245000, 710081 - 635000,
                           color='#DDEADD', alpha=.7, zorder=0))
    ax.axhline(710081, color='#737F82', linestyle='--', linewidth=1)
    ax.axvline(337324, color='#737F82', linestyle='--', linewidth=1)
    labels = ['Original contiguous', 'Host mapping only', 'Aggressive two-level', 'Balanced two-level']
    colors = ['#737F82', '#A94442', '#EB811B', '#375C6A']
    offsets = [(-130, 12), (12, -20), (12, 25), (15, -18)]
    for (x, y), label, color, offset in zip(points, labels, colors, offsets):
        ax.scatter([x], [y], s=105, color=color, edgecolor='#FAFAFA', linewidth=1.4, zorder=4)
        ax.annotate(f'{label}\n{x:,} / {y:,}', (x, y), xytext=offset,
                    textcoords='offset points', fontsize=11, color=color,
                    ha='left', va='center')
    ax.annotate('', points[2], points[1], arrowprops=dict(arrowstyle='->', color='#EB811B', lw=1.6, shrinkA=10, shrinkB=10))
    ax.annotate('', points[3], points[2], arrowprops=dict(arrowstyle='->', color='#375C6A', lw=1.6, shrinkA=10, shrinkB=10))
    ax.text(249000, 654000, 'At or below the original on both face counts', fontsize=10, color='#375C6A')
    formatter = FuncFormatter(lambda x, _: f'{x / 1000:.0f}')
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_xlabel('Cross-host unique interface faces (thousands)', fontsize=12)
    ax.set_ylabel('Same-host cross-NUMA unique interface faces (thousands)', fontsize=11)
    ax.grid(alpha=.15)
    for spine in ax.spines.values():
        spine.set_color('#CAD3D4')
    fig.suptitle('Placement choices: keep both face counts visible', x=.03, ha='left', fontsize=20, color='#23373B')
    fig.text(.03, .91, 'Lower is better on each axis. These are not latency, traffic or solver-speed measurements.', fontsize=11, color='#23373B')
    fig.text(.03, .045, 'Balanced NUMA total is only 78 faces below original; host cell-balance range is worse (0.627% vs 0.215%).', fontsize=10, color='#737F82')
    fig.text(.03, .018, 'All mappings are logical. Physical eight-domain topology and exact runtime placement remain unverified.', fontsize=10, color='#737F82')
    fig.subplots_adjust(left=.12, right=.97, top=.84, bottom=.17)
    folder = HERE / 'figures'
    outputs = []
    for ext in ('png', 'svg'):
        target = folder / ('placement-options.' + ext)
        fig.savefig(target, dpi=180, facecolor=fig.get_facecolor())
        outputs.append(dict(path=target.name, sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    plt.close(fig)
    (folder / 'placement-options-provenance.json').write_text(json.dumps(dict(
        sources=[dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (OLD, NEW)],
        labels=labels, points_host_and_same_host_numa_faces=points,
        no_physical_weight_or_speedup_model=True, outputs=outputs), indent=2) + '\n')


if __name__ == '__main__':
    main()
