#!/usr/bin/env python3
"""Refresh a committed local archive bundle and test recovery without source trees."""
import argparse, datetime, hashlib, json, os, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--store', type=Path, default=ROOT.with_name(ROOT.name + '-artifacts'))
    a = p.parse_args()
    store = a.store.resolve()
    subprocess.run(['python3', str(ROOT / 'tools/verify_git_tree.py'), '--report', str(store / 'git-integrity.json')], check=True)
    integrity = json.loads((store / 'git-integrity.json').read_text())
    bundle = store / 'research-history.bundle'
    tmp = store / 'research-history.bundle.tmp'
    subprocess.run(['git', '-c', 'pack.threads=4', '-c', 'pack.windowMemory=64m', 'bundle', 'create', str(tmp), '--all'], cwd=ROOT, check=True)
    subprocess.run(['git', 'bundle', 'verify', str(tmp)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    tmp.replace(bundle)
    rows = [json.loads(x) for x in (ROOT / 'backup/manifest.jsonl').read_text().splitlines()]
    source = 'workspace/notes/CURRENT.md'
    large = next(r['path'] for r in rows if r['storage'] == 'object' and r['path'].endswith('/inputs.json'))
    with tempfile.TemporaryDirectory(prefix='apac-milestone-recovery-') as temp:
        clone = Path(temp) / 'clone'
        subprocess.run(['git', 'clone', '-q', '--no-checkout', str(bundle), str(clone)], check=True)
        subprocess.run(['git', 'checkout', 'HEAD', '--', 'tools/restore_snapshot.py', 'backup/manifest.jsonl', source], cwd=clone, check=True)
        result = subprocess.check_output(['python3', str(clone / 'tools/restore_snapshot.py'), '--store', str(store), '--destination', str(Path(temp) / 'restored'), '--path', source, '--path', large], text=True)
        test = json.loads(result)
        test.update(passed=True, git_bundle_verified=True, cloned_head=integrity['head'], original_source_directories_used_for_restore=False)
    (store / 'bundle-recovery-test.json').write_text(json.dumps(test, indent=2) + '\n')
    (store / 'README.md').write_text(f'''# Local recovery set

The current Git bundle contains {integrity['commits']} commits, HEAD `{integrity['head']}`.
The initial 47 commits are the transparently dated retrospective import; later commits use actual work dates.

Keep this entire directory with the Git repository. To recover:

    git clone /path/to/apac-hpc-ai-research-artifacts/research-history.bundle apac-hpc-ai-research
    cd apac-hpc-ai-research
    python3 tools/verify_snapshot.py --store /path/to/apac-hpc-ai-research-artifacts --deep
    python3 tools/restore_snapshot.py --store /path/to/apac-hpc-ai-research-artifacts --destination ../restored-apac

`objects/` contains compressed content-addressed evidence. The two damaged collection archives in `local-review-objects/` require private review before any publication. Frozen runtime containers are opaque local objects, not automatically approved for redistribution. Public model weights are not copied. Only source data covered by the manifest is captured; no claim covers remote or unselected changes. Read BACKUP_SCOPE.md, REPRODUCIBILITY.md and dated milestone capture reports.

`git-integrity.json` checks actual captured Git blobs, fsck and a clean worktree. `bundle-recovery-test.json` verifies restoration from a fresh bundle clone without original source directories. `SHA256SUMS` checks compressed transport bytes; deep verification checks decompressed content. Git alone does not contain large objects. No GitHub upload has occurred. This same-machine copy does not protect against loss of the machine.
''')
    lines = []
    for file in sorted(store.rglob('*')):
        if not file.is_file() or file.name == 'SHA256SUMS':
            continue
        h = hashlib.sha256()
        with file.open('rb') as stream:
            for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                h.update(block)
        lines.append(h.hexdigest() + '  ' + str(file.relative_to(store)))
    (store / 'SHA256SUMS').write_text('\n'.join(lines) + '\n')
    print(json.dumps(dict(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), head=integrity['head'], commits=integrity['commits'], transport_files=len(lines), bundle_restore_passed=True, remote_uploaded=False)))


if __name__ == '__main__':
    main()
