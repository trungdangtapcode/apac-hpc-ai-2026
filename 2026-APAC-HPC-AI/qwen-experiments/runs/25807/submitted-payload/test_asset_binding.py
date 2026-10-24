"""CPU tests for immutable model/image verification and token-result binding."""
import hashlib
import http.server
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest

from asset_identity import EXPECTED_REVISION, verify_asset_identity


PROPOSAL = Path(__file__).resolve().parent
CORPUS = json.loads((PROPOSAL / "prepared-corpus.json").read_text())


def make_assets(base):
    model = base / "model"
    model.mkdir(parents=True)
    image = base / "sglang.sqsh"
    image.write_bytes(b"fixture container image")
    names = [f"model-{index:05d}-of-00024.safetensors" for index in range(1, 25)]
    names += ["LICENSE", "README.md", "config.json", "generation_config.json", "merges.txt",
              "model.safetensors.index.json", "tokenizer.json", "tokenizer_config.json", "vocab.json"]
    files = []
    for name in names:
        path = model / name
        path.write_bytes(("fixture:" + name).encode())
        st = path.stat()
        files.append({"path": str(path), "bytes": st.st_size,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
                      "passed": True})
    st = image.stat()
    files.append({"path": str(image), "bytes": st.st_size,
                  "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                  "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
                  "passed": True})
    manifest = {"state": "PASS", "errors": [], "model_revision": EXPECTED_REVISION,
                "expected_files": 34, "expected_bytes": sum(row["bytes"] for row in files),
                "files": files}
    manifest_path = base / "asset-verification.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return model, image, manifest_path, manifest


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AssetBindingTests(unittest.TestCase):
    def test_manifest_binds_model_image_and_small_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            model, image, manifest, _ = make_assets(Path(directory))
            identity = verify_asset_identity(manifest, model, image)
            self.assertEqual(identity["verified_file_count"], 34)
            self.assertEqual(len(identity["verification_manifest_sha256"]), 64)
            rows = identity["files"]
            self.assertEqual(sum(row["runtime_small_file_sha256"] is not None for row in rows), 9)
            self.assertTrue(all(row["full_hash_from_verification_manifest"] for row in rows))

    def test_rejects_nonpass_duplicate_wrong_revision_and_missing_path(self):
        mutations = [
            lambda data: data.update(state="VERIFYING"),
            lambda data: data["files"].append(data["files"][0]),
            lambda data: data.update(model_revision="wrong-revision"),
            lambda data: data["files"].pop(),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as directory:
                model, image, manifest_path, manifest = make_assets(Path(directory))
                data = json.loads(json.dumps(manifest))
                mutate(data)
                manifest_path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    verify_asset_identity(manifest_path, model, image)

    def test_rejects_runtime_size_metadata_hash_and_stale_weight_fingerprint(self):
        for target in ("size", "metadata", "weight", "image-path"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                model, image, manifest_path, _ = make_assets(Path(directory))
                if target == "size":
                    (model / "model-00001-of-00024.safetensors").write_bytes(b"different size")
                elif target == "metadata":
                    (model / "config.json").write_bytes(b"tampered metadata")
                elif target == "image-path":
                    image = Path(directory) / "other-image.sqsh"
                    image.write_bytes(b"different image")
                else:
                    weight = model / "model-00001-of-00024.safetensors"
                    st = weight.stat()
                    os.utime(weight, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
                with self.assertRaises(ValueError):
                    verify_asset_identity(manifest_path, model, image)

    def test_actual_client_and_head_checker_bind_all_1600_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            model, image, manifest, _ = make_assets(base)
            bundle = base / "bundle"
            bundle.mkdir()
            for name in ("token-control.py", "check-token-result.py", "token_observation.py",
                         "asset_identity.py", "prepared-corpus.json"):
                shutil.copy2(PROPOSAL / name, bundle / name)
            shutil.copy2(manifest, bundle / "asset-verification.json")
            artifact = base / "artifact"
            artifact.mkdir()

            class Handler(http.server.BaseHTTPRequestHandler):
                completion_count = 200

                def do_POST(self):
                    request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                    tokens = self.completion_count
                    body = {"meta_info": {
                        "completion_tokens": tokens,
                        "output_token_logprobs": [[-0.1, (index + 10) % 151936, "fixture"]
                                                   for index in range(tokens)],
                        "prompt_tokens": len(request["input_ids"]),
                        "finish_reason": {"type": "length"}}}
                    raw = json.dumps(body).encode()
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)

                def log_message(self, *_):
                    pass

            class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
                daemon_threads = True

            server = Server(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                env = dict(os.environ, QWEN_EXPERIMENT_ID="asset-binding-fixture",
                           QWEN_CLIENT_DEADLINE_EPOCH=str(__import__("time").time() + 30),
                           QWEN_IMAGE_PATH=str(image))
                client = subprocess.run([sys.executable, str(bundle / "token-control.py"),
                                         f"127.0.0.1:{server.server_port}", str(model), str(artifact)],
                                        env=env, capture_output=True, text=True, timeout=20)
                self.assertEqual(client.returncode, 0, client.stderr + client.stdout)
                result_path = artifact / "target-reference.json"
                result = json.loads(result_path.read_text())
                self.assertEqual(sum(len(row["observed"]["output_ids"])
                                     for stage in result["stages"].values() for row in stage), 1600)
                checker = subprocess.run([sys.executable, str(bundle / "check-token-result.py"),
                                          str(result_path), str(model)], env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(checker.returncode, 0, checker.stderr + checker.stdout)

                changed = json.loads(result_path.read_text())
                changed["asset_identity"]["verification_manifest_sha256"] = "0" * 64
                result_path.write_text(json.dumps(changed))
                rejected = subprocess.run([sys.executable, str(bundle / "check-token-result.py"),
                                           str(result_path), str(model)], env=env, capture_output=True, text=True, timeout=10)
                self.assertNotEqual(rejected.returncode, 0)

                Handler.completion_count = 199
                short_artifact = base / "short-artifact"
                short_artifact.mkdir()
                short = subprocess.run([sys.executable, str(bundle / "token-control.py"),
                                        f"127.0.0.1:{server.server_port}", str(model), str(short_artifact)],
                                       env=env, capture_output=True, text=True, timeout=20)
                self.assertNotEqual(short.returncode, 0)
                self.assertIn("all 200 actual output IDs", (short_artifact / "target-reference.json").read_text())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
