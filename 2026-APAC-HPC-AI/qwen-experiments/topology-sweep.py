"""Freeze and submit all 17 topology experiments, respecting the Slurm queue limit."""
import argparse
import csv
import fcntl
import hashlib
import itertools
import json
import os
import re
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SWEEP = ROOT/'topology-sweep'
REGISTRY = SWEEP/'registry.json'
TERMINAL = {'COMPLETED','FAILED','CANCELLED','TIMEOUT','NODE_FAIL','OUT_OF_MEMORY',
            'PREEMPTED','BOOT_FAIL','DEADLINE','REVOKED'}

def now(): return datetime.now(timezone.utc).isoformat()

def save(path, value):
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, indent=2)+'\n')
    temp.replace(path)

def command(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          check=True, timeout=120).stdout

def prepare():
    if REGISTRY.exists(): raise SystemExit('Existing registry; refusing to replace experiment history.')
    SWEEP.mkdir(exist_ok=True)
    worker = (ROOT/'candidate09-fine.sbatch').read_text().split("<<'EOF'\n",1)[1].split('\nEOF',1)[0]+'\n'
    benchmark = (ROOT/'benchmark.sh').read_text()
    benchmark = benchmark.replace('--benchmark-grace-period 30', '--benchmark-grace-period "${QWEN_GRACE:-30}"')
    benchmark = benchmark.replace('run_benchmark "$N" sweep 15 30', 'run_benchmark "$N" sweep "${QWEN_SWEEP_WARM:-10}" "${QWEN_SWEEP_DURATION:-20}"')
    benchmark = benchmark.replace("if r['sla_pass'] and r['good_output_tokens_s'] is not None",
        "if r['phase']=='sweep' and r['sla_pass'] and r['cancelled_requests']==0 and r['good_output_tokens_s'] is not None")
    benchmark = benchmark.replace('  run_benchmark "$BEST" confirm 60 120', '''  if (( ${QWEN_BENCHMARK_DEADLINE:-0} > 0 && $(date +%s)+230 > QWEN_BENCHMARK_DEADLINE )); then
    echo "CONFIRM_SKIPPED: insufficient remaining Slurm time; best sweep N=$BEST"
    printf '%s\\n' "$BEST" >"$ART/confirm-needed.txt"
  else
    run_benchmark "$BEST" confirm 60 120
  fi''')
    configs = []
    for pg in (8,4,12):
        dg = 16-pg
        for pt, dt in itertools.product((2,4,8),(2,4,8)):
            if pg%pt or dg%dt: continue
            configs.append({'id':f'P{pg}-TP{pt}_D{dg}-TP{dt}-EP{dt}',
                            'prefill_gpus':pg,'decode_gpus':dg,'prefill_tp':pt,'decode_tp':dt,
                            'decode_ep':dt,'prefill_workers':pg//pt,'decode_workers':dg//dt})
    assert len(configs)==17
    # Re-measure current best and official 07, then widen each TP direction.
    preferred = ['P8-TP4_D8-TP4-EP4','P8-TP2_D8-TP4-EP4',
                 'P8-TP8_D8-TP4-EP4','P8-TP4_D8-TP8-EP8',
                 'P4-TP4_D12-TP4-EP4','P12-TP4_D4-TP4-EP4']
    configs.sort(key=lambda c: preferred.index(c['id']) if c['id'] in preferred else 100)
    entries = []
    for index, config in enumerate(configs,1):
        config.update(image='/scratch/enroot-images/sglang-harbor.sqsh',
                      client_image='/scratch/enroot-images/aiperf.sqsh',
                      model='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8',
                      concurrency=[16,32,40,48],sweep_warmup_s=10,sweep_measure_s=20,
                      confirm_warmup_s=60,confirm_measure_s=120,grace_s=30,
                      memory_fraction=0.90,decode_max_running_requests=256,
                      context_length=8192,kv_dtype='auto',transfer='nixl')
        bundle = SWEEP/f'{index:02d}-{config["id"]}'
        bundle.mkdir()
        (bundle/'config.json').write_text(json.dumps(config,indent=2)+'\n')
        placement, per_node, used = [], [0,0], 0
        for role in ('prefill','decode'):
            for i in range(config[role+'_workers']):
                tp = config[role+'_tp']
                node = used//8
                assert per_node[node]+tp<=8
                per_node[node]+=tp
                placement.append(f'{role}-{i}\t{node}\t{tp}\t{(30100 if role=="prefill" else 30200)+i}\t{9000+i if role=="prefill" else 0}')
                used+=tp
        assert used==16 and per_node==[8,8]
        (bundle/'placement.tsv').write_text('\n'.join(placement)+'\n')
        for source in ('topology-job.sh','warm-topology.py','summarize.py'):
            (bundle/source).write_text((ROOT/source).read_text())
        (bundle/'worker.sh').write_text(worker)
        (bundle/'benchmark.sh').write_text(benchmark)
        (bundle/'job.sbatch').write_text(f'''#!/bin/bash
#SBATCH -J ap42-{config['id']}
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:17:00
#SBATCH --gres=gpu:8
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
export QWEN_BUNDLE={shlex.quote(str(bundle))}
cd "$QWEN_BUNDLE"
sha256sum --check SHA256SUMS
exec bash "$QWEN_BUNDLE/topology-job.sh"
''')
        hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.iterdir())}
        (bundle/'SHA256SUMS').write_text(''.join(f'{h}  {name}\n' for name,h in hashes.items()))
        for path in bundle.iterdir(): path.chmod(0o444)
        bundle.chmod(0o555)
        entries.append({'index':index,'config':config,'bundle':str(bundle),
                        'frozen_utc':now(),'payload_sha256':hashes,'job':None,'state':'NOT_SUBMITTED'})
    save(REGISTRY,{'created_utc':now(),'scope':'17 homogeneous-role TP topologies, 16 H200, local experiments',
                   'experiments':entries})
    print('Prepared 17 immutable bundles:',REGISTRY,flush=True)

