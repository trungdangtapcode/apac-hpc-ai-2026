#!/usr/bin/env python3
"""Build fixed native-token inputs offline; never load weights or contact a server."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

REVISION = "e156cb4efae43fbee1a1ab073f946a1377e6b969"
NEUTRAL = {"temperature": 0, "top_k": 1, "top_p": 1, "min_p": 0,
           "repetition_penalty": 1, "frequency_penalty": 0, "presence_penalty": 0, "n": 1}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def verify_assets(model):
    result = {}
    for name in ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt",
                 "config.json", "generation_config.json"):
        raw = (model / name).read_bytes()
        metadata_path = model / ".cache/huggingface/download" / (name + ".metadata")
        metadata = metadata_path.read_text().splitlines()
        require(len(metadata) >= 2 and metadata[0] == REVISION, name + ": revision mismatch")
        etag = metadata[1].strip('"')
        digest = sha(raw) if len(etag) == 64 else hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(digest == etag, name + ": cached content does not match metadata ETag")
        result[name] = {"sha256": sha(raw), "bytes": len(raw), "revision": metadata[0],
                        "cache_etag": etag, "metadata_sha256": sha(metadata_path.read_bytes())}
    return result


def prepare(model, outdir):
    require(not outdir.exists(), "output exists; preserve previous evidence")
    assets = verify_assets(model)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(model), local_files_only=True, trust_remote_code=False)
    config = json.loads((model / "tokenizer_config.json").read_text())
    require(tokenizer.chat_template == config["chat_template"], "resolved chat template differs")
    template = config["chat_template"]
    rows, cases = [], []

    def render(messages):
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
        require(ids == tokenizer.encode(text, add_special_tokens=False), "template/tokenization disagreement")
        require(tokenizer.decode(ids, skip_special_tokens=False, clean_up_tokenization_spaces=False) == text,
                "prompt roundtrip differs")
        require(text.endswith("<|im_start|>assistant\n"), "generation prefix differs")
        return text, ids

    def add(name, messages, cap=200, purpose="token comparison", **extra):
        text, ids = render(messages)
        require(ids and len(ids) + cap <= 8192, name + ": context budget exceeded")
        require(all(type(x) is int and 0 <= x < len(tokenizer) for x in ids), "invalid token ID")
        cases.append({"case_id": name, "request": {"input_ids": ids, "stream": False,
            "return_prompt_token_ids": True, "sampling_params": {**NEUTRAL,
                "max_new_tokens": cap, "min_new_tokens": 0, "ignore_eos": False,
                "skip_special_tokens": True, "no_stop_trim": False}}})
        rows.append({"case_id": name, "messages": messages, "rendered_prompt": text,
            "rendered_prompt_sha256": sha(text.encode()), "input_ids_sha256": sha(encode_json(ids)),
            "input_tokens_including_chat_template": len(ids), "max_new_tokens": cap,
            "purpose": purpose, **extra})

    def user(text):
        return [{"role": "user", "content": text}]

    boundary = user("List the integers from 1 through 30, separated by commas. Do not explain.")
    for cap in (1, 3, 4, 5, 200):
        add(f"draft4-boundary-cap{cap}", boundary, cap, "same prompt around draft_tokens=4; observe actual finish")
    add("eos-probe-ok", user("Reply with exactly OK and nothing else."),
        purpose="EOS candidate; EOS must be observed in runtime, never assumed from this prompt")
    add("vietnamese", user("Giải thích ngắn gọn vì sao bầu trời có màu xanh, bằng hai câu tiếng Việt."))
    add("chinese", user("请用两句话解释为什么天空是蓝色的。"))
    add("code", user("Write a Python function that returns the first index of a value in a sorted list, or -1. Output code only."))
    add("multi-turn", [{"role": "system", "content": "Follow the user's instructions precisely."},
        {"role": "user", "content": "Remember this identifier: cedar-4829."},
        {"role": "assistant", "content": "I will remember cedar-4829."},
        {"role": "user", "content": "Return only the identifier I gave you."}])

    def retrieval(count, position):
        lines = [f"Record {i:04d}: the archive contains ordinary notes about rivers and stones."
                 for i in range(count)]
        index = {"early": 0, "middle": count // 2, "late": count}[position]
        lines.insert(index, "The unique access label for the amber cabinet is MAPLE-7319.")
        return user("Read the archive and return only the access label for the amber cabinet.\n"
                    "<archive>\n" + "\n".join(lines) + "\n</archive>\nAccess label:")

    for target, position in ((3800, "early"), (3800, "middle"), (3800, "late"), (7900, "middle")):
        lo, hi = 0, 1000
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if len(render(retrieval(mid, position))[1]) <= target:
                lo = mid
            else:
                hi = mid - 1
        messages = retrieval(lo, position)
        size = len(render(messages)[1])
        require(target - 40 <= size <= target, "retrieval length outside intended window")
        add(f"retrieval-{target}-{position}", messages, purpose="long context token comparison",
            target_input_tokens=target, needle_position=position, diagnostic_answer="MAPLE-7319")

    suite = {"schema": 1, "target_revision": REVISION,
             "tokenizer_sha256": assets["tokenizer.json"]["sha256"], "cases": cases}
    provenance = {"state": "OFFLINE_INPUTS_ONLY_NO_MODEL_OUTPUT", "target_revision": REVISION,
        "model_path_at_build": str(model), "assets": assets,
        "chat_template_sha256": sha(template.encode()), "tokenizer_class": type(tokenizer).__name__,
        "versions": {x: importlib.metadata.version(x) for x in ("transformers", "tokenizers", "jinja2")},
        "add_generation_prompt": True, "add_special_tokens_after_template": False,
        "eos_token_id": tokenizer.eos_token_id, "case_count": len(cases),
        "sequential_capture_order": [x["case_id"] for x in cases],
        "limits": ["Local cache metadata and content verified; deployment/image/weights still require audit.",
            "EOS probe is not evidence of EOS; require a real stop in control and candidate captures.",
            "No model, GPU, draft compatibility, target token equality, accuracy or speed was tested."]}
    outdir.mkdir()
    files = {"suite.json": encode_json(suite), "prompts.json": encode_json(rows),
             "provenance.json": encode_json(provenance), "chat-template.jinja": template.encode()}
    for name, raw in files.items():
        with (outdir / name).open("xb") as handle:
            handle.write(raw)
    with (outdir / "SHA256SUMS").open("x") as handle:
        handle.writelines(f"{sha(raw)}  {name}\n" for name, raw in files.items())
    print(json.dumps({"state": provenance["state"], "case_count": len(cases),
        "input_tokens": {r["case_id"]: r["input_tokens_including_chat_template"] for r in rows}}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    prepare(args.model_dir, args.outdir)
