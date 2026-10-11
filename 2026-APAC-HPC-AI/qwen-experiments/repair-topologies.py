"""Recover missing benchmarks; a terminal Slurm job is never a completion criterion."""
import argparse
import csv
import fcntl
import hashlib
import json
import os
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DIR=ROOT/'topology-repair'
STATE=DIR/'recovery.json'
TERMINAL={'COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY','PREEMPTED'}
NS={16,32,40,48}

def now(): return datetime.now(timezone.utc).isoformat()

def save(path,data):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2)+'\n'); temporary.replace(path)

def cmd(args):
    return subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=True,timeout=120).stdout

def prepare():
    if STATE.exists(): raise SystemExit('Recovery already exists; refusing to replace history.')
    original=json.loads((ROOT/'topology-sweep/registry.json').read_text())
    pilot=json.loads((DIR/'registry.json').read_text())['pilot']
    entries=[]
    for e in original['experiments']:
        if e['metrics']: continue
        c=dict(e['config']); pt=c['prefill_tp']
        variant=pt==8
        if variant: c['id']=c['id'].replace('TP8_', 'TP8-EP2_',1)
        c['prefill_ep']=2 if variant else 1
        c['nccl_port_policy']='20000 + http_port - 30100 (outside ephemeral range)'
        record={'index':e['index'],'original_id':e['config']['id'],'original_job':e['job'],
                'config':c,'variant':variant,'attempts':[],
                'benchmark_complete':False,'confirmed':False,'measurements':[],
                'original_status':'INCOMPATIBLE_FP8_BLOCK_SHARD' if variant else 'UNMEASURED',
                'blocking_evidence':str(ROOT/'runs'/e['job']/'prefill-0.log') if variant else None}
        if e['job']==pilot['config']['repair_of_job']:
            record['attempts']=[{'job':pilot['job'],'bundle':pilot['bundle'],'phase':'sweep',
                                 'ns':[16,32,40,48],'state':'SUBMITTED','pair_timeout_s':360}]
        entries.append(record)
    save(STATE,{'created_utc':now(),'original_already_measured':8,'entries':entries,
                'benchmark_complete':False,'status':'RECOVERING',
                'criterion':'Four canonical measured sweeps with requests>0 and cancelled=0; FAILED/TIMEOUT is unmeasured. FP8-block-incompatible originals remain explicitly blocked; EP2 replacements are distinct variants.'})

