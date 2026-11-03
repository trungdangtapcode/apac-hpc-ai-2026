from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,tempfile
H=Path('/home/apacsc42');W=H/'workspace';O=W/'submission-review/ai-quality-update-20261103';R=W/'reports/ai-final-report-20261030';B=O/'offhost';B.mkdir(exist_ok=False)
repo='trungdangtapcode/apac-hpc-ai-research';tag='ai-quality-presentation-20261103-v1';A=H/'apac-hpc-ai-research'
assert json.loads(subprocess.check_output(['gh','repo','view',repo,'--json','isPrivate'],text=True))['isPrivate'] is True
head=subprocess.check_output(['git','-C',str(A),'rev-parse','HEAD'],text=True).strip()
files=[W/'VNUHCM - TripleU.zip',W/'VNUHCM - TripleU/Presentation/TripleU_APAC2026_Presentation.pptx',O/'TripleU_APAC2026_Main_Talk.pdf',O/'TripleU_APAC2026_Presentation.pdf',R/'TRANSCRIPT_EN.pdf',R/'TRANSCRIPT_VI.pdf',R/'TRANSCRIPT_EN.md',R/'TRANSCRIPT_VI.md']
entries=[dict(name=p.name,source_path=str(p.relative_to(H)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files];assert len(set(x['name'] for x in entries))==len(entries)
manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),repo=repo,tag=tag,source_git_head=head,scope='Final locally published AI-quality-integrated deliverables with unchanged embedded HPC. Private backup, not organiser submission.',files=entries)
(B/'ASSET_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(B/'RELEASE_NOTES.md').write_text('''# AI quality presentation and final submission materials

Private backup of the locally published 3 November edition. Main slide 16 and
both transcripts describe the complete H200 MMLU-Pro comparison: 9460 reference
versus 9452 candidate correct answers over 12032 questions each; 99.915433%
accuracy retention, passing the local gate. This is not organiser certification.

The submission ZIP includes original compressed response records and a CPU
score replay. Existing HPC payloads are retained byte-for-byte. The asset
manifest records exact source paths, hashes, sizes and Git capture identity.
No credentials, model weights or runtime homes are included.
''')
cmd=['gh','release','create',tag,*map(str,files),str(B/'ASSET_MANIFEST.json'),'--repo',repo,'--draft','--target',head,'--title','AI quality presentation and transcripts — 3 November 2026','--notes-file',str(B/'RELEASE_NOTES.md')]
r=subprocess.run(cmd,capture_output=True,text=True);(B/'UPLOAD_RECEIPT.json').write_text(json.dumps(dict(argv=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n');r.check_returncode();print('Private backup uploaded.',flush=True)
dest=Path(tempfile.mkdtemp(prefix='tripleu-quality-materials-verify-'))
r=subprocess.run(['gh','release','download',tag,'--repo',repo,'--dir',str(dest)],capture_output=True,text=True);r.check_returncode()
for x in entries:
 p=dest/x['name'];assert p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
assert json.loads((dest/'ASSET_MANIFEST.json').read_text())==manifest
receipt=dict(verified_utc=datetime.now(timezone.utc).isoformat(),passed=True,repo=repo,tag=tag,source_git_head=head,downloaded_files=len(entries),all_asset_hashes_and_sizes_match=True,download_directory=str(dest),scope=manifest['scope'])
(B/'DOWNLOAD_VERIFIED.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
