import tempfile
import unittest
from pathlib import Path

from audit_capacity import ROLES, audit


class CapacityAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.artdir = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write_role(self, role, policy="auto", args_overrides=None, scheduler_caps=None,
                   scheduler=True):
        expected = ROLES[role]
        backend = "None" if policy == "auto" else "'disabled'"
        phase_backend = ("disabled" if policy == "disabled" or role == "decode-0" else "breakable")
        values = {
            "dtype": "'bfloat16'",
            "max_running_requests": str(expected["max_running_requests"]),
            "tp_size": str(expected["tp_size"]),
            "ep_size": str(expected["ep_size"]),
            "chunked_prefill_size": "8192",
            "moe_runner_backend": repr(expected["moe_runner_backend"]),
            "disaggregation_mode": repr("decode" if role == "decode-0" else "prefill"),
            "cuda_graph_backend_prefill": backend,
            "disable_prefill_cuda_graph": "False",
            "speculative_algorithm": "None",
            "speculative_draft_model_path": "None",
            "speculative_num_steps": "None",
            "speculative_eagle_topk": "None",
            "speculative_num_draft_tokens": "None",
            "enable_multi_layer_eagle": "False",
        }
        values.update(args_overrides or {})
        fields = ", ".join(f"{key}={value}" for key, value in values.items())
        graph = (
            "cuda_graph_config=CudaGraphConfig("
            f"prefill=PhaseConfig(backend='{phase_backend}', max_bs=8192, bs=[64]))"
        )
        lines = [f"[t] server_args=ServerArgs({fields}, {graph})"]
        if scheduler:
            caps = scheduler_caps or [expected["max_running_requests"]]
            lines.extend(
                f"[t] max_total_num_tokens=100000, chunked_prefill_size=8192, max_running_requests={cap}, context_len=8192"
                for cap in caps
            )
        (self.artdir / f"{role}.log").write_text("\n".join(lines) + "\n")

    def write_all(self, policy="auto", **kwargs):
        for role in ROLES:
            self.write_role(role, policy=policy, **kwargs)

    def test_accepts_initialized_auto_policy_for_all_roles(self):
        self.write_all("auto")
        result = audit(self.artdir, "auto")
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(set(result["roles"]), set(ROLES))

    def test_accepts_explicit_disabled_policy_for_all_roles(self):
        self.write_all("disabled")
        result = audit(self.artdir, "disabled")
        self.assertTrue(result["passed"], result["errors"])


    def test_auto_decode_uses_source_role_default_disabled(self):
        self.write_all("auto")
        path = self.artdir / "decode-0.log"
        path.write_text(path.read_text().replace("backend='disabled'", "backend='breakable'"))
        result = audit(self.artdir, "auto")
        self.assertFalse(result["passed"])
        self.assertTrue(any("decode-0: initialized prefill graph config backend='breakable', expected 'disabled'" in item for item in result["errors"]))

    def test_missing_role_is_reported(self):
        for role in list(ROLES)[:-1]:
            self.write_role(role)
        result = audit(self.artdir, "auto")
        self.assertFalse(result["passed"])
        self.assertTrue(any("decode-0: missing role log" in item for item in result["errors"]))

    def test_malformed_server_args_is_reported(self):
        self.write_all()
        path = self.artdir / "prefill-0.log"
        path.write_text(path.read_text().replace("dtype='bfloat16'", "dtype=not-a-literal"))
        result = audit(self.artdir, "auto")
        self.assertFalse(result["passed"])
        self.assertTrue(any("malformed ServerArgs value for dtype" in item for item in result["errors"]))

    def test_contradictory_scheduler_receipts_are_reported(self):
        self.write_all()
        self.write_role("prefill-1", scheduler_caps=[64, 63])
        result = audit(self.artdir, "auto")
        self.assertFalse(result["passed"])
        self.assertTrue(any("does not uniquely equal 64" in item for item in result["errors"]))

    def test_no_logs_fails_for_every_role(self):
        result = audit(self.artdir, "auto")
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["errors"]), len(ROLES))

    def test_uninitialized_server_args_do_not_pass(self):
        self.write_all()
        self.write_role("decode-0", scheduler=False)
        result = audit(self.artdir, "auto")
        self.assertFalse(result["passed"])
        self.assertTrue(any("decode-0: no initialized scheduler capacity receipt" in item for item in result["errors"]))


    def test_literal_auto_is_rejected_as_server_args_backend(self):
        self.write_all()
        path = self.artdir / "prefill-0.log"
        path.write_text(path.read_text().replace("cuda_graph_backend_prefill=None", "cuda_graph_backend_prefill='auto'"))
        result = audit(self.artdir, "auto")
        self.assertFalse(result["passed"])
        self.assertTrue(any("cuda_graph_backend_prefill='auto'" in item for item in result["errors"]))

    def test_missing_server_arg_fails_closed(self):
        self.write_all()
        path = self.artdir / "prefill-0.log"
        path.write_text(path.read_text().replace(", ep_size=1", ""))
        result = audit(self.artdir, "auto")
        self.assertFalse(result["passed"])
        self.assertTrue(any("ServerArgs field ep_size" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
