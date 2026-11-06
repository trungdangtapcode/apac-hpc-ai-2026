#!/usr/bin/env python3
"""Apply the qualified generic proof-reader API to the selected N40/N48 arm."""
import argparse, json
from pathlib import Path
from read_rank_proofs import validate_proof_dir

p=argparse.ArgumentParser()
p.add_argument('--proof-dir',type=Path,required=True)
p.add_argument('--expected-ranks',type=int,choices=(40,48),required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
r=validate_proof_dir(a.proof_dir,a.expected_ranks)
a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='proofs'}))
