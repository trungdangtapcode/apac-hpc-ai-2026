#!/usr/bin/env python3
"""Fail closed unless accepted CPU job 27387 passed the exact pinned fixtures."""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
BUNDLE=Path(__file__).resolve().parent
JOB_ID=27387
EXPECTED_CONTROL_SCORE=3041.1195980583084
EXPECTED_CONTROL_GOOD_FRACTION=0.9863157894736843
PAGE16_SCOPE='page1 is the production-page-size fixture; page16 is metadata-only and does not qualify page16 KV behavior'
EXPECTED_PROBE_SCOPE='CPU-only C++ extension and synthetic radix-tree data structure; not RadixCacheCpp integration, P/D, Qwen, or performance.'
EXPECTED_IMAGE_SHA256='b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5'
FIXTURE_EXPECTATIONS={
    'result':'PASS','initial_insert_matched_tokens':0,'exact_repeat_matched_tokens':32,
    'prefix_tokens_checked':16,'overlap_matched_tokens':16,
    'unique_cached_indices_after_split':48,'protected_indices_while_locked':32,
    'indices_evicted_while_locked':16,'indices_evicted_after_unlock':32,
    'reset_sizes':{'total':0,'evictable':0,'protected':0},
}


def parse_actual_probe_json(raw: str | bytes) -> dict:
    """Parse the retained file bytes strictly; expose a pure path for mutation fixtures."""
    try:
        value=json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise ValueError('malformed actual CPU probe result JSON') from exc
    if not isinstance(value,dict):
        raise ValueError('actual CPU probe result must be a JSON object')
    return value


def parse_sacct(stdout: str, returncode: int=0, stderr: str='') -> list[tuple[str,str]]:
    if returncode!=0:
        raise ValueError(f'sacct failed for CPU prerequisite {JOB_ID}: {stderr.strip()}')
    rows=[]
    for line in stdout.splitlines():
        cols=line.strip().split('|')
        if len(cols)>=3 and cols[0]==str(JOB_ID):
            rows.append((cols[1].split()[0],cols[2]))
    if rows != [('COMPLETED','0:0')]:
        raise ValueError(f'CPU prerequisite {JOB_ID} must be actual COMPLETED 0:0, got {rows!r}')
    return rows


def parse_host_start(raw: str) -> dict:
    fields={}
    for line in raw.splitlines():
        if '=' in line:
            key,value=line.split('=',1)
            fields[key]=value
    try:
        fields['JOB']=int(fields['JOB'])
        fields['JOB_START_EPOCH']=int(fields['JOB_START_EPOCH'])
        fields['PROCESS_DEADLINE_EPOCH']=int(fields['PROCESS_DEADLINE_EPOCH'])
        fields['GPU_REQUEST']=int(fields['GPU_REQUEST'])
        fields['CPU_REQUEST']=int(fields['CPU_REQUEST'])
    except (KeyError,ValueError) as exc:
        raise ValueError('actual CPU host-start receipt is incomplete or malformed') from exc
    return fields


def validate_cpu_probe(result: dict, expected_sources: dict, host_start: dict) -> None:
    if host_start.get('PROBE_EXECUTION_STATE')!='running_diagnostic':
        raise ValueError('host-start execution state is missing or unexpected')
    if host_start.get('JOB')!=JOB_ID or host_start.get('GPU_REQUEST')!=0 or host_start.get('CPU_REQUEST')!=2:
        raise ValueError('host-start receipt does not bind this result to job 27387 / 2 CPU / 0 GPU')
    if host_start.get('PROCESS_DEADLINE_EPOCH')!=host_start.get('JOB_START_EPOCH')+90:
        raise ValueError('host-start process deadline is not absolute batch-start + 90 seconds')
    if result.get('absolute_job_start_epoch')!=host_start['JOB_START_EPOCH'] or result.get('process_deadline_epoch')!=host_start['PROCESS_DEADLINE_EPOCH']:
        raise ValueError('CPU probe JSON is not bound to the actual host-start timestamps')
    finalized=result.get('finalized_epoch')
    if not isinstance(finalized,int) or not host_start['JOB_START_EPOCH']<=finalized<=host_start['PROCESS_DEADLINE_EPOCH']+30:
        raise ValueError('CPU probe finalization fell outside the process deadline plus cleanup grace')
    if result.get('scope')!=EXPECTED_PROBE_SCOPE or result.get('image_sha256_from_pinned_provenance')!=EXPECTED_IMAGE_SHA256:
        raise ValueError('CPU probe scope or pinned image provenance differs')
    if result.get('cuda_visible_devices')!='' or result.get('nvidia_visible_devices')!='void':
        raise ValueError('CPU probe container did not record an explicitly hidden GPU')
    if result.get('state')!='PASS_CPU_FIXTURES_ONLY':
        raise ValueError(f"CPU probe state is {result.get('state')!r}")
    if result.get('launcher_exit_code')!=0 or result.get('native_remove_end_seen') is not True:
        raise ValueError('CPU probe exit or Enroot cleanup receipt failed')
    if result.get('torch_cuda_available') is not False or result.get('torch_visible_device_count')!=0:
        raise ValueError('prerequisite was not zero-GPU')
    if not re.fullmatch(r'[0-9a-f]{64}',result.get('extension_sha256','')) or 'radix_tree_cpp' not in result.get('extension_path',''):
        raise ValueError('native C++ JIT extension binary/hash was not recorded')
    compiler_fields=('compiler_version','gxx_version','ninja_version','torch','python')
    if any(not result.get(name) for name in compiler_fields):
        raise ValueError('CPU probe compiler/PyTorch/Python version record is incomplete')
    elapsed=result.get('phase_jit_import_seconds')
    if not isinstance(elapsed,(float,int)) or not 0<elapsed<=90:
        raise ValueError('cold JIT import exceeded or missed the 90-second process budget')
    if result.get('runtime_source_sha256')!=expected_sources:
        raise ValueError('CPU JIT runtime source hashes do not match the candidate payload')
    if result.get('prebuild_runtime_source_sha256')!=expected_sources:
        raise ValueError('pre-JIT runtime source hashes do not match the candidate payload')
    private_dir=result.get('torch_extensions_dir','')
    extension_path=result.get('extension_path','')
    if not private_dir or not extension_path.startswith(private_dir.rstrip('/')+'/'):
        raise ValueError('JIT binary path is not inside the recorded private torch extension cache')
    cases=result.get('cases')
    if not isinstance(cases,list) or len(cases)!=2 or {c.get('page_size') for c in cases}!={1,16}:
        raise ValueError('both page1 and metadata-only page16 fixtures are required')
    for case in cases:
        for key,value in FIXTURE_EXPECTATIONS.items():
            if case.get(key)!=value:
                raise ValueError(f"page{case.get('page_size')} fixture {key}={case.get(key)!r}, expected {value!r}")
        if case.get('page_size')==16 and case.get('interpretation')!=PAGE16_SCOPE:
            raise ValueError('page16 result must be explicitly labelled metadata-only')


