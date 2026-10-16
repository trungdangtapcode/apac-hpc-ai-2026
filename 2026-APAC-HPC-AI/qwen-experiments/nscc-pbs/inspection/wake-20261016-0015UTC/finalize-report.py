import datetime,hashlib,json
from pathlib import Path
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');A=Path('/home/apacsc42/workspace/research-autopilot');N=Path('/home/apacsc42/workspace/notes');O=Path(__file__).resolve().parent
old=(A/'LATEST.md').read_text()
latest='''# Báo cáo Qwen — 2026-10-16 00:19 UTC

- **23904 — MNNVL + FlashInfer:** **2631,09 goodtokens/s**, SLA 99,02%; hơn trung bình hai baseline **1,49%**. TTFT tăng 122,97 ms, ITL giảm 0,91 ms. Mới có một lượt, chưa xác nhận bằng repeat.
- **23905 — chunk2048:** **2331,35 goodtokens/s**, SLA 98,77%; goodput giảm **10,07%** dù ITL giảm 1,33 ms. TTFT tăng 676,50 ms. Runtime cũng đổi giới hạn graph prefill 4096→2048; chưa thể quy kết riêng cho chunk.
- Cả hai đã đối soát đủ giao thức 60/120/30, không lỗi/hủy; kiểm tra đầu ra 7/8, chỉ lỗi reverse đã biết. Checksum đạt cho 47 file mỗi run, gồm hai baseline và hai candidate. Accuracy BTC chưa xác minh.
- **H200 lúc 00:19:38 UTC:** 23906/23924/23934 PENDING(Resources), dùng 3/5 slot; watcher còn sống. Bước tiếp: thu ba job và kiểm tra graph thực của chunk8192. Không thêm job, repeat hay N56.
- **NSCC lúc 00:15:52 UTC:** chưa có phiên VPN sống; kết quả 220575 và credit hiện tại chưa xác minh. Giữ 1536 SU dự trù, trần campaign 16384 SU; lượt nghiên cứu này không đăng nhập lại hay qsub. Pilot 04→05 chờ đủ điều kiện truy cập, baseline, queue và credit.
- Đã cập nhật CURRENT, POLICY, Q&A, review và budget/plan; giữ artifact cùng các lần audit CPU và đính chính. Lượt này kết thúc sau phần việc độc lập; watcher tiếp tục thu kết quả.

[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0015UTC/).
'''
(A/'LATEST.md').write_text(latest)
p=A/'HISTORY.md';s=p.read_text();entry=old.replace('# Báo cáo Qwen','## Báo cáo Qwen',1);assert s.endswith(entry);p.write_text(s[:-len(entry)]+latest.replace('# Báo cáo Qwen','## Báo cáo Qwen',1))
# A separate interactive session updated CURRENT during this research wake. Preserve it,
# and distinguish its user-directed login attempt from this wake's existing-access check.
p=A/'POLICY.md';s=p.read_text();target='authentication attempted this wake. Use existing access only; do not assume it is live.'
if '00:18:46UTC' in (N/'CURRENT.md').read_text() and target in s:
 s=s.replace(target,target+'\n  Separate user-directed session: CURRENT records authentication rejection at\n  16Oct00:18:46UTC with IKE86400s; no successful tunnel. Preserve that newer VPN\n  finding; it does not provide PBS access or resolve the cause. No retry here.')
 p.write_text(s)
checks={}
d=json.loads((O/'wave9-final-review.json').read_text());b=json.loads((R/'nscc-pbs/nscc-budget.json').read_text());plan=json.loads((R/'nscc-pbs/continuous-plan.json').read_text())
checks['four_terminal_seals_verified']=all(d['runs'][j]['seal_files_verified']==47 for j in ['23778','23839','23904','23905'])
checks['baseline_comparisons_pass']=all(d['runs'][j]['output_comparison']['research_eligible'] for j in ['23904','23905'])
checks['budget_unchanged']=b['commissioning_cap_su']==16384 and sum(x['max_charge_su'] for x in b['pending_reservations'])==1536
checks['access_no_new_auth_or_qsub']=not b['latest_access_check']['new_authentication_attempted'] and not b['latest_access_check']['qsub_attempted']
checks['prepared_pilots_not_submitted']=all(p['state']=='PREPARED_NOT_SUBMITTED' for p in plan['pilots'])
checks['notes_contain_both_results']=all(j in (N/'CURRENT.md').read_text() and j in (A/'POLICY.md').read_text() and j in latest for j in ['23904','23905'])
assert all(checks.values()),checks
(O/'report-validation.json').write_text(json.dumps(dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks),indent=2)+'\n')
files=[p for p in O.iterdir() if p.is_file() and p.name!='evidence-sha256.json']
(O/'evidence-sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},indent=2)+'\n')
print(json.dumps(checks,indent=2))
