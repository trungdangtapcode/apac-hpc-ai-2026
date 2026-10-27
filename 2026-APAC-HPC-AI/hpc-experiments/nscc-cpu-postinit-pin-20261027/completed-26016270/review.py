#!/usr/bin/env python3
"""Independently replay job 26016270 from its native archive and manifest."""
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import sys
import tarfile

E = Path(__file__).resolve().parent
sys.path.insert(0, str(E.parent / 'payload'))
from offline_checks import select_core_slots, validate_pin_records

ARCHIVE = E / 'raw-records.tar.gz'
COLLECTION = json.loads((E / 'collection.json').read_text())
JOB = COLLECTION['job_id'].split('.', 1)[0]
BASE = f'runs/{JOB}/'


def decode(raw, path):
    return raw[BASE + path].decode('utf-8')


def rank_records(raw, path, count=512):
    prefix = BASE + path + '/rank-'
    found = {}
    for name, data in raw.items():
        if name.startswith(prefix) and name.endswith('.json'):
            index = int(name[len(prefix):-5])
            assert index not in found, f'duplicate file index under {path}'
            found[index] = json.loads(data)
    assert sorted(found) == list(range(count)), f'{path}: expected rank records 0..{count-1}'
    return found


def check_no_environment_keys(value):
    if isinstance(value, dict):
        assert not any(key in ('Variable_List', 'environment', 'Environment') for key in value)
        for child in value.values():
            check_no_environment_keys(child)
    elif isinstance(value, list):
        for child in value:
            check_no_environment_keys(child)


