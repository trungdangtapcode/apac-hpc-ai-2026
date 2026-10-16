"""Read-only PBS artifact snapshot over the existing authenticated SSH helper."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
REMOTE = '/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
HELPER = '/home/apacsc42/workspace/vpn-rootless/vpn.sh'


def remote(command, output, timeout=60):
    with output.open('wb') as handle:
        try:
            result = subprocess.run(
                ['bash', HELPER, 'ssh-batch', 'bash -lc ' + shlex.quote(command)],
                stdout=handle, stderr=subprocess.PIPE, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            output.with_suffix(output.suffix + '.stderr').write_bytes(error.stderr or b'')
            output.with_suffix(output.suffix + '.timeout.json').write_text(
                json.dumps({'timeout_s': timeout, 'partial_preserved': True}) + '\n')
            raise
    output.with_suffix(output.suffix + '.stderr').write_bytes(result.stderr)
    if result.returncode:
        raise RuntimeError(f'Remote command exited {result.returncode}; inspect {output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', help='Own PBS job ID, e.g. 220486.pbs111')
    parser.add_argument('--stream-timeout', type=int, default=600,
                        help='Artifact stream timeout in seconds (default: 600)')
    args = parser.parse_args()
    if args.stream_timeout <= 0:
        parser.error('--stream-timeout must be positive')
    if not re.fullmatch(r'\d+\.pbs\d+', args.job):
        parser.error('Expected a PBS job ID')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination = ROOT / 'collected' / args.job / stamp
    destination.mkdir(parents=True)
    remote(f'qstat -xf {args.job}', destination / 'pbs-accounting.txt')
    accounting = (destination / 'pbs-accounting.txt').read_text()
    if not re.search(r'Job_Owner\s*=\s*apacsc42@', accounting):
        raise RuntimeError('Refusing to collect a job not owned by apacsc42')
    remote('qstat -x -u apacsc42; myprojects', destination / 'own-jobs-and-credit.txt')
    archive = destination / 'raw-artifacts.tar.gz'
    number = args.job.split('.')[0]
    # pbsdsh child output can appear in the PBS spool rather than redirected role logs.
    remote(f'cd {shlex.quote(REMOTE)} && '
           f'files=(runs/{args.job}); '
           f'for path in *.o{number} *.e{number}; do '
           'if [[ -f "$path" ]]; then files+=("$path"); fi; done; '
           'tar -czf - "${files[@]}"', archive, timeout=args.stream_timeout)
    with tarfile.open(archive) as handle:
        members = handle.getmembers()
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or '..' in path.parts or not (member.isdir() or member.isfile()):
                raise RuntimeError(f'Unexpected archive member: {member.name}')
        handle.extractall(destination, members=members, filter='data')
    run = destination / 'runs' / args.job
    checksum = subprocess.run(['sha256sum', '--check', 'SHA256SUMS'],
                              cwd=run / 'submitted', capture_output=True, text=True)
    (destination / 'payload-checksums.txt').write_text(checksum.stdout + checksum.stderr)
    if checksum.returncode:
        raise RuntimeError('Submitted payload checksum mismatch')
    result = subprocess.run(['python3', str(run / 'summarize.py'), str(run)],
                            capture_output=True, text=True, check=True)
    rows = json.loads(result.stdout)
    (destination / 'derived-summary.json').write_text(result.stdout)
    protocols = []
    for export in sorted(run.glob('*/n*/artifacts/profile_export_aiperf.json')):
        data = json.loads(export.read_text())
        config = data.get('input_config', {})
        phases = {p.get('kind'): p for p in config.get('phases', [])}
        dataset = config.get('datasets', [{}])[0]
        prompts = dataset.get('prompts', {})
        protocol_pass = (
            phases.get('warmup', {}).get('duration') == 60
            and phases.get('profiling', {}).get('duration') == 120
            and phases.get('profiling', {}).get('grace_period') == 30
            and prompts.get('isl', {}).get('mean') == 4000
            and prompts.get('osl', {}).get('mean') == 200
            and config.get('slos') == {'time_to_first_token': 3000.0, 'inter_token_latency': 20.0}
            and data.get('was_cancelled') is False)
        protocols.append({'export': str(export.relative_to(destination)),
                          'full_protocol_pass': protocol_pass, 'phases': phases,
                          'error_summary': data.get('error_summary')})
    smoke_path = run / 'output-smoke.json'
    smoke = json.loads(smoke_path.read_text()) if smoke_path.exists() else None
    states = re.findall(r'^\s*job_state\s*=\s*(\S+)', accounting, re.M)
    exits = re.findall(r'^\s*Exit_status\s*=\s*(-?\d+)', accounting, re.M)
    review = {
        'job': args.job, 'collected_utc': stamp,
        'pbs_state': states[-1] if states else None,
        'exit_status': int(exits[-1]) if exits else None,
        'payload_checksums_pass': True, 'measurements': rows,
        'export_protocol_reviews': protocols,
        'output_smoke': smoke,
        'accuracy_verified': False,
        'interpretation': 'A live snapshot may be incomplete. Preserve raw exports; eight-case output checks do not establish organiser accuracy.',
    }
    (destination / 'review.json').write_text(json.dumps(review, indent=2) + '\n')
    hashes = {str(path.relative_to(destination)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(destination.rglob('*')) if path.is_file()}
    (destination / 'evidence-sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    print(json.dumps({'destination': str(destination), 'review': review}, indent=2))


if __name__ == '__main__':
    main()
