"""One bounded diagnostic retry; never count an aborted client as a measurement."""
from pathlib import Path
import json,shutil,hashlib,subprocess,ast
R=Path.cwd();D=R/'serving-tuning-10';O=R/'research-followup-20261018-1923';src=D/'s12-dg-chunk8192-repeat-n58';name='s13-dg-chunk8192-n58-bounded';dst=D/name;assert not dst.exists();shutil.copytree(src,dst);f=dst/'job.sbatch';f.write_text(f.read_text().replace(src.name,name));f=dst/'config.json';c=json.loads(f.read_text());c.update(experiment=name,source_experiment=src.name,source_job='24588',diagnostic_profile=False,accuracy_verified=False,purpose='One diagnostic retry after warmup completion stall; cap entire AIPerf invocation at360s without changing its phases, requests or scoring. Do not retry this failure again unchanged.',client_walltime_limit_s=360,retry_interpretation='Fail-fast diagnostic containment, not a proven root-cause repair; no accepted measurement unless full normal protocol and output gates pass.');f.write_text(json.dumps(c,indent=2)+'\n');f=dst/'benchmark.sh';s=f.read_text();assert s.count('  aiperf profile \\')==1;s=s.replace('  aiperf profile \\','  timeout --signal=TERM --kill-after=15s 360s aiperf profile \\',1);old='    --ui simple --artifact-dir "$RUN/artifacts" >"$RUN/client.log" 2>&1\n';assert old in s;s=s.replace(old,old.rstrip('\n')+''' || {
      client_status=$?
      printf 'AIPERF_CLIENT_FAILED exit=%s walltime_limit_s=360\\n' "$client_status" >&2
      if [[ $client_status == 124 || $client_status == 137 ]]; then
        touch "$RUN/client-walltime-limit-exceeded.txt"
      fi
      return "$client_status"
    }
''');f.write_text(s)
# Exact inverse patch verifies that the operational guard is the only client change.
a=s.replace('  timeout --signal=TERM --kill-after=15s 360s aiperf profile \\','  aiperf profile \\',1);a=a[:a.index(old.rstrip('\n')+' || {')]+old+a[a.index('  python3 "$ART/summarize.py"'):];assert a==(src/'benchmark.sh').read_text()
for f in dst.iterdir():
 if f.suffix=='.py':ast.parse(f.read_text())
 if f.suffix in ['.sh','.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
for filename in ['worker.sh','profile-serving.py','topology-job.sh','nixl-conn.py','output-smoke.py','long-context-check.py']:assert (src/filename).read_bytes()==(dst/filename).read_bytes()
h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));(O/'validation.json').write_text(json.dumps(dict(passed=True,exact_inverse_guard_patch_pass=True,client_image_has_gnu_timeout=True,payloads={name:h}),indent=2)+'\n');pilot=dict(id=name,bundle=str(dst),planned_ns=[58],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[58],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24588',manual_bounded_retry_limit=1);(O/'pilot.json').write_text(json.dumps(pilot,indent=2)+'\n');print('Bounded retry frozen; no model, request or phase change')
