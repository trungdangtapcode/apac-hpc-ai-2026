"""Inspect sealed startup success and launcher failure without scoring it."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,re
O=Path(__file__).resolve().parent; D=O/'collected/223055.pbs111'; run=D/'runs/223055.pbs111'
for name,digest in json.loads((D/'evidence-sha256.json').read_text()).items():
 assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest,name
c=json.loads((O/'collection.json').read_text()); assert c['exit_status']==1 and c['payload_hashes_passed']
assert not (run/'pair-warmup.log').read_text().strip()
aux=list(run.glob('task-aux-*.log'));warmup_errors=[p for p in aux if 'RuntimeError: Pair 0 HTTP 500:' in p.read_text(errors='replace')];assert len(warmup_errors)==1
assert 'NIXL_ERR_REMOTE_DISCONNECT' in warmup_errors[0].read_text()
token=json.loads((run/'token-control.json').read_text());assert not token['passed'] and token['failure']['type']=='HTTPError' and token['stages']=={'draft-a':[]}
locality=json.loads((run/'worker-locality-request.log').read_text());assert locality['all_roles_mapping_complete']
roles={}; telemetry={}; uuid_sets=[]
for role,n in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:
 files=list(run.glob('task-'+role+'-node*.log'));assert len(files)==1
 text=files[0].read_text();before=text.split('SIGTERM received',1)[0]
 disabled=collections.Counter(re.findall(r'TP(\d+)(?: EP\d+)?\] Disable prefill CUDA graph because',before))
 kv=re.findall(r'TP(\d+)(?: EP\d+)?\] KV Cache is allocated\. dtype: torch\.([a-z0-9]+)',before)
 nixl=collections.Counter(re.findall(r'TP(\d+)(?: EP\d+)?\] NIXL KVManager initialized',before))
 assert disabled=={str(i):2 for i in range(n)}
 assert collections.Counter(rank for rank,dtype in kv)=={str(i):2 for i in range(n)} and {dtype for rank,dtype in kv}=={'bfloat16'}
 assert nixl=={str(i):1 for i in range(n)}
 assert 'The server is fired up and ready to roll!' in before
 errors={s:before.count(s) for s in ['Traceback','RuntimeError','ERROR']}
 if role=='decode-0':
  for s in ['Capture draft decode CUDA graph end','Capture draft extend CUDA graph end']:assert s in before
 roles[role]=dict(native_ready=True,nixl_ranks=dict(nixl),prefill_graph_disabled_entries_by_rank=dict(disabled),bf16_kv_entries=len(kv),pre_cleanup_error_string_counts=errors,log=str(files[0].relative_to(D)))
 rows=[json.loads(line) for p in (run/'resource-telemetry').glob(role+'-*.jsonl') for line in p.read_text().splitlines()];samples=[r for r in rows if r['kind']=='sample'];assert samples
 uuids={g['uuid'] for r in samples for g in r.get('gpus',[])};assert len(uuids)==n;uuid_sets.append(uuids)
 gpus=[g for r in samples for g in r.get('gpus',[])]
 telemetry[role]=dict(startup_sample_count=len(samples),unique_gpu_uuids=len(uuids),all_samples_expected_devices=all(len(r.get('gpus',[]))==n for r in samples),first_utc=samples[0]['utc'],last_utc=samples[-1]['utc'],sampled_vram_min_mib=min(float(g['memory.used']) for g in gpus),sampled_vram_max_mib=max(float(g['memory.used']) for g in gpus),sampled_gpu_activity_max_percent=max(float(g['utilization.gpu']) for g in gpus),server_metrics_status_counts=dict(collections.Counter(str(r.get('server_http_status',r.get('server_metrics_status','missing'))) for r in samples)),node_cpu_ram_network='Collected raw counters; not converted to rates or per-worker demand')
assert len(set.union(*uuid_sets))==16 and sum(map(len,uuid_sets))==16
account=(D/'pbs-accounting.txt').read_text();h,m,s=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',account).groups());seconds=h*3600+m*60+s
batch=list(D.glob('**/*.o223055'));assert len(batch)==1;text=batch[0].read_text();assert 'ALL_WORKERS_READY after 587s' in text and 'ALL_PAIRS_WARM after 659s' in text
assert 'NIXL_ERR_REMOTE_DISCONNECT' in ''.join(p.read_text() for p in run.glob('task-prefill*.log'))
result=dict(job=c['job'],reviewed_utc=datetime.now(timezone.utc).isoformat(),state='ALL_ROLES_READY_PD_TRANSPORT_FAILED',exit_status=1,payload_and_raw_hashes_verified=True,walltime_s=seconds,estimated_allocated_charge_su=seconds*16*128/3600,posted_charge_reconciled=False,roles=roles,telemetry=telemetry,all_16_unique_devices_sampled=True,all_workers_and_router_ready_s=587,pair_warmup_started=True,pair_warmup_passed=False,false_head_warmup_marker=True,token_control_failure=token['failure'],responses_collected=0,actual_output_ids_collected=False,pd_output_equivalence=False,ranked_performance_measured=False,official_accuracy_verified=False,locality=dict(all_roles_mapping_complete=locality['all_roles_mapping_complete'],affinity_changed=locality['affinity_changed'],scope='Actual rank/GPU/thread mapping collected; not CPU saturation or scored demand'),assessment='Bash dispatch reaches actual warmup, but first requests fail with NIXL remote disconnect, then metadata-not-found. A head ALL_PAIRS_WARM marker is false because remote status was masked; final actual-token gate correctly rejects HTTP500' ,next_hypothesis='Do not retry full model unchanged. Require explicit per-pair semantic warmup receipt and investigate earlier cross-node NIXL disconnect separately from later missing peer metadata; use supported cheap transport probe or close branch' )
(O/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
