"""Static source evidence only: no model, torch import or GPU execution."""
import ast,datetime,hashlib,json
from pathlib import Path
out=Path(__file__).resolve().parent
srt=Path('sgl-workspace/sglang/python/sglang/srt')
sources={name:(out/'image-source'/srt/'speculative'/name).read_text() for name in ['eagle_utils.py','eagle_worker_common.py','spec_utils.py']}
tree=ast.parse(sources['eagle_utils.py'])
sample=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='eagle_sample')
greedy=next(n for n in sample.body if isinstance(n,ast.If) and 'is_all_greedy' in ast.unparse(n.test))
greedy_text='\n'.join(ast.unparse(n) for n in greedy.body)
sampling_text='\n'.join(ast.unparse(n) for n in greedy.orelse)
dispatch=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_tree_greedy_func')
sim=next(n for n in sample.body if isinstance(n,ast.If) and ast.unparse(n.test)=='SIMULATE_ACC_LEN > 0')
hook=(out/'image-source'/srt/'arg_groups/speculative_hook.py').read_text()
env=(out/'runner-source'/srt/'environ.py').read_text()
checks={
 'greedy_uses_target_argmax':'torch.argmax(next_token_logits, dim=-1)' in greedy_text,
 'greedy_calls_verify_tree':'verify_tree_greedy_func' in greedy_text,
 'greedy_no_accept_threshold_arguments':'threshold' not in greedy_text,
 'sampling_has_both_thresholds':all(x in sampling_text for x in ['speculative_accept_threshold_single','speculative_accept_threshold_acc']),
 'cuda_dispatches_compiled_sgl_kernel':'from sgl_kernel import verify_tree_greedy' in ast.unparse(dispatch),
 'target_forward_precedes_sample':sources['eagle_worker_common.py'].index('forward_batch_output = target_worker.forward_batch_generation(')<sources['eagle_worker_common.py'].index(') = eagle_sample('),
 'target_forward_is_verify':'is_verify=True' in sources['eagle_worker_common.py'],
 'simulation_after_real_verify':sim.lineno>greedy.end_lineno and 'generate_simulated_accept_index' in ast.unparse(sim),
 'simulation_can_replace_tokens':'predict.fill_(100)' in sources['spec_utils.py'] and 'predict[draft_node_indices] = candidates' in sources['spec_utils.py'],
 'simulation_default_off':'SGLANG_SIMULATE_ACC_LEN = EnvFloat(-1)' in env,
 'hook_default_max_running_48':'server_args.max_running_requests = 48' in hook,
 'topk1_forces_steps_plus_one':'server_args.speculative_num_draft_tokens = server_args.speculative_num_steps + 1' in hook,
}
files={str(p.relative_to(out)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for directory in ('image-source','kernel-source','runner-source') for p in sorted((out/directory).rglob('*.py'))}
old=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2007UTC/image-source')/srt/'server_args.py'
fresh=out/'runner-source'/srt/'server_args.py'
assert fresh.read_bytes()==old.read_bytes()
result={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'STATIC_IMAGE_SOURCE_REVIEW_NOT_GPU_VALIDATION','source_image':'/scratch/enroot-images/sglang-harbor.sqsh','observed_image_bytes':Path('/scratch/enroot-images/sglang-harbor.sqsh').stat().st_size,'extraction_processors':2,'full_image_rehash_this_wake':False,'fresh_server_args_matches_prior_hashed_source':True,'checks':checks,'all_static_checks_pass':all(checks.values()),'line_ranges':{'eagle_utils.py:greedy':[greedy.lineno,greedy.end_lineno],'eagle_utils.py:simulation':[sim.lineno,sim.end_lineno],'eagle_utils.py:dispatcher':[dispatch.lineno,dispatch.end_lineno]},'files':files,'limits':['CUDA branch calls compiled sgl_kernel.verify_tree_greedy; compiled execution not tested. Triton fallback source is not proof of the CUDA path.','No draft weights downloaded; Instruct-2507 acceptance/compatibility, memory and output identity unverified.','FP8 numerics, batching and verification kernels can differ from nonspeculative decoding; source call flow does not prove bitwise equality.','Thresholds1.0 retained, but no claim of stochastic distribution equivalence; first experiment restricted to all-greedy requests with neutral penalties and no grammar.']}
(out/'eagle-source-review.json').write_text(json.dumps(result,indent=2)+'\n')
assert all(checks.values()),checks
print(json.dumps({'static_checks':len(checks),'passed':all(checks.values()),'source_files_hashed':len(files)}))
