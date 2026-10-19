"""Record accepted interaction results, closed branch, budgets and actual receipts."""
from pathlib import Path
import csv,datetime,fcntl,json,shutil,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;W=Path('/home/apacsc42/workspace');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
reviews={j:json.loads((O/(j+'-review.json')).read_text()) for j in ['24723','24724']};assert all(x['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS' for x in reviews.values())
slurm=subprocess.check_output(['squeue','-u','apacsc42','-o','%.18i %.12P %.34j %.8T %.10M %.6D %R'],text=True);(O/'slurm-latest.txt').write_text(slurm)
raw=subprocess.check_output(['sacct','-X','-j','24723,24724,24732,24733,24736,24737,24738','-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True);(O/'slurm-latest-accounting.txt').write_text(raw);statuses={x['JobID']:x for x in csv.DictReader(raw.splitlines(),delimiter='|')}
result=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch',"bash -lc 'qstat -u apacsc42; qstat -f 221645.pbs111 221646.pbs111 221669.pbs111'"],capture_output=True,text=True,timeout=40);(O/'pbs-latest.txt').write_text(result.stdout);(O/'pbs-latest.stderr').write_text(result.stderr);assert result.returncode==0
budget=json.loads((R/'nscc-pbs/nscc-budget.json').read_text());active=[x for x in budget['pending_reservations'] if x['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'}];assert {x['job_id'] for x in active}=={'221645.pbs111','221646.pbs111','221669.pbs111'} and sum(x['max_charge_su'] for x in active)==4608
report='''# H200 chunk/decode interaction and prefill communication trial

Checked on 19 October 2026. The user requested further optimisation. [PLAN.md](PLAN.md) records hypotheses, controls, cost and stopping rules. Raw snapshots and post-completion hashes are retained; scheduler states below are dated checks.

## New completed H200 measurements

| Job | Configuration at concurrency 58 | Good tokens/s | Joint SLA (%) | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
|24721|Fresh DeepGEMM prefill chunk 8192, auto decode control|2780.403|98.7889|784.526|16.498|
|24723|DeepGEMM prefill chunk 12288, auto decode|2714.261|98.4724|922.231|16.258|
|24724|DeepGEMM prefill chunk 8192, HPC-Ops decode|2938.628|98.9065|871.991|14.998|

**24724 is the new highest locally accepted H200 observation: 2938.628 good tokens/s, +5.6907% versus the fresh same-N58 control 24721.** This isolates the decode runner at the chunk-8192 prefill setting. The earlier chunk-4096 runner comparison gained only about 0.21% at N58, so do not assume a runner effect independent of chunk/batching. This useful interaction requires an independent repeat and fresh matched control, now submitted. It is not a reproduced gain or a statistical confidence claim. It also changes more than load compared with the previous N60 auto-decode peak 2839.532, so do not use that cross-load comparison to isolate the backend gain.

**24723 loses 2.3789%** versus same-N58 chunk-8192 control. Mean TTFT worsens even though mean ITL is slightly lower. Close the chunk-12288 branch without an unchanged retry or automatically increasing chunk again. Retain the full passing-but-slower measurement as evidence.

Both completed candidates pass successful terminal accounting, exact planned submitted hashes, complete unchanged raw 60-second warmup / 120-second scoring / 30-second grace, no request errors/cancellations, joint latency gate, short-output nonregression and all 12 long retrieval checks. Their resolved runtime differences are restricted to the intended prefill chunk/graph geometry or decode main/inherited speculative MoE runner, apart from random seeds. Speculative decoding remains disabled, BF16 KV retained, all decode NIXL/MNNVL/attention ranks present, and HPC-Ops preflight passes. The whole-client guard did not fire. Full organiser accuracy at 99% of the reference score remains unverified.

Good tokens/s means qualifying requests per second multiplied by the prescribed 200 output tokens. Each request must satisfy TTFT ≤ 3000 ms and mean ITL ≤ 20 ms; at least 90% of all requests must pass jointly. The table reports means in milliseconds, which do not replace the per-request joint gate.

## New H200 jobs and matched comparisons

| Job | Purpose | Comparison |
|---|---|---|
|24736|Fresh chunk-8192 auto-decode N58 control|Match24737 at identical load and prefill setting|
|24737|Independent chunk-8192 HPC-Ops-decode N58 repeat|Repeat24724 and compare fresh24736|
|24738|Same HPC-Ops-decode interaction at N60|Compare24737 for load and pending auto-decode N60 repeat24732 for runner|

All three request 16 GPUs / 17 minutes. Operational worker/client/quality/precision/transport payloads are byte-identical to their declared sources. Existing 24732 auto-decode N60 repeat and 24733 N62 keep their positions. At the latest check 24732 is running; the other four are pending Resources. At most five own H200 jobs are active. No automatic next load step or unchanged failure retry.

## H100: one source-checked communication hypothesis

The existing both-phase HPC-Ops N54 repeat221645 and N56 trial221646 remain queued in sequence. Added **221669.pbs111**, fixed N54 with prefill-only `NCCL_ALGO=allreduce:Tree`, after221646. Decode worker code/environment remains unchanged. It enables the existing separate post-score diagnostic profile, not modified ranked benchmark traffic. Verify actual Tree execution on every prefill rank before claiming activation; a printed environment setting alone is insufficient.

Actual H100 prefill logs from sealed job221346 and new H200 logs report **NCCL2.28.9**. Sparse inspection of the tested image retains the matching header, PyNccl version query, NCCL all-reduce call and SGLang dispatch code with hashes under engine-source-v2/. SGLang can choose custom collective paths, which is another reason to verify the trace. The H100 profile shows one Ring all-reduce kernel at22.784%/24.007% of summed prefill kernel durations; these are not elapsed critical-path shares or predicted speedup.

NVIDIA documents per-collective algorithm selection from2.24, Tree support and automatic default selection. Restricting algorithms can fail or be slower. [NVIDIA NCCL2.28 environment reference](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2283/user-guide/docs/env.html#nccl-algo), accessed19October2026. The fixed-N54 trial compares with queued default-algorithm repeat221645 and source221590. Output checks remain mandatory because a different floating-point reduction order can change numerics. A useful outcome needs later confirmation; no new performance result is inferred from the documentation or CPU inspection.

The first source probe used unsupported `unsquashfs -cat`; the next sparse extraction refused an existing empty destination. These were local tooling failures, not missing runtime files. Successful corrected extraction uses a new destination, with original output/errors and hashes preserved. No GPU was allocated for inspection.

## Budget and current limits

The newly queried ledger as of19October13:40:01SGT reports **Used27975.680SU, Balance36024.320SU, InDoubt0SU**. The additional398.222SU reconciles terminal221590 (16 GPUs,11:40walltime at128SU/GPU-hour) within rounding. Its old conservative reservation is now released only because that charge appears in Used.

The new communication job reserves at most1536SU. All three outstanding PBS jobs reserve at most**4608SU total**, each16GPUs/45minutes in verified `221645→221646→221669` order. Conservative internal operating headroom is **18416.320SU**, under unchanged51000SU bound and13000SU buffer. These are planning limits, not organiser quotas or expected expenditure; no budget increase. Do not subtract In Doubt twice from reported Balance. New PBS jobs have no score yet.

No new VPN authentication, background AI, schedule, slide, official submission package, HPC task or organiser upload. The latest H100 accepted peak remains221590 N54 at2430.891goodtokens/s until new jobs finish and pass full review. Safe work is captured into the existing private Git archive; external artifact bytes remain local and require their separate off-host copy.
'''
replacements={'Match24737':'Match 24737','Repeat24724':'Repeat 24724','fresh24736':'fresh 24736','Compare24737':'Compare 24737','repeat24732':'repeat 24732','repeat221645':'repeat 221645','trial221646':'trial 221646','after221646':'after 221646','job221346':'job 221346','NCCL2.28.9':'NCCL 2.28.9','at22.784':'at 22.784','from2.24':'from 2.24','NCCL2.28':'NCCL 2.28','accessed19October2026':'accessed 19 October 2026','source221590':'source 221590','of19October13:40:01SGT':'of 19 October 13:40:01 SGT','Used27975.680SU':'Used 27975.680 SU','Balance36024.320SU':'Balance 36024.320 SU','InDoubt0SU':'In Doubt 0 SU','additional398.222SU':'additional 398.222 SU','terminal221590':'terminal 221590','11:40walltime':'11:40 walltime','at128SU/GPU-hour':'at 128 SU/GPU-hour','most1536SU':'most 1536 SU','4608SU':'4608 SU','each16GPUs/45minutes':'each 16 GPUs / 45 minutes','18416.320SU':'18416.320 SU','unchanged51000SU':'unchanged 51000 SU','and13000SU':'and 13000 SU','remains221590':'remains 221590','at2430.891goodtokens/s':'at 2430.891 good tokens/s'}
for a,b in replacements.items():report=report.replace(a,b)
(O/'RESULTS.md').write_text(report);(O/'checked-utc.txt').write_text(now+'\n')
# Preserve prior handoff; front-load current results without discarding history.
archive=W/'notes/archive';archive.mkdir(exist_ok=True);old=archive/'CURRENT-20261019-github.md'
if not old.exists():shutil.copyfile(W/'notes/CURRENT.md',old)
p=W/'notes/CURRENT.md';s=p.read_text();start=s.index('## Foreground repository publication');end=s.index('## Accepted local measurements',start)
front='''## Current research — 19 October 2026, 06:00–06:05 UTC

The user requested continued optimisation. Latest full review, source inspection, plan and actual receipts: [chunk/decode interaction and prefill communication](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md). Check live schedulers again for any later status claim.

**H200 24724 = 2938.628 good tokens/s**, +5.6907% versus fresh same-N58 auto-decode control 24721 = 2780.403. DeepGEMM prefill chunk 8192 plus HPC-Ops decode passes every local protocol/runtime/short/12-long gate. This is one observation, not a reproduced gain. New jobs: **24736** fresh auto-decode N58 control, **24737** interaction N58 repeat, **24738** interaction N60. Compare 24738 with 24737 for load and 24732 for runner. Five active H200 jobs: **24732** auto N60 repeat is running; **24733** auto N62 and **24736–24738** pending. Preserve positions; each 16 GPUs / 17 minutes.

**24723 chunk 12288 loses 2.3789%** versus control, despite local correctness/SLA pass. Close that branch without an unchanged retry or larger chunk. Original N60 auto-decode 24722 = 2839.532 remains a useful earlier point. No automatic higher load or promotion from a single result; whole-client timeout is failure, not a passing measurement.

H100 peak still **221590 N54 = 2430.891** (prior N52 repeat 221589 = 2411.304). PBS chain **221645 N54 repeat → 221646 N56 → 221669 N54 prefill-Tree** is verified serial, at most one 16-GPU allocation running. All three are queued/dependency-held at this check. New fixed-N54 candidate changes only prefill NCCL algorithm selection; decode retained. The existing separate post-score N48 profile must prove actual Tree execution. Log env alone is insufficient. No new PBS score yet.

Runtime logs and exact image header establish NCCL 2.28.9. Sealed H100 profile shows Ring all-reduce share 22.784%/24.007% of summed prefill kernel durations; not elapsed bottleneck shares or speed predictions. Exact image source shows PyNccl version/all-reduce calls and SGLang dispatch; actual GPU activation still required. NVIDIA 2.28 documentation and source hashes are linked in the latest report. Local extraction option/destination mistakes are preserved and corrected; no GPU used for inspection.

VPN/SSH remain usable without restart or authentication. Ledger as of 19 October 13:40:01 SGT: Used 27975.680 SU, Balance **36024.320 SU**, In Doubt 0. Terminal 221590 charge reconciled in Used. Total three-job PBS maximum reserve **4608 SU**, conservative internal headroom **18416.320 SU**, unchanged 51000-SU bound and 13000-SU buffer. Budget reconciled under lock; no increase or double prepayment deduction. Never retry uncertain submissions.

## Private Git archive

The private GitHub repo is https://github.com/trungdangtapcode/apac-hpc-ai-research. The 60-commit history correction was verified at 906ae52; new milestones use actual dates and ordinary pushes. Preserve provenance/history-rewrite-20261019.json. GitHub stores Git, not the sibling external object store; those bytes remain local. Edit active sources once, then explicit safe capture, verify, commit and push; no automatic mirror.

'''
s=s[:start]+front+s[end:];s=s.replace('Latest complete review: [new operating points](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0527/RESULTS.md).','Latest complete review: [interaction result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md).');s=s.replace('Potential future prefill communication trial needs exact NCCL version/active-communicator validation and a same-platform control before submission. No new credit reserved for it.','Prefill Tree trial is now explicitly submitted as 221669 after source/version/profile review. Its activation and performance still require GPU evidence; compare with 221645 N54 default-algorithm repeat.');p.write_text(s)
notice=f'''## Manual optimisation — {now}

H200 24724 passes at 2938.628 good tokens/s, +5.6907% versus fresh same-N58 control 24721. Chunk-12288 job 24723 passes but loses 2.3789%; close it. Submitted H200 24736/24737/24738 for fresh control, independent interaction repeat and N60. Existing 24732 running, 24733 pending. Submitted one source-checked H100 N54 prefill Tree trial 221669 after 221646, preserving 221645→221646→221669 serial chain. Total PBS max reserve 4608 SU; ledger Balance 36024.320 SU, internal headroom 18416.320 SU, no budget increase. Full local gates and actual Tree trace activation required. Report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md. No official accuracy claim, slides, organiser upload or AI schedule; autopilot OFF. Supersedes older snapshots below.

'''
policy=W/'research-autopilot/POLICY.md';policy.write_text(notice+policy.read_text());(W/'research-autopilot/LATEST.md').write_text(notice+s)
for p in [W/'notes/DECISIONS.md',W/'notes/TIMELINE.md',W/'research-autopilot/HISTORY.md']:
 with p.open('a') as f:f.write('\n'+notice)
# Update accepted raw summaries and run ledgers under the existing writer lock.
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);path=R/'serving-tuning/registry.json';state=json.loads(path.read_text());notes=json.loads((R/'run-notes.json').read_text());comparison=[x for x in json.loads((R/'comparison.json').read_text()) if x['job'] not in reviews]
 for e in state['entries']:
  for a in e['attempts']:
   j=a['job']
   if j in reviews:
    point=reviews[j]['point'];smoke=json.loads((R/'runs'/j/'output-smoke.json').read_text());a.update(state='COMPLETED',status=statuses[j],measurements=json.loads((R/'runs'/j/'summary.json').read_text()),output_smoke={'passed':smoke['passed'],'total':smoke['total']},output_baseline_comparison=point['short_output_comparison']);e['measurements']=[dict(job=j,experiment=e['id'],topology='P8-TP4_D8-TP8-EP8',output_smoke=a['output_smoke'],output_baseline_comparison=a['output_baseline_comparison'],**row) for row in a['measurements']];e.update(state='MEASURED',benchmark_complete=True,missing_ns=[]);comparison.extend(e['measurements']);notes[j]=dict(topology='P8-TP4_D8-TP8-EP8',purpose=e['purpose'],finding='Full local gates pass; chunk12288 loses, HPC-Ops decode plus chunk8192 improves. See research-followup-20261019-0600.',lesson='Control same load/chunk; interaction gains need repeats. Preserve losing evidence.',performance_evidence=True)
 for receipt in json.loads((O/'slurm-receipts.json').read_text()):
  p=next(x for x in json.loads((O/'pilots.json').read_text()) if x['id']==receipt['id']);notes[receipt['job']]=dict(topology='P8-TP4_D8-TP8-EP8',purpose=p['purpose'],finding='Submitted; no accepted result yet.',lesson='Fresh matched control and independent repeat before promotion.',performance_evidence=False)
 path.write_text(json.dumps(state,indent=2)+'\n');(R/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n');(R/'run-notes.json').write_text(json.dumps(notes,indent=2)+'\n');p=R/'job-status.json';d=json.loads(p.read_text());d.update(statuses);p.write_text(json.dumps(d,indent=2)+'\n')
for name in ['RUNS.md','SERVING_TUNING_RESULTS.md']:
 with (R/name).open('a') as f:f.write('\n## 19 October 2026 — prefill/decode interaction\n\nH200 24724 passes at 2938.628 good tokens/s (+5.6907% versus same-N58 control 24721); 24723 chunk 12288 loses 2.3789% and is closed. New H200 24736–24738 repeat/control/load trials, plus H100 prefill Tree N54 job 221669 after existing221645→221646. [Full report and source references](research-followup-20261019-0600/RESULTS.md). All new jobs await complete GPU gates; official accuracy unverified.\n')
print('Current handoff, closed branch and four new receipts persisted',now)
