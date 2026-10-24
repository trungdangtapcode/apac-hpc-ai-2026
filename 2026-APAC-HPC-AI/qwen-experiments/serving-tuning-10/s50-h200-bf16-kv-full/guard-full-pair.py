#!/usr/bin/env python3
"""Fail-closed CPU gate for the conditional full H200 KV pair."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
S47=ROOT/'serving-tuning-10/s47-h200-bf16-kv-control'
S48=ROOT/'serving-tuning-10/s48-h200-fp8-kv-screen'
S50=ROOT/'serving-tuning-10/s50-h200-bf16-kv-full'
RUNS=ROOT/'runs'

def run(cmd,cwd=None): return subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
def verify_bundle(path):
    m=hashlib.sha256((path/'SHA256SUMS').read_bytes()).hexdigest()
    p=run(['sha256sum','--check','SHA256SUMS'],path)
    if p.returncode: raise ValueError(f'{path.name} frozen manifest failed: {p.stdout[-1000:]}{p.stderr[-1000:]}')
    return m
def replay(bundle,job):
    artifact=RUNS/str(job)
    if not artifact.is_dir(): raise ValueError(f'missing completed screen artifact job {job}')
    if not (artifact/'submitted-payload/SHA256SUMS').is_file(): raise ValueError(f'job {job} has no preserved submitted-payload manifest')
    if hashlib.sha256((artifact/'submitted-payload/SHA256SUMS').read_bytes()).hexdigest()!=hashlib.sha256((bundle/'SHA256SUMS').read_bytes()).hexdigest(): raise ValueError(f'job {job} submitted payload differs from reviewed screen bundle')
    payload=run(['sha256sum','--check','SHA256SUMS'],artifact/'submitted-payload')
    if payload.returncode: raise ValueError(f'job {job} submitted payload checksum failed')
    p=run([sys.executable,str(bundle/'check-screen.py'),str(artifact)])
    if p.returncode:
        try: detail=json.loads(p.stdout)
        except Exception: detail={'stdout':p.stdout[-1500:],'stderr':p.stderr[-1500:]}
        raise ValueError(f'job {job} checker failed: {detail}')
    d=json.loads(p.stdout)
    if d.get('status')!='pass' or d.get('request_errors')!=0 or d.get('cancellations')!=0 or d.get('good_request_fraction',0)<=0.90:
        raise ValueError(f'job {job} did not pass frozen runtime/SLA/local response gates')
    return d

def decide_screens(control,candidate):
    for row in (control,candidate):
        if not isinstance(row,dict) or row.get('status')!='pass' or row.get('request_errors')!=0 or row.get('cancellations')!=0 or row.get('good_request_fraction',0)<=0.90:
            return 'SKIPPED_GUARD_UNKNOWN',None
    gain=candidate['good_output_tokens_s']/control['good_output_tokens_s']-1
    return ('PROCEED' if candidate['good_output_tokens_s'] > control['good_output_tokens_s']*1.01 else 'SKIPPED_GUARD_FALSE'),gain

def record(out,status,reason,extra=None):
    d={'status':status,'reason':reason,'gpu_workers_started':False,'timestamp_utc':'runtime generated'}
    if extra:d.update(extra)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(json.dumps(d,indent=2));return d

def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--role',choices=['control','candidate'],required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--control-artifact',type=Path);ap.add_argument('--fixture-case',choices=['valid_win','valid_lose','error','missing_artifact','candidate_missing_control','candidate_invalid_control'],help=argparse.SUPPRESS);a=ap.parse_args(argv)
    if a.fixture_case:
        valid={'status':'pass','request_errors':0,'cancellations':0,'good_request_fraction':0.95,'good_output_tokens_s':1000}
        candidate=dict(valid,good_output_tokens_s=1020 if a.fixture_case not in ('valid_lose',) else 1010)
        control=dict(valid)
        if a.fixture_case=='error': control={'status':'fail'}
        if a.fixture_case=='missing_artifact': control=None
        decision,gain=decide_screens(control,candidate)
        if decision=='SKIPPED_GUARD_UNKNOWN':
            record(a.out,'FAILED_GUARD_UNKNOWN','Injected missing or invalid screen evidence; fail closed.',{'fixture_case':a.fixture_case})
            return 2
        facts={'fixture_case':a.fixture_case,'screen_gain_fraction':gain}
        if decision=='SKIPPED_GUARD_FALSE':
            record(a.out,'SKIPPED_GUARD_FALSE','Valid screen evidence does not exceed the strict 1% threshold.',facts)
            return 0
        if a.role=='candidate' and a.fixture_case in ('candidate_missing_control','candidate_invalid_control'):
            reason='Candidate fixture has invalid full-control receipt.' if a.fixture_case=='candidate_invalid_control' else 'Candidate fixture has no full-control artifact.'
            record(a.out,'FAILED_CONTROL_INVALID',reason,facts)
            return 2
        a.out.parent.mkdir(parents=True,exist_ok=True)
        d={'status':'PROCEED','reason':'Injected valid screen winner.','gpu_workers_started':False,**facts}
        a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(d,indent=2));return 0
    try:
        h47=verify_bundle(S47);h48=verify_bundle(S48)
        c=replay(S47,25863);f=replay(S48,25864)
        decision,gain=decide_screens(c,f)
        facts={'screen_jobs':{'control':25863,'fp8_candidate':25864},'screen_manifest_sha256':{'s47':h47,'s48':h48},'screen_good_output_tokens_s':{'bf16':c['good_output_tokens_s'],'fp8':f['good_output_tokens_s']},'screen_gain_fraction':gain,'screen_checks':{'s47':'pass','s48':'pass'}}
        if decision=='SKIPPED_GUARD_UNKNOWN':
            record(a.out,'FAILED_GUARD_UNKNOWN','Screen checker evidence is missing or invalid; no workers launched.',facts);return 2
        if decision=='SKIPPED_GUARD_FALSE':
            record(a.out,'SKIPPED_GUARD_FALSE','FP8 short-screen gain is not strictly above 1%; no full GPU workers launched.',facts);return 0
        if a.role=='candidate':
            if not a.control_artifact:record(a.out,'FAILED_CONTROL_INVALID','Full control artifact path is missing; candidate cannot start.',facts);return 2
            ctl=Path(a.control_artifact)
            s50_manifest=verify_bundle(S50)
            status_file=ctl/'full-pair-status.json'
            if not status_file.is_file():record(a.out,'FAILED_CONTROL_INVALID','Full control receipt is missing; candidate cannot start.',facts);return 2
            status=json.loads(status_file.read_text())
            if status.get('status')!='pass':record(a.out,'FAILED_CONTROL_INVALID','Full BF16 control did not complete and pass; candidate cannot start.',dict(facts,control_status=status));return 2
            if not (ctl/'submitted-payload/SHA256SUMS').is_file():record(a.out,'FAILED_CONTROL_INVALID','Full control submitted payload manifest is missing.',facts);return 2
            p=run(['sha256sum','--check','SHA256SUMS'],ctl/'submitted-payload')
            if p.returncode:record(a.out,'FAILED_CONTROL_INVALID','Full control submitted payload manifest failed verification.',facts);return 2
            if hashlib.sha256((ctl/'submitted-payload/SHA256SUMS').read_bytes()).hexdigest()!=s50_manifest:record(a.out,'FAILED_CONTROL_INVALID','Full control submitted payload manifest does not match frozen S50.',facts);return 2
            full=run([sys.executable,str(S50/'check-screen.py'),str(ctl)])
            if full.returncode:record(a.out,'FAILED_CONTROL_INVALID','Full control checker replay failed.',dict(facts,checker_output=full.stdout[-1500:],checker_error=full.stderr[-1500:]));return 2
            full_result=json.loads(full.stdout)
            if full_result.get('status')!='pass' or full_result.get('request_errors')!=0 or full_result.get('cancellations')!=0 or full_result.get('good_request_fraction',0)<=0.90:record(a.out,'FAILED_CONTROL_INVALID','Full control frozen checker did not pass required gates.',dict(facts,full_control_check=full_result));return 2
            facts['full_control_check']=full_result
            facts['full_control_artifact']=str(ctl);facts['full_control_status']='pass';facts['full_control_manifest_sha256']=s50_manifest
        d={'status':'PROCEED','reason':'Both short screens pass, FP8 improvement exceeds 1%, and required full control receipt is valid.','gpu_workers_started':False,**facts}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(d,indent=2));return 0
    except Exception as e:
        record(a.out,'FAILED_GUARD_UNKNOWN',str(e));return 2
if __name__=='__main__':raise SystemExit(main())
