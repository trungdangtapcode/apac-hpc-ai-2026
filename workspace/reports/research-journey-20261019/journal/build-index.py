"""Index retained research records without inventing missing decisions or dates."""
from pathlib import Path
from urllib.parse import quote
import collections
import datetime
import hashlib
import json
import os
import re
import subprocess

HOME = Path('/home/apacsc42')
ARCHIVE = HOME / 'apac-hpc-ai-research'
RESEARCH = HOME / '2026-APAC-HPC-AI/qwen-experiments'
OUT = Path(__file__).resolve().parent
SELF_PREFIX = str(OUT.relative_to(HOME)) + '/'
PREFIXES = ('2026-APAC-HPC-AI/qwen-experiments/', 'workspace/')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ARCHIVE, text=True).strip()
manifest = [json.loads(line) for line in (ARCHIVE / 'backup/manifest.jsonl').read_text().splitlines()]
# Exclude this generated journal itself to avoid a self-referential checksum inventory.
records = [r for r in manifest if r['path'].endswith('.md')
           and r['path'].startswith(PREFIXES) and not r['path'].startswith(SELF_PREFIX)]
assert len(records) == len({r['path'] for r in records})
entries = subprocess.check_output(['git', 'ls-tree', '-rz', 'HEAD'], cwd=ARCHIVE).split(b'\0')
blobs = {}
for entry in entries:
    if entry:
        info, name = entry.split(b'\t', 1)
        blobs[name.decode()] = info.split()[2].decode()

def link(path, label=None, anchor=''):
    target = quote(os.path.relpath(HOME / path, OUT), safe='/.-_')
    return '[' + (label or Path(path).name).replace('|', '\\|') + '](' + target + anchor + ')'

texts = {}
documents = []
for row in sorted(records, key=lambda r: r['path']):
    path = row['path']
    data = (HOME / path).read_bytes()
    assert row['storage'] == 'git'
    assert hashlib.sha256(data).hexdigest() == row['sha256'], 'Uncaptured source: ' + path
    assert hashlib.sha256((ARCHIVE / path).read_bytes()).hexdigest() == row['sha256']
    oid = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert blobs.get(path) == oid, 'Not committed at audited HEAD: ' + path
    texts[path] = data.decode()
    if path.startswith(PREFIXES[0]):
        family = 'Qwen experiment plans and reviews'
    elif path.startswith('workspace/research-autopilot/'):
        family = 'Historical session reports and execution policy'
    elif path.startswith('workspace/notes/'):
        family = 'Persistent decisions and conversation notes'
    elif path.startswith('workspace/tutorial/'):
        family = 'Learning notes and cluster tutorials'
    elif path.startswith('workspace/reports/'):
        family = 'Research explanations and preservation reports'
    else:
        family = 'Supporting context and historical package records'
    documents.append(dict(path=path, family=family, bytes=len(data), sha256=row['sha256'], git_blob=oid))

runs_path = PREFIXES[0] + 'RUNS.md'
sections = {m.group(1): m.group(2) for m in re.finditer(
    r'^## Job (\d+)\s*\n(.*?)(?=^## |\Z)', texts[runs_path], re.M | re.S)}
slurm = {p.name for p in (RESEARCH / 'runs').iterdir() if p.is_dir() and p.name.isdigit()}
# IDs explicitly retained in the dated handoff but without collected run directories.
current = texts['workspace/notes/CURRENT.md']
pending_match = re.search(r'H200 \*\*([\d/]+)\*\*', current)
assert pending_match, 'Handoff structure changed; review pending-ID extraction'
slurm.update(pending_match.group(1).split('/'))
budget = json.loads((RESEARCH / 'nscc-pbs/nscc-budget.json').read_text())
pbs = {r['job_id']: r for r in budget['jobs']}
jobs = []
for platform, ids in [('H200 / Slurm', sorted(slurm, key=int)), ('H100 / PBS', sorted(pbs))]:
    for job in ids:
        number = job.split('.')[0]
        refs = [p for p, text in texts.items() if re.search(r'(?<!\d)' + number + r'(?!\d)', text)]
        assert refs, 'No retained Markdown reference: ' + job
        section = sections.get(number) if platform.endswith('Slurm') else None
        triplet = bool(section and all(label in section for label in ['Mục đích', 'Quan sát', 'Bài học']))
        # Prefer a specific result/correction over broad accumulated session logs.
        def priority(path):
            name = Path(path).name.upper()
            result = 0 if ('RESULT' in name or 'REVIEW' in name or 'CORRECTION' in name) else 1
            broad = 1 if name in {'RUNS.MD', 'HISTORY.MD', 'TIMELINE.MD', 'CURRENT.MD', 'POLICY.MD', 'LATEST.MD'} else 0
            return broad, result, len(texts[path]), path
        best = sorted(refs, key=priority)[:2]
        if section:
            first = link(runs_path, 'Job note', '#job-' + number)
        else:
            first = link(best[0], 'Recorded rationale/result')
            best = best[1:]
        narrative = [first] + [link(path, Path(path).parent.name + '/' + Path(path).name) for path in best[:1]]
        jobs.append(dict(job=job, platform=platform, markdown_references=refs,
                         dedicated_run_section=bool(section), purpose_observation_lesson_fields=triplet,
                         raw_run_directory_present=(RESEARCH / 'runs' / number).is_dir() if platform.endswith('Slurm') else None,
                         bundle=pbs[job].get('bundle') if platform.endswith('PBS') else None,
                         table_links=' · '.join(narrative)))

