"""Record reviewed PBS outcomes and reconcile only independently matched charges."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl, json, re, shutil
R = Path(__file__).resolve().parents[1]
O = Path(__file__).resolve().parent
P = R / 'nscc-pbs'
W = Path('/home/apacsc42/workspace')
now = datetime.now(timezone.utc).isoformat()
jobs = ['221645', '221646', '221669']
reviews = {j: json.loads((O / (j + '.pbs111-review.json')).read_text()) for j in jobs}
assert all(d['state'] == 'LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS' for d in reviews.values())
profile = json.loads((O / 'h100-prefill-tree-profile.json').read_text())
assert profile['prefill_tree_activation_all_ranks'] and not profile['prefill_ring_allreduce_seen']
raw = (O / 'pbs-queue-accounting.txt').read_text()
blocks = {m.group(1): m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)', raw, re.S)}
match = re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|', raw)
assert match
grant, used, balance, doubt = map(float, match.groups())
assert abs(grant - used - balance - doubt) < .01
charges = {}
walltimes = {}
for j in jobs:
    block = blocks[j + '.pbs111']
    assert re.search(r'job_state\s*=\s*F\b', block) and re.search(r'Exit_status\s*=\s*0\b', block)
    wall = re.search(r'resources_used.walltime\s*=\s*(\S+)', block).group(1)
    h, m, s = map(int, wall.split(':'))
    charges[j] = 16 * 128 * (h + m / 60 + s / 3600)
    walltimes[j] = wall
with (P / 'budget.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    path = P / 'nscc-budget.json'
    b = json.loads(path.read_text())
    unreconciled = [j for j in jobs if not next(x for x in b['jobs'] if x['job_id'] == j + '.pbs111').get('included_in_ledger_used')]
    delta = used - b['ledger']['used_su']
    assert abs(delta - sum(charges[j] for j in unreconciled)) < .01, (delta, charges)
    for j in jobs:
        item = next(x for x in b['jobs'] if x['job_id'] == j + '.pbs111')
        item.update(state='F', exit_status=0, observed_walltime=walltimes[j], estimated_charge_su=charges[j], included_in_ledger_used=True, accounting_pending=False, last_checked_utc=now, reconciliation_source=str(O / 'pbs-queue-accounting.txt'))
        for item in b['pending_reservations']:
            if item.get('job_id') == j + '.pbs111':
                item.update(state='RECONCILED_IN_LEDGER', last_checked_utc=now, reconciliation_source=str(O / 'pbs-queue-accounting.txt'))
    outstanding = sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in {'RECONCILED_IN_LEDGER', 'CANCELLED', 'RELEASED'})
    b['ledger'].update(as_of=re.search(r'balance as of (\S+)', raw).group(1), grant_su=grant, used_su=used, balance_su=balance, in_doubt_su=doubt, queried_utc=now, source=str(O / 'pbs-queue-accounting.txt'), freshness_note='Three terminal job charges reconcile exactly within ledger rounding; Balance already excludes In Doubt. This is a dated ledger snapshot.')
    b.update(updated_utc=now, active_pbs_jobs=[], campaign_headroom_after_reserved_su=b['commissioning_cap_su'] - used - outstanding, unallocated_commissioning_su=b['commissioning_cap_su'] - used - outstanding)
    temp = path.with_suffix('.tmp'); temp.write_text(json.dumps(b, indent=2) + '\n'); temp.replace(path)
points = {j: reviews[j]['point'] for j in jobs}
control = points['221645']['good_output_tokens_s']
earlier_n54 = json.loads((R / 'research-followup-20261019-0527/221590.pbs111-review.json').read_text())['point']['good_output_tokens_s']
previous_used = json.loads((O / 'budget-before.json').read_text())['ledger']['used_su']
assert abs(used - previous_used - sum(charges.values())) < .01
changes = {j: (v['good_output_tokens_s'] / control - 1) * 100 for j, v in points.items()}
rows = []
for j, label in [('221645', 'N54 default-collective independent repeat'), ('221646', 'N56 load trial'), ('221669', 'N54 forced prefill Tree')]:
    v = points[j]
    rows.append(f"| {j} | {label} | {v['good_output_tokens_s']:.3f} | {100*v['sla_fraction']:.4f} | {v['ttft_avg_ms']:.3f} | {v['itl_avg_ms']:.3f} | {changes[j]:+.4f}% |")
report = f'''# Reviewed H100 outcomes and H200 queue — 19 October 2026

Scheduler evidence checked at 11:11 UTC; review completed at {now}. All measurements remain platform-specific. This status review submitted no new allocation and did not authenticate or restart the VPN.

## Current answer

H200 jobs **24733, 24736, 24737 and 24738 are still pending for Priority**. The two hpcai nodes are allocated. The highest accepted H200 observation remains **24724 = 2938.628 good tokens/s**; its own interaction repeat 24737 has not run at this check. Do not cancel or resubmit these jobs solely to refresh their positions.

The three H100 jobs have finished, and all three pass full local protocol, request/error/SLA, frozen payload, resolved runtime, short-output and 12-case long-output checks. Their performance conclusions differ:

| Job | Trial | Good tokens/s | Joint success (%) | Mean TTFT (ms) | Mean ITL (ms) | Change vs fresh N54 |
|---|---|---:|---:|---:|---:|---:|
''' + '\n'.join(rows) + f'''

The N54 repeat is {(control/earlier_n54-1)*100:+.4f}% from the earlier 221590 observation of 2430.891. N54 is independently remeasured near its earlier result, but this pair alone does not prove a statistically significant gain over N52. N56 produces no observed improvement versus the fresh N54 repeat; do not automatically proceed to N58. The highest individual H100 observation remains 221590, not a new record in this batch.

Forced Tree is **{changes['221669']:.4f}% worse** than the fresh same-N54 default-collective control. It passes the acceptance checks but loses performance: close this branch, retain default selection and preserve the result. Mean TTFT increases substantially while mean ITL improves; one favourable metric does not make the overall configuration faster.

Good tokens/s means requests meeting both TTFT ≤3000 ms and per-request mean ITL ≤20 ms per second, multiplied by 200. Joint success includes request failures in its denominator and must reach at least 90%. All reported latency values are in milliseconds. Official accuracy at 99% of the organiser reference remains unverified.

## The Tree hypothesis really executed

The separately scored N54 benchmark is distinct from the subsequent N48 diagnostic profile. The latter contains **{profile['trace_count']} sealed, nonempty rank traces and {profile['successful_requests']}/{profile['requests']} successful diagnostic requests**. All eight prefill ranks show actual Tree all-reduce kernels; no Ring all-reduce kernel appears in those prefill traces. The decoded runtime keeps MNNVL and FlashInfer on all eight ranks. This is execution evidence rather than inference from an environment variable.

The N48 profile is diagnostic, not ranked traffic and not a causal decomposition of the N54 result. Kernel-duration shares sum event durations across ranks; they are not critical-path wall-time fractions. This outcome rejects forcing prefill Tree for this tested deployment; it does not prove every communication optimisation is exhausted.

## Credit and next decision

The ledger at {b['ledger']['as_of']} SGT reports **{balance:.3f} SU remaining**, Used {used:.3f}, In Doubt {doubt:.3f}. The three completed jobs consumed approximately **{sum(charges.values()):.3f} SU**, matching the Used delta within rounding; their former 4608-SU maximum reservations are released only after this reconciliation. No own PBS jobs remain active. Outstanding maximum reserves: {outstanding:.3f} SU. Internal headroom under the unchanged 51000-SU operating bound is **{b['campaign_headroom_after_reserved_su']:.3f} SU**, with the 13000-SU buffer retained. Reported balance is a dated published snapshot.

Keep the four H200 queue positions and review them when they run. On H100, stop this load-growth branch and forced Tree. A further GPU trial needs a distinct, evidence-backed hypothesis and matched control rather than a larger concurrency or unchanged rerun. Prioritise the pending H200 interaction confirmation and organiser accuracy; use the retained profile to prepare a targeted next experiment. This status check adds no new job, budget increase, slide change, official package promotion or AI schedule.

## Retained evidence

- [H200 queue](slurm-queue.txt) and [terminal accounting](slurm-accounting.txt).
- [PBS terminal accounting and project ledger](pbs-queue-accounting.txt).
- [N54 review](221645.pbs111-review.json), [N56 review](221646.pbs111-review.json), [Tree review](221669.pbs111-review.json).
- [Actual Tree rank analysis](h100-prefill-tree-profile.json) and [named kernel summary](profile-summary.txt).
- The collection receipts identify the immutable source snapshots: [221645](collect-221645.json), [221646](collect-221646.json), [221669](collect-221669.json).
- [Prior hypothesis and acceptance rules](../research-followup-20261019-0600/PLAN.md).
'''
(O / 'RESULTS.md').write_text(report)
(O / 'reconciliation.json').write_text(json.dumps(dict(charges_su=charges,walltimes=walltimes,this_invocation_ledger_delta=delta,previous_captured_used_su=previous_used,reconciled_batch_delta=used-previous_used,outstanding_reserves_su=outstanding,headroom_su=b['campaign_headroom_after_reserved_su'],changes_vs_fresh_n54_pct=changes),indent=2)+'\n')
path = P / 'continuous-plan.json'
plan = json.loads(path.read_text())
for item in plan['pilots']:
    j = item.get('job_id', '').split('.')[0]
    if j in jobs:
        item.update(state='F', result_state='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS', review=str(O / (j + '.pbs111-review.json')), accuracy_verified=False, measurements=[points[j]], research_outcome='INDEPENDENT_REPEAT' if j=='221645' else 'NO_OBSERVED_LOAD_GAIN' if j=='221646' else 'TREE_EXECUTED_PERFORMANCE_REGRESSION_CLOSED')
plan.update(updated_utc=now,next_bounded_step='H100 N54 repeated, N56 has no observed improvement and forced prefill Tree regresses with activation verified. No automatic load growth or unchanged Tree rerun. Preserve H200 queue positions; review pending interaction before a distinct evidence-backed experiment.')
path.write_text(json.dumps(plan,indent=2)+'\n')
notice=f'''## Status review — {now}

Live checks at 11:11 UTC: H200 24733/24736/24737/24738 remain pending for Priority; two hpcai nodes allocated. Highest H200 observation remains 2938.628 good tokens/s; its own interaction repeat has not run. All three PBS jobs completed and pass full local protocol/SLA/runtime/output checks: N54 repeat 221645 = 2418.588; N56 221646 = 2407.364; forced prefill Tree 221669 = 2160.946 good tokens/s. Tree execution is proved on all eight prefill ranks in 16 sealed diagnostic traces (355/355 successful requests); it loses 10.65% versus fresh N54 and is closed. N56 has no observed gain; no automatic N58. Highest H100 individual observation remains 2430.891. Official accuracy unverified. PBS queue empty; VPN/SSH usable without restart or authentication. Balance 34608.356 SU; three terminal charges reconcile, zero remaining reservations and internal headroom 21608.356 SU under the unchanged cap/buffer. No new GPU job, schedule, slide or submission change. [Full report and raw evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1111/RESULTS.md). This supersedes earlier queue and credit snapshots below.

'''
current=W/'notes/CURRENT.md'
archive=W/'notes/archive/CURRENT-before-20261019-1111.md';archive.parent.mkdir(exist_ok=True)
if not archive.exists():shutil.copyfile(current,archive)
s=current.read_text();s=s.replace('# Current APAC handoff — 19 October 2026\n', '# Current APAC handoff — 19 October 2026\n\n'+notice+'## Historical handoff entries\n\nThe entries below retain their original dated evidence cutoffs; the latest review above supersedes their queue, active-job and credit statements.\n',1)
current.write_text(s)
for path in [W/'notes/DECISIONS.md', W/'notes/TIMELINE.md', W/'research-autopilot/HISTORY.md']:
    with path.open('a') as f:f.write('\n'+notice)
for path in [W/'research-autopilot/POLICY.md', W/'research-autopilot/LATEST.md']:
    path.write_text(notice+path.read_text())
for path in [R/'RUNS.md',R/'SERVING_TUNING_RESULTS.md']:
    with path.open('a') as f:f.write('\n'+notice)
print(json.dumps(dict(balance_su=balance,headroom_su=b['campaign_headroom_after_reserved_su'],charges_su=sum(charges.values()),changes_pct=changes)))
