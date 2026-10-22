"""Hash actual shared H200 assets against retained pinned reference identities."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'eagle3-h200-reference-assets-20261022'
MODEL = Path('/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8')
IMAGE = Path('/scratch/enroot-images/sglang-harbor.sqsh')
REFERENCE = ROOT / 'eagle3-pd-eager-prefill-r3-20261021'


def now():
    return datetime.now(timezone.utc).isoformat()


def stable_hash(path):
    before = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(8 << 20), b''):
            digest.update(block)
    after = path.stat()
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    assert all(getattr(before, f) == getattr(after, f) for f in fields), str(path)
    return dict(path=str(path), bytes=after.st_size, sha256=digest.hexdigest(),
                device=after.st_dev, inode=after.st_ino, mtime_ns=after.st_mtime_ns,
                ctime_ns=after.st_ctime_ns)


def save(value):
    path = OUT / 'VERIFICATION.json'
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def main():
    OUT.mkdir(exist_ok=False)
    staging_path = REFERENCE / 'target-staging-record.json'
    image_path = REFERENCE / 'asset-contract.json'
    staging = json.loads(staging_path.read_text())
    contract = json.loads(image_path.read_text())
    assert staging['complete'] and len(staging['verified']) == 33
    expected = []
    for name, row in sorted(staging['verified'].items()):
        assert Path(name).name == name
        if name.endswith('.safetensors'):
            assert row['official_lfs_sha256'] == row['sha256']
        expected.append((MODEL / name, row['bytes'], row['sha256']))
    img = contract['images'][IMAGE.name]
    expected.insert(0, (IMAGE, img['bytes'], img['sha256']))
    result = dict(started_utc=now(), state='VERIFYING', workers=3,
                  model_revision=staging['revision'], expected_files=len(expected),
                  expected_bytes=sum(x[1] for x in expected), files=[], errors=[],
                  reference_sources={str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in (staging_path, image_path)},
                  scope='Current H200 bytes versus retained pinned official model/LFS identities and image digest; no weights or image copied into the archive')
    save(result)

    def check(item):
        path, size, digest = item
        assert path.stat().st_size == size, f'Size mismatch: {path.name}'
        row = stable_hash(path)
        assert row['sha256'] == digest, f'SHA256 mismatch: {path.name}'
        row['passed'] = True
        return row

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(check, item): item[0] for item in expected}
        for future in as_completed(futures):
            path = futures[future]
            try:
                row = future.result()
            except Exception as error:
                result['errors'].append(dict(path=str(path), error=str(error)))
                print('HASH_FAIL', path.name, flush=True)
            else:
                result['files'].append(row)
                print('HASH_PASS', len(result['files']), '/', len(expected), path.name, flush=True)
            save(result)
    result['files'].sort(key=lambda row: row['path'])
    result.update(finished_utc=now(), state='PASS' if not result['errors'] and
                  len(result['files']) == len(expected) else 'FAIL')
    save(result)
    assert result['state'] == 'PASS', 'Asset identities did not all pass'


if __name__ == '__main__':
    main()
