from pathlib import Path
import subprocess,json,hashlib,tempfile,os,datetime
W=Path('/home/apacsc42/workspace'); O=W/'submission-review/hpc-iris-slides-20261103';B=O/'offhost';B.mkdir(exist_ok=True)
repo='trungdangtapcode/apac-hpc-ai-research';tag='hpc-iris-slides-20261103-v1'
run=lambda args:subprocess.check_output(args,text=True).strip()
assert json.loads(run(['gh','repo','view',repo,'--json','visibility']))['visibility']=='PRIVATE'
A=Path('/home/apacsc42/apac-hpc-ai-research')
head=run(['git','-C',str(A),'rev-parse','HEAD'])
assert run(['git','-C',str(A),'ls-remote','origin','refs/heads/main']).split()[0]==head
files={
 'TripleU_APAC2026_Presentation.pptx':W/'VNUHCM - TripleU/Presentation/TripleU_APAC2026_Presentation.pptx',
 'TripleU_APAC2026_Presentation.pdf':O/'TripleU_APAC2026_Presentation.pdf',
 'TripleU_APAC2026_Main_Talk.pdf':O/'TripleU_APAC2026_Main_Talk.pdf',
 'TripleU_APAC2026_HPC_Section.pdf':O/'slide-section/HPC-section.pdf',
 'TripleU_APAC2026_Presenter_Notes.md':O/'PRESENTER_NOTES.md',
 'TripleU_APAC2026_Submission.zip':W/'VNUHCM - TripleU.zip',
}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((O/'publication-validation.json').read_text());assert r['passed']
assert sha(files['TripleU_APAC2026_Presentation.pptx'])==r['pptx_sha256']
assert sha(files['TripleU_APAC2026_Submission.zip'])==r['zip_sha256']
rows=[dict(asset=n,source=str(p),bytes=p.stat().st_size,sha256=sha(p)) for n,p in files.items()]
(B/'ASSET_MAP.json').write_text(json.dumps({'private_repository':repo,'release':tag,'source_commit':head,'files':rows},indent=2)+'\n')
notes=B/'RELEASE_NOTES.md';notes.write_text('Private recovery copy of the 3 November HPC-only presentation update. The existing 34 AI slides and their notes remain unchanged. Eight HPC slides explain Iris recipe comparisons and screening horizons. The ZIP is the canonical team package; scripts and measurements in both tracks are unchanged. This backup is not an organiser submission. See ASSET_MAP.json and the subsequent download-verification receipt in the research archive.\n')
with tempfile.TemporaryDirectory(prefix='hpc-slide-assets-') as tmp:
 tmp=Path(tmp); paths=[]
 for n,p in files.items():
  target=tmp/n
  try:os.link(p,target)
  except OSError:target.write_bytes(p.read_bytes())
  paths.append(str(target))
 args=['gh','release','create',tag,'--repo',repo,'--target',head,'--title','HPC Iris presentation backup — 3 November 2026','--notes-file',str(notes),'--prerelease','--latest=false',*paths]
 print('Creating private backup with',len(paths),'assets',flush=True)
 url=run(args);print(url,flush=True)
 download=tmp/'download';download.mkdir()
 subprocess.run(['gh','release','download',tag,'--repo',repo,'--dir',str(download)],check=True)
 for row in rows:
  p=download/row['asset'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'];row['download_sha256_verified']=True
 receipt={'passed':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'private_repository':repo,'release':tag,'url':url,'source_commit':head,'assets':rows,'official_upload':False}
 (B/'DOWNLOAD_VERIFIED.json').write_text(json.dumps(receipt,indent=2)+'\n')
(B/'README.md').write_text('# Verified private presentation backup\n\nAll six current presentation/package files were uploaded to private release `'+tag+'`, downloaded again and verified by byte length and SHA-256. The source commit is `'+head+'`. [Asset paths and names](ASSET_MAP.json) and [verification receipt](DOWNLOAD_VERIFIED.json) retain the exact mapping.\n\nThis is a private recovery copy, not an organiser submission. It preserves the canonical PPTX, full/main/HPC PDFs, combined presenter notes and current team ZIP. Source scripts and notes are in Git. Other external research artifacts are outside the scope of this six-file copy.\n')
print('Verified all',len(rows),'downloaded assets',flush=True)
