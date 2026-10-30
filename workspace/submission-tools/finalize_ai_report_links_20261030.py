from pathlib import Path
import copy,datetime,fcntl,hashlib,json,os,re,stat,zipfile
W=Path('/home/apacsc42/workspace');T=W/'VNUHCM - TripleU';Z=W/'VNUHCM - TripleU.zip';O=W/'submission-review/ai-update-20261030'
sha=lambda b:hashlib.sha256(b).hexdigest()
enc=lambda x:(json.dumps(x,indent=2)+'\n').encode()
def inv():return {str(p.relative_to(T)):p.read_bytes() for p in T.rglob('*') if p.is_file()}
def portable_report(text):
 text=text.replace('[research journal](../research-journey-20261019/journal/README.md)','research journal retained in the research archive')
 start=text.index('- [Updated presentation]')
 return text[:start]+"""- [Team presentation](../../Presentation/TripleU_APAC2026_Presentation.pptx)
- [Detailed metrics and configuration](measured/latest-results.md)
- [Publication and preservation scope](report-update-20261030.json)

The review PDF, full speaker notes and historical journal are retained separately in the research archive.
"""
def manifest(d,now):
 mf='AI_Task/logs/FILE_MANIFEST.json';sums='AI_Task/logs/SHA256SUMS'
 d[mf]=enc({'created_utc':now,'paths_relative_to_team_directory':True,'files':[{'path':p,'bytes':len(b),'sha256':sha(b)} for p,b in sorted(d.items()) if p not in [mf,sums]]})
 d[sums]=''.join(sha(b)+'  '+os.path.relpath(p,'AI_Task/logs')+'\n' for p,b in sorted(d.items()) if p!=sums).encode()
with (W/'.submission-publication.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 before=inv();d=dict(before);rel='AI_Task/logs/FINAL_REPORT.md'
 corrected=portable_report(before[rel].decode()).encode();d[rel]=corrected
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest(d,now)
 with zipfile.ZipFile(Z) as old:
  infos={i.filename:copy.copy(i) for i in old.infolist()}
  archive={n[len(T.name)+1:]:old.read(n) for n in old.namelist() if not n.endswith('/')}
 archive[rel]=corrected;manifest(archive,now)
 temp=O/'VNUHCM - TripleU.final.zip'
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for n,i in infos.items():
   if i.is_dir():out.writestr(i,b'')
  for p,b in archive.items():out.writestr(copy.copy(infos[T.name+'/'+p]),b)
 with zipfile.ZipFile(temp) as z:
  assert z.testzip() is None
  for p,b in archive.items():assert sha(z.read(T.name+'/'+p))==sha(b)
 assert inv()==before
 for p,b in d.items():
  if b==before.get(p):continue
  assert p.startswith('AI_Task/')
  t=T/p;tmp=t.with_name('.'+t.name+'.report-final');tmp.write_bytes(b);tmp.chmod(stat.S_IMODE(t.stat().st_mode));tmp.replace(t)
 temp.replace(Z)
 (W/'VNUHCM - TripleU.zip.sha256').write_text(sha(Z.read_bytes())+'  VNUHCM - TripleU.zip\n')
 assert {p:sha(b) for p,b in inv().items() if p.startswith('HPC_Task/')}=={p:sha(b) for p,b in before.items() if p.startswith('HPC_Task/')}
 assert (T/'Presentation/TripleU_APAC2026_Presentation.pptx').read_bytes()==before['Presentation/TripleU_APAC2026_Presentation.pptx']
 (O/'AI_Task/logs/FINAL_REPORT.md').write_bytes(corrected)
 report=json.loads((O/'publication-validation.json').read_text());report.update(final_report_links_portable=True,zip_sha256=sha(Z.read_bytes()),zip_bytes=Z.stat().st_size,final_report_link_correction_utc=now)
 (O/'publication-validation.json').write_bytes(enc(report))
 print(json.dumps({'zip_bytes':Z.stat().st_size,'zip_sha256':sha(Z.read_bytes()),'report_links_portable':True,'HPC_and_presentation_unchanged':True}))
