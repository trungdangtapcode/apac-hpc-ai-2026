"""Execute the frozen candidate's native request-plan builder on labeled CPU pointers."""
import ast,hashlib,importlib.util,json,sys,types
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parent
candidate=R/'serving-tuning-10/s39-h200-eagle3-correctness/nixl-conn.py'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8'
spec=importlib.util.spec_from_file_location('layout_source',O/'cpu_native_layout_fixture.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)
def method(path,class_name,name):
 tree=ast.parse(path.read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==class_name)
 return next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name==name)
def compile_function(node,env):
 import copy
 node=copy.deepcopy(node);node.decorator_list=[];node.returns=None
 for a in node.args.args:a.annotation=None
 module=ast.Module(body=[node],type_ignores=[]);ast.fix_missing_locations(module);exec(compile(module,'<pinned-native-method>','exec'),env)
 return env[node.name]
staging=R/'nixl-native-registration-probe-20261021/staging_buffer.py'
assert hashlib.sha256(staging.read_bytes()).hexdigest()=='52693777d6ee25d1919555a5b910677ba58fa6c18e35782faa7a0470b43839ab'
head_node=next(x for x in ast.parse(staging.read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='compute_head_slice_params')
head=compile_function(head_node,{})
module=types.ModuleType('sglang.srt.disaggregation.common.staging_buffer');module.compute_head_slice_params=head
saved=sys.modules.get(module.__name__);sys.modules[module.__name__]=module
# Only NumPy's opaque pointer-container conversion is replaced. Native source,
# integer head arithmetic, list selection and stored plan fields execute as-is.
np=types.SimpleNamespace(uint64=int,asarray=lambda values,dtype:list(values))
env={'np':np,'logger':types.SimpleNamespace(info=lambda *a,**k:None)}
build=compile_function(method(candidate,'NixlKVManager','_init_hetero_tp_prep_handle'),env)
rows=[]
try:
 for with_prefill_draft in [True,False]:
  target=layout.pool('target',94);draft=layout.pool('draft',1)
  source=target+draft if with_prefill_draft else target
  destination=target+draft
  for source_rank in range(4):
   for destination_rank in [source_rank*2,source_rank*2+1]:
    args=types.SimpleNamespace(page_size=1,total_kv_head_num=4,kv_head_num=1,engine_rank=source_rank,kv_item_lens=[256]*len(source),kv_data_ptrs=source)
    manager=types.SimpleNamespace(attn_tp_size=4,kv_args=args)
    manager.get_mha_kv_ptrs_with_pp=lambda src,dst:layout.native_nixl_selector(src,dst)
    peer=types.SimpleNamespace(decode_tp_size=8,dst_kv_item_len=256,decode_tp_rank=destination_rank,dst_kv_ptrs=destination,gpu_id=0)
    build(manager,'fixture-peer',peer)
    plan=manager._ondemand_slice_plans['fixture-peer']
    assert plan['src_ptrs']==source
    assert plan['dst_ptrs']==(destination if with_prefill_draft else target)
    assert all(plan[k]==256 for k in ['src_stride','dst_stride','length'])
    assert plan['src_offset']==plan['dst_offset']==0
    rows.append(dict(prefill_draft=with_prefill_draft,source_rank=source_rank,destination_rank=destination_rank,source_entries=len(plan['src_ptrs']),destination_entries=len(plan['dst_ptrs']),opaque_origin_identity=True,byte_stride=256))
finally:
 if saved is None:sys.modules.pop(module.__name__,None)
 else:sys.modules[module.__name__]=saved
for name in ['both_roles_have_eagle3','plain_prefill_to_eagle_decode']:
 data=layout.result[name]
 assert data['final_source_pointer_order_matches_expected_origin_order'] and data['final_destination_pointer_order_matches_expected_origin_order']
result=dict(passed=True,cases=len(rows),rows=rows,candidate_native_module_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),native_staging_source_sha256=hashlib.sha256(staging.read_bytes()).hexdigest(),scope='Actual frozen request-plan and pinned head-selection methods with opaque CPU labels and a pointer-container shim; no NumPy memory layout, GPU, NIXL or output equivalence proof.')
(O/'candidate_patch_identity.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,cases=len(rows),candidate_source_pinned=True)))
