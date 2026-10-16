"""Synthetic CPU checks; these are NOT Qwen model outputs."""
import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SCRIPT = ROOT / 'nscc-pbs/research-next/eagle3-01/review-token-pairs.py'
spec = importlib.util.spec_from_file_location('pairs', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sample = {'schema': 1, 'target_revision': module.TARGET_REVISION,
          'tokenizer_sha256': 'a' * 64, 'cases': [{
              'case_id': 'synthetic-length',
              'request': {'input_ids': [11, 22], 'stream': False,
                          'return_prompt_token_ids': True,
                          'sampling_params': dict(module.NEUTRAL, max_new_tokens=2,
                            min_new_tokens=0, ignore_eos=False, skip_special_tokens=True,
                            no_stop_trim=False)},
              'response': {'prompt_token_ids': [11, 22], 'output_ids': [31, 32],
                           'text': 'SYNTHETIC', 'meta_info': {'prompt_tokens': 2,
                               'completion_tokens': 2, 'finish_reason': {'type': 'length', 'length': 2}}}}]}
checks = []


def test(name, mutate=None, expected='INVALID_OR_INCOMPLETE_CAPTURE'):
    candidate = copy.deepcopy(sample)
    if mutate:
        mutate(candidate)
    try:
        state = module.compare(sample, candidate)['state']
    except (ValueError, TypeError, KeyError):
        state = 'INVALID_OR_INCOMPLETE_CAPTURE'
    checks.append({'name': name, 'expected': expected, 'observed': state, 'pass': state == expected})


def req(c): return c['cases'][0]['request']
def resp(c): return c['cases'][0]['response']
def meta(c): return resp(c)['meta_info']


test('identical', expected='CAPTURED_CASES_MATCH')
test('text_not_used_for_ids', lambda c: resp(c).update(text='different rendering'), 'CAPTURED_CASES_MATCH')
test('same_text_different_id', lambda c: resp(c).update(output_ids=[31, 99]), 'CAPTURED_CASES_DIFFER')
test('finish_reason_difference', lambda c: meta(c).update(finish_reason={'type': 'stop', 'matched': 32}), 'CAPTURED_CASES_DIFFER')
test('empty_cases', lambda c: c.update(cases=[]))
test('duplicate_case', lambda c: c['cases'].append(copy.deepcopy(c['cases'][0])))
test('case_set_mismatch', lambda c: c['cases'][0].update(case_id='other'))
test('revision_mismatch', lambda c: c.update(target_revision='wrong'))
test('tokenizer_mismatch', lambda c: c.update(tokenizer_sha256='b' * 64))
test('missing_output_ids', lambda c: resp(c).pop('output_ids'))
test('boolean_token_id', lambda c: resp(c).update(output_ids=[True, 32]))
test('negative_token_id', lambda c: resp(c).update(output_ids=[-1, 32]))
test('missing_prompt_ids', lambda c: resp(c).pop('prompt_token_ids'))
test('changed_prompt_ids', lambda c: resp(c).update(prompt_token_ids=[11, 23]))
test('missing_finish', lambda c: meta(c).update(finish_reason=None))
test('aborted_response', lambda c: meta(c).update(finish_reason={'type': 'abort'}))
test('response_error', lambda c: resp(c).update(error='synthetic failure'))
test('count_mismatch', lambda c: meta(c).update(completion_tokens=1))
test('premature_length', lambda c: (resp(c).update(output_ids=[31]), meta(c).update(completion_tokens=1)))
test('non_greedy', lambda c: req(c)['sampling_params'].update(temperature=0.7))
test('non_neutral', lambda c: req(c)['sampling_params'].update(repetition_penalty=1.1))
test('grammar_rejected', lambda c: req(c)['sampling_params'].update(regex='.*'))
test('logit_bias_rejected', lambda c: req(c)['sampling_params'].update(logit_bias={'31': 100}))
test('stream_rejected', lambda c: req(c).update(stream=True))
test('prompt_count_mismatch', lambda c: meta(c).update(prompt_tokens=99))
test('request_difference', lambda c: req(c)['sampling_params'].update(ignore_eos=True))

# Valid unequal tails and EOS are compared without stripping a token or retokenizing text.
early = copy.deepcopy(sample)
resp(early).update(output_ids=[31])
meta(early).update(completion_tokens=1, finish_reason={'type': 'stop', 'matched': 31})
report = module.compare(sample, early)
checks.append({'name': 'shorter_stop_tail_preserved', 'pass': report['state'] == 'CAPTURED_CASES_DIFFER'
               and report['cases'][0]['first_difference_index'] == 1})
checks.append({'name': 'eos_capture_self_match', 'pass': module.compare(early, early)['state'] == 'CAPTURED_CASES_MATCH'})

for role in ('control', 'candidate'):
    (OUT / ('synthetic-' + role + '.json')).write_text(json.dumps(sample, indent=2) + '\n')
args = [sys.executable, str(SCRIPT), str(OUT/'synthetic-control.json'),
        str(OUT/'synthetic-candidate.json'), '--out', str(OUT/'synthetic-cli-report.json')]
p = subprocess.run(args, capture_output=True, text=True)
checks.append({'name': 'cli_identical', 'pass': p.returncode == 0 and p.stdout.strip() == 'CAPTURED_CASES_MATCH'})
before = (OUT/'synthetic-cli-report.json').read_bytes()
p = subprocess.run(args, capture_output=True, text=True)
checks.append({'name': 'cli_refuses_overwrite', 'pass': p.returncode != 0 and
               (OUT/'synthetic-cli-report.json').read_bytes() == before})

srt = Path('sgl-workspace/sglang/python/sglang/srt')
manager = (OUT/'api-source'/srt/'managers/tokenizer_manager.py').read_text()
http = (OUT/'http-source'/srt/'entrypoints/http_server.py').read_text()
detok = (OUT/'http-source'/srt/'managers/detokenizer_manager.py').read_text()
io = (OUT/'api-source'/srt/'managers/io_struct.py').read_text()
sampling = (OUT/'api-source'/srt/'sampling/sampling_params.py').read_text()
source_checks = {
    'native_nonstream_returns_manager_payload': 'return orjson_response(ret)' in http,
    'normal_text_path_has_output_ids': '"text": state.get_text(),\n                        "output_ids": state.output_ids.copy(),' in manager,
    'detokenizer_preserves_scheduler_ids': 'output_ids=recv_obj.output_ids,' in detok,
    'prompt_ids_from_tokenized_input': 'state.prompt_token_ids = list(tokenized_obj.input_ids)' in manager,
    'request_prompt_token_option': 'return_prompt_token_ids: bool = False' in io,
    'temperature_zero_becomes_greedy_topk1': 'if 0 <= self.temperature < _SAMPLING_EPS:' in sampling and 'self.top_k = 1' in sampling,
}
for folder in ('api-source', 'http-source'):
    for path in (OUT/folder).rglob('*.py'):
        ast.parse(path.read_text())
files = {str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest()
         for folder in ('api-source', 'http-source') for p in sorted((OUT/folder).rglob('*.py'))}
result = {'kind': 'SYNTHETIC_CPU_AND_STATIC_SOURCE_ONLY_NO_MODEL_EXECUTION',
          'tests': checks, 'test_count': len(checks), 'source_checks': source_checks,
          'source_files_sha256': files, 'tool_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
          'all_pass': all(c['pass'] for c in checks) and all(source_checks.values()),
          'limits': ['Actual /generate HTTP capture and EAGLE3 runtime are unvalidated.',
                     'The sources were extracted from the local image with two CPUs; no full image rehash or remote image check.']}
(OUT/'token-review-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
assert result['all_pass']
