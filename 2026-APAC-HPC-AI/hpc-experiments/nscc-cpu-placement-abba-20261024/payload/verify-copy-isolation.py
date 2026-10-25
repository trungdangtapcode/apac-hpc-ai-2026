"""Require that a copied OpenFOAM case shares no regular-file inodes with its baseline."""
import argparse
import json
import os
from pathlib import Path


def inventory(root):
    out = {}
    for path in root.rglob('*'):
        if path.is_file() and not path.is_symlink():
            stat = path.stat()
            out[str(path.relative_to(root))] = (stat.st_dev, stat.st_ino)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseline')
    parser.add_argument('copy')
    parser.add_argument('--output')
    args = parser.parse_args()
    baseline, copy = Path(args.baseline), Path(args.copy)
    left, right = inventory(baseline), inventory(copy)
    shared = sorted(set(left).intersection(right))
    assert shared, 'Expected matching relative case files were not found.'
    shared_inodes = set(left.values()).intersection(right.values())
    collisions = [rel for rel, inode in right.items() if inode in shared_inodes]
    assert not collisions, ('hard-linked files share inode with baseline', collisions[:20])
    report = {'passed': True, 'matching_regular_files': len(shared),
              'shared_regular_file_inodes': 0,
              'copy_policy': 'Independent inodes; reflink data sharing is permitted.'}
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
