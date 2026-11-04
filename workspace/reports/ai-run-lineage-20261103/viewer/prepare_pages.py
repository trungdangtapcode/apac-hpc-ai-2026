#!/usr/bin/env python3
"""Stage only the reviewed standalone viewer, never the research repository root."""
import argparse,gzip,hashlib,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    source=Path(__file__).resolve().parents[3]/'reports/team-research-atlas-20261104/index.html.gz'
    content=gzip.decompress(source.read_bytes())
    assert b'<!doctype html>' in content and b'id="teamData"' in content
    assert b'/home/apacsc42/' not in content
    a.output.mkdir(parents=True,exist_ok=True)
    assert not any(a.output.iterdir()),'Output directory must be empty'
    (a.output/'index.html').write_bytes(content)
    (a.output/'.nojekyll').write_text('')
    (a.output/'hpc').mkdir()
    redirect='<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../#hpc"><title>HPC · TripleU</title><a href="../#hpc">Open HPC in the team research atlas</a><script>location.replace("../#hpc")</script></html>'
    (a.output/'hpc/index.html').write_text(redirect)
    print(json.dumps({'files':['index.html','.nojekyll','hpc/index.html'],'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}))
if __name__=='__main__':main()
