"""Verify SHA-256 identities for all fixed payload files except the manifest."""
from pathlib import Path
import argparse
import hashlib
import json


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.root)
    payload = root / 'payload'
    expected = json.loads((payload / 'source-sha256.json').read_text())['files']
    actual = {str(path.relative_to(payload)): path for path in payload.rglob('*')
              if path.is_file() and not path.is_symlink() and path.name != 'source-sha256.json'
              and '__pycache__' not in path.parts and path.suffix != '.pyc'}
    assert set(actual) == set(expected), (sorted(set(actual) - set(expected)), sorted(set(expected) - set(actual)))
    mismatch = {name: {'actual': sha256(path), 'expected': expected[name]}
                for name, path in actual.items() if sha256(path) != expected[name]}
    assert not mismatch, mismatch
    print(json.dumps({'passed': True, 'source_files': len(expected), 'all_hashes_match': True}, indent=2))


if __name__ == '__main__':
    main()
