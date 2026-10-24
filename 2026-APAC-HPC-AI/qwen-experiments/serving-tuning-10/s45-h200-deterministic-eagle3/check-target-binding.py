#!/usr/bin/env python3
"""Fail closed until a real reviewed S44 receipt is bound to the candidate."""
import json,sys
x=json.load(open(sys.argv[1]))
required=("target_job","target_reference_file","target_reference_sha256","target_review_path","target_review_json_sha256","target_review_seal_sha256")
if x.get("state")!="S44_TARGET_ACCEPTED" or any(not x.get(key) for key in required):
 raise SystemExit("candidate is blocked until root binds actual reviewed S44 target receipt")
