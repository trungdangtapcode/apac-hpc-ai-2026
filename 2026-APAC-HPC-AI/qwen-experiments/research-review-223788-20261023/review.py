"""Review original failed gate separately from actual native registration evidence."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,importlib.util,json,re
O=Path(__file__).resolve().parent;R=O.parent;D=O/'collected';run=D/'runs/223788.pbs111';B=R/'eagle3-h100-geometry-probe-20261023/payload'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in json.loads((D/'evidence-sha256.json').read_text()):assert sha(D/row['path'])==row['sha256']
for line in (B/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  ',1);assert sha(B/name)==digest and sha(run/'submitted'/name)==digest
original=json.loads((run/'probe-result.json').read_text());assert original['passed'] is False
assert original['geometry_error']=='ValueError: full-model geometry requires a nonempty KV layer list'
proof=original['proof'];assert all(proof[k] for k in ['experiment_context_verified','readiness_loop_passed','server_ready_log','native_graph_source_verified','runtime_h100_verified','draft_sha256_verified','derived_nixl_source_verified','hpc_ops_preflight_passed'])
assert proof['http_health_status']=='200' and proof['resolved_server_config']['passed'] and not proof['fatal_runtime_lines'] and not proof['prefill_graph_capture_started']
account=(D/'pbs-accounting.txt').read_text();assert re.search(r'Exit_status\s*=\s*1\b',account)
h,m,s=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',account).groups());seconds=h*3600+m*60+s
receipts=[json.loads(p.read_text()) for p in sorted((run/'kv-geometry').glob('*.json'))];assert len(receipts)==8
by_rank={}
for rank in range(4):
 pair={x['phase']:x for x in receipts if x['engine_rank']==rank};assert set(pair)=={'before','after'} and pair['before']['registration_returned'] is None and pair['after']['registration_returned'] is True
 a,b=({k:v for k,v in pair[phase].items() if k not in ['phase','registration_returned']} for phase in ['before','after']);assert a==b
 assert b['kv_layer_ids']==[] and len(b['kv_regions'])==190 and b['kv_head_num']==1 and b['total_kv_head_num']==4 and b['page_size_tokens']==1
 assert len(b['aux_region_lengths_bytes'])==10 and b['state_region_lengths_bytes']==[]
 assert all(x['memory_kind']=='VRAM' and x['region_bytes']==76132096 and x['item_bytes']==x['token_stride_bytes']==256 and x['page_count']==297391 for x in b['kv_regions'])
 by_rank[str(rank)]=dict(native_registration_returned=True,kv_region_count=190,advertised_kv_region_bytes=sum(x['region_bytes'] for x in b['kv_regions']),per_region_bytes=76132096,per_token_stride_bytes=256,page_count=297391,aux_region_lengths_bytes=b['aux_region_lengths_bytes'],state_regions=[],kv_layer_ids_observed=[],explicit_semantic_layer_ids='not_collected',heads_per_rank=1,total_kv_heads=4,page_size_tokens=1)
source=R/'nixl-descriptor-probe-20261021/source/common-conn.py';assert sha(source)=='ba33d63c6920f87b55cf57f9224bb7d08af67e1476bd70b8e1a70067f33a29d7'
text=source.read_text();start=text.index('    def get_mha_kv_ptrs_with_pp(');end=text.index('    def get_mla_kv_ptrs_with_pp(',start);snippet=text[start:end]
assert 'num_kv_layers = len(src_kv_ptrs) // 2' in snippet and 'kv_layer_ids' not in snippet
(O/'native-positional-mha-source.py.txt').write_text(snippet)
rows=[json.loads(line) for p in (run/'resource-telemetry').glob('*.jsonl') for line in p.read_text().splitlines()];samples=[x for x in rows if x.get('kind')=='sample'];gpus=[g for x in samples for g in x.get('gpus',[])];uuids={g['uuid'] for g in gpus}
review=dict(job='223788.pbs111',reviewed_utc=datetime.now(timezone.utc).isoformat(),state='NATIVE_READY_REGISTRATION_RECORDED_ORIGINAL_GATE_REJECTED',original_scheduler_state='F',original_exit_status=1,original_semantic_gate_passed=False,original_failure=original['geometry_error'],actual_runtime_and_health_passed=True,actual_before_after_registration_rank_count=4,actual_receipt_count=8,per_rank=by_rank,source_positional_mha_function='CommonKVManager.get_mha_kv_ptrs_with_pp',source_sha256=sha(source),source_finding='Pinned MHA code computes positional layer counts from pointer list length and PP range; it does not require explicit nonempty kv_layer_ids. Why the runtime supplies [] was not separately traced.',corrected_contract='Only a separately derived Qwen MHA validator allows observed[] with exact190 regions/head1,total4/page1 and complete stable before/after pairs; missing/malformed metadata remains rejected. No layer sequence is invented.',cost=dict(walltime_s=seconds,allocated_gpus=4,estimated_allocated_charge_su=seconds*4*128/3600,maximum_reservation_su=4*128*20/60,posting_reconciled=False),telemetry=dict(samples=len(samples),unique_sampled_gpu_uuids=len(uuids),sampled_vram_min_mib=min(float(g['memory.used']) for g in gpus),sampled_vram_max_mib=max(float(g['memory.used']) for g in gpus),scope='Startup/native health only; no scored workload, causal saturation or peak guarantee. Raw CPU/RAM/network counters collected but not converted to per-worker rates.'),limits=['Original allocation and original semantic gate remain failed, not retroactively a passing run.','Native registration success and observed region geometry do not prove peer transfer, model output equivalence or speedup.','190 advertised regions do not establish190 independent physical allocations or explicit semantic layer identities.','Ten actual auxiliary buffers differ from earlier three-buffer synthetic probe; per-request auxiliary strides were not collected.','KV dtype/tensor strides are not directly measured by receipt metadata; BF16 allocation logs are a separate actual runtime observation.','No official accuracy or performance measurement.'],next_decision='Reuse retained metadata to correct the diagnostic contract; no duplicate GPU run just to change validation. Candidate25682 must independently validate its own H200 registration, transfer and all actual IDs.')
reconciliation=json.loads((O/'RECONCILIATION.json').read_text()) if (O/'RECONCILIATION.json').exists() else None
if reconciliation and reconciliation['posted']:
 review['cost'].update(posting_reconciled=True,posted_charge_su=reconciliation['published_delta_su'],reservation_released=True,reconciliation_source='RECONCILIATION.json')
 cost_note=f"Posted charge is **{reconciliation['published_delta_su']:.3f} SU**; the maximum reservation is released. Internal headroom is **{reconciliation['internal_headroom_su']:.3f} SU** under the unchanged cap and reserve."
else:
 cost_note='The **170.666667 SU maximum reservation remains** until the posted ledger uniquely reconciles it.'
(O/'REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
(O/'REVIEW.md').write_text(f'''# H100223788: real registration data exposed an invalid diagnostic assumption

The original PBS job is **F / exit1**, and its original semantic result is **FAIL**. It reached actual native readiness and HTTP200; all source/H100/draft/HPC-Ops/config checks, eight BF16 target/draft allocation records, eight eager-prefill messages and four native NIXL ranks pass. The sole final rejection is our rule that explicit KV layer IDs must be nonempty. Original frozen bytes/result remain unchanged. [Original result](collected/runs/223788.pbs111/probe-result.json).

## Actual observations

Each of the four ranks has an atomic before/after pair, stable geometry and a successful native registration return. Each advertises **190 VRAM regions**,76,132,096bytes each, totaling **14,465,098,240 advertised bytes per rank**. Item/token byte stride is256, page size1 and page count297391. Local/total KV head metadata is1/4. There are **10 auxiliary regions** with lengths `[6144,6144,6144,6144,49152,49152,6144,12288,786432,6144]` bytes and no advertised state regions. `kv_layer_ids` is explicitly observed as `[]`, not missing; no semantic layer sequence was captured or invented.

The pinned native `get_mha_kv_ptrs_with_pp` computes positional counts from pointer-list length and PP ranges, without requiring `kv_layer_ids`. Thus our nonempty invariant was unsupported. [Exact source excerpt](native-positional-mha-source.py.txt), source SHA `{sha(source)}`. This does not separately establish why the runtime leaves the field empty or prove semantic pointer ordering.

A separately derived candidate-local validator now permits this observed-empty field only for the known190-region/head1,total4/page1 Qwen MHA contract; every rank must still have stable successful before/after receipts and valid bounded values. Missing/null/string/malformed or mismatched shapes still fail. The original shared validator is preserved. Replay of these eight actual hash-verified receipts avoids paying for another startup simply to reclassify retained metadata. Candidate25682 must still collect and validate its own H200 data, both P/D transfers and all1600 exact outputs.

## Cost and observability

Actual allocated runtime: **{seconds} seconds**, four H100 GPUs on a2ap-dgx038; estimated charge **{seconds*4*128/3600:.6f}SU**. {cost_note}48 hardware samples cover four UUIDs; sampled VRAM spans{review['telemetry']['sampled_vram_min_mib']:.0f}–{review['telemetry']['sampled_vram_max_mib']:.0f}MiB. These are startup/native-health observations, not a scored load, utilization proof, startup speedup or physical-region accounting.

Local registration does not prove remote transfer, correct generation, EAGLE3 speedup or official accuracy. Ten actual auxiliary buffers also show why the earlier three-buffer component probe was narrow; per-request auxiliary strides remain uncollected. Keep original failure, useful raw data and corrected interpretation distinct. [Complete raw hashes](collected/evidence-sha256.json), [detailed assessment](REVIEW.json).
'''.replace('H100223788','H100 223788').replace('exit1','exit 1').replace('HTTP200','HTTP 200').replace('regions**,76','regions**, 76').replace('096bytes','096 bytes').replace('is256','is 256').replace('size1','size 1').replace('count297391','count 297391').replace('is1/4','is 1/4').replace('known190','known 190').replace('head1,total4/page1','head 1, total 4 / page 1').replace('Candidate25682','Candidate 25682').replace('all1600','all 1600').replace(':.6f}SU',':.6f} SU').replace('45.368889SU','45.368889 SU').replace('170.666667SU','170.666667 SU').replace('it.48','it. 48').replace('spans','spans ').replace('MiB',' MiB'))
print(json.dumps(dict(job=review['job'],state=review['state'],estimated_su=review['cost']['estimated_allocated_charge_su'],per_rank_regions=190,aux_buffers=10),indent=2))
