"""Normalize a single tokenizer sequence before retaining or serializing it."""
from collections.abc import Mapping

def token_ids(value):
    if isinstance(value, Mapping):
        value=value['input_ids']
    if not isinstance(value,list) or not value:
        raise ValueError('Require a nonempty plain list of token IDs')
    if any(type(t) is not int or not 0<=t<151936 for t in value):
        raise ValueError('Require one unbatched sequence of valid target integer IDs')
    return list(value)
