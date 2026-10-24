"""Require the actual identity arm to establish the 4x128 and 8x16 topology basis."""
import argparse
import json
from pathlib import Path
from mapping_common import read_nodefile, validate_probe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('identity')
    ap.add_argument('nodefile')
    ap.add_argument('--output')
    args = ap.parse_args()
    _, node_counts = read_nodefile(args.nodefile)
    _, summary = validate_probe(args.identity, node_counts)
    summary['passed'] = True
    summary['scope'] = 'Identity-arm placement only; not proof of candidate mapping or future-allocation stability.'
    text = json.dumps(summary, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
