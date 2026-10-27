"""Check a complete numeric 512-part processor mesh tree."""
from pathlib import Path
import json,sys
p=Path(sys.argv[1]); ds=[x.name for x in p.glob('processor*') if x.is_dir()]
assert len(ds)==512 and set(ds)=={'processor'+str(i) for i in range(512)}
assert all((p/('processor'+str(i))/'constant/polyMesh').is_dir() for i in range(512))
print(json.dumps({'passed':True,'processor_directories':512,'numeric_ids':[0,511]},indent=2))
