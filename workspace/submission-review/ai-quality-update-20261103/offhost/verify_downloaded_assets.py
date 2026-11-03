#!/usr/bin/env python3
"""Verify all release bytes and record actual remote names after download."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--download-directory',type=Path,required=True);a=p.parse_args()
m=json.loads((B/'ASSET_MANIFEST.json').read_text())
remote=json.loads(subprocess.check_output(['gh','release','view',m['tag'],'--repo',m['repo'],'--json','assets'],text=True))['assets']
actual={x['name']:x['size'] for x in remote}
assert json.loads((a.download_directory/'ASSET_MANIFEST.json').read_text())==m
files=[]
for source in m['files']:
 matches=[]
 for path in a.download_directory.iterdir():
  if not path.is_file() or path.stat().st_size!=source['bytes']:continue
  if hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256']:matches.append(path)
 assert len(matches)==1,(source['name'],len(matches))
 path=matches[0];assert actual[path.name]==source['bytes']
 files.append(dict(source_name=source['name'],remote_asset_name=path.name,bytes=source['bytes'],sha256=source['sha256']))
receipt=dict(verified_utc=datetime.now(timezone.utc).isoformat(),passed=True,repo=m['repo'],tag=m['tag'],source_git_head=m['source_git_head'],downloaded_files=len(files),all_asset_hashes_and_sizes_match=True,files=files,download_directory=str(a.download_directory),scope=m['scope'])
(B/'DOWNLOAD_VERIFIED.json').write_text(json.dumps(receipt,indent=2)+'\n')
(B/'REMOTE_ASSET_MAP.json').write_text(json.dumps(dict(repo=m['repo'],tag=m['tag'],files=files),indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
