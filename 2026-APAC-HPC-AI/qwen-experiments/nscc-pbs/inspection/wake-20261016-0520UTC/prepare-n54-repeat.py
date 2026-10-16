import datetime,hashlib,json,pathlib,shutil,subprocess
root=pathlib.Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
ev=root/'nscc-pbs/inspection/wake-20261016-0520UTC'
r=json.loads((ev/'n54-23924-review.json').read_text())
c=r['candidate'];m=c['metrics']
assert r['state']=='MEASURED_SLA_PASS' and m['sla_fraction']>=.95 and m['itl_ms']<=19.3
assert r['comparison']['vs_mean']['goodput_gain_percent']>0
assert c['short_output_comparison']['research_eligible']
name='s10-mnnvl-repeat-n54';source=root/'runs/23924/submitted';bundle=root/'serving-tuning-10'/name
bundle.mkdir()
for f in source.iterdir():
 if f.is_file() and f.name!='SHA256SUMS':shutil.copyfile(f,bundle/f.name)
original=json.loads((source/'config.json').read_text());cfg=dict(original)
purpose='One independent full-protocol MNNVL N54 replication after sealed job23924 gained 1.6004% over both N52 controls mean; same load and execution, no N56 or automatic promotion.'
cfg.update(experiment=name,purpose=purpose)
(bundle/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
oldscript=(source/'job.sbatch').read_text()
oldpath=next(l.split('=',1)[1] for l in oldscript.splitlines() if l.startswith('export QWEN_BUNDLE='))
script=oldscript.replace(oldpath,str(bundle))
script='\n'.join('#SBATCH -J ap42-s10-mnnvl-repeat-n54' if l.startswith('#SBATCH -J ') else l for l in script.splitlines())+'\n'
(bundle/'job.sbatch').write_text(script)
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
operational=[f.name for f in source.iterdir() if f.is_file() and f.name not in ('SHA256SUMS','config.json','job.sbatch')]
assert len(operational)==12 and all(hashfile(source/f)==hashfile(bundle/f) for f in operational)
assert {k for k in cfg.keys()|original.keys() if cfg.get(k)!=original.get(k)}=={'experiment','purpose'}
assert script.replace(str(bundle),oldpath).replace('ap42-s10-mnnvl-repeat-n54','ap42-tune-s7-mnnvl-n54')==oldscript
for f in bundle.glob('*.sh'):subprocess.run(['bash','-n',str(f)],check=True)
subprocess.run(['bash','-n',str(bundle/'job.sbatch')],check=True)
hashes={f.name:hashfile(f) for f in sorted(bundle.iterdir()) if f.is_file()}
(bundle/'SHA256SUMS').write_text(''.join(f'{v}  {k}\n' for k,v in hashes.items()))
x=subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,text=True,check=True)
for f in bundle.iterdir():f.chmod(0o444)
bundle.chmod(0o555)
pilot={'id':name,'bundle':str(bundle),'planned_ns':[54],'state':'PLANNED','wave':10,'purpose':purpose,'diagnostic_profile':False,'expected_profile_ranks':{},'payload_sha256':hashes,'measurements':[],'missing_ns':[54],'benchmark_complete':False,'profile_complete':None,'traces':[],'attempts':[],'replication_source_job':'23924'}
(ev/'n54-repeat-pilot.json').write_text(json.dumps(pilot,indent=2)+'\n')
validation={'passed':True,'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_job':'23924','candidate':name,'operational_files_identical':operational,'config_changes':['experiment','purpose'],'launcher_changes':['job name','bundle path'],'hashes':hashes,'sha256_check':x.stdout,'no_gpu_execution':True,'config_metadata_note':'wave=7 and matched_concurrency=52 inherited unchanged; actual launcher and planned_ns explicitly54, pilot wave10.'}
(ev/'n54-repeat-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps({'passed':True,'bundle':str(bundle),'operational_files':len(operational)}))
