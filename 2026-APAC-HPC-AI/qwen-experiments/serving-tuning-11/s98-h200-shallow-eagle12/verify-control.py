#!/usr/bin/env python3
"""Bind the full candidate to frozen, raw-reviewed S93 control job 26949."""
import hashlib, json, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ALLOW_DIFFERENCES={
 'arm','experiment','label','matched_pair','expected_prefill_kv_regions_by_arm',
 'expected_decode_kv_regions_by_arm','source_parent','source_parent_job','study_arm',
 'prerequisite_job','native_argument_prerequisite','speculation','matched_control',
}
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def review_control(binding):
    ctl=json.loads((HERE/'matched-control.json').read_text())
    assert ctl['state']=='BOUND_TO_26949_FROZEN_RAW_REPLAY_REQUIRED'
    assert ctl['control_job']=='26949'
    payload=Path(ctl['control_payload_dir']); bundle=Path(ctl['control_bundle_dir']); art=Path(ctl['control_artifact_dir'])
    review_path=Path(ctl['control_review_report'])
    assert sha(payload/'SHA256SUMS')==ctl['control_payload_manifest_sha256']
    assert sha(bundle/'SHA256SUMS')==ctl['control_bundle_manifest_sha256']==ctl['control_payload_manifest_sha256']
    assert sha(payload/'check-performance.py')==ctl['frozen_control_checker_sha256']
    assert sha(art/'submitted-payload/SHA256SUMS')==ctl['control_payload_manifest_sha256']
    assert sha(review_path)==ctl['control_review_report_sha256']
    for directory in (payload,art/'submitted-payload'):
        subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=directory,capture_output=True,text=True,check=True)
    # Bind the terminal receipt to the already-frozen actual scheduler job.
    terminal=None
    for _ in range(6):
        raw=subprocess.check_output(['sacct','-X','-n','-P','-j','26949','--format=JobIDRaw,State,ExitCode'],text=True)
        rows=[line.split('|') for line in raw.splitlines() if line.strip()]
        terminal=next((row for row in rows if row[0]=='26949'),None)
        if terminal: break
        time.sleep(1)
    assert terminal and terminal[1:3]==['COMPLETED','0:0'], f'control job is not terminal successful: {terminal}'
    live=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
    assert '26949' not in live, 'control allocation remains live'
    # Replay the exact immutable gate from the control's submitted payload.
    proc=subprocess.run([sys.executable,'-B',str(payload/'check-performance.py'),str(art)],capture_output=True,text=True,check=True)
    replay=json.loads(proc.stdout)
    assert replay.get('state')=='PASS_UNRANKED_PERFORMANCE_PROTOCOL' and replay.get('arm')=='control'
    assert replay.get('errors')==0 and replay.get('cancelled')==0 and replay.get('completed')>0 and replay.get('good_request_fraction',0)>=.90
    assert replay.get('quality')=='UNKNOWN_NOT_EVALUATED' and replay.get('ranked') is False and replay.get('speedup_claim') is False
    root_review=json.loads(review_path.read_text())
    assert root_review.get('job')==26949 and root_review.get('state')==ctl['control_review_state']
    assert root_review.get('scheduler',{}).get('State')=='COMPLETED' and root_review.get('scheduler',{}).get('ExitCode')=='0:0'
    assert root_review.get('raw_fixed_workload',{}).get('completed')==replay.get('completed')
    assert root_review.get('raw_fixed_workload',{}).get('errors')==0
    assert abs(root_review.get('raw_fixed_workload',{}).get('good_output_tokens_per_second',0)-replay.get('good_output_tokens_per_second',0))<1e-8
    cconfig=json.loads((art/'config.json').read_text())
    fconfig=json.loads((payload/'config.json').read_text())
    bconfig=json.loads((bundle/'config.json').read_text())
    assert cconfig==fconfig==bconfig and sha(art/'config.json')==ctl['control_config_sha256']
    candidate=json.loads((HERE/'config.json').read_text())
    differences={k for k in candidate.keys()|cconfig.keys() if candidate.get(k)!=cconfig.get(k)}
    assert differences<=ALLOW_DIFFERENCES, f'unreviewed control/candidate config differences: {sorted(differences-ALLOW_DIFFERENCES)}'
    for key in cconfig:
        if key not in ALLOW_DIFFERENCES: assert candidate[key]==cconfig[key], f'control common config differs: {key}'
    # Ensure exact one-field serving intervention and exact prerequisite tuple.
    spec=candidate.get('speculation',{})
    assert spec=={'algorithm':'EAGLE3','role':'decode-0 only','draft_model_path':EXPECTED_DRAFT,
      'num_steps':1,'eagle_topk':1,'num_draft_tokens':2,'draft_attention_backend':'flashinfer',
      'draft_model_quantization':None,'draft_fingerprint':'pinned draft verification remains mandatory before workers; decode TP ranks must each load draft architecture and select FlashInfer'}
    return {'state':'PASS_ACTUAL_26949_CONTROL_RAW_REVIEW','control_job':'26949',
      'terminal':{'state':terminal[1],'exit_code':terminal[2]},
      'control_payload_manifest_sha256':ctl['control_payload_manifest_sha256'],
      'frozen_checker_sha256':ctl['frozen_control_checker_sha256'],
      'control_review_report_sha256':ctl['control_review_report_sha256'],
      'control_config_sha256':ctl['control_config_sha256'],'config_differences':sorted(differences),
      'independent_raw_protocol_replay':replay,'official_accuracy':'UNKNOWN',
      'scope':'Completed matched control replay and root review binding only; no official accuracy or speedup claim.'}
EXPECTED_DRAFT='/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'
if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: verify-control.py OUTPUT_JSON')
    try: result=review_control(sys.argv[1])
    except Exception as exc:
        print(json.dumps({'state':'FAIL','reason':str(exc)},indent=2)); raise SystemExit(1)
    out=Path(sys.argv[1]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
