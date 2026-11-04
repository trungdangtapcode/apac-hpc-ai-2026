#!/usr/bin/env python3
"""Stage only the reviewed standalone viewer, never the research repository root."""
import argparse,gzip,hashlib,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    source=Path(__file__).resolve().parents[1]/'index.html.gz'
    content=gzip.decompress(source.read_bytes())
    assert b'<!doctype html>' in content and b'id="researchData"' in content
    assert b'/home/apacsc42/' not in content
    a.output.mkdir(parents=True,exist_ok=True)
    assert not any(a.output.iterdir()),'Output directory must be empty'
    (a.output/'index.html').write_bytes(content)
    (a.output/'.nojekyll').write_text('')
    print(json.dumps({'files':['index.html','.nojekyll'],'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}))
if __name__=='__main__':main()