def get_status(ids):
    if not ids: return {}
    out = command(['sacct','-j',','.join(ids),'-X','-P',
                   '--format=JobID,State%30,ExitCode,Elapsed,Start,End'])
    return {r['JobID']:r for r in csv.DictReader(out.splitlines(),delimiter='|')}

def failure_evidence(job, run):
    evidence=[]
    paths=[ROOT/'runs'/f'{job}.err',*sorted(run.glob('*.log'))]
    for path in paths:
        if not path.is_file(): continue
        with path.open('rb') as f:
            f.seek(max(0,path.stat().st_size-16384))
            tail=f.read().decode(errors='replace')
        errors=[line for line in tail.splitlines() if re.search(
            r'FATAL|OutOfMemory|out of memory|AssertionError|RuntimeError|ValueError|TIME LIMIT|error:|Traceback',line,re.I)]
        if errors: evidence.append({'path':str(path.relative_to(ROOT)), 'message':errors[-1][:500]})
    return evidence

def refresh(registry):
    status = get_status([e['job'] for e in registry['experiments'] if e['job']])
    allstatus = json.loads((ROOT/'job-status.json').read_text())
    allstatus.update(status)
    save(ROOT/'job-status.json',allstatus)
    notes = json.loads((ROOT/'run-notes.json').read_text())
    for e in registry['experiments']:
        if not e['job']: continue
        job, run = e['job'], ROOT/'runs'/e['job']
        e['status'] = status.get(job,{})
        e['state'] = e['status'].get('State','SUBMITTED').split()[0].rstrip('+')
        metrics = []
        if run.exists():
            metrics = json.loads(command(['python3',str(ROOT/'summarize.py'),str(run)]))
            save(run/'summary.json',metrics)
        e['metrics'] = metrics
        valid = [r for r in metrics if r['sla_pass'] and r['cancelled_requests']==0 and r['good_output_tokens_s'] is not None]
        best = max(valid,key=lambda r:(r['phase']=='confirm',r['good_output_tokens_s'] or 0),default=None)
        failed=e['state'] in TERMINAL and e['state']!='COMPLETED'
        if failed: e['failure_evidence']=failure_evidence(job,run)
        error_note=' '.join(x['message'] for x in e.get('failure_evidence',[])[:2])
        notes[job] = {'topology':e['config']['id'],'purpose':'Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.',
            'finding':f"Trạng thái {e['state']}; {len(metrics)} lượt đã có raw export."+
                (f" Tốt nhất ({best['phase']}) N{best['concurrency']}: {best['good_output_tokens_s']:.2f} good tokens/s, {best['good_request_fraction']:.2%} SLA." if best else '')+
                (' Dấu lỗi trong log: '+error_note if error_note else ''),
            'lesson':('Nếu thiếu bộ nhớ cần giảm số bản sao/model buffer hoặc tăng TP, rồi đo lại. '
                      if 'out of memory' in error_note.lower() or 'outofmemory' in error_note.lower() else '')+
                     'Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.',
            'performance_evidence':bool(metrics),
            'provenance_note':f"Payload cố định trước submit, hash ở {e['bundle']}/SHA256SUMS; bản sao ở runs/{job}/submitted/. Weights/images ngoài payload."}
    save(ROOT/'run-notes.json',notes)
    registry['updated_utc']=now()
    save(REGISTRY,registry)
    report(registry)

