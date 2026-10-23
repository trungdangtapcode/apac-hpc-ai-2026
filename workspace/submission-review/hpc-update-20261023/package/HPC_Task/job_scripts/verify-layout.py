from pathlib import Path
import json,sys
p=Path(sys.argv[1]);n=int(sys.argv[2]);ds=[x.name for x in p.glob('processor*') if x.is_dir() and not x.is_symlink()];assert len(ds)==n and set(ds)=={'processor'+str(i) for i in range(n)},(len(ds),ds[:10]);assert all((p/('processor'+str(i))/'constant/polyMesh').is_dir() for i in range(n));print(json.dumps({'passed':True,'processor_directories':n,'ids':[0,n-1]},indent=2))
