"""Semantic readiness gate: no serving request or performance claim."""
import json,re,sys
from pathlib import Path
root=Path(sys.argv[1]);text=(root/'prefill.log').read_text(errors='replace')
nixl=set(re.findall(r' TP(\d+)\] NIXL KVManager initialized',text))
proof=dict(health_200=sys.argv[2]=='1',source_and_devices='SOURCE_AND_FOUR_HOPPER_DEVICES_VERIFIED' in text,
 ready_log='The server is fired up and ready to roll!' in text,
 disable_logs=len(re.findall('resolved prefill.backend=',text)),nixl_ranks=sorted(nixl),
 capture_begin=bool(re.search('Capture (target|draft) prefill CUDA graph begin',text)),
 fatal=bool(re.search('Traceback|RuntimeError:|OutOfMemoryError:|Mismatched Tensor',text)))
passed=proof['health_200'] and proof['source_and_devices'] and proof['ready_log'] and proof['disable_logs']>=8 and nixl=={'0','1','2','3'} and not proof['capture_begin'] and not proof['fatal']
print(json.dumps(dict(passed=passed,proof=proof,scope='Single TP4 EAGLE3 prefill readiness only; no complete PD, token-equivalence or ranked performance'),indent=2))
sys.exit(0 if passed else 1)
