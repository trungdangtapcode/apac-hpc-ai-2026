#!/usr/bin/env python3
"""Freeze reviewed English documents and resolve only evidence actually packaged.

This operates in staging. It never changes the live team folder or ZIP.
"""
from pathlib import Path
from urllib.parse import unquote
import hashlib
import json
import os
import re

W = Path(__file__).resolve().parents[1]
O = W / 'submission-review/ai-final-update-20261101'
B = O / 'package-files'
R = W / 'reports/ai-final-report-20261030'
TEAM = W / 'VNUHCM - TripleU'
MAP = O / 'package-file-map.json'
sha = lambda data: hashlib.sha256(data).hexdigest()
initial = json.loads((B / 'package-file-map.json').read_text())
files = {}
for target, source in initial.items():
    target = target.replace('AI_Task/logs/AI_Task/logs/', 'AI_Task/logs/')
    if target == 'AI_Task/logs/package-file-map.json':
        continue
    if target == 'AI_Task/logs/latest-results.md':
        target = 'AI_Task/logs/measured/latest-results.md'
    assert target.startswith('AI_Task/logs/') and '..' not in Path(target).parts
    assert target not in files
    files[target] = source

sources = {}
doc_names = {
    'PRESENTATION_PLAN.md': 'PRESENTATION_PLAN.md',
    'EVIDENCE_CARDS.md': 'EVIDENCE_CARDS.md',
    'PANEL_QA.md': 'PANEL_QA.md',
    'FINAL_REPORT.md': 'REPORT.md',
    'TALK_SCRIPT_EN.md': 'TALK_SCRIPT_EN.md',
    'TEACHER_FEEDBACK_RESPONSE.md': 'FEEDBACK_RESPONSE.md',
    'MOCK_QA_EVIDENCE.md': 'MOCK_QA_EVIDENCE.md',
    'RESEARCH_JOURNEY.md': 'JOURNEY_COVERAGE.md',
}
for name, source_name in doc_names.items():
    source = R / source_name
    staged = B / name
    staged.write_bytes(source.read_bytes())
    target = 'AI_Task/logs/' + name
    files[target] = str(staged)
    sources[target] = source

manifest_target = 'AI_Task/logs/research-20261101/source-manifest.json'
manifest = json.loads(Path(files[manifest_target]).read_text())
for entry in manifest['entries']:
    entry['path'] = entry['path'].replace('AI_Task/logs/AI_Task/logs/', 'AI_Task/logs/')
    if entry['path'] in files and entry.get('source_path'):
        sources[entry['path']] = Path(entry['source_path'])
Path(files[manifest_target]).write_text(json.dumps(manifest, indent=2) + '\n')

# Extra exact report copies retain their original resolution base as well.
for target in files:
    if '/source-reports/' in target:
        suffix = target.split('/source-reports/', 1)[1]
        sources[target] = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments') / suffix

# Link identity uses exact retained bytes, including pre-existing package evidence.
by_hash = {}
for path in sorted((TEAM / 'AI_Task/logs').rglob('*')):
    if path.is_file():
        by_hash.setdefault(sha(path.read_bytes()), str(path.relative_to(TEAM)))
for target, source in files.items():
    by_hash[sha(Path(source).read_bytes())] = target
by_source = {str(source.resolve()): target for target, source in sources.items()}
by_source[str((W / 'VNUHCM - TripleU/Presentation/TripleU_APAC2026_Presentation.pptx').resolve())] = 'Presentation/TripleU_APAC2026_Presentation.pptx'
by_source[str((O / 'TripleU_APAC2026_Presentation.pptx').resolve())] = 'Presentation/TripleU_APAC2026_Presentation.pptx'

unpackaged = []
rewritten = 0
for target, original in sources.items():
    if not target.endswith('.md'):
        continue
    path = Path(files[target])
    body = original.read_text() if original.is_file() else path.read_text()
    def resolve_link(match):
        global rewritten
        label, raw = match.groups()
        if raw.startswith(('http://', 'https://', '#')):
            return match.group(0)
        local, separator, fragment = raw.strip('<>').partition('#')
        resolved = (original.parent / unquote(local)).resolve()
        destination = by_source.get(str(resolved))
        if destination is None and resolved.is_file():
            destination = by_hash.get(sha(resolved.read_bytes()))
        if destination:
            relative = os.path.relpath(destination, str(Path(target).parent))
            rewritten += 1
            return f'[{label}](<{relative}{separator + fragment if separator else ""}>)'
        unpackaged.append({'document': target, 'label': label, 'retained_source': str(resolved)})
        return f'{label} (retained research source: `{resolved}`; outside this compact package)'
    body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', resolve_link, body)
    path.write_text(body)

