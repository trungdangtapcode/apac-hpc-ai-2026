"""Read live and retained Iris job state without treating live eviction as access failure."""
import argparse
import json
from pathlib import Path

from iris_bridge import run_json


def query(job_id):
    if not str(job_id).isdigit():
        raise ValueError('A numeric job ID is required')
    body = 'JOB = ' + repr(str(job_id)) + '''
import datetime, socket, subprocess

def command(arguments):
    try:
        proc = subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True, timeout=15)
        return {'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
    except subprocess.TimeoutExpired:
        return {'error_type': 'TimeoutExpired', 'timeout_seconds': 15}
    except OSError as error:
        return {'error_type': type(error).__name__}

result = {
    'utc': datetime.datetime.utcnow().isoformat() + 'Z',
    'host': socket.gethostname(),
    'job_id': JOB,
    'queue': command(['squeue', '-j', JOB, '-h', '-o', '%i|%j|%T|%M|%N|%R']),
    'accounting': command(['sacct', '-j', JOB, '-X', '-P', '-n',
                           '--format=JobID,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList']),
    'interpretation': 'A nonzero live queue response does not establish an access failure. '
                      'Use retained accounting for terminal jobs; preserve unknown states.',
}
'''
    return run_json(body, timeout=55)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job_id')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = query(args.job_id)
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        with args.output.open('x') as stream:
            stream.write(text)
    print(text, end='')
