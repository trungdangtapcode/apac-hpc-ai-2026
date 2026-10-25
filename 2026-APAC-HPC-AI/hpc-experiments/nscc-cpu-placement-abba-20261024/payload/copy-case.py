"""Make one checked, sequential case copy without hard links."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path


def regular_bytes(root):
    total = 0
    for path in root.rglob('*'):
        if path.is_file() and not path.is_symlink():
            total += path.stat().st_size
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('destination')
    parser.add_argument('--reserve-bytes', type=int, default=536870912)
    args = parser.parse_args()
    source, destination = Path(args.source), Path(args.destination)
    assert source.is_dir() and not destination.exists()
    destination.parent.mkdir(parents=True, exist_ok=True)
    apparent_bytes = regular_bytes(source)
    free_bytes = shutil.disk_usage(str(destination.parent)).free
    required_bytes = apparent_bytes + args.reserve_bytes
    assert free_bytes >= required_bytes, {'free_bytes': free_bytes,
                                          'estimated_copy_bytes': apparent_bytes,
                                          'required_with_reserve_bytes': required_bytes}
    subprocess.check_call(['cp', '-a', '--reflink=auto', str(source), str(destination)])
    report = {'passed': True, 'source': str(source), 'destination': str(destination),
              'regular_file_apparent_bytes': apparent_bytes, 'free_bytes_before_copy': free_bytes,
              'reserve_bytes': args.reserve_bytes,
              'copy_command': 'cp -a --reflink=auto; inode isolation is checked separately',
              'quota_limitations': 'Filesystem free-byte check does not prove a user/project quota allowance.'}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
