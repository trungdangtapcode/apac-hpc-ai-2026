#!/usr/bin/env python3
"""Publish reviewed AI changes atomically per file, preserving HPC bytes and ZIP attributes."""
from pathlib import Path
from datetime import datetime,timezone
import copy,csv,fcntl,hashlib,io,json,os,shutil,stat,subprocess,zipfile
from lxml import etree as E
from pptx import Presentation
W=Path('/home/apacsc42/workspace');O=W/'submission-review/ai-update-20261028';T=W/'VNUHCM - TripleU';Z=W/'VNUHCM - TripleU.zip';V=Path('/tmp/apac-slides-20261022-venv/bin/python')
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(o):return (json.dumps(o,indent=2)+'\n').encode()
def inventory(root):return {str(p.relative_to(root)):p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}
def atomic(path,data,mode=None):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name('.'+path.name+'.ai28-publish');assert not tmp.exists();tmp.write_bytes(data)
 if mode is not None:tmp.chmod(mode)
 tmp.replace(path)
def verify_source_hashes():
 d=json.loads((O/'slides/presentation-data.json').read_text())
 for p,h in d['sources'].items():assert sha(Path(p).read_bytes())==h,p
 return len(d['sources'])
def slide_texts(path):
 p=Presentation(path);return p,[s.text for sl in p.slides for s in sl.shapes if s.has_text_frame]
