"""Validate a complete three-arm order, preserving a fixed candidate set."""
import json,sys
sequence=sys.argv[1].split(',')
assert len(sequence)==3 and set(sequence)=={'S0','Hxyz','Hzyx'} and len(set(sequence))==3,sequence
print(json.dumps({'passed':True,'sequence':sequence,'arms':3},indent=2))
