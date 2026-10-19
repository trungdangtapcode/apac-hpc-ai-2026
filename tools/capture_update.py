#!/usr/bin/env python3
"""Capture an explicit milestone without replacing history or scheduling work.

The selection is a JSON list of paths relative to the original source root.
No deletion, Git commit, authentication or network access is performed.
"""
import argparse, datetime, fcntl, hashlib, importlib.util, json, os, shutil, stat, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('capture_policy', ROOT / 'tools/build_snapshot.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def write_json(path, data):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(path)


def verify_object(path, digest, size):
    proc = subprocess.Popen(['zstd', '-q', '-d', '-c', str(path)], stdout=subprocess.PIPE)
    h, count = hashlib.sha256(), 0
    for block in iter(lambda: proc.stdout.read(4 * 1024 * 1024), b''):
        h.update(block)
        count += len(block)
    if proc.wait() or (h.hexdigest(), count) != (digest, size):
        raise ValueError('Object verification failed: ' + digest)


def capture(args):
    source, store = args.source.resolve(), args.store.resolve()
    rows = {r['path']: r for r in map(json.loads, (ROOT / 'backup/manifest.jsonl').read_text().splitlines())}
    index = json.loads((store / 'objects-index.json').read_text())
    objects = {r['sha256']: r for r in index}
    selected = json.loads(args.selection.read_text())
    candidates = {}
    for relative in selected:
        p = Path(relative)
        if p.is_absolute() or '..' in p.parts or p.parts[0] not in {'workspace', '2026-APAC-HPC-AI', 'AGENTS.md'}:
            raise ValueError('Selection outside authorised sources')
        start = source / p
        if start.is_symlink() or not start.resolve().is_relative_to(source):
            raise ValueError('Symlink or source escape')
        for file in sorted(start.rglob('*')) if start.is_dir() else [start]:
            rel = str(file.relative_to(source))
            if file.is_symlink():
                raise ValueError('Symlink in selected milestone: ' + rel)
            if file.is_dir():
                continue
            if any(part in policy.PRUNE for part in file.relative_to(source).parts):
                continue
            if policy.policy(rel):
                raise ValueError('Sensitive or excluded selection: ' + rel)
            dest = 'provenance/current-home-AGENTS.md' if rel == 'AGENTS.md' else rel
            candidates[dest] = file
    prepared = []
    for dest, file in sorted(candidates.items()):
        before = file.stat()
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('Nonregular source')
        synthetic = file.name == 'inputs.json' or file.name.endswith('-inputs.json')
        digest, flags = policy.inspect(file, synthetic=synthetic)
        if not flags and file.name.endswith(('.zip', '.tar', '.tar.gz', '.tgz', '.tar.xz')):
            flags = policy.archive_scan(file)
        after = file.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('Unstable source: ' + dest)
        if flags:
            raise ValueError('Potential sensitive content; inspect privately: ' + dest + ' rules=' + ','.join(flags))
        if rows.get(dest, {}).get('sha256') == digest:
            continue
        row = dict(path=dest, bytes=before.st_size, sha256=digest, mode=stat.S_IMODE(before.st_mode), mtime_ns=before.st_mtime_ns,
                   secret_scan='synthetic public benchmark dataset' if synthetic else 'patterns plus archive members' if file.name.endswith(('.zip', '.tar', '.tar.gz', '.tgz', '.tar.xz')) else 'patterns')
        prepared.append((file, row))
    changed, new_objects = [], []
    for file, row in prepared:
        digest = row['sha256']
        if row['bytes'] > 1024 * 1024:
            obj = 'objects/' + digest[:2] + '/' + digest + '.zst'
            target = store / obj
            if digest not in objects:
                target.parent.mkdir(parents=True, exist_ok=True)
                tmp = target.with_suffix('.tmp')
                subprocess.run(['zstd', '-q', '-T1', '-3', '-f', str(file), '-o', str(tmp)], check=True)
                verify_object(tmp, digest, row['bytes'])
                tmp.replace(target)
                objects[digest] = dict(sha256=digest, bytes=row['bytes'], stored_bytes=target.stat().st_size, object=obj)
                new_objects.append(digest)
            elif not (store / objects[digest]['object']).is_file():
                raise ValueError('Previously captured object missing')
            row.update(storage='object', object=objects[digest]['object'])
            old_inline = ROOT / row['path']
            if rows.get(row['path'], {}).get('storage') == 'git' and old_inline.is_file():
                old_inline.unlink()
        else:
            target = ROOT / row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(target.suffix + '.tmp')
            shutil.copyfile(file, tmp)
            assert hashlib.sha256(tmp.read_bytes()).hexdigest() == digest
            os.chmod(tmp, row['mode'])
            os.utime(tmp, ns=(row['mtime_ns'], row['mtime_ns']))
            tmp.replace(target)
            row['storage'] = 'git'
        changed.append(dict(path=row['path'], previous_sha256=rows.get(row['path'], {}).get('sha256'), sha256=digest, storage=row['storage']))
        rows[row['path']] = row
    manifest = ROOT / 'backup/manifest.jsonl'
    tmp = manifest.with_suffix('.jsonl.tmp')
    tmp.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in sorted(rows.values(), key=lambda r: r['path'])))
    tmp.replace(manifest)
    write_json(store / 'objects-index.json', list(objects.values()))
    summary = json.loads((ROOT / 'backup/summary.json').read_text())
    summary.update(last_incremental_capture_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), retained_files=len(rows), git_files=sum(r['storage'] == 'git' for r in rows.values()), logical_bytes=sum(r['bytes'] for r in rows.values()), git_worktree_bytes=sum(r['bytes'] for r in rows.values() if r['storage'] == 'git'), unique_external_objects=len(objects), external_object_bytes=sum(r['stored_bytes'] for r in objects.values()))
    write_json(ROOT / 'backup/summary.json', summary)
    directories = set(json.loads((ROOT / 'backup/directories.json').read_text()))
    for path in rows:
        directories.update(str(p) for p in Path(path).parents if str(p) != '.')
    write_json(ROOT / 'backup/directories.json', sorted(directories))
    result = dict(captured_utc=summary['last_incremental_capture_utc'], selected_paths=selected, scanned_files=len(candidates), changed=changed, new_objects_verified=new_objects, deleted_paths=[], remote_uploaded=False, scope='Only explicit selected paths; unselected source changes are not claimed captured.')
    write_json(args.report, result)
    print(json.dumps(dict(scanned_files=len(candidates), changed_files=len(changed), new_objects=len(new_objects), report=str(args.report))), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--selection', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--source', type=Path, default=Path('/home/apacsc42'))
    p.add_argument('--store', type=Path, default=ROOT.with_name(ROOT.name + '-artifacts'))
    a = p.parse_args()
    with (ROOT / 'backup/capture.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        capture(a)
