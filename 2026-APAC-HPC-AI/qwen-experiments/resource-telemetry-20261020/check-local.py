"""Validate missing-data handling, metric filtering, phase clocks and the native polling selector without GPUs."""
import ast
import enum
import http.server
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import types

O=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('sampler',O/'resource-sampler.py');sampler=importlib.util.module_from_spec(s);s.loader.exec_module(sampler)
class Fixture(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.end_headers();self.wfile.write(b'sglang:num_running_reqs{model_name="qwen"} 51\nprivate_unselected_metric 999\nsglang:token_usage 0.11\n')
    def log_message(self,*_):pass
server=http.server.HTTPServer(('127.0.0.1',0),Fixture);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();checks=[]
try:
    calls=[]
    def gpu(args,**kwargs):
        calls.append(args)
        return types.SimpleNamespace(returncode=0,stdout='0, GPU-test, TestGPU, 80, 40, 9000, 140000, 300, 60, 1800, 2619, P0\n')
    d=sampler.sample('0',server.server_port,command=gpu)
    assert d['gpu_status']=='ok' and d['gpus'][0]['memory.used']=='9000' and '--id=0' in calls[0]
    assert d['node_cpu_jiffies'] and d['node_memory']['MemTotal_KiB']>0 and len(d['server_metrics'])==2
    assert not any('private_unselected' in x for x in d['server_metrics']);checks.append('selected_gpu_ids_units_proc_and_metric_whitelist')
    def missing(*a,**k):raise FileNotFoundError()
    d=sampler.sample('0',server.server_port,command=missing);assert d['gpu_status']=='FileNotFoundError' and 'gpus' not in d and d['server_metrics'];checks.append('missing_gpu_is_unknown_and_does_not_disable_other_samples')
    def bad(*a,**k):return types.SimpleNamespace(returncode=0,stdout='bad\n')
    assert sampler.sample('0',server.server_port,command=bad)['gpu_status']=='invalid_csv_shape';checks.append('malformed_gpu_csv_not_accepted')
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp);subprocess.run(['python3',str(O/'phase-marker.py'),str(p),'benchmark_start','confirm','60'],check=True);d=json.loads((p/'phase-markers.jsonl').read_text());assert d['event']=='benchmark_start' and d['utc_ns']>10**18 and d['monotonic_ns']>0;checks.append('explicit_phase_event_epoch_and_monotonic_clocks')
    source=O.parent/'research-followup-20261020-0132/runtime-source/extracted/sgl-workspace/sglang/python/sglang/srt/managers/scheduler_components/recv_skipper.py'
    node=next(x for x in ast.parse(source.read_text()).body if isinstance(x,ast.ClassDef) and x.name=='SchedulerRecvSkipper')
    class Mode(enum.Enum):IDLE=0;PREBUILT=1;DECODE=2;TARGET_VERIFY=3;EXTEND=4
    def val(v):return types.SimpleNamespace(get=lambda:v)
    envs=types.SimpleNamespace(**{'SGLANG_SCHEDULER_RECV_SKIPPER_WEIGHT_'+k:val(v) for k,v in [('DEFAULT',1000),('DECODE',1),('TARGET_VERIFY',1),('NONE',1)]})
    namespace={'ForwardMode':Mode,'envs':envs};future=ast.parse('from __future__ import annotations').body[0]
    exec(compile(ast.Module(body=[future,node],type_ignores=[]),'actual-native-skipper','exec'),namespace)
    cls=namespace['SchedulerRecvSkipper'];assert cls.maybe_create(types.SimpleNamespace(scheduler_recv_interval=1)) is None
    obj=cls.maybe_create(types.SimpleNamespace(scheduler_recv_interval=2,enable_dp_attention=False));batch=types.SimpleNamespace(forward_mode=Mode.DECODE)
    assert [obj.handle(batch) for _ in range(4)]==[False,True,False,True];checks.append('native_interval2_alternates_decode_receive_without_changing_forward_work')
    obj=cls.maybe_create(types.SimpleNamespace(scheduler_recv_interval=2,enable_dp_attention=False));assert obj.handle(types.SimpleNamespace(forward_mode=Mode.EXTEND));checks.append('native_extend_mode_still_polls_immediately')
finally:
    server.shutdown();server.server_close();thread.join(timeout=3)
(O/'validation.json').write_text(json.dumps(dict(passed=True,checks=checks,gpu_live_validation=False,monitoring_overhead_unknown=True),indent=2)+'\n');print(json.dumps({'passed':True,'checks':checks}))
