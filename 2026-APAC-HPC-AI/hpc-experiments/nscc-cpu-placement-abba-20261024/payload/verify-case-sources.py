"""Compare every accepted source file in a derived case with the frozen payload case."""
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
    parser.add_argument('--source', required=True, help='Frozen payload/case directory')
    parser.add_argument('--case', required=True, help='Derived working case directory')
    parser.add_argument('--accepted', required=True, help='accepted-source-manifest.json')
    parser.add_argument('--output')
    args = parser.parse_args()
    source, case = Path(args.source), Path(args.case)
    accepted = json.loads(Path(args.accepted).read_text())
    expected = set(accepted['files'])
    source_files = {str(p.relative_to(source)): p for p in source.rglob('*')
                    if p.is_file() and not p.is_symlink()}
    assert set(source_files) == expected, (sorted(set(source_files) - expected),
                                           sorted(expected - set(source_files)))
    protected_directories = {rel.split('/', 1)[0] for rel in expected if '/' in rel}
    protected = {}
    for path in case.rglob('*'):
        if not path.is_file() or path.is_symlink():
            continue
        rel = str(path.relative_to(case))
        if rel == 'rank-order.txt':
            continue
        parts = rel.split('/')
        if len(parts) == 1 or parts[0] in protected_directories:
            protected[rel] = path
    assert set(protected) == expected, (sorted(set(protected) - expected),
                                       sorted(expected - set(protected)))
    checked = []
    for rel in sorted(expected):
        src, dst = source_files[rel], case / rel
        assert dst.is_file() and not dst.is_symlink(), str(dst)
        want, got = sha256(src), sha256(dst)
        assert want == got, (rel, want, got)
        checked.append({'file': rel, 'sha256': got, 'bytes': dst.stat().st_size})
    report = {'passed': True, 'source_file_count': len(checked),
              'source_files_match_frozen_payload': True, 'files': checked}
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
