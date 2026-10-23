"""Verify hashes for the fixed, source-only preflight payload."""
from pathlib import Path
import argparse
import hashlib
import json


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    args = ap.parse_args()
    root = Path(args.root)
    payload = root / 'payload'
    manifest = json.loads((payload / 'source-sha256.json').read_text())['files']
    actual = {str(p.relative_to(payload)): p for p in payload.rglob('*')
              if p.is_file() and not p.is_symlink() and p.name != 'source-sha256.json'
              and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    assert set(actual) == set(manifest), (sorted(set(actual) - set(manifest)),
                                         sorted(set(manifest) - set(actual)))
    mismatch = {name: {'actual': sha256(path), 'expected': manifest[name]}
                for name, path in actual.items() if sha256(path) != manifest[name]}
    assert not mismatch, mismatch
    print(json.dumps({'passed': True, 'source_files': len(manifest), 'all_hashes_match': True}, indent=2))


if __name__ == '__main__':
    main()