def freeze(entry,phase,ns,timeout_s):
    number=len(entry['attempts'])+1
    bundle=DIR/f"{entry['index']:02d}-{entry['config']['id']}-a{number}-{phase}"
    bundle.mkdir()
    original=json.loads((ROOT/'topology-sweep/registry.json').read_text())
    source=Path(next(e['bundle'] for e in original['experiments'] if e['job']==entry['original_job']))
    for name in ('worker.sh','summarize.py','placement.tsv'):
        (bundle/name).write_text((source/name).read_text())
    # Cold NIXL registration must have time to finish. These initialization
    # deadlines do not change the measured TTFT/ITL limits or client grace.
    worker=(bundle/'worker.sh').read_text()
    worker=worker.replace('set -euo pipefail', 'set -euo pipefail\nexport SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=600\nexport SGLANG_DISAGGREGATION_WAITING_TIMEOUT=600',1)
    patch_enabled=bool(entry['config'].get('nixl_on_demand'))
    patch_meta=None
    if patch_enabled:
        patchdir=(ROOT/entry['config'].get('nixl_patch_directory','nixl-ondemand')).resolve()
        if patchdir.parent != ROOT:
            raise ValueError('NIXL patch directory must be directly inside experiment root')
        patch_meta=json.loads((patchdir/'metadata.json').read_text())
        patch_bytes=(patchdir/'conn.py').read_bytes()
        if hashlib.sha256(patch_bytes).hexdigest()!=patch_meta['patched_sha256']:
            raise ValueError('NIXL patch source hash mismatch')
        if not json.loads((patchdir/'geometry-test.json').read_text()).get('passed'):
            raise ValueError('NIXL patch geometry test has not passed')
        for src,dst in [('conn.py','nixl-conn.py'),('nixl-ondemand.patch','nixl-ondemand.patch'),
                        ('metadata.json','nixl-patch-metadata.json'),('geometry-test.json','nixl-geometry-test.json')]:
            (bundle/dst).write_bytes((patchdir/src).read_bytes())
        worker=worker.replace('exec python3 -m sglang.launch_server', '''python3 - <<'PATCHCHECK'
import hashlib,os
from pathlib import Path
path=Path('/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py')
actual=hashlib.sha256(path.read_bytes()).hexdigest()
assert actual==os.environ['QWEN_NIXL_PATCH_SHA256'], 'NIXL patch mount/hash mismatch'
print('NIXL_PATCH_VERIFIED',actual,flush=True)
PATCHCHECK
exec python3 -m sglang.launch_server''',1)
    (bundle/'worker.sh').write_text(worker)
    benchmark=(source/'benchmark.sh').read_text()
    # Avoid starting a four-point sweep that can collide with the 17-minute limit.
    # Remaining points are scheduled under a new job ID if needed.
    benchmark=benchmark.replace('for N in ${QWEN_SWEEP_NS:-16 32 64}; do', '''for N in ${QWEN_SWEEP_NS:-16 32 64}; do
  if (( $(date +%s)+100 > ${QWEN_BENCHMARK_DEADLINE:-0} )); then
    echo "SWEEP_INCOMPLETE: insufficient job time before N=$N; schedule remaining points separately"
    exit 0
  fi''')
    (bundle/'benchmark.sh').write_text(benchmark)
    for name in ('topology-job.sh','warm-topology.py'):
        (bundle/name).write_text((ROOT/name).read_text())
    config=dict(entry['config'],phase=phase,concurrency=ns,pair_timeout_s=timeout_s,
                nccl_port_policy='20000 + http_port - 30100 (outside ephemeral range)',
                disaggregation_bootstrap_timeout_s=600,disaggregation_waiting_timeout_s=600,
                original_job=entry['original_job'],is_prefill_ep_variant=entry['variant'])
    config['transport_patch']=patch_meta['name'] if patch_meta else None
    if patch_meta:config['transport_patch_metadata']=patch_meta
    (bundle/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    extra=f'export QWEN_CONFIRM_ONLY=1\nexport QWEN_CONFIRM_N={ns[0]}\n' if phase=='confirm' else ''
    if patch_meta:extra+=f"export QWEN_NIXL_PATCH_SHA256={patch_meta['patched_sha256']}\n"
    (bundle/'job.sbatch').write_text(f'''#!/bin/bash
#SBATCH -J ap42-fix-{entry['index']:02d}-{phase}
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE={shlex.quote(str(bundle))}
export QWEN_PREFILL_EP={config['prefill_ep']}
export QWEN_PAIR_TIMEOUT={timeout_s}
export QWEN_SWEEP_NS={shlex.quote(' '.join(map(str,ns)))}
{extra}cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
''')
    for name in ('job.sbatch','topology-job.sh','worker.sh','benchmark.sh'):
        cmd(['bash','-n',str(bundle/name)])
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
    (bundle/'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()))
    for p in bundle.iterdir():p.chmod(0o444)
    bundle.chmod(0o555)
    return bundle,hashes

def refresh(data):
    attempts=[a for e in data['entries'] for a in e['attempts']]
    ids=[a['job'] for a in attempts]
    status={}
    if ids:
        text=cmd(['sacct','-j',','.join(ids),'-X','-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'])
        status={r['JobID']:r for r in csv.DictReader(text.splitlines(),delimiter='|')}
    allstatus=json.loads((ROOT/'job-status.json').read_text()); allstatus.update(status)
    save(ROOT/'job-status.json',allstatus)
    notes=json.loads((ROOT/'run-notes.json').read_text())
    rows=[]
    for e in data['entries']:
        e['measurements']=[]
        for a in e['attempts']:
            a['status']=status.get(a['job'],{})
            a['state']=a['status'].get('State','SUBMITTED').split()[0].rstrip('+')
            if (a.get('replacement_requested') and a['state']=='CANCELLED'
                and a['status'].get('Start') in (None,'None','Unknown','')
                and a['status'].get('Elapsed')=='00:00:00'):
                a['replaced_before_start']=True
                a['replacement_reason']=a['replacement_requested']
            run=ROOT/'runs'/a['job']
            metrics=[]
            if run.is_dir():
                metrics=json.loads(cmd(['python3',str(ROOT/'summarize.py'),str(run)]))
                save(run/'summary.json',metrics)
            a['metrics']=metrics
            actual_config=json.loads((Path(a['bundle'])/'config.json').read_text())
            patch_name=actual_config.get('transport_patch')
            e['measurements'] += [{'job':a['job'],'topology':e['config']['id'],
                                  'transport_patch':patch_name,**m} for m in metrics]
            notes[a['job']]={'topology':e['config']['id'],'purpose':f"Recovery of {e['original_job']}; {a['phase']} N{a['ns']}.",
                'finding':f"Slurm {a['state']}; {len(metrics)} exports. Failure is not a completed benchmark.",
                'lesson':'Fixed distinct NCCL ports and bounded cold-path warmup. '+('Prefill EP2 is a distinct variant to align FP8 expert shards.' if e['variant'] else 'Original worker TP/EP arrangement retained.')+(f' Transport patch: {patch_name}.' if patch_name else ''),
                'performance_evidence':bool(metrics),'provenance_note':f"Frozen payload before submission: {a['bundle']}; original failed logs preserved."}
            if a.get('replacement_reason'):
                notes[a['job']]['finding']+=' '+a['replacement_reason']
        required_patch=e['config'].get('required_measurement_transport')
        eligible=[m for m in e['measurements'] if not required_patch or m.get('transport_patch')==required_patch]
        measured={m['concurrency'] for m in eligible if m['phase']=='sweep' and (m.get('requests') or 0)>0 and m['cancelled_requests']==0}
        e['benchmark_complete']=NS.issubset(measured)
        e['missing_ns']=sorted(NS-measured)
        e['confirmed']=any(m['phase']=='confirm' and (m.get('requests') or 0)>0 and m['cancelled_requests']==0 for m in eligible)
        e['has_passing_sweep']=any(m['phase']=='sweep' and m['sla_pass'] and m['cancelled_requests']==0 and m['good_output_tokens_s'] is not None for m in eligible)
        if e['benchmark_complete'] and not e['variant']:e['original_status']='BENCHMARK_MEASURED'
        rows += e['measurements']
    save(ROOT/'run-notes.json',notes)
    save(DIR/'measurements.json',rows)
    data['updated_utc']=now()
    data['benchmark_complete']=all(e['benchmark_complete'] for e in data['entries'])
    data['status']='BENCHMARKS_RECOVERED_WITH_EXPLICIT_EP2_VARIANTS' if data['benchmark_complete'] else 'INCOMPLETE'
    save(STATE,data)
    report(data)
    # Reuse raw artifact sealing and include new measurements in the existing ledger.
    cmd(['python3',str(ROOT/'compare.py')])
    previous=json.loads((ROOT/'comparison.json').read_text())
    save(ROOT/'comparison.json',previous+json.loads((ROOT/'topology-comparison.json').read_text())+rows)
    cmd(['python3',str(ROOT/'audit-runs.py')])

def report(data):
    exact=8+sum(e['benchmark_complete'] and not e['variant'] for e in data['entries'])
    variants=sum(e['benchmark_complete'] and e['variant'] for e in data['entries'])
    lines=['# Đang phục hồi benchmark còn thiếu','',f'Cập nhật UTC: {now()}','',
        f'**{exact}/17 cấu hình gốc có đủ bốn lượt sweep.** '
        f'**{variants}/3 biến thể prefill EP2 có đủ số đo.** '
        'Ba cấu hình gốc TP8/EP1 không khớp block FP8 trong image hiện tại; biến thể EP2 được ghi riêng, không tính giả thành cấu hình gốc đã đo.','',
        'Job lỗi, timeout hoặc chỉ deploy server không được tính là hoàn thành benchmark. '
        'Các mức N thiếu được gửi lại dưới job ID mới. Điểm qua SLA được đo dài nếu cần.','',
        '| # | Cấu hình chạy lại | Gốc / biến thể | Job và trạng thái | Mức N còn thiếu | Confirm |',
        '|---:|---|---|---|---|---|']
    for e in data['entries']:
        jobs=', '.join(f"{a['job']}:{a['state']}" for a in e['attempts']) or 'chưa gửi'
        lines.append(f"| {e['index']} | {e['config']['id']} | {'EP2 variant' if e['variant'] else 'gốc'} | {jobs} | {e['missing_ns']} | {e['confirmed']} |")
    lines+=['','Bản vá truyền KV theo request, nếu áp dụng, được ghi riêng ở cột Transport. '
            'Nó giữ weights, precision và phép tính model; số đo có bản vá là serving stack đã sửa.','',
            '## Số đo','', '| Job | Config | Transport | Lượt/N | SLA | Good tokens/s | Cancelled |', '|---|---|---|---|---:|---:|---:|']
    for e in data['entries']:
        for m in e['measurements']:
            fraction=f"{m['good_request_fraction']:.2%}" if m['good_request_fraction'] is not None else 'chưa có'
            rate=f"{m['good_output_tokens_s']:.2f}" if m['good_output_tokens_s'] is not None else 'chưa có'
            lines.append(f"| {m['job']} | {m['topology']} | {m.get('transport_patch') or 'image gốc'} | {m['phase']}/N{m['concurrency']} | {fraction} | {rate} | {m['cancelled_requests']} |")
    lines+=['','[Registry phục hồi](topology-repair/recovery.json) · [Đợt đầu](TOPOLOGY_RESULTS.md) · [Log và lịch sử](RUNS.md)','']
    (ROOT/'RECOVERY_RESULTS.md').write_text('\n'.join(lines))

def promote_transport_after_measurement(data):
    """Use the patch elsewhere only after its pilot actually serves the workload."""
    pilot_job=data.get('transport_validation_pilot')
    if not pilot_job or data.get('transport_patch_proven'):return
    pilot=next((a for e in data['entries'] for a in e['attempts'] if a['job']==pilot_job),None)
    if pilot is None:return
    config=json.loads((Path(pilot['bundle'])/'config.json').read_text())
    if not config.get('transport_patch'):return
    evidence=next((m for m in pilot.get('metrics',[]) if m['phase']=='sweep'
        and (m.get('requests') or 0)>0 and m['cancelled_requests']==0 and m.get('errors')==0),None)
    if evidence is None:return
    data['transport_patch_proven']={'job':pilot_job,'utc':now(),'export':evidence['export'],
        'criterion':'Real 4000/200 sweep with requests>0, errors=0 and cancelled=0; not an accuracy claim.'}
    for entry in data['entries']:
        if entry['benchmark_complete'] or entry['config']['prefill_tp']==entry['config']['decode_tp']:continue
        entry['config']['nixl_on_demand']=True
        for attempt in entry['attempts']:
            if attempt['state']!='PENDING' or attempt['phase']!='sweep':continue
            cfg=json.loads((Path(attempt['bundle'])/'config.json').read_text())
            if cfg.get('transport_patch'):continue
            state=cmd(['squeue','-h','-j',attempt['job'],'-o','%T']).strip()
            if state!='PENDING':continue
            cmd(['scancel','--state=PENDING',attempt['job']])
            attempt['replacement_requested']='Pilot '+pilot_job+' served the actual workload; replace unstarted full-pool transfer retry with on-demand descriptors.'
            print(now(),'REPLACE_PENDING',attempt['job'],entry['config']['id'],flush=True)
    save(STATE,data)
    print(now(),'TRANSPORT_PATCH_PROVEN',pilot_job,'N',evidence['concurrency'],flush=True)

def run():
    lock=(DIR/'recovery.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    (DIR/'recovery.pid').write_text(str(os.getpid())+'\n')
    previous=None
    while True:
        try:
            data=json.loads(STATE.read_text()); refresh(data)
            promote_transport_after_measurement(data)
            pilot=data['entries'][0]
            # Do not mass-submit a shared warmup fix until the pilot produces data.
            pilot_proven=any((m.get('requests') or 0)>0 and m['cancelled_requests']==0 for m in pilot['measurements'])
            live=cmd(['squeue','-h','-u',os.environ['USER'],'-o','%i']).splitlines()
            room=max(0,4-len(live))
            for e in data['entries']:
                if room<=0:break
                if e is not pilot and not pilot_proven:continue
                if any(a['state'] not in TERMINAL for a in e['attempts']):continue
                if e['benchmark_complete']:
                    if e['confirmed'] or not e['has_passing_sweep']:continue
                    if sum(a['phase']=='confirm' and not a.get('replaced_before_start') for a in e['attempts'])>=2:continue
                    phase='confirm'
                    required_patch=e['config'].get('required_measurement_transport')
                    valid=[m for m in e['measurements'] if m['phase']=='sweep' and m['sla_pass'] and m['cancelled_requests']==0 and m['good_output_tokens_s'] is not None and (not required_patch or m.get('transport_patch')==required_patch)]
                    ns=[max(valid,key=lambda m:m['good_output_tokens_s'])['concurrency']]
                else:
                    counted=[a for a in e['attempts'] if a['phase']=='sweep' and not a.get('replaced_before_start')]
                    if len(counted)>=e.get('max_sweep_attempts',4):continue
                    phase='sweep'; ns=e['missing_ns']
                    patch_first_try=e['config'].get('nixl_on_demand') and not any(
                        json.loads((Path(a['bundle'])/'config.json').read_text()).get('transport_patch')
                        for a in counted)
                    if counted and not patch_first_try: ns=ns[:2]
                timeout_s=360 if not e['attempts'] else 480
                bundle,hashes=freeze(e,phase,ns,timeout_s)
                job=cmd(['sbatch','--parsable','--chdir',str(ROOT),str(bundle/'job.sbatch')]).strip().split(';')[0]
                assert job.isdigit()
                e['attempts'].append({'job':job,'bundle':str(bundle),'phase':phase,'ns':ns,
                                     'state':'SUBMITTED','submitted_utc':now(),'payload_sha256':hashes,'pair_timeout_s':timeout_s})
                save(STATE,data);room-=1
                print(now(),'SUBMITTED',job,e['config']['id'],phase,ns,flush=True)
            states=[(e['config']['id'],e['benchmark_complete'],e['missing_ns'],[(a['job'],a['state']) for a in e['attempts']]) for e in data['entries']]
            if states!=previous:print(now(),json.dumps(states),flush=True);previous=states
            done=data['benchmark_complete'] and all(e['confirmed'] or not e['has_passing_sweep'] for e in data['entries'])
            if done:
                print(now(),'Recovery measurements complete; three EP2 variants remain explicitly distinct from incompatible original EP1 configs.',flush=True);break
            # Keep monitoring if retries are exhausted; never report success on failure.
        except Exception as error:print(now(),type(error).__name__,str(error),flush=True)
        time.sleep(45)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--run',action='store_true')
    a=p.parse_args()
    if a.prepare:prepare();refresh(json.loads(STATE.read_text()))
    if a.run:run()