def report(registry):
    def fmt(value, percent=False):
        if value is None: return 'chưa có'
        return f'{value:.2%}' if percent else f'{value:.2f}'
    required=set(registry['experiments'][0]['config']['concurrency'])
    measured=sum(required.issubset({r['concurrency'] for r in e.get('metrics',[]) if r['phase']=='sweep'}) for e in registry['experiments'])
    lines = ['# Đợt đầu: benchmark 17 topology Qwen','',f'Cập nhật UTC: {now()}','',
        'Bảng này giữ số liệu đợt đầu. Tiến độ và số đo chạy lại nằm ở [kết quả phục hồi](RECOVERY_RESULTS.md).','',
        f'**{measured}/17 cấu hình có đủ bốn lượt sweep. {17-measured} cấu hình chưa đo đủ.** '
        'Job FAILED/TIMEOUT hoặc chỉ khởi động được server không được tính là benchmark xong. '
        'Xem [đính chính và sửa lỗi](TOPOLOGY_REVIEW.md).','',
        'Mỗi cấu hình dùng đủ 16 H200, FP8 checkpoint chính thức, SGLang harbor, NIXL, '
        'KV auto, context 8192, memory fraction 0.90. Decode EP bằng TP. '
        'Worker TP2/4/8 nằm trong một node. P/D chia 4+12, 8+8, 12+4; TP phải chia hết số GPU mỗi giai đoạn.','',
        'Sweep N16/32/40/48: warmup 10s, đo 20s, grace 30s. '
        'Confirm điểm sweep tốt nhất qua SLA và không cancelled: 60s/120s/30s nếu còn đủ thời gian job 17 phút. '
        'Sweep ngắn chỉ dùng sàng lọc; confirm là đo nội bộ theo thời lượng BTC, chưa có accuracy/điểm BTC.','',
        'Warm tất cả cặp P/D bằng prompt ngắn riêng trước benchmark; không dùng seed/dataset benchmark. '
        'Payload và checksum được đóng băng trước submit; mỗi job giữ config, placement, logs và exports.','',
        '| # | Topology | P workers | D workers | Job | Trạng thái | Lượt có số đo |',
        '|---:|---|---:|---:|---|---|---:|']
    rows=[]
    for e in registry['experiments']:
        c=e['config']; job=e['job'] or 'chưa gửi'
        lines.append(f"| {e['index']} | {c['id']} | {c['prefill_workers']} | {c['decode_workers']} | {job} | {e['state']} | {len(e.get('metrics',[]))} |")
        rows.extend({'job':e['job'],'topology':c['id'],**r} for r in e.get('metrics',[]))
    lines += ['','## Số đo đã có','',
              '| Job | Topology | Lượt/N | SLA | Good tokens/s | TTFT TB ms | ITL TB ms | Cancelled |',
              '|---|---|---|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['job']} | {r['topology']} | {r['phase']}/N{r['concurrency']} | {fmt(r['good_request_fraction'],True)} | {fmt(r['good_output_tokens_s'])} | {fmt(r['ttft_avg_ms'])} | {fmt(r['itl_avg_ms'])} | {r['cancelled_requests']} |")
    valid = [r for r in rows if r['phase']=='confirm' and r['sla_pass'] and r['cancelled_requests']==0 and r['good_output_tokens_s'] is not None]
    lines += ['','## Điểm đo dài cao nhất trong đợt này','',
              'Mốc trước đợt này: 09/N40, job 22200, **1649.27 good tokens/s, 97.81% SLA**, cancelled=0.','']
    if valid:
        best=max(valid,key=lambda r:r['good_output_tokens_s'])
        lines += [f"**{best['topology']} /N{best['concurrency']}**: **{best['good_output_tokens_s']:.2f} good tokens/s**, "
                  f"{best['good_request_fraction']:.2%} SLA, job {best['job']}. Đây là số đo một deployment, chưa đánh giá độ dao động."]
    else: lines += ['Chưa có confirm hợp lệ trong đợt 17 topology.']
    failed=[e for e in registry['experiments'] if e.get('failure_evidence')]
    if failed:
        lines+=['','## Lỗi được giữ làm dữ kiện','']
        for e in failed:
            lines.append(f"- Job {e['job']}, {e['config']['id']}, {e['state']}:")
            for evidence in e['failure_evidence'][:3]:
                message=evidence['message'].replace('`','').replace('\n',' ')
                lines.append(f"  - [{evidence['path']}]({evidence['path']}): `{message}`")
    lines += ['','[Registry cấu hình, hash payload, trạng thái và metrics](topology-sweep/registry.json) · '
              '[JSON tất cả số đo](topology-comparison.json) · [Sổ lỗi/các lần chạy trước](RUNS.md)','']
    (ROOT/'TOPOLOGY_RESULTS.md').write_text('\n'.join(lines))
    save(ROOT/'topology-comparison.json',rows)
    with (ROOT/'topology-experiments.csv').open('w',newline='') as f:
        fields=['job','topology','phase','concurrency','sla_pass','good_request_fraction',
                'good_output_tokens_s','ttft_avg_ms','itl_avg_ms','cancelled_requests','export']
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)