# Explain the package's current route without modifying the frozen serving entry.
readme_target = 'AI_Task/logs/README.md'
readme_path = Path(files[readme_target])
readme_path.write_text('''# AI submission: current evidence and presentation guide

Updated 1 November 2026. The selected entry remains the replicated H200 N64 recipe; no final alternative established a useful improvement. The serving scripts and earlier raw evidence are preserved.

- [Final AI report](FINAL_REPORT.md) separates the historical repeated H200 mean, the native reproduction, isolated higher points and the final fresh-control tests.
- [Concise English speaking script](TALK_SCRIPT_EN.md), [pacing plan](PRESENTATION_PLAN.md), [teacher response](TEACHER_FEEDBACK_RESPONSE.md) and [Q&A](MOCK_QA_EVIDENCE.md) support the 16-slide main AI route. AI backups 17–34 are hidden; the preserved HPC section is slides 35–42. The public combined talk is 15–20 minutes plus a separate 10-minute Q&A; the AI 10–12-minute target must leave the agreed HPC time.
- [Final nine-job verification](research-20261101/README.md) contains exact selected exports, losslessly compressed request records, comparison reports and the per-job ledger. Eight jobs use N64; 27781 is N54. Two controls have distinct comparison roles.
- [Detailed retained metrics](measured/latest-results.md) and the historical evidence folders preserve earlier successful, failed and losing branches. [Research coverage](RESEARCH_JOURNEY.md) explains what appears in the main talk or appendix.

H100 and H200 scores remain separate. The direct transfer tests ran on 16 H200; none established a useful gain above the team's prospective 1% gate. Small smoke/retrieval checks do not certify official model quality: the organiser's ≥99%-reference evaluation remains UNKNOWN. Corrected readers passed saved datasets on CPU; a complete fresh portable GPU replay after repair is not claimed. Human rehearsal and live slideshow/device checks are prepared, not recorded as performed.

Some full research sources remain outside this compact package. Those are labelled explicitly rather than linked as if available here. The complete research archive retains their provenance; model weights, authentication state and disposable caches are excluded. The separate HPC payload is preserved independently.
''')

# Check relative Markdown destinations against the eventual package mapping.
known = {str(path.relative_to(TEAM)) for path in TEAM.rglob('*') if path.is_file()} | set(files)
links = 0
for target, staged in files.items():
    if not target.endswith('.md'):
        continue
    for raw in re.findall(r'\]\(([^)]+)\)', Path(staged).read_text()):
        if raw.startswith(('http://', 'https://', '#')):
            continue
        local = raw.strip('<>').split('#')[0]
        resolved = os.path.normpath(os.path.join(str(Path(target).parent), unquote(local)))
        assert resolved in known, (target, raw, resolved)
        links += 1

# Recompute transformed evidence hashes; retain original source hashes as provenance.
for entry in manifest['entries']:
    path = Path(files[entry['path']])
    entry['bytes'] = path.stat().st_size
    entry['sha256'] = sha(path.read_bytes())
manifest['note'] = 'Package paths are relative to the team folder. Original source hashes remain separate from transformed or losslessly compressed package bytes.'
Path(files[manifest_target]).write_text(json.dumps(manifest, indent=2) + '\n')
MAP.write_text(json.dumps(files, indent=2) + '\n')
(B / 'package-file-map.json').write_text(json.dumps(files, indent=2) + '\n')
(O / 'package-doc-validation.json').write_text(json.dumps({
    'passed': True,
    'explicit_files': len(files),
    'bytes': sum(Path(source).stat().st_size for source in files.values()),
    'relative_links_checked': links,
    'resolved_source_links': rewritten,
    'sources_explicitly_outside_compact_package': unpackaged,
    'stage_only': True,
    'hpc_changed': False,
}, indent=2) + '\n')
print(json.dumps({'files': len(files), 'relative_links_checked': links, 'source_links_rewritten': rewritten, 'outside_source_references': len(unpackaged)}))
