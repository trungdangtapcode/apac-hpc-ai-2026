#!/usr/bin/env python3
"""Illustrate conserved face categories, without interpreting them as runtime."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2] / '2026-APAC-HPC-AI/hpc-experiments/rank-placement-512-numa-screen-20261023/root-review.json'


def main():
    data = json.loads(SOURCE.read_text())
    assert data['passed']
    rows = data['full_face_category_recomputations']
    assert len(rows) == 3 and all(sum(r[k] for k in (
        'cross_host_faces', 'same_host_cross_numa_faces', 'within_host_same_numa_faces')) == 2927022 for r in rows)
    names = ['Original contiguous', 'Host mapping only', 'Host + NUMA refinement']
    categories = [('cross_host_faces', 'Across logical hosts', '#EB811B'),
                  ('same_host_cross_numa_faces', 'Same host, across logical NUMA groups', '#375C6A'),
                  ('within_host_same_numa_faces', 'Within the same logical NUMA group', '#CAD3D4')]
    fig, ax = plt.subplots(figsize=(12.6, 5.8))
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FAFAFA')
    left = [0] * 3
    for key, label, color in categories:
        values = [r[key] for r in rows]
        ax.barh(range(3), values, left=left, color=color, height=.52, label=label)
        for i, value in enumerate(values):
            ax.text(left[i] + value / 2, i, f'{value:,}', ha='center', va='center',
                    fontsize=11, color='white' if key == 'same_host_cross_numa_faces' else '#23373B')
        left = [a + b for a, b in zip(left, values)]
    ax.set_yticks(range(3), names, fontsize=12)
    ax.invert_yaxis()
    ax.set_xlim(0, 3000000)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x / 1e6:.1f}'))
    ax.set_xlabel('Unique interface faces (millions); each bar totals 2,927,022', fontsize=11)
    ax.grid(axis='x', alpha=.15)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='y', length=0)
    fig.suptitle('The same partitions: a placement trade-off', fontsize=20, x=.03, ha='left', color='#23373B')
    fig.text(.03, .89, 'Host cuts decrease 22.59%; refined NUMA cuts remain 3.19% above the original logical control.',
             fontsize=11, color='#23373B')
    ax.legend(loc='upper left', bbox_to_anchor=(0, -.25), frameon=False, ncol=1, fontsize=10)
    fig.text(.03, .025, 'Graph categories only. Eight logical NUMA groups per host are assumed; topology, traffic and speedup are unmeasured.',
             fontsize=10, color='#737F82')
    fig.subplots_adjust(left=.24, right=.97, top=.81, bottom=.36)
    folder = HERE / 'figures'
    outputs = []
    for extension in ('png', 'svg'):
        path = folder / ('placement-tradeoff.' + extension)
        fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
        outputs.append(dict(path=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    plt.close(fig)
    (folder / 'placement-tradeoff-provenance.json').write_text(json.dumps(dict(
        source=str(SOURCE), source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        all_faces_retained=True, numerical_source=data['full_face_category_recomputations'],
        interpretation='Conserved interface-face categories under logical placement; not an estimated speedup.',
        outputs=outputs), indent=2) + '\n')


if __name__ == '__main__':
    main()
