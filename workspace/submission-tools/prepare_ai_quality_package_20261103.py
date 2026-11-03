#!/usr/bin/env python3
"""Stage final quality evidence and documentation; preserve accepted serving code."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import re
import runpy
import shutil
import urllib.parse
from datetime import datetime, timezone
from ai_release_context import review_path

W = Path(__file__).resolve().parents[1]
O = review_path(W)
S = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102')
D = W / 'reports/ai-quality-verification-20261103'
runpy.run_path(str(Path(__file__).with_name('prepare_ai_basic_polish_20261102.py')), run_name='__main__')
mapping = json.loads((O / 'package-file-map.json').read_text())
publish = json.loads((O / 'publish-file-map.json').read_text())
root = O / 'package-files/AI_Task/logs/quality-20261103'
root.mkdir(exist_ok=True)
origins = {}

def copy(source, relative, compressed=False):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if compressed:
        with source.open('rb') as src, target.open('wb') as dst:
            with gzip.GzipFile(filename='', mode='wb', fileobj=dst, mtime=0) as zipped:
                shutil.copyfileobj(src, zipped)
    else:
        shutil.copy2(source, target)
    origins[str(source.resolve())] = target
    return target

copy(S / 'client/aggregate_full.py', 'aggregate_full.py')
copy(S / 'prepared-4k/prepare-manifest.json', 'prepare-manifest.json')
copy(S / 'prepared-4k/compiled-corpus.jsonl', 'compiled-corpus.jsonl.gz', True)
copy(S / 'workflow/FULL_COMPARISON.json', 'FULL_COMPARISON.json')
copy(S / 'frozen-full8/FROZEN_PAYLOAD.json', 'FROZEN_PAYLOAD.json')
copy(S / 'workflow/CODE_GUARD.json', 'CODE_GUARD.json')
copy(S / 'reviews/full-terminal-accounting-20261103/ACCOUNTING.json', 'ACCOUNTING.json')
copy(S / 'reviews/full-terminal-accounting-20261103/sacct.txt', 'sacct.txt')
copy(S / 'reviews/API_PROMPT_LENGTH_CHECK_FULL_24064.json', 'PROMPT_LENGTH_CHECK.json')
for name in ['FULL_RESULTS.md', 'METHODOLOGY.md']:
    copy(D / name, name)
for directory in ['final-independent-20261103', 'final-diagnostics-20261103']:
    for source in sorted((S / 'reviews' / directory).iterdir()):
        if source.is_file(): copy(source, 'reviews/' + directory + '/' + source.name)

ledger = json.loads((S / 'admission-full8/ledger.json').read_text())
runs = []
for role in ['reference', 'candidate']:
    for shard in range(8):
        job = ledger['jobs'][f'{role}-{shard:02}']['job']
        source = S / (f'jobs/full-ref-{shard:02}of08/runs/{job}/reference/evaluation' if role == 'reference' else f'jobs/full-cand-{shard:02}of08/AI_Task/logs/full-shards/{job}/evaluation')
        target = f'runs/{role}-{shard:02}'
        for name in ['run.json', 'summary.json']:
            copy(source / name, target + '/' + name)
        copy(source / 'responses.jsonl', target + '/responses.jsonl.gz', True)
        runs.append(dict(role=role, shard=shard, job=job, directory=target,
                         responses_sha256=hashlib.sha256((source/'responses.jsonl').read_bytes()).hexdigest()))
(root / 'RUNS.json').write_text(json.dumps(runs, indent=2) + '\n')
(root / 'replay.py').write_text('''#!/usr/bin/env python3
"""Recompute the complete paired quality score from lossless packaged answers."""
from pathlib import Path
import argparse, gzip, hashlib, json, shutil, subprocess, sys, tempfile
ROOT = Path(__file__).resolve().parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
if a.out.exists(): raise SystemExit('Refusing to overwrite an existing comparison')
runs = json.loads((ROOT/'RUNS.json').read_text())
with tempfile.TemporaryDirectory(prefix='tripleu-quality-replay-') as name:
    temp = Path(name)
    with gzip.open(ROOT/'compiled-corpus.jsonl.gz','rb') as src, (temp/'compiled-corpus.jsonl').open('wb') as dst:
        shutil.copyfileobj(src,dst)
    roles = {'reference': [], 'candidate': []}
    for run in runs:
        source = ROOT/run['directory']; dest = temp/run['directory']; dest.mkdir(parents=True)
        shutil.copy2(source/'run.json',dest/'run.json')
        with gzip.open(source/'responses.jsonl.gz','rb') as src, (dest/'responses.jsonl').open('wb') as dst:
            shutil.copyfileobj(src,dst)
        assert hashlib.sha256((dest/'responses.jsonl').read_bytes()).hexdigest() == run['responses_sha256']
        roles[run['role']].append(str(dest))
    command = [sys.executable,str(ROOT/'aggregate_full.py'),'--prepare-manifest',str(ROOT/'prepare-manifest.json'),
        '--compiled-corpus',str(temp/'compiled-corpus.jsonl'),'--reference-runs',*roles['reference'],
        '--candidate-runs',*roles['candidate'],'--out',str(a.out.resolve())]
    subprocess.run(command,check=True)
result=json.loads(a.out.read_text())
assert result['reference']['correct']==9460 and result['candidate']['correct']==9452
assert result['status']=='LOCAL_FULLSET_GATE_PASS'
print('Replayed 24,064 responses: reference 9460/12032; candidate 9452/12032; retention 99.915433%; local gate PASS.')
''')
(root / 'README.md').write_text('''# Full local MMLU-Pro accuracy-retention check

The same 12,032 questions were evaluated with a stock FP8 reference and the
optimised service, both on the same 16 H200 GPUs. Reference: 9,460 correct
(78.623670%). Candidate: 9,452 correct (78.557181%). Accuracy retention:
9,452 / 9,460 = **99.915433%**, passing the predeclared local 99% point gate.
All sixteen allocations completed with zero service errors. This is a team-run
quality regression check, not an official BTC certification or GPQA result.

Read [the result](FULL_RESULTS.md), [method](METHODOLOGY.md), and the independent
review for coverage, category losses, truncation/invalid handling and limits.
[RUNS.json](RUNS.json) maps each fixed paired shard to its actual Slurm job.
Raw answers and prepared prompts are losslessly compressed; original hashes and
source version identities are retained. Files are data, not new model weights.

## Replay the score without GPUs

Use Python 3.9 or later. The replay needs only the Python standard library and
a temporary directory with room for decompressed answers. From this directory:

```bash
sha256sum -c SHA256SUMS
python3 replay.py --out /tmp/tripleu-quality-replayed.json
```

Choose a new output path; existing files are refused. This reparses all saved
answers with the frozen scorer and verifies complete identical coverage. It is
not a second model inference run. Serving code remains the accepted payload in
`../../job_scripts/`; inherited `NOT_RUN` or `unknown` fields describe their
original performance-only snapshot, while this later evidence records the
separate completed quality test. No historical payload was rewritten to claim
an earlier test. Full research materials and raw runtime logs remain preserved
in the private research archive; no account credentials are bundled here.
''')

# Resolve packaged report links where evidence is present, otherwise state the source scope.
for source, target in origins.items():
    if target.suffix != '.md': continue
    def rewrite(match):
        label, raw = match.groups()
        if raw.startswith(('https://','http://','#')): return match.group(0)
        local, sep, fragment = raw.strip('<>').partition('#')
        resolved = str((Path(source).parent / urllib.parse.unquote(local)).resolve())
        mapped = origins.get(resolved)
        if mapped:
            return f'[{label}](<{os.path.relpath(mapped,target.parent)}{sep+fragment if sep else ""}>)'
        if Path(local).name == 'MATERIALS.md':
            return '[Package evidence and replay instructions](README.md)'
        return f'{label} (retained research source: `{Path(resolved).name}`)'
    target.write_text(re.sub(r'\[([^\]]+)\]\(([^)]+)\)',rewrite,target.read_text()))

# Replace outdated current-claim wording; preserve immutable historical result JSON.
for target in ['AI_Task/job_scripts/README.md','AI_Task/logs/README.md','AI_Task/logs/measured/latest-results.md']:
    p = Path(mapping[target]); text = p.read_text()
    text = text.replace('results; no numerical full-set model-quality score is asserted.', 'results. A later full local MMLU-Pro comparison retained 99.915433% of a measured stock FP8 reference score; this is separate from organiser Q1 certification.')
    text = text.replace('no\nteam full-set quality score or completed organiser review is claimed here.', 'the later full local MMLU-Pro check retains 99.915433% of stock reference accuracy. No completed organiser review is claimed here.')
    text = text.replace('no numerical full-set quality result is asserted.', 'the later full local MMLU-Pro comparison passes at 99.915433% accuracy retention; no organiser certification is claimed.')
    link = '../logs/quality-20261103/README.md' if '/job_scripts/' in target else ('../quality-20261103/README.md' if '/measured/' in target else 'quality-20261103/README.md')
    text += f'\n## Complete local answer-quality verification — 3 November 2026\n\nReference **9460/12032**, candidate **9452/12032**, accuracy retention **99.915433%**. Same 16 H200 and same prepared questions; all sixteen jobs completed, zero service errors. This measured local MMLU-Pro pass is distinct from the 98.636602% latency fraction and from organiser certification. [Method, retained answers and CPU replay]({link}).\n'
    p.write_text(text)
# Link the current packaged final report to the new portable quality documents.
p = Path(mapping['AI_Task/logs/FINAL_REPORT.md'])
t = p.read_text().replace('full quality results (source: `FULL_RESULTS.md`, retained outside this compact package)', '[full quality results](quality-20261103/FULL_RESULTS.md)').replace('methodology (source: `METHODOLOGY.md`, retained outside this compact package)', '[methodology](quality-20261103/METHODOLOGY.md)');p.write_text(t)
for directory in [root, Path(mapping['AI_Task/job_scripts/README.md']).parent]:
    sums = directory/'SHA256SUMS'
    sums.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(directory)}\n' for p in sorted(directory.rglob('*')) if p.is_file() and p!=sums))
for p in sorted(root.rglob('*')):
    if p.is_file():
        target = str(p.relative_to(O/'package-files'));mapping[target]=str(p);publish[target]=str(p)
(O/'package-file-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
(O/'publish-file-map.json').write_text(json.dumps(publish,indent=2)+'\n')
(O/'QUALITY_PREPARATION.json').write_text(json.dumps(dict(prepared_utc=datetime.now(timezone.utc).isoformat(),staged_only=True,full_quality_jobs=16,questions_per_role=12032,local_quality_gate='PASS',official_quality_certification=False,runtime_files_changed=[],quality_files=sum(1 for p in root.rglob('*') if p.is_file())),indent=2)+'\n')
print('Staged complete lossless quality response evidence and replay; serving runtime unchanged.')
