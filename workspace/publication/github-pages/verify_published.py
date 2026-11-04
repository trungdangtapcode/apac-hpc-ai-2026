#!/usr/bin/env python3
"""Verify the deployed viewer is exactly the reviewed standalone HTML."""
import argparse,datetime,gzip,hashlib,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--url',default='https://trungdangtapcode.github.io/apac-hpc-ai-2026/')
p.add_argument('--report',type=Path,required=True)
p.add_argument('--source',type=Path,help='Reviewed compressed HTML for a companion page')
a=p.parse_args()
source=a.source or Path(__file__).resolve().parents[2]/'reports/ai-run-lineage-20261103/index.html.gz'
expected=gzip.decompress(source.read_bytes())
req=urllib.request.Request(a.url,headers={'User-Agent':'TripleU-static-publication-verifier'})
with urllib.request.urlopen(req,timeout=30) as response:
    content=response.read();status=response.status
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':a.url,'http_status':status,'sha256':hashlib.sha256(content).hexdigest(),'expected_sha256':hashlib.sha256(expected).hexdigest(),'bytes':len(content),'passed':status==200 and content==expected}
a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if not result['passed']:raise SystemExit(1)
