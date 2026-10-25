"""Verify an externally sealed payload without creating or changing its manifest."""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest_path = root / 'payload-sha256.json'
    assert manifest_path.is_file(), 'Parent must create and review payload-sha256.json before any submission.'
    manifest = json.loads(manifest_path.read_text())
    expected = manifest['files']
    actual = {str(p.relative_to(root)): p for p in (root / 'payload').rglob('*')
              if p.is_file() and not p.is_symlink() and p.name != 'payload-sha256.json'
              and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    assert set(actual) == set(expected), (sorted(set(actual) - set(expected)),
                                          sorted(set(expected) - set(actual)))
    mismatches = {name: {'actual': sha256(path), 'expected': expected[name]}
                  for name, path in actual.items() if sha256(path) != expected[name]}
    assert not mismatches, mismatches
    print(json.dumps({'passed': True, 'files': len(expected), 'all_hashes_match': True}, indent=2))


if __name__ == '__main__':
    main()
