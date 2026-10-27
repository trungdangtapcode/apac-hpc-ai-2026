"""Independent semantics for SGLang target output-token observations."""
VOCAB = 151936


def observed(response, expected_prompt_tokens):
    if not isinstance(response, dict) or not isinstance(response.get("meta_info"), dict):
        raise ValueError("response must contain meta_info")
    meta = response["meta_info"]
    count, rows = meta.get("completion_tokens"), meta.get("output_token_logprobs")
    if type(count) is not int or count != 200 or not isinstance(rows, list) or len(rows) != count:
        raise ValueError("require all 200 actual output IDs, including the first token")
    if type(meta.get("prompt_tokens")) is not int or meta["prompt_tokens"] != expected_prompt_tokens:
        raise ValueError("prompt length changed")
    if any(not isinstance(row, list) or len(row) != 3 or type(row[1]) is not int
           or not 0 <= row[1] < VOCAB for row in rows):
        raise ValueError("missing or invalid actual target-vocabulary token IDs")
    finish = meta.get("finish_reason")
    if not isinstance(finish, dict) or finish.get("type") != "length":
        raise ValueError("unexpected or missing finish reason")
    return {"output_ids": [row[1] for row in rows], "finish_reason": finish}