def main():
    assert COLLECTION['job_id'] == '26016270.pbs101'
    expected_sources = json.loads((E.parent / 'deployment.json').read_text())['files']
    assert COLLECTION['deployed_payload_sha256'] == expected_sources
    for relative, digest in expected_sources.items():
        assert hashlib.sha256((E.parent / relative).read_bytes()).hexdigest() == digest

    fresh = json.loads((E / 'fresh-qstat.stdout.json').read_text())
    check_no_environment_keys(fresh)
    assert (E / 'fresh-qstat.exit-code.txt').read_text().strip() == '0'
    assert (E / 'fresh-qstat.stderr.txt').read_text() == ''

    archive_hash = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    assert archive_hash == COLLECTION['archive_sha256']
    raw = {}
    with tarfile.open(ARCHIVE, 'r:gz') as archive:
        files = [member for member in archive.getmembers() if member.isfile()]
        assert len(files) == 1569 == len(COLLECTION['files'])
        assert len({member.name for member in files}) == len(files)
        assert {member.name for member in files} == set(COLLECTION['files'])
        for member in files:
            path = PurePosixPath(member.name)
            assert not path.is_absolute() and '..' not in path.parts
            data = archive.extractfile(member).read()
            details = COLLECTION['files'][member.name]
            assert len(data) == details['bytes']
            assert hashlib.sha256(data).hexdigest() == details['sha256']
            assert not member.name.endswith('/mpi-init-probe')
            assert not member.name.endswith('/postinit-pin-probe')
            assert b'Variable_List' not in data
            raw[member.name] = data
    uncompressed_bytes = sum(len(data) for data in raw.values())
    assert uncompressed_bytes == 1609012

    # Baseline probe: all PMI-rank entry and world-rank post-init records are retained.
    base_pre = rank_records(raw, 'arms/baseline/native/pre')
    base_post = rank_records(raw, 'arms/baseline/native')
    assert all(row['phase'] == 'before_mpi_init_thread' and row['affinity_status'] == 0 and row['errno'] == 0 for row in base_pre.values())
    assert all(row['phase'] == 'after_mpi_init_thread' and row['affinity_status'] == 0 and row['errno'] == 0 for row in base_post.values())
    assert all(len(row['cpus']) == 1 for row in base_pre.values())
    assert all(row['cpus'] == list(range(256)) for row in base_post.values())
    base_pre_by_pmi = {row['pmi_rank']: row for row in base_pre.values()}
    base_post_by_pmi = {row['pmi_rank']: row for row in base_post.values()}
    assert len(base_pre_by_pmi) == len(base_post_by_pmi) == 512
    assert set(base_pre_by_pmi) == set(base_post_by_pmi) == set(range(512))
    assert sorted(row['rank'] for row in base_post.values()) == list(range(512))
    assert all(base_pre_by_pmi[pmi]['host'] == base_post_by_pmi[pmi]['host'] for pmi in range(512))
    baseline_hosts = Counter(row['host'] for row in base_post.values())
    assert len(baseline_hosts) == 4 and set(baseline_hosts.values()) == {128}

    # Candidate process records retain world/PMI/local-rank identities and all phases.
    candidate_rows = [json.loads(data) for name, data in raw.items()
                      if name.startswith(BASE + 'arms/postinit_pin/rank-') and name.endswith('.json')]
    assert len(candidate_rows) == 512
    candidate_by_world = {row['world_rank']: row for row in candidate_rows}
    assert set(candidate_by_world) == set(range(512))
    candidate_pmi_by_world = {rank: row['pmi_rank'] for rank, row in candidate_by_world.items()}
    baseline_pmi_by_world = {rank: row['pmi_rank'] for rank, row in base_post.items()}
    assert candidate_pmi_by_world == baseline_pmi_by_world
    assert all(row['pre_init_status'] == row['post_init_status'] == 0 and
               row['pre_init_errno'] == row['post_init_errno'] == 0 and
               len(row['pre_init_allowed']) == 1 and row['post_init_allowed'] == list(range(256))
               for row in candidate_rows)
    assert all(row['topology_status'] == 0 and
               row['sched_setaffinity_status'] == 0 and row['sched_setaffinity_errno'] == 0 and
               row['immediate_mask_status'] == 0 and row['immediate_mask_errno'] == 0 and
               row['after_allreduce_status'] == 0 and row['after_allreduce_errno'] == 0 and
               row['after_2s_status'] == 0 and row['after_2s_errno'] == 0 and
               row['after_final_allreduce_status'] == 0 and row['after_final_allreduce_errno'] == 0
               for row in candidate_rows)
    host_rows = defaultdict(list)
    for row in candidate_rows:
        host_rows[row['host']].append(row)
    assert set(host_rows) == set(baseline_hosts)
    for rows in host_rows.values():
        assert len(rows) == 128
        assert [row['local_rank'] for row in sorted(rows, key=lambda row: row['world_rank'])] == list(range(128))

    # Each shared-memory leader retains every allowed CPU's sysfs identity; replay the selection.
    topology_members = [name for name in raw
                        if name.startswith(BASE + 'arms/postinit_pin/host-topology-world-') and name.endswith('.json')]
    assert len(topology_members) == 4
    target_maps = {}
    topology_summary = {}
    for name in topology_members:
        topology = json.loads(raw[name])
        host = topology['host']
        leader = candidate_by_world[topology['world_rank']]
        assert leader['host'] == host and leader['local_rank'] == 0
        assert topology['pmi_rank'] == leader['pmi_rank']
        allowed = set(topology['post_init_allowed'])
        sysfs = topology['allowed_cpu_sysfs_map']
        assert {row['cpu'] for row in sysfs} == allowed and len(sysfs) == len(allowed) == 256
        assert all(row['online'] is True and all(row[key] >= 0 for key in ('package', 'core', 'node')) for row in sysfs)
        computed = select_core_slots(sysfs, allowed, allowed, required_cores=128)
        recorded = topology['selected_slots_sorted_package_core']
        assert recorded == computed, f'{host}: slots differ from lowest allowed logical CPU by sorted physical core'
        assert topology['post_init_allowed'] == leader['post_init_allowed']
        target_maps[host] = [{key: slot[key] for key in ('cpu', 'package', 'core', 'node')} for slot in computed]
        logical_by_node = Counter(str(row['node']) for row in sysfs)
        cores_by_node = Counter()
        for row in sysfs:
            cores_by_node[(row['node'], row['package'], row['core'])] += 1
        physical_by_node = Counter(str(node) for node, package, core in cores_by_node)
        topology_summary[host] = {
            'allowed_logical_cpus': len(allowed),
            'physical_cores': len({(row['package'], row['core']) for row in sysfs}),
            'packages': sorted({row['package'] for row in sysfs}),
            'logical_cpus_by_numa_node': dict(sorted(logical_by_node.items())),
            'physical_cores_by_numa_node': dict(sorted(physical_by_node.items())),
            'selected_cpu_min_max': [min(slot['cpu'] for slot in computed), max(slot['cpu'] for slot in computed)],
        }
    assert set(target_maps) == set(host_rows)
    candidate_summary = validate_pin_records(candidate_rows, target_maps)
    sleep_ns = [row['sleep_elapsed_ns'] for row in candidate_rows]
    assert min(sleep_ns) >= 1_900_000_000 and max(sleep_ns) <= 10_000_000_000
    assert all(len(row['immediate_mask']) == len(row['after_allreduce_mask']) ==
               len(row['after_2s_mask']) == len(row['after_final_allreduce_mask']) == 1
               for row in candidate_rows)

    # Wrapper return codes and pinned source hashes are independently checked.
    return_rows = [json.loads(line) for line in decode(raw, 'command-return-codes.jsonl').splitlines()]
    command_rc = {row['command']: row['return_code'] for row in return_rows}
    assert len(command_rc) == len(return_rows) == 18
    assert all(row['return_code'] == 0 for row in return_rows)
    assert decode(raw, 'payload-sha256-before.txt') == decode(raw, 'payload-sha256-after.txt')
    hash_lines = decode(raw, 'payload-sha256-before.txt').splitlines()
    assert len(hash_lines) == len(expected_sources) == 6 and all(line.endswith(': OK') for line in hash_lines)
    worker = json.loads(decode(raw, 'worker-status.json'))
    assert worker['worker_return_code'] == worker['post_hash_return_code'] == 0
    runtime = decode(raw, 'logs/selected-runtime-settings.txt')
    assert 'MPICH_RANK_REORDER_METHOD=0' in runtime
    assert all(setting in runtime for setting in ('PALS_CPU_BIND=unset', 'MPICH_RANK_ORDER=unset',
                                                   'MPICH_RANK_REORDER_FILE=unset', 'LD_PRELOAD=empty'))
    baseline_stdout = decode(raw, 'logs/arm-baseline.stdout.txt')
    pin_stdout = decode(raw, 'logs/arm-postinit_pin.stdout.txt')
    assert 'MPI_SUMMARY_JSON {"world_size":512,"ranks_with_capture_or_identity_errors":0}' in baseline_stdout
    assert ('POSTINIT_PIN_SUMMARY {"world_size":512,"preflight_error_ranks":0,'
            '"immediate_audit_error_ranks":0,"postwait_audit_error_ranks":0,"record_write_error_ranks":0}') in pin_stdout
    batch = raw['postinit-pin-qual.o' + JOB]
    assert b'COLLECTION_FINISHED\n' in batch and b'COLLECTION_FINISHED_WITH_ARM_FAILURE' not in batch

    # Runtime linkage and allocation/resource evidence.
    pstream_path = decode(raw, 'logs/pstream-path.txt').strip()
    pstream_ldd = decode(raw, 'logs/pstream-ldd.txt')
    assert 'OpenFOAM-v2512' in pstream_path and 'lib/cray-mpich/libPstream.so' in pstream_path
    assert '/mpich/8.1.15/' in pstream_ldd and 'libmpi_gnu_91.so.12' in pstream_ldd
    for arm in ('baseline', 'pin'):
        linkage = decode(raw, f'logs/ldd-{arm}.txt')
        assert '/mpich/8.1.15/' in linkage and 'libmpi_gnu_91.so.12' in linkage
        assert decode(raw, f'logs/compile-{arm}.stderr.txt') == ''
    nodefile = decode(raw, 'pbs-nodefile.txt').splitlines()
    node_hosts = Counter(host.split('.', 1)[0] for host in nodefile)
    assert len(nodefile) == 512 and node_hosts == baseline_hosts
    resources = {}
    for arm in ('baseline', 'postinit_pin'):
        report = decode(raw, f'logs/arm-{arm}.resource.txt')
        elapsed = re.search(r'Elapsed \(wall clock\) time .*: ([0-9:.]+)', report)
        max_rss = re.search(r'Maximum resident set size \(kbytes\): (\d+)', report)
        assert elapsed and max_rss
        resources[arm] = {'launcher_wall_seconds': elapsed.group(1),
                          'launcher_max_rss_kib': int(max_rss.group(1)),
                          'scope': 'time(1) measurement of mpiexec wrapper tree, not aggregate MPI-rank telemetry'}

    terminal = COLLECTION['terminal']
    assert terminal['job_state'] == 'F' and terminal['Exit_status'] == 0
    assert terminal['project'] == '59000042' and terminal['queue'] == 'q5'
    assert terminal['resources_used']['ncpus'] == 512 and terminal['resources_used']['ngpus'] == 0
    assert terminal['resources_used']['walltime'] == '00:00:17'
    assert terminal['Resource_List']['nodect'] == 4 and terminal['Resource_List']['walltime'] == '00:05:00'

    result = {
        'passed': True, 'job_id': COLLECTION['job_id'],
        'terminal_evidence_source': COLLECTION['terminal_evidence_source'],
        'fresh_qstat_variable_list_removed_before_save': True,
        'archive_sha256_verified': archive_hash, 'archive_file_count': len(raw),
        'archive_uncompressed_bytes': uncompressed_bytes,
        'terminal': terminal, 'worker': worker, 'all_18_worker_return_codes_zero': True,
        'source_hash_checks': {'deployed_payload_files': len(expected_sources), 'before_after_identical': True, 'all_checks_ok': True},
        'baseline': {'pre_records': 512, 'post_records': 512,
                     'pre_singleton_masks': True, 'post_masks_cpus_0_through_255': True,
                     'hosts': dict(sorted(baseline_hosts.items()))},
        'postinit_pin': candidate_summary,
        'world_to_pmi_nonidentity_pairs': sum(rank != pmi for rank, pmi in candidate_pmi_by_world.items()),
        'world_to_pmi_crosswalk_matches_baseline': True,
        'localrank_world_order_verified_per_host': True,
        'post_init_masks_cpus_0_through_255_all_ranks': True,
        'pin_masks_stable_in_all_four_audit_phases': True,
        'sleep_elapsed_ns_min_max': [min(sleep_ns), max(sleep_ns)],
        'per_host_topology': topology_summary,
        'lowest_allowed_cpu_per_physical_core_recomputed_from_archived_sysfs_map': True,
        'Pstream_path': pstream_path, 'Cray_MPICH_8_1_15_linkage_verified': True,
        'launcher_resource_samples': resources,
        'limits': [
            'sched_setaffinity pid zero binds each process main thread only; MPI helper/progress-thread affinity was not measured.',
            'This is a binding-mechanism qualification probe, not an OpenFOAM solve or performance result.',
            'No sampled per-rank CPU/GPU utilization telemetry was collected; PBS and time(1) fields have limited scope.'
        ]
    }
    (E / 'review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': True, 'job_id': COLLECTION['job_id'],
                      'archive_file_count': len(raw), 'baseline_records': 1024,
                      'candidate_records': candidate_summary['records'],
                      'hosts': candidate_summary['hosts'],
                      'world_to_pmi_nonidentity_pairs': result['world_to_pmi_nonidentity_pairs'],
                      'min_max_sleep_ns': result['sleep_elapsed_ns_min_max']}, indent=2))


if __name__ == '__main__':
    main()
