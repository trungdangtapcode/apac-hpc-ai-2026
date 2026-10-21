from pathlib import Path
import json,hashlib,shutil,datetime
W=Path('/home/apacsc42/workspace');R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');O=W/'submission-review/full-update-2026-10-21';old=W/'submission-review/research-update-2026-10-20'
d=json.loads((old/'presentation-data.json').read_text());d['snapshot_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
for n in ['background-manifest.json','drawing-helpers.py','requirements.txt']:shutil.copyfile(old/n,O/n)
paths=[R/'research-followup-20261020-h100-restored/222048.pbs111-review.json',R/'research-followup-20261020-h100-restored/RESULTS.md',R/'cpu-envelope-balance-20261020/PAIR_REVIEW.md',R/'startup-prefetch-confirm-20261020/PAIR_REVIEW.md',R/'eagle3-pd-candidate-20261021/REVIEW.md',R/'eagle3-dtype-probe-20261021/REVIEW.md',R/'eagle3-reference-corpusfix-20261021/REVIEW.md']
s=R/'nscc-pbs/collected/222048.pbs111/20261020T061435059479Z/derived-summary.json';row=json.loads(s.read_text())[0];row.update(job='222048.pbs111',source=str(s));d['historical_records']['records']['H100']['good_output_tokens_s']={'value':row['good_output_tokens_s'],'ties':[row]};d['historical_records']['scope']+=' Updated H100 goodput with reviewed 222048; other metric records retain the earlier scan scope.';paths += [s,Path(row['export'])]
for p in paths:d['sources'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(O/'presentation-data.json').write_text(json.dumps(d,indent=2)+'\n')
t=(W/'submission-tools/build_research_update_20261020.py').read_text().replace("OUT = WORK/'submission-review/research-update-2026-10-20'","OUT = WORK/'submission-review/full-update-2026-10-21'")
t=t.replace('20 October 2026','21 October 2026')
t=t.replace('through 20 October','through 21 October').replace('through 20 October 2026','through 21 October 2026')
t=t.replace('2,430.89','2,433.02').replace('2430.890867','2433.019859').replace('2430.891 as the highest','2433.020 as the highest').replace('Highest H100 individual is 221590','Highest H100 individual is 222048').replace('H100 221590','H100 222048').replace('221590 retained full-protocol export','222048 retained full-protocol export').replace('221590 incumbent','222048 incumbent')
start=t.index('# 23\n');end=t.index('# 24\n',start)
t=t[:start]+'''# 23
s=slide('EAGLE3: prove correctness before measuring speed', 'The target-only reference 222761 supplies 1600 actual output IDs in four exact repeated prompt pairs. The first native PD candidate 222763 fails before readiness: a shared BF16 target embedding reaches a draft FP16 input RMSNorm. Native one-GPU fixture 222769 reproduces that mismatch and validates explicit BF16 draft normalization, including CUDA graph replay. A separately frozen full PD repair 222780 adds explicit BF16 and draft unquant on both roles; its result is not yet collected because remote access is unavailable. These are integration findings, not a speculative speedup or official quality result. The retained public draft is nebius EAGLE3 at the pinned revision, about 1.146 GB serialized BF16 tensors, no team training. Full output equality and actual PD state/graphs must pass before a matched-load short screen. CPU-envelope tuning delivered only 0.289% against a prospective 1% gate; startup prefetch reverse confirmation saved 9.836% against 10%; neither is promoted.', '222761 reference; 222763 failure; 222769 native dtype fixture; 222780 frozen repair; CPU and prefetch pair reviews')
for i,(number,title,detail) in enumerate([('01','Exact reference','1,600 actual target IDs\\nFour A/B prompt pairs'),('02','Reproduce failure','Shared BF16 embedding\\nDraft auto resolves FP16'),('03','Validate the repair','BF16 native norm + graph\\nFull PD result still needed')]):
 x=.95+i*4.16;s.text(number,x,1.57,3.7,.67,37,ORANGE,bold=True);s.text(title,x,2.57,3.7,.55,25,bold=True);s.text(detail,x,3.38,3.7,1.10,22)
 if i<2:s.arrow(x+3.47,2.00,x+3.99,2.00,ORANGE)
s.text('No speculative speedup claimed. Next: full PD equality, then a matched screen.',1.0,5.42,11.3,.74,22)
s.text('Closed below useful-gain gates: CPU envelopes +0.289%; startup saving 9.836%.',1.0,6.40,11.3,.36,18,GRAY);s.end()
''' +t[end:]
t=t.replace('The next work measures observer overhead, validates a native polling hypothesis and completes quality evaluation','The next work collects the BF16 EAGLE3 integration repair, validates output equality before a matched screen and completes quality evaluation')
t=t.replace('New observed polling pilots are submitted and validation is in progress, not claimed results.','Later CPU balancing misses its 1% gate. EAGLE3 native dtype repair passes a layer fixture; the full PD repair is not yet reviewed.')
t=t.replace("['Observed polling pilots','24926, 24927, 24928','222048, 222049, 222050']","['CPU / EAGLE3 repair','H200 followups pending','222551/52; 222769/780']")
(W/'submission-tools/build_research_update_20261021.py').write_text(t)
