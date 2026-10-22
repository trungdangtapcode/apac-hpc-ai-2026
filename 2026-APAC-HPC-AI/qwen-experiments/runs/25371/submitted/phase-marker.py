"""Append one explicit orchestration event; AIPerf phase manifests define ranked phase boundaries."""
import datetime,json,os,socket,sys,time
from pathlib import Path
art, event = sys.argv[1:3]
path = Path(art) / 'phase-markers.jsonl'
row = dict(event=event,utc_ns=time.time_ns(),monotonic_ns=time.monotonic_ns(),
           utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),host=socket.gethostname(),
           local_utc_offset_s=getattr(time.localtime(),'tm_gmtoff',None),detail=sys.argv[3:])
with path.open('a') as handle:
    handle.write(json.dumps(row)+'\n')