def run():
    lock=(SWEEP/'controller.lock').open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    (SWEEP/'controller.pid').write_text(str(os.getpid())+'\n')
    previous=None
    while True:
        try:
            registry=json.loads(REGISTRY.read_text())
            refresh(registry)
            live=command(['squeue','-h','-u',os.environ['USER'],'-o','%i']).splitlines()
            room=max(0,4-len(live))
            for e in [e for e in registry['experiments'] if e['job'] is None][:room]:
                output=command(['sbatch','--parsable','--chdir',str(ROOT),str(Path(e['bundle'])/'job.sbatch')])
                e['job']=output.strip().split(';')[0]
                assert e['job'].isdigit(),output
                e['submitted_utc']=now(); e['state']='SUBMITTED'
                save(REGISTRY,registry)
                print(now(),'SUBMITTED',e['job'],e['config']['id'],flush=True)
            # Audit every terminal attempt, not just successful measurements.
            # Include topology rows while retaining the old comparison report.
            command(['python3',str(ROOT/'compare.py')])
            original=json.loads((ROOT/'comparison.json').read_text())
            save(ROOT/'comparison.json',original+json.loads((ROOT/'topology-comparison.json').read_text()))
            command(['python3',str(ROOT/'audit-runs.py')])
            states={e['config']['id']:e['state'] for e in registry['experiments']}
            if states!=previous: print(now(),json.dumps(states),flush=True); previous=states
            if all(e['job'] and e['state'] in TERMINAL for e in registry['experiments']):
                measured=sum({16,32,40,48}.issubset({r['concurrency'] for r in e.get('metrics',[]) if r['phase']=='sweep'}) for e in registry['experiments'])
                print(now(),f'All original job attempts ended; {measured}/17 benchmarks complete. Failed deployments are NOT complete benchmarks. See repair pipeline.',flush=True)
                break
        except Exception as error:
            print(now(),type(error).__name__,str(error),flush=True)
        time.sleep(45)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--refresh',action='store_true')
    args=parser.parse_args()
    if args.prepare: prepare(); report(json.loads(REGISTRY.read_text()))
    if args.refresh: refresh(json.loads(REGISTRY.read_text()))
    if args.run: run()
