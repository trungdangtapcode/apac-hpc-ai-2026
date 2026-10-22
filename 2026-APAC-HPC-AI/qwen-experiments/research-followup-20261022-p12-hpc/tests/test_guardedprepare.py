import importlib.util
import hashlib
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("guardedprepare", HERE / "guardedprepare.py")
gp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gp)


class PlacementTests(unittest.TestCase):
    def test_control_is_two_tp4_prefills_and_tp8_decode(self):
        gp.validate_placement(gp.DESTS["s32-h200-p8d8-current-n60-screen"]["placement"], 2, 8)

    def test_candidate_is_three_tp4_prefills_and_tp4ep4_decode(self):
        gp.validate_placement(gp.DESTS["s33-h200-p12d4-hpc-n60-screen"]["placement"], 3, 4)
        self.assertEqual(gp.DESTS["s33-h200-p12d4-hpc-n60-screen"]["placement"],
                         "prefill-0\t0\t4\t30100\t9000\nprefill-1\t0\t4\t30101\t9001\nprefill-2\t1\t4\t30102\t9002\ndecode-0\t1\t4\t30200\t0\n")

    def test_rejects_overfull_node(self):
        bad = "prefill-0\t0\t4\t30100\t31100\nprefill-1\t0\t4\t30101\t31101\nprefill-2\t0\t4\t30102\t31102\ndecode-0\t1\t4\t30200\t0\n"
        with self.assertRaisesRegex(ValueError, "eight GPUs"):
            gp.validate_placement(bad, 3, 4)

    def test_cpu_task_shape_is_eight_cpus_per_gpu_within_node_limit(self):
        rows = gp.parse_placement(gp.DESTS["s33-h200-p12d4-hpc-n60-screen"]["placement"])
        cpu_by_node = {}
        for _name, node, tp, _port, _bootstrap in rows:
            cpu_by_node[node] = cpu_by_node.get(node, 0) + tp * 8
        self.assertEqual(cpu_by_node, {0: 64, 1: 64})

    def test_actual_launchers_are_role_count_generic(self):
        source = gp.SOURCE
        topology = (source / "topology-job.sh").read_text()
        warmup = (source / "warm-topology.py").read_text()
        worker = (source / "worker.sh").read_text()
        self.assertIn('done <"$BUNDLE/placement.tsv"', topology)
        self.assertIn("itertools.product(p_workers, d_workers)", warmup)
        self.assertIn('if [[ $role == prefill ]]; then', topology)
        self.assertIn('extra=(--ep-size "$tp" --max-running-requests 256)', topology)
        self.assertIn("--moe-runner-backend hpc_ops", worker)
        self.assertIn("--chunked-prefill-size 8192 --moe-runner-backend deep_gemm", worker)
        self.assertNotIn("CUDA_VISIBLE_DEVICES=0,1,2,3", topology + worker)

    def test_p12_equal_tp_uses_full_pool_descriptor_builder(self):
        nixl = (HERE / "proposals/s33-h200-p12d4-hpc-n60-screen/nixl-conn.py").read_text()
        self.assertIn("peer_info.decode_tp_size == self.attn_tp_size", nixl)
        self.assertIn("self._init_equal_tp_prep_handle(", nixl)
        self.assertIn("n = num_slots if num_slots is not None else (data_len // item_len)", nixl)
        self.assertIn("np.arange(n, dtype=np.uint64) * np.uint64(item_len) + base_ptr", nixl)
        self.assertIn("np.vstack(arrays)", nixl)
        self.assertIn("self._init_hetero_tp_prep_handle(", nixl)

    def test_prepared_proposals_are_matched_short_screen_drafts(self):
        proposals = HERE / "proposals"
        if not proposals.exists():
            self.skipTest("guardedprepare.py has not produced draft proposals")
        control = proposals / "s32-h200-p8d8-current-n60-screen"
        candidate = proposals / "s33-h200-p12d4-hpc-n60-screen"
        for path in (control, candidate):
            self.assertTrue(path.is_dir())
            config = json.loads((path / "config.json").read_text())
            self.assertEqual(config["concurrency"], [60])
            self.assertEqual((config["screen_warmup_s"], config["screen_measure_s"], config["grace_s"]), (20, 40, 30))
            self.assertEqual(config["decode_extra_flags"], ["--flashinfer-allreduce-fusion-backend", "mnnvl", "--decode-attention-backend", "flashinfer", "--moe-runner-backend", "hpc_ops"])
            bench = (path / "benchmark.sh").read_text()
            self.assertIn('run_benchmark "$N" screen 20 40', bench)
            self.assertIn("r['phase']=='screen'", bench)
            self.assertFalse(config["diagnostic_profile"])
        self.assertEqual((control / "benchmark.sh").read_bytes(), (candidate / "benchmark.sh").read_bytes())
        self.assertEqual((control / "worker.sh").read_bytes(), (candidate / "worker.sh").read_bytes())
        self.assertEqual((control / "topology-job.sh").read_bytes(), (candidate / "topology-job.sh").read_bytes())
        self.assertNotEqual((control / "placement.tsv").read_bytes(), (candidate / "placement.tsv").read_bytes())
        # Source inventory is retained as provenance, not as a draft manifest.
        self.assertTrue((candidate / "SOURCE_SHA256SUMS").is_file())
        self.assertFalse((candidate / "SHA256SUMS").exists())
        expected = next(line.split()[0] for line in (candidate / "SOURCE_SHA256SUMS").read_text().splitlines()
                        if line.split(None, 1)[1].strip() == "benchmark.sh")
        actual = hashlib.sha256((candidate / "benchmark.sh").read_bytes()).hexdigest()
        self.assertNotEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