def main():
 with (W/'.submission-publication.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  before=inventory(T);assert {p.name for p in T.iterdir()}=={'AI_Task','HPC_Task','Presentation'}
  hpc=json.loads((O/'HPC_BEFORE.json').read_text());oldhpc={p:sha(b) for p,b in before.items() if p.startswith('HPC_Task/')}
  assert oldhpc==hpc['hpc_task_files'],'HPC changed concurrently; rebuild from the new reviewed delivery'
  hpcmodes={str(p.relative_to(T)):stat.S_IMODE(p.stat().st_mode) for p in (T/'HPC_Task').rglob('*')}
  assert sha(before['Presentation/TripleU_APAC2026_Presentation.pptx']) in {hpc['presentation']['sha256'],json.loads((O/'merge-validation.json').read_text())['pptx_sha256']},'Published deck changed concurrently'
  validation=json.loads((O/'VALIDATION.json').read_text());assert validation['passed'] and all(r['passed'] for r in validation['checks'])
  source_count=verify_source_hashes();merge=json.loads((O/'merge-validation.json').read_text());assert merge['passed']
  newdeck=O/'TripleU_APAC2026_Presentation.pptx';assert sha(newdeck.read_bytes())==merge['pptx_sha256']
  deck,texts=slide_texts(newdeck);assert len(deck.slides)==40
  ai=[s.text for sl in list(deck.slides)[:32] for s in sl.shapes if s.has_text_frame]
  for label in ['3,044.40','3,045.50','3,034.09','3,020.94','28 October 2026','Not verified','-4.74%']:assert any(label in t for t in ai),label
  for stale in ['N68 gain still needs full confirmation','No HPC task scripts','README','AI_Task/','HPC_Task/','FILE_MANIFEST']:assert not any(stale.lower() in t.lower() for t in ai),stale
  with zipfile.ZipFile(newdeck) as z:
   assert z.testzip() is None
   for p,h in hpc['presentation']['hpc_dependency_closure_parts'].items():assert sha(z.read(p))==h,p
  # The first full-slide photo per slide is the ambient background.
  backgrounds=[]
  for n,sl in enumerate(deck.slides,1):
   pics=[s for s in sl.shapes if s.shape_type==13 and s.left==0 and s.top==0]
   assert pics,(n,'Missing background');backgrounds.append({'slide':n,'sha256':sha(pics[0].image.blob)})
  assert len({r['sha256'] for r in backgrounds})==40,'Background photo reused'
  after={p:b for p,b in before.items() if not p.startswith('AI_Task/')}
  staged=inventory(O/'AI_Task');omitted=[]
  for p,b in staged.items():
   if '__pycache__' in Path(p).parts or p.endswith('.pyc'):continue
   if Path(p).name=='inputs.json' and len(b)>1024*1024:
    omitted.append({'path':'AI_Task/'+p,'bytes':len(b),'sha256':sha(b),'reason':'Large generated synthetic dataset; raw scored requests and input configuration retained, original research artifact preserved separately.'});continue
   after['AI_Task/'+p]=b
  after['Presentation/TripleU_APAC2026_Presentation.pptx']=newdeck.read_bytes()
  cfg=json.loads(after['AI_Task/job_scripts/config.json']);assert cfg['declared_concurrency']==64 and cfg['concurrency']==[64]
  assert sum(p.endswith('.sbatch') for p in after if p.startswith('AI_Task/job_scripts/'))==1
  now=datetime.now(timezone.utc)
  report={'checked_utc':now.isoformat(),'passed':True,'publication_scope':'AI_Task and 32 AI slides; existing eight HPC slides and entire HPC_Task preserved','slides':40,'ai_slides_updated':32,'hpc_slides_preserved':8,'hpc_files_preserved':len(oldhpc),'hpc_pptx_dependency_parts_preserved':len(hpc['presentation']['hpc_dependency_closure_parts']),'distinct_backgrounds':40,'package_checks_passed':len(validation['checks']),'current_sources_hash_checked':source_count,'primary_concurrency':64,'primary_gpu_replayed':False,'official_accuracy_verified':False,'organiser_upload_performed':False,'pptx_sha256':sha(newdeck.read_bytes()),'render_scope':'Coordinate-based AI PDF/previews; HPC PDF pages preserved; not an Office render'}
  after['AI_Task/logs/package-validation.json']=enc(validation)
  after['AI_Task/logs/replay-status.json']=enc({'primary':'N64 portable Pyxis entry','configuration_evidence_jobs':[25366,25373,25487,26766],'portable_entry_gpu_replayed':False,'static_mock_and_raw_replay_checks':'PASS','official_accuracy':'UNKNOWN'})
  after['AI_Task/logs/presentation-validation.json']=enc(report)
  after['AI_Task/logs/presentation-backgrounds.json']=enc({'slides':backgrounds})
  evidence=json.loads((O/'evidence-manifest.json').read_text())
  evidence['files']=[r for r in evidence['files'] if 'AI_Task/'+r['path'] in after]
  evidence['omitted_large_generated_inputs']=omitted
  evidence['scope']='Published compact AI payload. Generated inputs and disposable bytecode excluded; full raw scored requests, input config, profiles and source hashes retained.'
  after['AI_Task/logs/evidence-manifest-20261028.json']=enc(evidence)
  after['AI_Task/logs/omitted-artifacts-20261028.json']=enc({'paths_relative_to_team_directory':True,'omitted_generated_datasets':omitted,'total_omitted_bytes':sum(r['bytes'] for r in omitted),'authentication_or_weights_included':False})
  latest='AI_Task/logs/measured/latest-results.md'
  after[latest]+=b'\nGenerated inputs.json dataset exports are omitted from the compact submission with exact byte sizes and SHA-256 hashes in ../omitted-artifacts-20261028.json. The fixed official AIPerf command regenerates the synthetic workload. Raw profiling requests, input configuration, performance exports and the retained research originals are preserved.\n'
  # Preserve the prior provenance document and point the current one at current source metadata.
  previous=before.get('AI_Task/logs/source-provenance.json')
  if previous:after['AI_Task/logs/historical-source-provenance-20261021.json']=previous
  after['AI_Task/logs/source-provenance.json']=enc({'captured_utc':now.isoformat(),'current_preparation':json.loads((O/'PREPARATION.json').read_text()),'evidence_manifest':'evidence-manifest-20261028.json','historical_source_provenance':'historical-source-provenance-20261021.json','presentation_sources_sha256':json.loads((O/'slides/presentation-data.json').read_text())['sources']})
  fields=['platform','job','concurrency','chunk_tokens','good_output_tokens_s','good_request_fraction','ttft_avg_ms','ttft_p95_ms','itl_avg_ms','itl_p95_ms','errors','cancelled_requests','scope']
  stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
  Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
  for j in [25366,25373,25487,26766,26768,26770]:
   cfgj=json.loads((Q/f'runs/{j}/config.json').read_text());rows=json.loads((Q/f'runs/{j}/summary.json').read_text());r=next(r for r in rows if r['phase']=='confirm' and r['concurrency']==64)
   row={k:r[k] for k in fields if k in r};row.update(platform='H200',job=j,concurrency=64,chunk_tokens=cfgj.get('prefill_chunked_prefill_size',cfgj.get('prefill_chunk_size',8192)),scope='Historical full run' if j<26000 else 'Separate native-runtime full run');writer.writerow(row)
  after['AI_Task/logs/results.csv']=stream.getvalue().encode()
  manifest_name='AI_Task/logs/FILE_MANIFEST.json';sums_name='AI_Task/logs/SHA256SUMS'
  after[manifest_name]=enc({'created_utc':now.isoformat(),'paths_relative_to_team_directory':True,'files':[{'path':p,'bytes':len(b),'sha256':sha(b)} for p,b in sorted(after.items()) if p not in [manifest_name,sums_name]]})
  after[sums_name]=''.join(sha(b)+'  '+os.path.relpath(T/p,T/'AI_Task/logs')+'\n' for p,b in sorted(after.items()) if p!=sums_name).encode()
  assert {p:sha(b) for p,b in after.items() if p.startswith('HPC_Task/')}==oldhpc
  # Preserve the old ZIP's HPC member permissions/timestamps, besides file bytes.
  with zipfile.ZipFile(Z) as oldzip:
   oldinfos={i.filename:copy.copy(i) for i in oldzip.infolist()}
   for p in oldhpc:assert sha(oldzip.read(T.name+'/'+p))==oldhpc[p]
  ztmp=O/'VNUHCM - TripleU.reviewed.zip';dirs={T.name+'/'}
  dirs.update(n for n in oldinfos if n.startswith(T.name+'/HPC_Task/') and n.endswith('/'))
  for p in after:
   dirs.update(T.name+'/'+str(d)+'/' for d in Path(p).parents if str(d)!='.')
  for folder in ['Presentation','AI_Task/job_scripts','AI_Task/logs/slurm','AI_Task/logs/reruns','HPC_Task/job_scripts','HPC_Task/logs']:dirs.add(T.name+'/'+folder+'/')
  with zipfile.ZipFile(ztmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for name in sorted(dirs):
    info=copy.copy(oldinfos[name]) if name in oldinfos and name.startswith(T.name+'/HPC_Task/') else zipfile.ZipInfo(name)
    info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b'')
   for p,b in sorted(after.items()):
    name=T.name+'/'+p
    if p.startswith('HPC_Task/'):
     info=copy.copy(oldinfos[name]);z.writestr(info,b)
    else:
     info=zipfile.ZipInfo(name,date_time=now.timetuple()[:6]);info.compress_type=zipfile.ZIP_DEFLATED
     source=O/p if p.startswith('AI_Task/') else T/p
     mode=stat.S_IMODE(source.stat().st_mode) if source.exists() else 0o644
     info.external_attr=(stat.S_IFREG|mode)<<16;z.writestr(info,b)
  with zipfile.ZipFile(ztmp) as z:
   assert z.testzip() is None
   for p,b in after.items():assert sha(z.read(T.name+'/'+p))==sha(b),p
   for p in oldhpc:
    a=oldinfos[T.name+'/'+p];b=z.getinfo(T.name+'/'+p);assert (a.external_attr,a.date_time,a.comment)==(b.external_attr,b.date_time,b.comment)
  assert {p:sha(b) for p,b in inventory(T).items()}=={p:sha(b) for p,b in before.items()},'Concurrent source edit'
  already_reviewed=sha(before['Presentation/TripleU_APAC2026_Presentation.pptx'])==merge['pptx_sha256']
  if already_reviewed:
   previous_report=json.loads((O/'publication-validation.json').read_text());backup=Path(previous_report['backup']);assert backup.is_dir()
  else:
   backup=W/'submission-archive'/('before-ai-update-'+now.strftime('%Y%m%dT%H%M%SZ'));backup.mkdir()
   shutil.copytree(T/'AI_Task',backup/'AI_Task');(backup/'Presentation').mkdir();shutil.copy2(T/'Presentation/TripleU_APAC2026_Presentation.pptx',backup/'Presentation/TripleU_APAC2026_Presentation.pptx')
   for name in ['VNUHCM - TripleU.zip','VNUHCM - TripleU.zip.sha256']:shutil.copy2(W/name,backup/name)
  # Apply only AI/new presentation paths. HPC is never written.
  for p,b in after.items():
   if p.startswith('HPC_Task/'):continue
   if before.get(p)!=b:
    source=O/p if p.startswith('AI_Task/') else T/p;mode=stat.S_IMODE(source.stat().st_mode) if source.exists() else 0o644
    atomic(T/p,b,mode)
  for p in before.keys()-after.keys():assert p.startswith('AI_Task/');(T/p).unlink()
  atomic(Z,ztmp.read_bytes(),0o644);atomic(W/'VNUHCM - TripleU.zip.sha256',(sha(ztmp.read_bytes())+'  VNUHCM - TripleU.zip\n').encode(),0o644)
  actual=inventory(T);assert {p:sha(b) for p,b in actual.items()}=={p:sha(b) for p,b in after.items()}
  assert {p:sha(b) for p,b in actual.items() if p.startswith('HPC_Task/')}==oldhpc
  assert {str(p.relative_to(T)):stat.S_IMODE(p.stat().st_mode) for p in (T/'HPC_Task').rglob('*')}==hpcmodes
  subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=T/'AI_Task/job_scripts',check=True,stdout=subprocess.DEVNULL)
  subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=T/'AI_Task/logs',check=True,stdout=subprocess.DEVNULL)
  report.update(zip_sha256=sha(ztmp.read_bytes()),zip_bytes=ztmp.stat().st_size,zip_crc_verified=True,hpc_zip_attributes_preserved=True,hpc_file_modes_unchanged=True,omitted_duplicate_dataset_files=len(omitted),omitted_generated_dataset_bytes=sum(r['bytes'] for r in omitted),global_hash_entries=len(after)-1,backup=str(backup),files_written=sum(before.get(p)!=b for p,b in after.items()),files_deleted=len(before.keys()-after.keys()))
  (O/'publication-validation.json').write_bytes(enc(report));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
