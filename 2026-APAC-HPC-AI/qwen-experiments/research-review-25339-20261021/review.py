"""Replay the sealed short screen with exact 20/40 timing; never rank it as full."""
from pathlib import Path
from datetime import datetime,timezone
import ast,csv,importlib.util,inspect,json,subprocess
O=Path(__file__).resolve().parent;R=O.parent;job='25339'
s=importlib.util.spec_from_file_location('wave',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);core=w.core
# Adapt only this offline review's expected phase/path/timings. All raw protocol,
# error, payload, output and seal checks remain the inherited implementation.
text=inspect.getsource(core.validate_metrics);assert "[('warmup', 60, n), ('profiling', 120, n)]" in text and 'zip(rows, (60, 120))' in text
text=text.replace("[('warmup', 60, n), ('profiling', 120, n)]","[('warmup', 20, n), ('profiling', 40, n)]").replace('zip(rows, (60, 120))','zip(rows, (20, 40))');exec(compile(text,'<derived-short-metric-review>','exec'),core.__dict__)
text=inspect.getsource(core.point);assert "f'confirm/n{n}/artifacts'" in text;text=text.replace("f'confirm/n{n}/artifacts'","f'screen/n{n}/artifacts'");exec(compile(text,'<derived-short-path-review>','exec'),core.__dict__)
points={str(n):core.point(R,job,n) for n in (62,64)};long=w.long_check(R/'runs'/job)
assert points['62']['normalized_protocol']==points['64']['normalized_protocol']
assert all(p['metrics']['sla_pass'] for p in points.values()) and long['state']=='PASSED'
gain=(points['64']['metrics']['good_tokens_s']/points['62']['metrics']['good_tokens_s']-1)*100
result=dict(job=job,reviewed_utc=datetime.now(timezone.utc).isoformat(),state='SHORT_LOCAL_PROTOCOL_SLA_OUTPUT_PASS',points=points,long_context=long,within_job_gain_percent=gain,practical_one_percent_screen_gate=gain>=1.0,full_scored=False,ranking_promotion_allowed=False,official_accuracy_verified=False,assessment='Matched short N64 is faster than short N62, but fixed order and shortened timing cannot replace a full result',next_step='Fresh equally observed full N62 control and N64 candidate,60/120/30 in separate bounded17-minute deployments')
(O/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(state=result['state'],gain_percent=gain,metrics={n:p['metrics'] for n,p in points.items()},long_context=long),indent=2))
