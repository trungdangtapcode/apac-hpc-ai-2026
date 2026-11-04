"""Strictly verify the accepted Scotch source plus reviewed ancillary files."""
from pathlib import Path
import hashlib,json,sys
from qualification_utils import exact_tree_paths,supplementary_hashes,validate_manifest_paths
from seal_tree import inventory

src=Path(sys.argv[1]); core=json.loads(Path(sys.argv[2]).read_text()); extra=json.loads(Path(sys.argv[3]).read_text())
assert extra['source']==str(src)
validate_manifest_paths(core,extra)
actual=inventory(src)
assert actual==core,'accepted 1,040-file source differs'
combined={'files':{**core['files'],**extra['files']},'symlinks':{**core['symlinks'],**extra['symlinks']}}
exact_tree_paths(src,combined,extra['directories'])
supplementary_hashes(src,extra)
out={'passed':True,'core_file_count':len(core['files']),'supplementary_file_count':len(extra['files']),
     'core_manifest_sha256':hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),
     'supplementary_manifest_sha256':hashlib.sha256(Path(sys.argv[3]).read_bytes()).hexdigest(),
     'combined_file_count':len(combined['files']),'symlinks':combined['symlinks'],
     'exact_directory_count':len(extra['directories'])}
Path(sys.argv[4]).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out))
