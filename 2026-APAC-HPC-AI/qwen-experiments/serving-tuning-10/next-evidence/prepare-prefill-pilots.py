from pathlib import Path
import json,shutil,hashlib,subprocess,datetime,re,statistics
R=Path(__file__).resolve().parents[2];D=R/'serving-tuning-10';O=D/'next-evidence';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
stats={}
for job in ['23975','24235','24236']:
 stats[job]={}
 for role in ['prefill-0','prefill-1']:
  p=R/'runs'/job/(role+'.log');rows=[]
  for line in p.read_text().splitlines():
   if 'Prefill batch,' in line:
    m=re.search(r'#new-seq: (\d+).*#new-token: (\d+)',line)
    if m:rows.append(tuple(map(int,m.groups())))
  stats[job][role]={'log_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'steps':len(rows),'multi_sequence_steps':sum(n>1 for n,t in rows),'mean_step_tokens':statistics.mean(t for n,t in rows),'scope':'entireworkerlogincludingstartup/warmup/measurement/long;notprofilingphaseonly;norequestmatchedcausalclaim'}
(O/'prefill-observations.json').write_text(json.dumps(stats,indent=2)+'\n')
new=[];validation={}
for name,kind in [('s10-combo-prefill-single-n56','single'),('s10-combo-prefill-tp8-n56','tp8')]:
 src=D/'s10-combo-repeat-n56';dst=D/name;assert not dst.exists();shutil.copytree(src,dst);dst.chmod(0o755)
 for f in dst.iterdir():
  if f.is_file():f.chmod(0o644)
 p=dst/'job.sbatch';p.write_text(p.read_text().replace('s10-combo-repeat-n56',name))
 p=dst/'config.json';c=json.loads(p.read_text());c.update(experiment=name,concurrency=[56],source_job='24235',purpose='Test prefill batching or parallelism after N56/N58 ITLplateau and TTFTgrowth;compareunchangedcomboN56,notassumedbottleneck',source_experiment='s10-combo-repeat-n56')
 if kind=='single':
  p=dst/'worker.sh';s=p.read_text();assert s.count('extra=(--chunked-prefill-size 4096)')==1;p.write_text(s.replace('extra=(--chunked-prefill-size 4096)','extra=(--chunked-prefill-size 4096 --prefill-max-requests 1)'))
  c.update(prefill_max_requests=1,prefill_extra_flags=['--chunked-prefill-size','4096','--prefill-max-requests','1'])
  allowed={'worker.sh','config.json','job.sbatch','SHA256SUMS'}
 else:
  (dst/'placement.tsv').write_text('prefill-0\t0\t8\t30100\t9000\ndecode-0\t1\t8\t30200\t0\n')
  c.update(id='P8-TP8_D8-TP8-EP8',prefill_tp=8,prefill_workers=1,prefill_ep=1,prefill_gpus=8,prefill_extra_flags=['--chunked-prefill-size','4096'],p_d_paths=1)
  allowed={'placement.tsv','config.json','job.sbatch','SHA256SUMS'}
 p.write_text(p.read_text()) if False else None
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in src.iterdir():
  if f.name not in allowed:assert f.read_bytes()==(dst/f.name).read_bytes(),f.name
 for f in list(dst.glob('*.sh'))+[dst/'job.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
 placement=[l.split() for l in (dst/'placement.tsv').read_text().splitlines()];assert sum(int(x[2]) for x in placement if x[0].startswith('prefill'))==8 and sum(int(x[2]) for x in placement if x[0].startswith('decode'))==8
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));validation[name]={'allowed_changed_files':sorted(allowed),'hashes':h,'shell_syntax_pass':True,'placement_16GPU_pass':True,'gpu_runtime_validated':False}
 new.append(dict(id=name,bundle=str(dst),planned_ns=[56],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[56],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24235'))
(O/'pilot-validation.json').write_text(json.dumps({'created_utc':now,'pilots':validation,'compatibility':'stagedserverargsdeclaresprefill_max_requests;genericlauncherandwarmupderiveworkersfromplacement;equalTPNIXLpathretained,noGPUvalidation'},indent=2)+'\n')
text='''# Prefill interaction pilots — '''+now+'''

User asks whether existing evidence justifies more H200experiments. Yes, two
bounded new interactions, independent of pendingprofile/holdout. No claim that
TTFT growth identifies a bottleneck by itself.

Evidence: N52combo ITL~16.23ms/TTFT~634ms;N56~16.27ms/~850ms;N58~16.27ms/~991ms
withgoodputplateau. Wholeprefillworkerlogs contain far more multi-sequence steps
atN56/N58 thanN52 (prefill-observations.json). Logs mixstartup/warmup/measure/long,
so counts are descriptive, not isolated phase-level causal evidence.

A. Same2xTP4prefills, addonly--prefill-max-requests1,chunk4096unchanged.
Hypothesis: fewer carried-over requestfragments improve firsttoken latency and
continuousdecodefeed;counterhypothesis:lostMoEbatchingreducesgoodput. Old23324
showedonly0.34%single-run gain undercacheawarerouting BEFOREcurrentRR/MNNVL/
FlashInfer;itdoesnotestablishinteractioninthenewwinner. This isexplicitlyone
newinteractiontrial,notrepeatoflosingchunk2048/8192jobs.

B. Same8P+8DGPUs,replace2prefillworkersTP4EP1with1prefillworkerTP8EP1.
DecodeTP8EP8/MNNVL/FlashInferunchanged. Hypothesis:lowerperrequestprefilllatency
orlessreplicaimbalancereducesTTFT;counterhypothesis:loseprefillparallelismand
additionalTPcommunicationhurts. Resourcefactorisparallelism/replicationplan,
notasinglescalarflag. KVtransfernowequalTP8;originalequalTPpatchpathretained.
Launcherderivesplacementandwarmup1pair;manualreviewmustexpect1P/Dpathand
prefilllogTP8,notreusehardcoded2workerreviewerblindly. Modelheads/runtimecompatibility
stillrequireactualGPUstartup;do notcountfaileddeploymentasmeasurement.

Primaryrefs:DistServe https://arxiv.org/abs/2401.09670v3 supportsphase-specific
parallelism/resourceoptimization,notaspeeduppredictionforQwen.
SGLang https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
motivatesrequest/compute/memorytradeoffs;offlinebatchsaturationadviceisnotourSLO.
Exactstagedserver_args.py snapshotdeclaresprefill_max_requestsOptional[int],
unlimiteddefault. Runtimeworkerlogsandfrozenpayloadarequantitativeevidence.

BothfullN56,16H20017min,BF16KV/officialFP8/routerRR/client60/120/30+short+12long
unchanged. Existing24263N56benchmark(beforeprofiler)servesfreshcontrol;also
compare24190/24235andallcontrolsfor drift. Requirezerorequesterrors/cancel,
SLA>=90%,shortnonregression,longPASSED,correctruntime. Reportnegativefindings.
Anywinnerneedsindependentrepeatbeforepromotion;noautomaticrepeat,newloador
H100qsub. Twoexistingpendingjobs+two new=4/5cap;preservequeuepositions.
Profilemayoverturnthesehypotheses;do notattributekernelcausewithouttraces.
'''
(O/'PLAN.md').write_text(text)
with (D/'PLAN.md').open('a') as f:f.write('\n'+text)
q=subprocess.run(['squeue','-h','-u','apacsc42','-o','%i'],capture_output=True,text=True,check=True);assert len(q.stdout.splitlines())+len(new)<=5
p=D/'prepared-pilots.json';plan=json.loads(p.read_text());assert not any(e['id'] in [x['id'] for x in new] for e in plan['pilots']);plan['pilots'].extend(new);plan.update(state='ACTIVE',updated_utc=now);tmp=p.with_suffix('.prefill.tmp');tmp.write_text(json.dumps(plan,indent=2)+'\n');tmp.replace(p)
print('Armed2prefillinteractionpilots;source/placement/shellvalidationpass;runtimeunverified')
