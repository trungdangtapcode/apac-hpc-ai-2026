#!/usr/bin/env python3
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
