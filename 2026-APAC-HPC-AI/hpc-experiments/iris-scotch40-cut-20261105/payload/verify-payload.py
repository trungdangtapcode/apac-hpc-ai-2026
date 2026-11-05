from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]);m=json.loads((root/'payload-sha256.json').read_text())['files']
for name,want in m.items():
 p=root/name;assert p.is_file() and not p.is_symlink(),name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==want,name
print(json.dumps({'passed':True,'files':len(m),'all_source_hashes_match':True},indent=2))
