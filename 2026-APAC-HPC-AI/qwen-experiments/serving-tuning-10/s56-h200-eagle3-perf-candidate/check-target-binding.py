#!/usr/bin/env python3
"""Fail-closed verification of the immutable actual S46 target receipt."""
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]); root=p.parent; x=json.loads(p.read_text())
required=("target_job","target_reference_file","target_reference_sha256","target_review_path","target_review_json_sha256","target_review_seal_sha256")
if x.get("state")!="S46_TARGET_ACCEPTED" or any(not x.get(k) for k in required): raise SystemExit("candidate requires an accepted actual S46 target receipt")
def read(name,digest):
 q=(root/name).resolve(strict=True)
 if root.resolve() not in q.parents: raise SystemExit("bound target artifact escapes candidate directory")
 b=q.read_bytes()
 if hashlib.sha256(b).hexdigest()!=digest: raise SystemExit(f"bound artifact hash mismatch: {name}")
 return json.loads(b)
r=read(x["target_reference_file"],x["target_reference_sha256"]); v=read(x["target_review_path"],x["target_review_json_sha256"])
if str(v.get("job"))!=str(x["target_job"]) or v.get("state")!="H200_DETERMINISTIC_TARGET_REFERENCE_ACCEPTED" or v.get("accepted_reference") is not True: raise SystemExit("review is not accepted S46 target job")
if v.get("seal_sha256")!=x["target_review_seal_sha256"] or v.get("reference_sha256")!=x["target_reference_sha256"] or r.get("passed") is not True or r.get("platform")!="H200": raise SystemExit("target reference/review seal contract mismatch")
print("S46_TARGET_REFERENCE_BINDING_VERIFIED")
