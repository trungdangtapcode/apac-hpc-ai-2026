#!/usr/bin/env python3
"""CPU protocol integrity tests; never calls an inference endpoint or claims model quality."""
from __future__ import annotations

import hashlib
import json
import random
import unittest
from collections import Counter
from pathlib import Path

import eval_client

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "dataset"


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class ParserTests(unittest.TestCase):
    def test_valid_final_letter_forms(self):
        self.assertEqual(eval_client.strict_answer("reasoning. The answer is (B)"), "B")
        self.assertEqual(eval_client.strict_answer("the answer is (j)."), "J")
        self.assertEqual(eval_client.strict_answer("**The answer is (A)**"), "A")

    def test_malformed_or_ambiguous_outputs_are_invalid(self):
        for text in (None, "", "Answer: C", "The answer is K", "The answer is C",
                     "The answer is (C), maybe D", "The answer is (A). Then the answer is (B)"):
            with self.subTest(text=text):
                self.assertIsNone(eval_client.strict_answer(text))


class PinnedSglangApiTests(unittest.TestCase):
    def test_pinned_image_route_and_schema_source(self):
        source = ROOT / "pinned-sglang"
        server = (source / "http_server.py").read_text(encoding="utf-8")
        protocol = (source / "protocol.py").read_text(encoding="utf-8")
        tokenize = (source / "serving_tokenize.py").read_text(encoding="utf-8")
        self.assertIn('"/v1/tokenize"', server)
        self.assertIn("async def openai_v1_tokenize", server)
        self.assertIn("request: TokenizeRequest", server)
        self.assertIn("class TokenizeRequest(BaseModel)", protocol)
        self.assertIn("prompt: Optional[Union[str, List[str]]] = None", protocol)
        self.assertIn("messages: Optional[List[ChatCompletionMessageParam]] = None", protocol)
        self.assertIn("Exactly one of 'prompt' or 'messages' must be provided.", protocol)
        self.assertIn("class TokenizeResponse(BaseModel)", protocol)
        self.assertIn("tokens: Union[List[int], List[List[int]]]", protocol)
        self.assertIn("count: Union[int, List[int]]", protocol)
        self.assertIn("max_model_len: int", protocol)
        self.assertIn("if request.messages is not None:", tokenize)
        self.assertIn("self._tokenize_chat_request(request)", tokenize)
        self.assertIn("tokens=tokens, count=count, max_model_len=max_model_len", tokenize)
        self.assertIn("self._router.start()", (source / "router.py").read_text(encoding="utf-8"))
        gateway_http = (source / "gateway/http_router.rs").read_text(encoding="utf-8")
        gateway_tokenize = (source / "gateway/tokenize_handlers.rs").read_text(encoding="utf-8")
        self.assertIn('"/v1/chat/completions"', gateway_http)
        self.assertNotIn("route_tokenize", gateway_http)
        self.assertIn("request.prompt.as_strings()", gateway_tokenize)
        self.assertIn("char_count", gateway_tokenize)
        self.assertNotIn("max_model_len", gateway_tokenize)

    def test_offline_chat_rendering_and_token_ids(self):
        messages = [{"role": "user", "content": "one exact prompt"}]
        body = {"model": "Qwen/Qwen3-235B-A22B-Instruct-2507", "messages": messages}
        self.assertEqual(set(body), {"model", "messages"})
        class PinnedTemplateFixture:
            def apply_chat_template(self, wire_messages, *, tokenize, add_generation_prompt):
                self.seen = (wire_messages, tokenize, add_generation_prompt)
                return [101, 102, 103]
        fixture = PinnedTemplateFixture()
        tokens = eval_client.tokenize_wire_messages(fixture, messages)
        self.assertEqual(tokens, [101, 102, 103])
        self.assertEqual(fixture.seen, (messages, True, True))
        class InvalidFixture:
            def apply_chat_template(self, *_args, **_kwargs):
                return [True]
        with self.assertRaises(ValueError):
            eval_client.tokenize_wire_messages(InvalidFixture(), messages)


class FrozenCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
        cls.prompts = read_jsonl(DATA / "screen-128.jsonl")
        cls.demos = read_jsonl(DATA / "validation-5-per-category.jsonl")
        cls.provenance = json.loads((ROOT / "source-provenance.json").read_text(encoding="utf-8"))

    def test_raw_dataset_hashes_and_license_metadata(self):
        self.assertEqual(self.manifest["dataset_revision"], self.provenance["dataset"]["revision"])
        self.assertEqual(self.manifest["dataset_license"], "MIT")
        for name, row in self.manifest["source_files"].items():
            path = DATA / "source" / name
            self.assertEqual(path.stat().st_size, row["bytes"])
            self.assertEqual(file_sha(path), row["sha256"])

    def test_fixed_stratification_and_demo_ids(self):
        self.assertEqual(len(self.prompts), 128)
        self.assertEqual(len({row["question_id"] for row in self.prompts}), 128)
        self.assertEqual(len(self.demos), 70)
        self.assertEqual(Counter(row["category"] for row in self.prompts), self.manifest["category_quotas"])
        self.assertEqual(Counter(row["category"] for row in self.demos), {c: 5 for c in self.manifest["categories"]})
        by_category = {c: [r["question_id"] for r in self.demos if r["category"] == c]
                       for c in self.manifest["categories"]}
        self.assertEqual(by_category, self.manifest["validation_fewshot_ids_by_category"])

    def test_prompt_hashes_and_generation_isolation(self):
        for row in self.prompts:
            self.assertEqual(hashlib.sha256(row["prompt"].encode("utf-8")).hexdigest(), row["prompt_sha256"])
            final_query = row["prompt"].rsplit("Question:\n", 1)[-1]
            self.assertTrue(final_query.rstrip().endswith("Answer: Let's think step by step."))
        screen_bytes = (DATA / "screen-128.jsonl").read_bytes()
        demo_bytes = (DATA / "validation-5-per-category.jsonl").read_bytes()
        self.assertEqual(hashlib.sha256(screen_bytes).hexdigest(), self.manifest["screen_jsonl_sha256"])
        self.assertEqual(hashlib.sha256(demo_bytes).hexdigest(), self.manifest["validation_jsonl_sha256"])

    def test_tokenizer_config_and_chat_template_hashes(self):
        config_path = ROOT / "upstream/tokenizer_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        tokenizer = self.provenance["target_model_tokenizer"]
        self.assertEqual(file_sha(config_path), tokenizer["tokenizer_config_json_sha256"])
        template_hash = hashlib.sha256(config["chat_template"].encode("utf-8")).hexdigest()
        self.assertEqual(template_hash, tokenizer["chat_template_sha256_utf8"])
        self.assertEqual(tokenizer["model_variant"], "Qwen3-235B-A22B-Instruct-2507-FP8")

    def test_deterministic_sample_selection_algorithm(self):
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            self.skipTest("PyArrow 19.0.1 is only required to regenerate the sample from raw parquet")
        source_rows = pq.read_table(DATA / "source/test-00000-of-00001.parquet").to_pylist()
        groups = {category: [] for category in self.manifest["categories"]}
        for idx, source in enumerate(source_rows):
            groups[source["category"]].append((idx, source["question_id"]))
        categories = self.manifest["categories"]
        rng = random.Random(2026)
        extras = set(rng.sample(categories, 2))
        expected = []
        quotas = {}
        for index, category in enumerate(categories):
            rows = list(groups[category])
            random.Random(2026 + index).shuffle(rows)
            quota = 9 + int(category in extras)
            quotas[category] = quota
            expected.extend(qid for _row_index, qid in rows[:quota])
        actual = [row["question_id"] for row in self.prompts]
        self.assertEqual(actual, expected)
        self.assertEqual(quotas, self.manifest["category_quotas"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
