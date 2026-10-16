"""One read-only runtime snapshot of an own running PBS pilot; no model requests."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent
HELPER = '/home/apacsc42/workspace/vpn-rootless/vpn.sh'
REMOTE_CODE = r'''
import datetime, hashlib, ipaddress, json, re, subprocess, sys, urllib.request
from pathlib import Path
job=sys.argv[1]
accounting=subprocess.run(['qstat','-xf',job],capture_output=True,text=True,check=True).stdout
assert re.search(r'Job_Owner\s*=\s*apacsc42@',accounting), 'Not own job'
assert re.search(r'^\s*job_state\s*=\s*R\s*$',accounting,re.M), 'Job must be running'
run=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/runs')/job
endpoints=(run/'endpoints.tsv').read_text()
keys=('model_path','served_model_name','context_length','dtype','quantization',
      'kv_cache_dtype','tp_size','ep_size','disaggregation_mode',
      'disaggregation_transfer_backend','attention_backend','decode_attention_backend',
      'flashinfer_allreduce_fusion_backend','chunked_prefill_size','max_running_requests',
      'cuda_graph_config','version','startup_time','memory_usage',
      'weight_loader_disable_mmap','weight_loader_prefetch_checkpoints',
      'weight_loader_prefetch_num_threads','effective_max_running_requests_per_dp')
def selected(info):
 return {k:info[k] for k in keys if k in info}
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'job':job,'pbs_accounting':accounting,'endpoints':endpoints,'servers':{},'pair_logs':{}}
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
for line in endpoints.splitlines():
 name,url,bootstrap=line.split()
 assert name in ('prefill-0','prefill-1','decode-0'), 'Unexpected role'
 match=re.fullmatch(r'http://(10\.\d+\.\d+\.\d+):(30100|30101|30200)',url)
 assert match and ipaddress.ip_address(match[1]).is_private, 'Unexpected endpoint'
 try:
  with opener.open(url+'/get_server_info',timeout=5) as response:
   raw=response.read(2*1024*1024+1)
   assert len(raw)<=2*1024*1024, 'Response too large'
   info=json.loads(raw)
   result['servers'][name]={'url':url,'http_status':response.status,
      'response_sha256':hashlib.sha256(raw).hexdigest(),'reported':selected(info),
      'internal_state_count':len(info.get('internal_states',[])),
      'internal_states':[selected(s) for s in info.get('internal_states',[])]}
 except Exception as error:
  result['servers'][name]={'url':url,'error':str(error)}
for path in sorted((run/'pair-warmup').glob('router-prefill-*-decode-0.log')):
 with path.open('rb') as handle:
  raw=handle.read(128*1024+1)
 result['pair_logs'][path.name]={'bytes':path.stat().st_size,
    'prefix':raw[:128*1024].decode(errors='replace'),'truncated':len(raw)>128*1024}
print(json.dumps(result))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job')
    parser.add_argument('--out', type=Path, required=True, help='Fresh evidence directory')
    args = parser.parse_args()
    if not re.fullmatch(r'\d+\.pbs\d+', args.job):
        parser.error('Expected PBS job ID')
    plan = json.loads((ROOT / 'continuous-plan.json').read_text())
    permitted = {p.get('job_id') for group in ('pilots', 'startup_pilots') for p in plan[group]}
    if args.job not in permitted:
        parser.error('Job not in current pilot plan; inspect replacements manually')
    args.out.mkdir(parents=True, exist_ok=False)
    command = 'python3 -c ' + shlex.quote(REMOTE_CODE) + ' ' + shlex.quote(args.job)
    record = {'started_utc': datetime.now(timezone.utc).isoformat(), 'job': args.job}
    try:
        result = subprocess.run(['bash', HELPER, 'ssh-batch', 'bash -lc ' + shlex.quote(command)],
                                capture_output=True, text=True, timeout=50)
        record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        record.update(timeout=True, stdout=(error.stdout or b'').decode(errors='replace'),
                      stderr=(error.stderr or b'').decode(errors='replace'))
    (args.out / 'transport.json').write_text(json.dumps(record, indent=2) + '\n')
    if record.get('returncode') == 0:
        report = json.loads(record['stdout'])
        report['interpretation'] = (
            'Live reported configuration and startup timings only. Internal states are not '
            'a rank census or proof of MNNVL initialization. auto dtype is not resolved dtype. '
            'HTTP200 is not accuracy. No benchmark requests, retry, authentication or promotion.')
        (args.out / 'runtime.json').write_text(json.dumps(report, indent=2) + '\n')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in args.out.iterdir() if p.is_file()}
    (args.out / 'evidence-sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    print(json.dumps({'output': str(args.out), 'returncode': record.get('returncode'),
                      'timeout': record.get('timeout', False)}))
    raise SystemExit(0 if record.get('returncode') == 0 else 1)


if __name__ == '__main__':
    main()
