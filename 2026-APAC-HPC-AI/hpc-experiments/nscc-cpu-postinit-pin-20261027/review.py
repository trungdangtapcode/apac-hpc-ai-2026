#!/usr/bin/env python3
"""Replay the baseline and pin-arm records from the native archive and hash manifest."""
from collections import Counter
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import sys
import tarfile

E = Path(__file__).resolve().parent
sys.path.insert(0, str(E / 'payload'))
from offline_checks import validate_pin_records
from offline_checks import select_core_slots

ARCHIVE = E / 'raw-records.tar.gz'
COLLECTION = json.loads((E / 'collection.json').read_text())
JOB = COLLECTION['job_id'].split('.', 1)[0]
BASE = f'runs/{JOB}/'


def decode(raw, path):
    return raw[BASE + path].decode('utf-8')


def load_rank_records(raw, path, count=512):
    prefix = BASE + path + '/rank-'
    output = {}
    for name, value in raw.items():
        if name.startswith(prefix) and name.endswith('.json'):
            key = int(name[len(prefix):-5])
            assert key not in output, f'duplicate rank record file: {name}'
            output[key] = json.loads(value)
    assert sorted(output) == list(range(count)), f'{path}: expected exact records 0..{count-1}'
    return output


def main():
    assert COLLECTION['job_id'].endswith('.pbs101')
    archive_hash = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    assert archive_hash == COLLECTION['archive_sha256']
    raw = {}
    with tarfile.open(ARCHIVE, 'r:gz') as archive:
        files = [item for item in archive.getmembers() if item.isfile()]
        assert len(files) == len(COLLECTION['files'])
        assert len({item.name for item in files}) == len(files)
        assert {item.name for item in files} == set(COLLECTION['files'])
        for item in files:
            path = PurePosixPath(item.name)
            assert not path.is_absolute() and '..' not in path.parts
            value = archive.extractfile(item).read()
            metadata = COLLECTION['files'][item.name]
            assert len(value) == metadata['bytes']
            assert hashlib.sha256(value).hexdigest() == metadata['sha256']
            assert not item.name.endswith('/mpi-init-probe')
            assert not item.name.endswith('/postinit-pin-probe')
            raw[item.name] = value
    assert sum(item['bytes'] for item in COLLECTION['files'].values()) == sum(len(value) for value in raw.values())

    baseline_entry = load_rank_records(raw, 'arms/baseline/native/pre')
    baseline_post = load_rank_records(raw, 'arms/baseline/native')
    assert all(row['phase'] == 'before_mpi_init_thread' and row['affinity_status'] == 0 and row['errno'] == 0 for row in baseline_entry.values())
    assert all(row['phase'] == 'after_mpi_init_thread' and row['affinity_status'] == 0 and row['errno'] == 0 for row in baseline_post.values())
    pre_by_pmi = {row['pmi_rank']: row for row in baseline_entry.values()}
    post_by_pmi = {row['pmi_rank']: row for row in baseline_post.values()}
    assert len(pre_by_pmi) == len(post_by_pmi) == 512
    assert set(pre_by_pmi) == set(post_by_pmi) == set(range(512))
    assert sorted(row['rank'] for row in baseline_post.values()) == list(range(512))
    assert all(pre_by_pmi[pmi]['host'] == post_by_pmi[pmi]['host'] for pmi in range(512))
    baseline_hosts = Counter(row['host'] for row in baseline_post.values())
    assert len(baseline_hosts) == 4 and set(baseline_hosts.values()) == {128}

    candidate_rows = [json.loads(value) for name, value in raw.items()
                      if name.startswith(BASE + 'arms/postinit_pin/rank-') and name.endswith('.json')]
    assert len(candidate_rows) == 512
    candidate_by_world = {row['world_rank']: row for row in candidate_rows}
    assert len(candidate_by_world) == 512
    topology_members = [name for name in raw if name.startswith(BASE + 'arms/postinit_pin/host-topology-world-')
                        and name.endswith('.json')]
    assert len(topology_members) == 4
    target_maps = {}
    for name in topology_members:
        topology = json.loads(raw[name])
        host = topology['host']
        leader = candidate_by_world[topology['world_rank']]
        assert leader['host'] == host and leader['local_rank'] == 0
        assert topology['pmi_rank'] == leader['pmi_rank']
        allowed = set(topology['post_init_allowed'])
        rows = topology['allowed_cpu_sysfs_map']
        assert {row['cpu'] for row in rows} == allowed and len(rows) == len(allowed)
        assert all(row['online'] is True for row in rows)
        computed = select_core_slots(rows, allowed, allowed, required_cores=128)
        recorded = topology['selected_slots_sorted_package_core']
        assert recorded == computed, f'{host}: recorded slots are not the lowest allowed CPU per sorted physical core'
        assert topology['post_init_allowed'] == leader['post_init_allowed']
        target_maps[host] = [{key: slot[key] for key in ('cpu', 'package', 'core', 'node')}
                             for slot in computed]
    assert len(target_maps) == 4
    candidate_summary = validate_pin_records(candidate_rows, target_maps)

    rc_rows = [json.loads(line) for line in decode(raw, 'command-return-codes.jsonl').splitlines()]
    command_rc = {row['command']: row['return_code'] for row in rc_rows}
    assert len(command_rc) == len(rc_rows)
    assert command_rc.get('arm_baseline') == 0 and command_rc.get('arm_postinit_pin') == 0
    assert command_rc.get('payload_hash_before') == command_rc.get('payload_hash_after') == 0
    assert decode(raw, 'payload-sha256-before.txt') == decode(raw, 'payload-sha256-after.txt')
    assert all(line.endswith(': OK') for line in decode(raw, 'payload-sha256-before.txt').splitlines())
    worker = json.loads(decode(raw, 'worker-status.json'))
    assert worker['worker_return_code'] == 0 and worker['post_hash_return_code'] == 0
    baseline_out = decode(raw, 'logs/arm-baseline.stdout.txt')
    candidate_out = decode(raw, 'logs/arm-postinit_pin.stdout.txt')
    assert 'MPI_SUMMARY_JSON {"world_size":512,"ranks_with_capture_or_identity_errors":0}' in baseline_out
    assert ('POSTINIT_PIN_SUMMARY {"world_size":512,"preflight_error_ranks":0,'
            '"immediate_audit_error_ranks":0,"postwait_audit_error_ranks":0,"record_write_error_ranks":0}') in candidate_out
    batch_path = 'postinit-pin-qual.o' + JOB
    assert batch_path in raw and b'COLLECTION_FINISHED' in raw[batch_path]
    terminal = COLLECTION['terminal']
    assert terminal['job_state'] == 'F' and terminal['Exit_status'] == 0
    assert terminal['project'] == '59000042'
    assert terminal['resources_used']['ncpus'] == 512 and terminal['resources_used']['ngpus'] == 0

    result = {'passed': True, 'job_id': COLLECTION['job_id'],
              'terminal_evidence_source': COLLECTION['terminal_evidence_source'],
              'archive_sha256_verified': archive_hash, 'archive_file_count': len(raw),
              'archive_uncompressed_bytes': sum(len(value) for value in raw.values()),
              'terminal': terminal, 'worker': worker, 'all_arm_and_source_return_codes_zero': True,
              'baseline': {'entry_records': 512, 'post_records': 512,
                           'world_ranks_unique': True, 'pmi_ranks_unique': True,
                           'hosts': dict(sorted(baseline_hosts.items()))},
              'postinit_pin': candidate_summary,
              'per_host_topology_maps': len(topology_members),
              'lowest_allowed_cpu_per_physical_core_recomputed_from_archived_sysfs_map': True,
              'rank_zero_pin_threads_only': True,
              'limits': ['sched_setaffinity pid zero binds only the calling thread; MPI helper/progress threads are unqualified.',
                         'This is a mechanism qualification diagnostic, not a solver or performance result.',
                         'The archived synthetic fixtures are not evidence of NSCC physical topology.']}
    (E / 'review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': True, 'archive_file_count': len(raw), 'baseline_records': 1024,
                      'candidate_records': candidate_summary['records'], 'hosts': candidate_summary['hosts'],
                      'pmi_nonidentity_pairs': candidate_summary['pmi_nonidentity_pairs']}, indent=2))


if __name__ == '__main__':
    main()
