"""Strict actual-token and EAGLE3 verification-counter semantics."""
import math
from token_observation import observed as target_observed
COUNTERS=('spec_verify_ct','spec_num_correct_drafts','spec_num_proposed_drafts','spec_accept_rate','spec_accept_length')
def observed(response, prompt_tokens):
    tokens=target_observed(response,prompt_tokens)
    meta=response['meta_info']
    missing=[key for key in COUNTERS if key not in meta]
    if missing: raise ValueError(f'missing native speculative verification metadata: {missing}')
    verify,correct,proposed=(meta[k] for k in COUNTERS[:3])
    rate,length=(meta[k] for k in COUNTERS[3:])
    if type(verify) is not int or verify<=0: raise ValueError('spec_verify_ct must be a positive integer')
    if type(correct) is not int or type(proposed) is not int or not (0<=correct<=proposed): raise ValueError('invalid speculative draft token counts')
    if proposed != 2*verify: raise ValueError('proposed draft count is inconsistent with two-step verification')
    if type(rate) not in (int,float) or not math.isfinite(rate) or not math.isclose(rate,correct/proposed,rel_tol=1e-6,abs_tol=1e-8): raise ValueError('spec_accept_rate is inconsistent with token counts')
    if type(length) not in (int,float) or not math.isfinite(length) or not math.isclose(length,200/verify,rel_tol=1e-6,abs_tol=1e-8): raise ValueError('spec_accept_length is inconsistent with output and verification counts')
    tokens['speculative']={key:meta[key] for key in COUNTERS}
    tokens['speculative']['verification_observed']=True
    return tokens
