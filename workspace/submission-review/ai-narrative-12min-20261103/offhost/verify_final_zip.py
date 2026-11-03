from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,subprocess,tempfile
H=Path('/home/apacsc42');W=H/'workspace';A=H/'apac-hpc-ai-research';B=W/'submission-review/ai-narrative-12min-20261103/offhost';T=H/'apac-hpc-ai-research-artifacts/portable-narrative-20261103';T.mkdir(exist_ok=True)
source=W/'VNUHCM - TripleU.zip';transport=T/'TripleU-narrative-final-v2.zip';assert not transport.exists();shutil.copy2(source,transport)
repo='trungdangtapcode/apac-hpc-ai-research';tag='ai-narrative-12min-20261103-v1';head=subprocess.check_output(['git','-C',str(A),'rev-parse','HEAD'],text=True).strip();sha=hashlib.sha256(source.read_bytes()).hexdigest()
subprocess.run(['gh','release','upload',tag,str(transport),'--repo',repo],check=True)
download=Path(tempfile.mkdtemp(prefix='tripleu-narrative-final-zip-'));subprocess.run(['gh','release','download',tag,'--repo',repo,'--pattern',transport.name,'--dir',str(download)],check=True)
back=download/transport.name;assert back.stat().st_size==source.stat().st_size and hashlib.sha256(back.read_bytes()).hexdigest()==sha
r=dict(verified_utc=datetime.now(timezone.utc).isoformat(),passed=True,repo=repo,release_tag=tag,source_git_head=head,asset_name=transport.name,source_path='workspace/VNUHCM - TripleU.zip',sha256=sha,bytes=source.stat().st_size,retained_transport=str(transport),downloaded_hash_and_size_match=True,scope='Final ZIP after Q&A-title synchronisation; earlier v1 ZIP remains retained. Slide and guide assets remain the previously verified identical bytes.')
(B/'FINAL_ZIP_VERIFIED.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