counts = collections.Counter(d['family'] for d in documents)
summary = dict(audited_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), archive_head=head,
               retained_markdown_documents=len(documents), original_source_hashes_match=True,
               archive_inline_hashes_match=True, git_blobs_match_audited_head=True,
               own_jobs_indexed=len(jobs), jobs_without_markdown_reference=0,
               h200_jobs=sum(j['platform'].startswith('H200') for j in jobs), h100_jobs=len(pbs),
               dedicated_job_sections=sum(j['dedicated_run_section'] for j in jobs),
               explicit_purpose_observation_lesson_sections=sum(j['purpose_observation_lesson_fields'] for j in jobs),
               document_families=dict(counts), scheduler_checked=False, official_accuracy_verified=False,
               scope='All retained Markdown in the two named trees at the audited archive HEAD, excluding this generated journal. A textual reference is not a complete review or proof of original chat coverage. No remote, excluded, deleted or unrecorded material is certified.')
(OUT / 'coverage.json').write_text(json.dumps(dict(summary=summary, documents=documents, jobs=jobs), indent=2) + '\n')
lines = ['# Retained document index', '',
         'Generated from the captured manifest and verified against original source bytes, archive bytes and committed Git blobs. '
         'Read [the earlier overview](../REPORT.md) for the milestone explanation and [the job index](JOBS.md) for individual records.', '',
         f"Audit base: `{head}`. **{len(documents)} retained Markdown documents**. Dates and scheduler statements inside linked records are historical snapshots. "
         'Some original records retain their original Vietnamese text; this index does not rewrite those records.', '',
         'A link does not certify a complete analysis, a passing measurement or full conversation preservation. '
         'Supporting package/OpenFOAM history is catalogued for preservation only; active research remains Qwen.', '']
for family in counts:
    lines += ['## ' + family, '']
    for d in documents:
        if d['family'] == family:
            lines.append('- ' + link(d['path'], d['path']))
    lines.append('')
(OUT / 'DOCUMENTS.md').write_text('\n'.join(lines) + '\n')
lines = ['# Individual job records', '',
         f"This index covers **{len(jobs)} own research jobs**: {summary['h200_jobs']} H200/Slurm IDs and {summary['h100_jobs']} H100/PBS IDs. "
         f"All have at least one retained Markdown reference; {summary['dedicated_job_sections']} have a dedicated job section in the original run ledger. "
         f"{summary['explicit_purpose_observation_lesson_sections']} of those sections explicitly contain purpose, observation and lesson fields. "
         'The remaining entries link reports or plans and are not certified as equally detailed reviews.', '',
         'Job IDs and records identify historical evidence, not live scheduler state. A failed allocation or pending plan is not a measured performance result. '
         'The initial hello-GPU learning job 20201 is outside this Qwen research-job inventory and remains in the tutorials/notes.', '',
         'Search for a job ID, then read its purpose, result, interpretation, limitations and next decision in the linked records. '
         'Raw exports, frozen bundles and reviews are under the research tree; files above the inline limit require the sibling object store.', '']
for platform in ['H200 / Slurm', 'H100 / PBS']:
    lines += ['## ' + platform, '', '| Job | Assessment and decision records |', '|---|---|']
    lines += ['| ' + j['job'] + ' | ' + j['table_links'] + ' |' for j in jobs if j['platform'] == platform]
    lines.append('')
(OUT / 'JOBS.md').write_text('\n'.join(lines) + '\n')
(OUT / 'AUDIT.md').write_text('# What the coverage audit establishes\n\n'
    f"Audited at **{summary['audited_utc']}**, against committed archive HEAD `{head}`.\n\n"
    f"All **{len(documents)}** retained Markdown documents in the selected source trees match their captured SHA-256, archive copy and committed Git blob. "
    f"All **{len(jobs)}** indexed own research IDs occur in at least one of those documents. "
    f"There are **{summary['dedicated_job_sections']}** dedicated Slurm job sections, including **{summary['explicit_purpose_observation_lesson_sections']}** with explicit purpose/observation/lesson fields.\n\n"
    'This verifies that retained written records are in Git, rather than only on the temporary source filesystem. '
    'It does not prove every historical chat statement was written down, every deleted edit survived, every job has a complete causal analysis, or every old result passed later quality gates. '
    'An ID mentioned in a plan is not a completed review. The job index deliberately preserves this distinction.\n\n'
    'The authored journey is a retrospective, source-linked reading guide. Its summaries are written now; they are not fabricated original dated entries or a complete transcript. '
    'Read corrections before treating old conclusions as current. No scheduler, credit, accuracy or throughput rerun is performed by this audit.\n\n'
    'Scope is the manifest at the stated HEAD. Unselected source changes, remote uncollected jobs and authentication state are outside this claim. '
    'Large logs, traces and containers remain external objects: Git includes their manifests and recovery metadata, not all bytes. '
    'An off-host copy of that sibling store is still required.\n\n'
    'Rebuild with `python3 build-index.py` on the original machine after a completed capture. '
    'The script refuses source/archive/Git hash disagreements and excludes this generated journal to avoid self-reference. '
    'Later document edits make this a dated audit, not a continuous mirror. See `coverage.json` for every input path and hash.\n')
print(json.dumps(summary, indent=2))
