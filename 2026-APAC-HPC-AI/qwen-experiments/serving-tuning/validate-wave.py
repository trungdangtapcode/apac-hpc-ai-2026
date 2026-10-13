import argparse,ast,dataclasses,importlib.util,json,os,subprocess,sys,tempfile,types
from pathlib import Path
root=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');wave=root/'serving-tuning';report={}
engine=root/'serving-tuning/inspection'
spec=importlib.util.spec_from_file_location('apac_arg_utils',engine/'arg_groups/arg_utils.py');argutils=importlib.util.module_from_spec(spec);sys.modules[spec.name]=argutils;spec.loader.exec_module(argutils)
tree=ast.parse((engine/'server_args.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ServerArgs');fields=[n for n in cls.body if isinstance(n,ast.AnnAssign) and getattr(n.target,'id','') in {'cuda_graph_max_bs_decode','cuda_graph_bs_decode'}]
assert len(fields)==2
module=types.ModuleType('apac_thin_args');sys.modules[module.__name__]=module
source='from typing import Optional,List\nfrom dataclasses import dataclass\nfrom apac_arg_utils import A,NS\n@dataclass\nclass ThinArgs:\n'+''.join('    '+ast.unparse(n)+'\n' for n in fields);exec(source,module.__dict__)
parser=argparse.ArgumentParser();argutils.add_cli_args_from_dataclass(parser,module.ThinArgs)
flags=json.loads((wave/'dense-decode-graphs/config.json').read_text())['decode_extra_flags'];args=parser.parse_args(flags)
assert args.cuda_graph_max_bs_decode==64 and args.cuda_graph_bs_decode==list(range(1,65));report['graph_flags_match_image_parser']=True
benchmark=(wave/'control-load/benchmark.sh').read_text();function=benchmark[benchmark.index('run_benchmark() {'):benchmark.index('for N in ${QWEN_TUNE_NS')]
tail=benchmark[benchmark.index('for N in ${QWEN_TUNE_NS'):]
with tempfile.TemporaryDirectory(prefix='apac42-tune-cpu-') as temporary:
 temp=Path(temporary);shim=temp/'bin';shim.mkdir();mock=shim/'aiperf';mock.write_text('''#!/usr/bin/python3
import json,os,sys
from pathlib import Path
a=sys.argv[1:];get=lambda flag:a[a.index(flag)+1]
n=int(get('--concurrency'));p=Path(get('--artifact-dir'));p.mkdir(parents=True)
for flag,expected in [('--warmup-duration','60'),('--benchmark-duration','120'),('--benchmark-grace-period','30'),('--synthetic-input-tokens-mean','4000'),('--output-tokens-mean','200'),('--random-seed','2026'),('--num-dataset-entries','12800')]:assert get(flag)==expected,(flag,get(flag))
assert get('--goodput')=='time_to_first_token:3000 inter_token_latency:20'
frac=.85 if n==int(os.environ.get('APAC_TEST_FAIL_N','0')) else .97
export={k:{'avg':v} for k,v in {'goodput':5,'good_request_fraction':frac,'request_count':10,'error_request_count':0,'time_to_first_token':1000,'inter_token_latency':15}.items()}
(p/'profile_export_aiperf.json').write_text(json.dumps(export))
(p/'argv.json').write_text(json.dumps(a));print('Phase profiling (profiling) complete | completed=10, cancelled=0, errors=0')
''');mock.chmod(0o755)
 for case,failure,expired,expected in [('pass',0,False,[48,52,56]),('fail52',52,False,[48,52]),('budget',0,True,[])]:
  art=temp/case;art.mkdir();(art/'summarize.py').write_bytes((root/'summarize.py').read_bytes())
  script=temp/(case+'.sh');script.write_text('set -euo pipefail\nHOST=mock:8000\nTOKENIZER=Qwen/Qwen3-235B-A22B-Instruct-2507\nART='+str(art)+'\n'+function+tail)
  env=dict(os.environ,PATH=str(shim)+':'+os.environ['PATH'],QWEN_TUNE_NS='48 52 56',QWEN_BENCHMARK_DEADLINE='1' if expired else '4102444800',QWEN_DIAGNOSTIC_PROFILE='0',APAC_TEST_FAIL_N=str(failure))
  subprocess.run(['bash',str(script)],env=env,capture_output=True,text=True,check=True)
  actual=sorted(int(p.name[1:]) for p in (art/'confirm').glob('n*')) if (art/'confirm').exists() else []
  assert actual==expected,(case,actual,expected)
  if expired:assert (art/'deferred-ns.txt').read_text().split()==['48','52','56']
  report[case]={'ns':actual,'passed':True}
for trial in ['control-load','dense-decode-graphs','profile-control']:
 bundle=wave/trial
 subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
 assert (bundle/'nixl-conn.py').read_bytes()==(root/'runs/22415/submitted/nixl-conn.py').read_bytes()
 assert (bundle/'placement.tsv').read_bytes()==(root/'runs/22415/submitted/placement.tsv').read_bytes()
report['frozen_payload_checksums_and_topology']=True;report['passed']=True
(wave/'cpu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
