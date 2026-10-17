from pathlib import Path
import json,shutil,hashlib,subprocess,datetime
R=Path.cwd();P=R/'nscc-pbs';D=R/'serving-tuning-10';O=P/'inspection/manual-20261017-1410';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def clone(src,dst,old,name,pbs,kind):
 assert not dst.exists();shutil.copytree(src,dst);dst.chmod(0o755)
 for f in dst.iterdir():
  if f.is_file():f.chmod(0o644)
 p=dst/('benchmark.pbs' if pbs else 'job.sbatch');s=p.read_text().replace(old,name)
 if pbs:s=s.replace('walltime=00:40:00','walltime=00:45:00').replace('QWEN_TUNE_NS="48 50 52"','QWEN_TUNE_NS="50"')
 if kind=='tp8ep2':s=s.replace('QWEN_PREFILL_EP=1','QWEN_PREFILL_EP=2')
 p.write_text(s);c=json.loads((dst/'config.json').read_text());c.update(experiment=name,concurrency=[50] if pbs else [56],purpose='Matched control / phase-specific compute or startup hypothesis; full protocol, no assumed transfer gain',source_job='221058.pbs111' if pbs else '24235')
 allowed={'job.sbatch','benchmark.pbs','config.json','SHA256SUMS'}
 if pbs:
  p=dst/'topology-job.sh';s=p.read_text();assert '+2400-SECONDS-40' in s;p.write_text(s.replace('+2400-SECONDS-40','+2700-SECONDS-40'));c['walltime_minutes']=45;allowed.add('topology-job.sh')
 if kind in ['deepgemm','prefetch']:
  flag='--moe-runner-backend deep_gemm' if kind=='deepgemm' else '--weight-loader-prefetch-checkpoints';p=dst/'worker.sh';s=p.read_text();assert s.count('extra=(--chunked-prefill-size 4096)')==1;p.write_text(s.replace('extra=(--chunked-prefill-size 4096)','extra=(--chunked-prefill-size 4096 '+flag+')'));c['prefill_extra_flags']=['--chunked-prefill-size','4096']+flag.split();allowed.add('worker.sh')
 if kind=='tp8ep2':
  (dst/'placement.tsv').write_text('prefill-0\t0\t8\t30100\t9000\ndecode-0\t1\t8\t30200\t0\n');c.update(id='P8-TP8-EP2_D8-TP8-EP8',prefill_tp=8,prefill_ep=2,prefill_workers=1,prior_failed_job='24282',failure_correction='MoE TP=8/2=4,1536/4=384 divisible by FP8 block128; weights and precision unchanged');allowed.add('placement.tsv')
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in src.iterdir():
  if f.name not in allowed:assert f.read_bytes()==(dst/f.name).read_bytes()
 for f in list(dst.glob('*.sh'))+[dst/('benchmark.pbs' if pbs else 'job.sbatch')]:subprocess.run(['bash','-n',str(f)],check=True)
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));return h
report={'created_utc':now,'pbs':{},'slurm':{}}
for name,kind in [('h100-combo-control-16','control'),('h100-prefill-deepgemm-17','deepgemm'),('h100-prefill-prefetch-18','prefetch')]:report['pbs'][name]=clone(P/'h100-combo-load-repeat-15',P/name,'h100-combo-load-repeat-15',name,True,kind)
new=[]
for name,kind in [('s10-combo-control-n56-v3','control'),('s10-prefill-tp8ep2-n56','tp8ep2'),('s10-prefill-prefetch-n56','prefetch')]:
 h=clone(D/'s10-combo-repeat-n56',D/name,'s10-combo-repeat-n56',name,False,kind);report['slurm'][name]=h
 new.append(dict(id=name,bundle=str(D/name),planned_ns=[56],state='PLANNED',wave=10,purpose='Fresh N56 control / corrected TP8EP2 prefill / prefill weight prefetch, same decode and protocol',diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[56],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24235'))
text='''# Parallel hypothesis tests on H100 and H200

Prepared17October2026 after the user explicitly requested continuing with the
remaining project credit, following clarification that the16,384SUlimit was an
internal planning choice. Preserve a conservative13,000SU project reserve; this
is not a BTC requirement. Fresh ledger and queue must precede every qsub.

## H100: three sequential16GPU/45minute jobs

1. Fresh comboN50 control: establishes same-load performance and startup timing.
2. Prefill-only DeepGEMM: tests the phase-specific MoE hypothesis motivated by
   H200 profiles. H100 benefit is unknown; no cross-platform gain is assumed.
3. Prefill weight prefetch: tests startup/cost, not an assumed ranked-throughput
   improvement. The old prefetch trial had a short18:49allocation but different
   load/backend and unobserved cache confounders, so it is only a hypothesis.

All three retain full60/120/30,4000/200,N50,modelFP8,BF16KV,2TP4EP1prefills,
TP8EP8decode,MNNVL+FlashInfer,task-side logs andshort/12long checks. Use rank
Loadweightbegin/end elapsed logs and PBSwalltime for startup. Ordering/cache/
nodes are confounders; a single control→candidate sequence is not causal proof
of an I/O improvement. Defer startup claims if source logs are incomplete.
Reserve4608SUmaxbeforeqsub,strictafteranychain,max1running16GPU andcap3active.

## H200: three bounded17minute/16GPU jobs

Fresh comboN56 control avoids comparing new candidates only against hours-old
runs. One TP8EP2prefill candidate corrects the failed24282TP8EP1 geometry:
modelMoEintermediate1536 /MoETP8=192,notdivisiblebyFP8block128. Exactstaged
parallel_state.pycomputesMoETP=TP/EP/DP;EP2givesMoETP4,1536/4=384divisible128,
128experts/EP2=64. This fixes a source-level compatibility condition without
changing checkpoint/precision; GPUstartup/quality still unverified. Compare the
combined prefillparallelism/EPplan,notclaimisolatedTPspeedup.

The third job adds only prefillweightprefetch. Keep decode unchanged. It can
reduce startup cost/time without improving rankedgoodput; preserve that distinction.

No repeat of batchlimit24281, which lost1.73%goodput. No blindN60,quantization,
new weights,orautomaticcandidatepromotion. Any useful gain needs replication,
fullruntime/SLA/error/short/long review. All failures remain artifacts.
'''
(O/'PLAN.md').write_text(text)
with (D/'PLAN.md').open('a') as f:f.write('\n'+text)
q=subprocess.run(['squeue','-h','-u','apacsc42','-o','%i'],capture_output=True,text=True,check=True);assert len(q.stdout.splitlines())+len(new)<=5
f=D/'prepared-pilots.json';plan=json.loads(f.read_text());plan['pilots'].extend(new);plan.update(state='ACTIVE',updated_utc=now);tmp=f.with_suffix('.parallel.tmp');tmp.write_text(json.dumps(plan,indent=2)+'\n');tmp.replace(f)
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared3H100andarmed3H200hypothesistests')
