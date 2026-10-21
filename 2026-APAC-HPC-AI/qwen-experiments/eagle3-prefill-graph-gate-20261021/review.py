"""Review sealed readiness and startup coverage; no throughput acceptance."""
from pathlib import Path
import collections,datetime,hashlib,json,re,subprocess
O=Path(__file__).resolve().parent;D=O/'collected/223005.pbs111';run=D/'runs/223005.pbs111'
for name,digest in json.loads((D/'evidence-sha256.json').read_text()).items():assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest
c=json.loads((O/'collection.json').read_text());assert c['semantic_pass'] and c['exit_status']==0 and c['payload_subset_hashes_passed']
r=subprocess.run(['python3',str(run/'submitted/check-probe.py'),str(run),'1'],capture_output=True,text=True);assert r.returncode==0
log=(run/'prefill.log').read_text();before=log.split('SIGTERM received',1)[0]
disabled=collections.Counter(re.findall(r' TP(\d+)\] Disable prefill CUDA graph because',before));assert disabled=={str(i):2 for i in range(4)}
kv=re.findall(r' TP(\d+)\] KV Cache is allocated\. dtype: torch\.([a-z0-9]+)',before);assert collections.Counter(rank for rank,dtype in kv)=={str(i):2 for i in range(4)} and {dtype for _,dtype in kv}=={'bfloat16'}
records=[]
for p in (run/'resource-telemetry').glob('*.jsonl'):
 for line in p.open():
  row=json.loads(line)
  if row.get('kind')=='sample':records.append(row)
assert records
uuids={g['uuid'] for s in records for g in s.get('gpus',[])};assert len(uuids)==4
assert all(len(s.get('gpus',[]))==4 for s in records)
gpus=[g for s in records for g in s['gpus']]
account=(D/'pbs-accounting.txt').read_text();h,m,s=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',account).groups());wall=h*3600+m*60+s
result=dict(job=c['job'],reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='NATIVE_TP4_PREFILL_READINESS_PASS_FULL_PD_UNVERIFIED',payload_and_raw_hashes_passed=True,semantic_gate_replayed=True,native_disabled_messages_by_rank=dict(disabled),kv_cache_bfloat16_entries=len(kv),all_four_nixl_ranks=True,ranked_performance_measured=False,pd_output_equivalence=False,official_accuracy_verified=False,walltime_s=wall,requested_gpus=4,estimated_allocated_charge_su=wall*4*128/3600,charge_posting_reconciled=False,
 telemetry=dict(startup_samples=len(records),unique_gpu_uuids=len(uuids),all_samples_have_four_devices=True,first_utc=records[0]['utc'],last_utc=records[-1]['utc'],vram_min_mib=min(float(g['memory.used']) for g in gpus),vram_max_mib=max(float(g['memory.used']) for g in gpus),activity_max_percent=max(float(g['utilization.gpu']) for g in gpus),server_http_status_counts=dict(collections.Counter(str(s.get('server_http_status',s.get('server_metrics_status','missing'))) for s in records)),node_cpu_ram_network='Collected counters; not converted into per-worker demand or rates'),
 limitations=['Only one prefill role; no router/decode/cross-node transfer or real output IDs.','Native health may execute an internal one-token forward; no user benchmark workload was sent.','Only launcher mask captured; actual scheduler/rank/thread NUMA mapping not collected.','Startup samples do not describe scored utilization, latency or critical path.','Post-readiness SIGTERM and detokenizer -15/SIGQUIT are from the driver cleanup; preserved, not silently treated as startup failures.','Different physical node than 222780; this is a validated configuration repair, not a matched causal speedup study.'])
(O/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['limitations','telemetry']},indent=2))
