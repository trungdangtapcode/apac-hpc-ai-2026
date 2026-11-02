#!/usr/bin/env python3
"""Stage documentary edits from the current accepted release; retain tested runtime bytes."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import urllib.parse

from ai_release_context import review_path

W = Path(__file__).resolve().parents[1]
O = review_path(W)
OLD = W / 'submission-review/ai-acceptance-update-20261102'
T = W / 'VNUHCM - TripleU'
B = O / 'package-files'
B.mkdir(exist_ok=True)
sha = lambda data: hashlib.sha256(data).hexdigest()
mapping = {}
for target in json.loads((OLD / 'package-file-map.json').read_text()):
    assert target.startswith('AI_Task/') and '..' not in Path(target).parts
    source = T / target
    assert source.is_file(), target
    dest = B / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    mapping[target] = str(dest)

readme = Path(mapping['AI_Task/job_scripts/README.md'])
body = readme.read_text().split('# TripleU Qwen Basic deployment\n', 1)[1]
body = body.replace(
    'compute CPU job 27152 for both retained raw datasets; a whole-allocation\n'
    'end-to-end run after that repair has not been performed.',
    'compute CPU job 27152 for both retained raw datasets. The subsequent complete\n'
    'portable entry, job 28197, passed both semantic routes, the original official\n'
    'client, corrected readers, the performance gate and cleanup in 611 seconds.')
body = body.replace(
    'The organiser full-set accuracy check (at least 99% of reference) remains\n'
    'unverified. Small output checks and SLA acceptance do not certify it.',
    'Model-quality evaluation follows the organiser Q1 protocol against the\n'
    'unchanged official FP8 reference. The checkpoint and model precision are\n'
    'preserved; performance and answer-accuracy measurements remain distinct.')
readme.write_text('''# TripleU Qwen Basic deployment

## Submission scope and verified execution

This Basic submission retains the official Qwen3-235B-A22B-Instruct-2507-FP8
checkpoint, all model layers and experts, and BF16 KV. It does not requantise
the checkpoint or intentionally approximate model computation. The work tunes
the serving topology, supported backends, scheduling and KV-transfer metadata.
Model-quality evaluation follows the organiser Q1 protocol.

The complete portable entry passed as **job 28197** on **16 H200 GPUs / N64**:
**3051.518173 good output tokens/s**, **1881/1907 joint SLA passes (98.636602%)**,
zero request errors/cancellations, and successful readers, gate and cleanup.
Total allocation duration was **10 min 11 s**. These are measured serving
results; no numerical full-set model-quality score is asserted.

The earlier readiness failure 28194 and reader failures remain historical
evidence under `../logs/`; they are not the status of this accepted entry.

## Retained configuration
'''+body)
root = readme.parent
sums = root / 'SHA256SUMS'
sums.write_text(''.join(f'{sha(p.read_bytes())}  {p.relative_to(root)}\n'
                        for p in sorted(root.rglob('*')) if p.is_file() and p != sums))

reports = W / 'reports/ai-final-report-20261030'
docs = {'FINAL_REPORT.md': 'REPORT.md', 'PRESENTATION_PLAN.md': 'PRESENTATION_PLAN.md',
        'EVIDENCE_CARDS.md': 'EVIDENCE_CARDS.md', 'PANEL_QA.md': 'PANEL_QA.md',
        'TALK_SCRIPT_EN.md': 'TALK_SCRIPT_EN.md', 'TEACHER_FEEDBACK_RESPONSE.md': 'FEEDBACK_RESPONSE.md',
        'MOCK_QA_EVIDENCE.md': 'MOCK_QA_EVIDENCE.md', 'RESEARCH_JOURNEY.md': 'JOURNEY_COVERAGE.md'}
origins = {}
for target, source in docs.items():
    rel = 'AI_Task/logs/' + target
    shutil.copy2(reports / source, mapping[rel])
    origins[rel] = reports / source

index = Path(mapping['AI_Task/logs/README.md'])
index.write_text('''# TripleU AI submission: native FP8 serving on 16 H200 GPUs

The Basic deliverable preserves the published Qwen FP8 model, BF16 KV and all
layers/experts. It supplies reconstruction instructions, the text transport patch,
one deployment-plus-official-benchmark job and the presentation. No model weights,
authentication material or disposable runtime cache are bundled.

## Complete portable verification

**Job 28197 completed 0:0 in 10 min 11 s** on two H200 nodes at N64. It measured
**3051.518173 good output tokens/s**, with **1881/1907 requests passing both
latency limits (98.636602%)**, zero errors/cancellations, both P/D semantic paths,
the original official client, corrected readers, performance gate and cleanup.
This reproduces the retained operating level; it is not a matched new speedup.
The earlier failed jobs remain in the historical evidence folders.

- [Reconstruct and run](../job_scripts/README.md).
- [Final AI report](FINAL_REPORT.md), [result review](acceptance-20261102/RESULTS.md)
  and [latest measured results](measured/latest-results.md).
- [English speaking script](TALK_SCRIPT_EN.md), [presentation plan](PRESENTATION_PLAN.md),
  [evidence cards](EVIDENCE_CARDS.md) and [technical Q&A](PANEL_QA.md).
- [Nine final H200 verification allocations](research-20261101/README.md) retain
  eight N64 observations and one N54 observation, with separate branch controls.

## Evaluation provenance

The 98.636602% value is joint request-latency success, not answer accuracy.
Model-quality evaluation follows organiser Q1 against its unchanged official FP8
reference. The submitted methods preserve the target model and precision; no
team full-set quality score or completed organiser review is claimed here.
The Q&A distinguishes source checks, local output screens and that evaluation.
H100 and H200 scores remain separate. The existing HPC payload is preserved.

The main deck contains 16 AI slides followed by eight HPC slides; 18 additional
AI slides are hidden backups. The combined talk is 15–20 minutes with a separate
10-minute Q&A. The AI rehearsal target leaves the agreed HPC speaking time.
''')
latest = Path(mapping['AI_Task/logs/measured/latest-results.md'])
latest.write_text(latest.read_text().replace(
    'Official organiser accuracy is UNKNOWN.',
    'Model-quality evaluation follows the organiser Q1 protocol against its unchanged FP8 reference; no numerical full-set quality result is asserted.'))

# Keep report references portable or explicitly identify evidence outside the compact package.
hash_targets = {sha(Path(src).read_bytes()): target for target, src in mapping.items()}
source_targets = {str(origin.resolve()): target for target, origin in origins.items()}
for target, origin in origins.items():
    staged = Path(mapping[target])
    def rewrite(match):
        label, raw = match.groups()
        if raw.startswith(('http://', 'https://', '#')):
            return match.group(0)
        local, sep, fragment = raw.strip('<>').partition('#')
        resolved = (origin.parent / urllib.parse.unquote(local)).resolve()
        dest = source_targets.get(str(resolved))
        if dest is None and resolved.is_file():
            dest = hash_targets.get(sha(resolved.read_bytes()))
        if dest:
            relative = os.path.relpath(dest, str(Path(target).parent))
            return f'[{label}](<{relative}{sep + fragment if sep else ""}>)'
        return f'{label} (source: `{resolved.name}`, retained outside this compact package)'
    staged.write_text(re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rewrite, staged.read_text()))

allowed = {'AI_Task/job_scripts/README.md', 'AI_Task/job_scripts/SHA256SUMS',
           'AI_Task/job_scripts/deploy-and-benchmark.sh'}
publish = {target: source for target, source in mapping.items()
           if target.startswith('AI_Task/logs/') or target in allowed}
(O / 'package-file-map.json').write_text(json.dumps(mapping, indent=2) + '\n')
(O / 'publish-file-map.json').write_text(json.dumps(publish, indent=2) + '\n')
(O / 'PREPARATION.json').write_text(json.dumps({
    'prepared_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'stage_only': True, 'mapped_files': len(mapping), 'job_id': 28197,
    'runtime_changes': [], 'changes': 'AI documentary framing and slide 16; README/checksum metadata only',
    'quality_score_claimed': False, 'organiser_upload': False, 'HPC_modified': False,
}, indent=2) + '\n')
print(json.dumps({'mapped_files': len(mapping), 'publish_files': len(publish), 'runtime_changes': []}))
