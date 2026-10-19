#!/usr/bin/env python3
"""Draw a reproducible, evidence-linked research map with standard SVG tools.

Run from any working directory. Requires Python 3 and rsvg-convert.
The figure is a dated view of retained research, not live scheduler state.
"""
from pathlib import Path
from html import escape
import json
import subprocess

HERE = Path(__file__).resolve().parent
EVIDENCE = json.loads((HERE.parent / 'evidence.json').read_text())
ROWS = EVIDENCE['rows']
W, H = 1800, 2430
parts = []
texts = []


def raw(value):
    parts.append(value)


def box(x, y, w, h, fill='#ffffff', stroke='none', radius=18, sw=1):
    raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def line(x1, y1, x2, y2, color='#90a0b4', width=2, arrow=False, dash=False):
    raw(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{width}"'
        + (' marker-end="url(#arrow)"' if arrow else '')
        + (' stroke-dasharray="6 6"' if dash else '') + '/>')


def text(x, y, value, size=21, color='#29394d', weight=400, anchor='start'):
    texts.append(dict(x=x, y=y, text=value, size=size))
    raw(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')


def title(y, index, value, detail):
    text(60, y, index, 17, '#4d6c8b', 700)
    text(112, y, value, 25, '#14243a', 700)
    text(1740, y, detail, 17, '#5c6c7d', anchor='end')


def pill(x, y, w, label, fill='#e8eff8', color='#35577d', size=17):
    box(x, y, w, 32, fill, radius=16)
    text(x + w / 2, y + 22, label, size, color, 600, 'middle')


def card(x, y, n, heading, color, fill='#ffffff'):
    box(x, y, 536, 294, fill, '#d9e2ed', sw=1.4)
    box(x, y, 536, 6, color, radius=3)
    pill(x + 24, y + 20, 40, n, color, '#ffffff', 19)
    text(x + 78, y + 44, heading, 24, '#14243a', 700)


def gpu(x, y, n, color, label):
    for i in range(n):
        xx = x + i * 28
        box(xx, y, 21, 25, color, radius=4)
        for offset in (6, 13, 20):
            line(xx - 3, y + offset, xx, y + offset, color, 1.5)
            line(xx + 21, y + offset, xx + 24, y + offset, color, 1.5)
    text(x + (n * 28 - 7) / 2, y + 49, label, 16, color, 600, 'middle')


def number(job):
    return ROWS[str(job)]['good_tokens_s']


raw(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="figure-title figure-desc">
<title id="figure-title">Qwen research journey: from working deployment to a measured kernel interaction</title>
<desc id="figure-desc">Six illustrated H200 research stages, a good output throughput trajectory, rejected branches, a separate H100 lane and the remaining verification loop. Dated evidence reviewed 19 October 2026 at 06:14 UTC. The 2938.628 H200 peak is a single locally accepted observation; independent interaction repeat and official accuracy are unverified.</desc>
<defs>
<linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f1f6fd"/><stop offset=".55" stop-color="#fafbfe"/><stop offset="1" stop-color="#edf7f4"/></linearGradient>
<linearGradient id="hero" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#12345b"/><stop offset="1" stop-color="#176962"/></linearGradient>
<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0,0 L8,4 L0,8 Z" fill="#7b91ab"/></marker>
</defs>
<rect width="1800" height="2430" fill="url(#background)"/>
<g font-family="DejaVu Sans, sans-serif">''')

text(60, 66, 'QWEN / THE RESEARCH JOURNEY', 20, '#34678b', 700)
text(60, 120, 'Make it work. Measure it. Improve it. Verify it.', 42, '#12243b', 700)
text(60, 157, '29 Sep–19 Oct 2026  •  Qwen3-235B-A22B-Instruct-2507-FP8  •  SGLang serving', 21, '#586b80')
pill(1380, 43, 360, 'Evidence: 19 Oct 2026, 06:14 UTC', '#e0eaf4', '#35516f', 16)
box(60, 185, 1680, 78, 'url(#hero)')
text(86, 218, 'FIXED WORKLOAD', 16, '#bde8e1', 700)
text(86, 244, '~4,000 input → 200 output tokens', 21, '#ffffff', 600)
text(655, 218, 'GOOD REQUEST', 16, '#bde8e1', 700)
text(655, 244, 'TTFT ≤ 3,000 ms AND request mean ITL ≤ 20 ms', 20, '#ffffff', 600)
text(1260, 218, 'SCORE / GATE', 16, '#bde8e1', 700)
text(1260, 244, 'good requests/s × 200; ≥90% jointly good', 19, '#ffffff', 600)

title(307, 'A', 'H200: six stages of improvement', '16 GPUs • selected milestones, not isolated causal effects')
x1, x2, x3 = 60, 632, 1204
y1, y2 = 332, 676

# Stage 1: deployment and the benchmark itself, shown as a request stream.
card(x1, y1, '01', 'Build a trustworthy test', '#397d96')
for i in range(3):
    box(88 + i * 31, 416 + i * 6, 23, 34, '#d3e7ef', '#5c91a6', radius=4)
line(186, 443, 240, 443, arrow=True)
box(254, 416, 140, 52, '#eaf4f8', radius=8)
text(324, 448, 'Serving API', 19, '#28576e', 600, 'middle')
line(401, 443, 451, 443, arrow=True)
box(465, 416, 101, 52, '#eaf4f8', radius=8)
text(516, 448, 'Metrics', 18, '#28576e', 600, 'middle')
text(127, 489, 'AIPerf', 15, '#397d96', 600, 'middle')
text(84, 508, 'Slurm smoke test; later a separate PBS cluster.', 19)
text(84, 539, 'Pin model, containers, protocol and output checks.', 19)
text(84, 570, 'Fix startup races, offline paths and port conflicts.', 19)
text(84, 607, '60 s warmup → 120 s scoring → 30 s grace', 19, '#397d96', 600)

# Stage 2: the actual GPU split, rather than an abstract topology name.
card(x2, y1, '02', 'Repair topology + KV transfer', '#496fb4')
gpu(658, 416, 4, '#668bd2', 'Prefill 1 · TP4')
gpu(812, 416, 4, '#668bd2', 'Prefill 2 · TP4')
line(944, 440, 1000, 440, arrow=True)
box(1015, 411, 134, 49, '#e9edfb', radius=8)
text(1082, 442, '8-GPU decode', 16, '#496fb4', 600, 'middle')
text(658, 508, '17 named trials: failures are not valid scores.', 19)
text(658, 539, 'Request-scoped NIXL enables TP4 → TP8 KV.', 19)
text(658, 570, 'Retained: 8 prefill GPUs + 8 decode GPUs.', 19)
text(658, 607, '1,912.300 good tokens/s · 22415 · N48', 23, '#496fb4', 700)

# Stage 3: pipeline ingredients; the combination is not a one-factor ablation.
card(x3, y1, '03', 'Improve the serving pipeline', '#7162b3')
for xx, label in [(1230, 'Route'), (1394, 'Graphs'), (1558, 'Transfer')]:
    box(xx, 416, 145, 52, '#eeebf8', radius=8)
    text(xx + 72, 448, label, 18, '#65559e', 600, 'middle')
line(1377, 442, 1390, 442, arrow=True)
line(1541, 442, 1554, 442, arrow=True)
text(1230, 508, 'Chunk 4096 + load: 2,140.096 (23114).', 19)
text(1230, 539, 'Round robin, graphs, MNNVL: 2,592.162.', 19)
text(1230, 570, 'FlashInfer decode attention: 2,632.610.', 19)
text(1230, 607, 'N56 pipeline: 2,667.465 · 24263', 23, '#7162b3', 700)
line(601, 481, 626, 481, arrow=True)
line(1173, 481, 1198, 481, arrow=True)
line(1472, 633, 1472, 667, arrow=True)
text(1437, 654, 'then', 15, '#667a91', anchor='end')

# Stage 4 sits on the right: follow the serpentine arrows to the left.
card(x3, y2, '04', 'Choose kernels for each phase', '#b47b2d')
box(1230, 756, 218, 56, '#fbf0df', radius=8)
text(1339, 778, 'PREFILL', 14, '#94601d', 700, 'middle')
text(1339, 802, 'DeepGEMM', 20, '#94601d', 600, 'middle')
box(1472, 756, 230, 56, '#f4eadc', radius=8)
text(1587, 778, 'DECODE', 14, '#94601d', 700, 'middle')
text(1587, 802, 'auto / HPC-Ops', 20, '#94601d', 600, 'middle')
text(1230, 851, 'Prefill and decode have different batch shapes.', 19)
text(1230, 882, 'DeepGEMM prefill: +1.74% vs fresh control.', 19)
text(1230, 913, 'Independent repeat supports the H200 gain.', 19)
text(1230, 950, '2,716.787 good tokens/s · 24327 · N56', 23, '#9e6a26', 700)

card(x2, y2, '05', 'Refine chunk size + client load', '#8b60b1')
for xx, width, label in [(658, 110, '4096'), (799, 144, '6144'), (974, 171, '8192')]:
    box(xx, 763, width, 34, '#dbcbe9', radius=6)
    text(xx + width / 2, 787, label, 19, '#704796', 600, 'middle')
text(658, 819, 'Prefill token budget; the prompt stays ~4k.', 17, '#6e5b81')
text(658, 858, 'Chunk 6144 / N56: 2,737.410 (24573).', 19)
text(658, 889, 'Chunk 8192 / N58: 2,780.403 (24721).', 19)
text(658, 920, 'Auto-decode N60: 2,839.532 (24722).', 19)
text(658, 950, 'N60 repeat: 2,836.531 · 24732', 23, '#8053a7', 700)

card(x1, y2, '06', 'Combine the useful changes', '#248973', '#f1fbf6')
pill(84, 750, 215, 'BEST OBSERVED H200', '#d6eee3', '#216d56', 15)
text(84, 818, f'{number(24724):,.3f}', 48, '#176d57', 700)
text(404, 815, 'good tokens/s', 19, '#3b6c60')
text(84, 856, 'DeepGEMM prefill · chunk 8192 · HPC-Ops decode', 18)
text(84, 887, 'N58 · job 24724 · +5.69% vs fresh N58 control', 19, '#176d57', 600)
text(84, 918, 'One accepted deployment; own repeat pending.', 19)
text(84, 949, 'Official accuracy and global optimum unverified.', 18, '#596a66')
line(1198, 824, 1173, 824, arrow=True)
line(626, 824, 601, 824, arrow=True)

# Data-based visual trajectory: selected observations, uneven categorical x-axis.
title(1023, 'B', 'What the measured progression looks like', 'good output tokens/s • H200 only')
box(60, 1048, 1680, 240, '#ffffff', '#d9e2ed')
series = [('22415', 'N48'), ('23114', 'N52'), ('23778', 'N52'), ('23975', 'N52'),
          ('24327', 'N56'), ('24573', 'N56'), ('24721', 'N58'), ('24722', 'N60'), ('24724', 'N58')]
xpos = [136 + i * 189 for i in range(len(series))]
ypos = [1194 - (number(job) - 1850) / 1150 * 104 for job, _ in series]
line(112, 1205, 1686, 1205, '#dbe3ed', 1)
raw('<polyline points="' + ' '.join(f'{x},{y:.3f}' for x, y in zip(xpos, ypos)) + '" fill="none" stroke="#338f86" stroke-width="4"/>')
for x, y, (job, load) in zip(xpos, ypos, series):
    raw(f'<circle cx="{x}" cy="{y:.3f}" r="6" fill="#248973" stroke="white" stroke-width="2"/>')
    text(x, y - 14, f'{number(job):,.0f}', 20, '#176d57', 700, 'middle')
    text(x, 1232, job, 17, '#586d85', anchor='middle')
    text(x, 1258, load, 17, '#586d85', anchor='middle')
text(84, 1080, '+53.67% from the early baseline; settings and loads differ. This is research progression, not a cumulative causal ablation.', 18, '#617185')
text(60, 1323, 'Latest matched N58 change: mean ITL 16.498 → 14.998 ms; TTFT 784.526 → 871.991 ms; joint success 98.907%.', 21, '#255e55', 600)
text(60, 1354, 'Faster repeated decode intervals can offset slower first-token arrival. This is a plausible explanation, not a profiled causal proof.', 19, '#627387')

# Closed branches are shown as actual research outcomes, not successes.
title(1407, 'C', 'Branches that taught us where to stop', 'Failure, invalid output and slower performance have different meanings')
failed = [
    ('Larger chunk: 12288', '2,714.261 · job 24723', '−2.38% at matched N58', 'CLOSE: slower than chunk 8192'),
    ('Disable prefill graphs', '1,590.313 · job 24426', 'Only 72.72% jointly good', 'REJECT: fails the latency gate'),
    ('Equal TP8 / EP2 layout', 'Job 24375', 'Output checks fail', 'QUARANTINE: score is not valid'),
    ('Startup / warmup failures', 'NIXL, router, job 24588', 'No scored benchmark result', 'DIAGNOSE: retain logs, no score'),
]
for i, (heading, a, b, c) in enumerate(failed):
    x = 60 + i * 429
    box(x, 1430, 393, 158, '#fff8f5', '#eadbd5')
    text(x + 20, 1465, heading, 19, '#97573b', 700)
    text(x + 20, 1500, a, 19)
    text(x + 20, 1530, b, 18)
    text(x + 20, 1564, c, 15.5, '#97573b', 600)

# Independent hardware lane: only within-platform comparisons are implied.
title(1641, 'D', 'H100: a separate research lane', 'PBS • 16 GPUs • no pooled H100/H200 ranking')
for x in (60, 632, 1204):
    box(x, 1666, 536, 190, '#eff5fb', '#d3dfed')
text(84, 1702, 'Re-measure on the second platform', 22, '#345f89', 700)
text(84, 1739, 'H200 DeepGEMM gains did not transfer reliably.', 19)
text(84, 1770, 'Faster weight loading did not prove goodput gain.', 19)
text(84, 1801, 'Both-phase HPC-Ops earned repeated support.', 19)
text(84, 1832, 'N50 repeat: 2,371.341 · job 221339', 21, '#345f89', 600)
text(656, 1702, 'Refine the operating load', 22, '#345f89', 700)
text(656, 1739, 'N52 repeat: 2,411.304 · job 221589', 20)
text(656, 1786, '2,430.891 good tokens/s', 32, '#345f89', 700)
text(656, 1824, 'N54 · job 221590 · best observed, own repeat pending', 18)
text(1228, 1702, 'Profile → test communication', 22, '#345f89', 700)
text(1228, 1739, 'Ring all-reduce appears in sealed GPU traces.', 19)
text(1228, 1770, 'N54 repeat → N56 → prefill NCCL Tree trial.', 19)
text(1228, 1801, '221645 → 221646 → 221669; outcomes pending.', 18)
text(1228, 1832, 'Prove actual Tree activation before crediting it.', 18, '#345f89', 600)
line(601, 1757, 626, 1757, arrow=True)
line(1173, 1757, 1198, 1757, arrow=True)

# Future gates, not claimed future gains.
title(1912, 'E', 'What makes the next improvement credible', 'Planned / pending at the evidence cutoff; not new measurements')
next_steps = [
    ('1  Reproduce + bound the load', ['Fresh control 24736; interaction repeat 24737.', 'N60 interaction 24738; auto N62 trial 24733.', 'Promote only if the gain survives local gates.']),
    ('2  Establish official accuracy', ['Freeze model, payloads, scripts and runtime.', 'Run the organiser harness and reference tasks.', '≥99% reference score is still unverified.']),
    ('3  Profile, then choose the next target', ['Profile the actual winning H200 combination.', 'Test demonstrated kernel / collective costs.', 'Close losing branches; avoid blind larger sweeps.']),
]
for x, (heading, body) in zip((60, 632, 1204), next_steps):
    box(x, 1937, 536, 159, '#ffffff', '#cdded9')
    text(x + 24, 1973, heading, 22, '#28715f', 700)
    for i, item in enumerate(body):
        text(x + 24, 2012 + i * 29, item, 18.5)

# The research loop and record keeping are the foundation, not another score.
box(60, 2140, 1680, 168, '#e8eff7', radius=20)
text(84, 2178, 'THE LOOP USED THROUGHOUT', 17, '#4e6885', 700)
labels = ['Inspect logs', 'Hypothesis', 'Freeze', 'Measure', 'Validate', 'Repeat', 'Promote / close']
for i, label in enumerate(labels):
    x = 84 + i * 235
    box(x, 2198, 208, 44, '#ffffff', radius=9)
    text(x + 104, 2226, label, 18, '#294660', 600, 'middle')
    if i < len(labels) - 1:
        line(x + 210, 2220, x + 231, 2220, arrow=True)
raw('<path d="M1598,2247 L1598,2268 L188,2268 L188,2247" fill="none" stroke="#7b91ab" stroke-width="2" marker-end="url(#arrow)"/>')
text(900, 2295, 'Preserve raw logs + failed runs + frozen configs + checksums + controls + credit ledger + dated decisions.', 19, '#425c78', anchor='middle')
text(60, 2350, 'READING KEY', 16, '#506881', 700)
text(220, 2350, 'Arrows = research progression. N = active requests. All throughput figures = good output tokens/s.', 19, '#53677c')
text(60, 2387, 'Sources: REPORT.md, evidence.json and the linked run reviews. Snapshot only; no live queue status, official accuracy or global-optimum claim.', 18, '#53677c')
raw('</g></svg>')
svg = HERE / 'research-journey.svg'
svg.write_text('\n'.join(parts) + '\n')
for suffix, fmt in [('png', 'png'), ('pdf', 'pdf')]:
    subprocess.run(['rsvg-convert', '--format', fmt, '--output', str(HERE / f'research-journey.{suffix}'), str(svg)], check=True)

validation = dict(
    evidence_cutoff='2026-10-19 06:14 UTC',
    svg_dimensions=[W, H],
    plotted_jobs=[j for j, _ in series],
    plotted_values_from_evidence=True,
    trajectory_gain_percent=(number(24724) / number(22415) - 1) * 100,
    matched_n58_gain_percent=(number(24724) / number(24721) - 1) * 100,
    svg_text_nodes=len(texts),
    text_baselines_inside_canvas=all(0 <= t['x'] <= W and 0 <= t['y'] <= H for t in texts),
    external_bitmap_assets=False,
    new_gpu_jobs_submitted=False,
    note='Milestone arrows are descriptive. Rendered PNG must also be visually inspected.',
)
assert validation['text_baselines_inside_canvas']
assert round(validation['trajectory_gain_percent'], 2) == 53.67
assert round(validation['matched_n58_gain_percent'], 2) == 5.69
(HERE / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
print(json.dumps(validation, indent=2))
