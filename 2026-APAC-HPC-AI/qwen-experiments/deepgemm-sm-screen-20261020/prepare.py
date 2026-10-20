"""Freeze a native DeepGEMM scheduler screen derived from the validated pilot."""
from pathlib import Path
import ast, hashlib, json, shutil, subprocess, tarfile

O = Path(__file__).resolve().parent
R = O.parent
old = R/'fp8-privatehome-20261020'
B = R/'nscc-pbs/h100-deepgemm-sm-66'
assert not B.exists(), 'Never overwrite a frozen bundle'
B.mkdir()
source = O/'runtime-source/usr/local/lib/python3.12/dist-packages/deep_gemm/__init__.py'
wrapper = old/'runtime-source/sgl-workspace/sglang/python/sglang/srt/layers/deep_gemm_wrapper/compile_utils.py'
guards = {str(source): hashlib.sha256(source.read_bytes()).hexdigest(),
          str(wrapper): hashlib.sha256(wrapper.read_bytes()).hexdigest()}
config = json.loads((old/'config.json').read_text())
config.update(experiment='native-deepgemm-sm-scheduler-screen', batch_tokens=[32,48,54,60,64],
              sm_settings=[132,120,96], backends=['sms_132','sms_120','sms_96'],
              deepgemm_init_sha256=guards[str(source)], compile_utils_sha256=guards[str(wrapper)])
(O/'config.json').write_text(json.dumps(config,indent=2)+'\n')
s = (old/'bench.py').read_text()
a = s.index('    funcs = {'); z = s.index('    report = dict(',a)
s = s[:a]+'''    import deep_gemm
    from sglang.srt.layers.deep_gemm_wrapper import compile_utils
    assert hashlib.sha256(Path(deep_gemm.__file__).read_bytes()).hexdigest() == config['deepgemm_init_sha256']
    assert hashlib.sha256(Path(compile_utils.__file__).read_bytes()).hexdigest() == config['compile_utils_sha256']
    assert not compile_utils._ENABLE_JIT_DEEPGEMM_PRECOMPILE
    default_sms = deep_gemm.get_num_sms()
    assert default_sms == torch.cuda.get_device_properties(rank).multi_processor_count == 132
    funcs = {'sms_' + str(n): fp8.deepgemm_w8a8_block_fp8_linear_with_fallback for n in config['sm_settings']}
''' +s[z:]
s=s.replace("backends = ['deep_gemm', 'triton'] + (['flashinfer_deepgemm'] if m < 32 else [])", "backends = ['sms_' + str(n) for n in config['sm_settings']]")
s=s.replace('                    func = funcs[backend]', '''                    requested_sms = int(backend.split('_')[1])
                    deep_gemm.set_num_sms(requested_sms)
                    assert deep_gemm.get_num_sms() == requested_sms
                    func = funcs[backend]''')
s=s.replace("relative_rmse=rel_rmse, samples_us=samples,", "relative_rmse=rel_rmse, configured_sms=deep_gemm.get_num_sms(), samples_us=samples,")
s=s.replace("outputs['deep_gemm'].float()", "outputs['sms_132'].float()")
s=s.replace("    report.update(completed=True", "    deep_gemm.set_num_sms(default_sms)\n    assert deep_gemm.get_num_sms() == default_sms\n    report.update(default_sms_restored=True)\n    report.update(completed=True")
(O/'bench.py').write_text(s)
s=(old/'runtime_cache.py').read_text().replace("    return {key:", "    os.environ['SGLANG_JIT_DEEPGEMM_PRECOMPILE'] = '0'\n    return {key:")
(O/'runtime_cache.py').write_text(s)
s=(old/'run-micro.sh').read_text().replace('batch_tokens=[16,54]', 'batch_tokens=[54]').replace("len(x['cases'])==10", "len(x['cases'])==6")
(O/'run-micro.sh').write_text(s)
for name in ['bench.py','config.json','runtime_cache.py','run-micro.sh']:
    shutil.copy2(O/name,B/name)
for name in ['pbs-container.sh','pbs-exec.py']:
    shutil.copy2(R/'nscc-pbs/h100-fp8-privatehome-64'/name,B/name)
s=(R/'nscc-pbs/h100-fp8-privatehome-64/benchmark.pbs').read_text().replace('h100-fp8-privatehome-64',B.name).replace('ap42-fp8-private64','ap42-dg-sm66')
(B/'benchmark.pbs').write_text(s)
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(B.iterdir())}
(B/'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()))
pilot=dict(id=B.name,platform='H100',bundle=str(B),requested_gpus=8,minutes=10,max_su=8*128/6,
           payload_sha256=hashes,state='PREPARED_NOT_SUBMITTED',kind='isolated_microbenchmark',
           model_loaded=False,planned_ns=[],source_job='222242.pbs111')
for path in [O/'pilot.json',B/'pilot.json']: path.write_text(json.dumps(pilot,indent=2)+'\n')
(O/'pilots.json').write_text(json.dumps([pilot],indent=2)+'\n')
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as archive:
    for p in sorted(B.iterdir()): archive.add(p,arcname=B.name+'/'+p.name)
for p in B.iterdir():
    if p.suffix=='.py': ast.parse(p.read_text())
    if p.suffix in {'.sh','.pbs'}: subprocess.run(['bash','-n',str(p)],check=True,capture_output=True)
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=B,check=True,capture_output=True)
assert (B/'pbs-container.sh').read_bytes()==(R/'nscc-pbs/h100-fp8-privatehome-64/pbs-container.sh').read_bytes()
# Exercise the pinned real hook AST with mocked compiler/native execution.
node=next(n for n in ast.parse(wrapper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='_maybe_compile_deep_gemm_one_type_all')
from typing import Any
calls=[]
env=dict(DeepGemmKernelType=Any,_ENABLE_JIT_DEEPGEMM_PRECOMPILE=False,_DO_COMPILE_ALL=True,
         _INITIALIZATION_DICT={},_BUILTIN_M_LIST=[1,2],_IN_PRECOMPILE_STAGE=False,_IS_FIRST_RANK_ON_NODE=False,
         _compile_deep_gemm_one_type_all=lambda **kw:calls.append(kw),logger=type('Log',(),{'info':lambda *a:None})())
exec(compile(ast.Module(body=[node],type_ignores=[]),str(wrapper),'exec'),env)
env['_maybe_compile_deep_gemm_one_type_all'](type('Kernel',(),{'name':'fixture'})(),1280,4096,1)
assert calls==[], 'Disabled broad precompile must not compile unrelated Ms'
(O/'validation.json').write_text(json.dumps(dict(passed=True,syntax_and_payload_hashes=True,
    private_home_wrapper_identical_to_gpu_validated_222242=True,pinned_precompile_hook_fixture_passed=True,
    preflight_cases=6,full_cases_per_rank=30,full_cases=240,source_sha256=guards,
    scope='CPU source/AST and payload checks only. GPU must validate actual set/get, numerical gates, all ranks and native SM-bearing kernels.'),indent=2)+'\n')
print('Frozen native scheduler screen with six-case provider preflight and 240 full cases')
