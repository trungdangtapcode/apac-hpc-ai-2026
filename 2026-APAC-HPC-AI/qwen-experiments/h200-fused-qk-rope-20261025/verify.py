#!/usr/bin/env python3
"""Exercise derived native selection gates using clearly labelled CPU fixtures."""
from pathlib import Path
import datetime,hashlib,json,subprocess,tempfile
S=Path(__file__).resolve().parent;R=S.parent;report={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'CPU fixtures based on real25947 logs with synthetic flag/selection records; NOT actual candidate GPU evidence.','arms':[]}
for stage,sid in [('prefill',66),('decode',67)]:
 b=R/f'serving-tuning-11/s{sid}-h200-{stage}-fused-qk-rope';cfg=json.loads((b/'config.json').read_text())
 baseline=json.loads((R/'serving-tuning-11/s65-h200-router-rr-control/expected-input-config.json').read_text());assert baseline==json.loads((b/'expected-input-config.json').read_text())
 with tempfile.TemporaryDirectory(prefix='ai-fusion-cpu-') as temp:
  d=Path(temp)
  for role,tp in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:
   selected=role in cfg['fused_qk_norm_rope_roles'];text=(R/f'runs/25947/{role}.log').read_text()
   assert text.count('enable_fused_qk_norm_rope=False')==1
   if selected:text=text.replace('enable_fused_qk_norm_rope=False','enable_fused_qk_norm_rope=True')
   text+=''.join(f'[CPU_FIXTURE TP{i}] FUSED_QK_ROPE_SELECTION selected={selected} head_dim=128\n' for i in range(tp))
   (d/f'{role}.log').write_text(text)
  def run():return subprocess.run(['python3','-B',str(b/'check-fast-runtime.py'),str(d),'control','64'],capture_output=True,text=True)
  good=run();assert good.returncode==0,good.stderr
  target=cfg['fused_qk_norm_rope_roles'][0];p=d/f'{target}.log';correct=p.read_text();p.write_text(correct.replace('selected=True','selected=False'))
  fallback=run();assert fallback.returncode!=0 and 'fell back' in fallback.stderr,fallback.stderr
  p.write_text(correct.replace('enable_fused_qk_norm_rope=True','enable_fused_qk_norm_rope=False'));wrong=run();assert wrong.returncode!=0 and 'flag differs' in wrong.stderr,wrong.stderr
  report['arms'].append({'bundle':b.name,'matched_workload':True,'valid_synthetic_selection_fixture':'PASS','synthetic_fallback_rejected':True,'wrong_native_flag_rejected':True,'all_payload_hashes':subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,stdout=subprocess.DEVNULL).returncode==0})
source_files=list((S/'source').rglob('*.py'))+list((S/'kernel').rglob('*.py'))
report['native_source_hashes']={str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
report['known_gpu_prerequisites']='Actual BF16 JIT build, per-rank native selected markers and all semantic/output/performance gates remain unverified.'
(S/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
