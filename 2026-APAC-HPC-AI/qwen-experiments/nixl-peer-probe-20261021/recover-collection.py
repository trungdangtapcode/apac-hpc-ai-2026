"""Preserve the failed flat-copy check, recover original remote bundle, replay and seal."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,re,shlex,subprocess,tarfile
O=Path(__file__).resolve().parent;job='223091.pbs111';D=O/'collected'/job;run=D/'runs'/job
assert D.is_dir() and not (D/'evidence-sha256.json').exists(),'Only resume this unsealed collection; never overwrite a seal'
assert 'source/nixl_api.py: FAILED open or read' in (D/'payload-checksums.txt').read_text()
helper='/home/apacsc42/workspace/vpn-rootless/vpn.sh';root='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/'+O.name
with (D/'original-bundle.tar.gz').open('xb') as stream:
 command='cd '+root+' && sha256sum --check SHA256SUMS >/dev/null && tar -czf - --files-from <(awk \'{print $2}\' SHA256SUMS) SHA256SUMS'
 r=subprocess.run(['bash',helper,'ssh-batch','bash -lc '+shlex.quote(command)],stdout=stream,stderr=subprocess.PIPE,timeout=120)
assert r.returncode==0,r.stderr
B=D/'original-bundle';B.mkdir()
with tarfile.open(D/'original-bundle.tar.gz') as t:
 members=t.getmembers();assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in members);t.extractall(B,members=members,filter='data')
r=subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=B,capture_output=True,text=True);(D/'original-bundle-checksums.txt').write_text(r.stdout+r.stderr);assert r.returncode==0
assert (B/'SHA256SUMS').read_bytes()==(O/'SHA256SUMS').read_bytes()==(run/'submitted/SHA256SUMS').read_bytes()
checks=[]
for line in (B/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  ',1);actual=run/'submitted'/name;flattened=False
 if not actual.exists():actual=run/'submitted'/Path(name).name;flattened=True
 assert actual.is_file() and hashlib.sha256(actual.read_bytes()).hexdigest()==digest,name
 checks.append(dict(original_path=name,actual_copy_path=str(actual.relative_to(run)),flattened_directory=flattened,sha256_verified=True))
account=(D/'pbs-accounting.txt').read_text();assert re.search(r'job_state\s*=\s*F',account);exit_status=int(re.search(r'Exit_status\s*=\s*(-?\d+)',account)[1]);assert exit_status==0
s=importlib.util.spec_from_file_location('probe',B/'probe.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
rows=[json.loads((run/('rank'+str(i)+'-result.json')).read_text()) for i in range(2)];passed,reason=m.result_rows_valid(*rows);assert passed,reason
final=json.loads((run/'final.json').read_text());assert final['status']=='pass'
assert final['rank_result_sha256']=={str(i):hashlib.sha256((run/('rank'+str(i)+'-result.json')).read_bytes()).hexdigest() for i in range(2)}
h,minute,second=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',account).groups());wall=h*3600+minute*60+second
seal={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.rglob('*')) if p.is_file()};(D/'evidence-sha256.json').write_text(json.dumps(seal,indent=2)+'\n')
result=dict(job=job,collected_utc=datetime.now(timezone.utc).isoformat(),state='BASE_NIXL_VRAM_PASS',exit_status=exit_status,payload_and_raw_hashes_verified=True,semantic_replayed_without_raw_mutation=True,semantic_passed=True,semantic_reason=reason,rank_results=rows,walltime_s=wall,estimated_allocated_charge_su=wall*2*128/3600,official_accuracy_verified=False,ranked_performance_measured=False,model_loaded=False,private_peer_exchange_collected=False,provenance_correction=dict(initial_check_failed_due_to_flattened_source_subdirectory=True,original_failed_report_preserved=True,remote_original_bundle_collected_and_verified=True,flat_copies_match_original_manifest=checks,no_raw_files_rewritten=True),scope='Two actualH100 nodes040/035; a base peer/VRAM pass does not validate SGLang heterogeneous KV, EAGLE3, or failed019/031 pair',hardware_telemetry='No utilization/power/memory sampling; device identity and realtransfer/checksum evidence only',task_log_bytes={str(i):(run/('rank'+str(i)+'-task.log')).stat().st_size for i in range(2)})
(O/'collection.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['rank_results','provenance_correction']},indent=2))
