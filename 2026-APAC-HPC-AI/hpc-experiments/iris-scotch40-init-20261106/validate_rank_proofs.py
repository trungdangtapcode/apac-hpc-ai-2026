#!/usr/bin/env python3
"""Apply the qualified strict rank-proof reader to the N40 initialization probe."""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from read_rank_proofs import validate_proof_dir
p=argparse.ArgumentParser()
p.add_argument('--proof-dir',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
r=validate_proof_dir(a.proof_dir,40)
a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='proofs'},indent=2))