def validate_control(control: dict, parent: dict) -> None:
    if control.get('state')!='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY':
        raise ValueError('fresh native control 27376 is not locally gate-passing')
    summary=control.get('summary',{})
    if summary.get('good_output_tokens_s')!=parent.get('control_good_output_tokens_s'):
        raise ValueError('retained control score differs from frozen S106 comparator')
    if summary.get('good_output_tokens_s')!=EXPECTED_CONTROL_SCORE:
        raise ValueError('job 27376 comparator value differs from reviewed source record')
    if summary.get('good_request_fraction')!=EXPECTED_CONTROL_GOOD_FRACTION:
        raise ValueError('job 27376 good-request fraction differs from reviewed source record')


def validate_admission(sacct_stdout: str, sacct_returncode: int, sacct_stderr: str,
                       host_start_text: str, probe_json: str | bytes, expected_sources: dict,
                       control: dict, parent: dict) -> dict:
    parse_sacct(sacct_stdout,sacct_returncode,sacct_stderr)
    validate_control(control,parent)
    host_start=parse_host_start(host_start_text)
    probe=parse_actual_probe_json(probe_json)
    validate_cpu_probe(probe,expected_sources,host_start)
    return {'state':'PASS_CPU_PREREQUISITE','job':JOB_ID,
            'cpu_probe_state':probe['state'],'source_hashes_match_candidate':True,
            'page_sizes_tested':[1,16],
            'page16_interpretation':'metadata-only, not page16 KV qualification',
            'control_job':27376,'control_good_output_tokens_s':parent['control_good_output_tokens_s']}


def main() -> dict:
    proc=subprocess.run(['sacct','--parsable2','--noheader','--jobs',str(JOB_ID),
                         '--format=JobID,State,ExitCode'],text=True,
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=15)
    control_path=ROOT/'h200-cold-prefill-cache-study-20261029/control-review-27376.json'
    run_dir=ROOT/'runs'/str(JOB_ID)
    probe_path=run_dir/'probe.json'
    host_start_path=run_dir/'host-start.txt'
    parent=json.loads((BUNDLE/'PARENT_PAYLOAD_PROVENANCE.json').read_text())
    expected=json.loads((BUNDLE/'CPP_SOURCE_HASHES.json').read_text())['cpu_probe_runtime_sha256']
    if not control_path.is_file(): raise ValueError(f'missing retained control review: {control_path}')
    if not probe_path.is_file(): raise ValueError(f'missing actual CPU probe result: {probe_path}')
    if not host_start_path.is_file(): raise ValueError(f'missing actual CPU host-start receipt: {host_start_path}')
    control=parse_actual_probe_json(control_path.read_bytes())
    return validate_admission(proc.stdout,proc.returncode,proc.stderr,
                              host_start_path.read_text(),probe_path.read_bytes(),expected,control,parent)


if __name__=='__main__':
    try:
        print(json.dumps(main(),indent=2))
    except (ValueError,subprocess.TimeoutExpired) as exc:
        raise SystemExit(f'FATAL: {exc}')
