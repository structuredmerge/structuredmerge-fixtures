import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import check_cli_contract as gate


class CLIContractTest(unittest.TestCase):
    def setUp(self):
        (gate.ROOT / "tmp").mkdir(exist_ok=True)
        self.scratch = tempfile.TemporaryDirectory(prefix="cli-runner-tests-", dir=gate.ROOT / "tmp")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.manifest = json.loads(gate.MANIFEST.read_text())

    def run_script(self, script, expect, timeout=2):
        result = gate.run_case([sys.executable, "-c", script],
            {"id": "test", "argv": [], "expect": expect}, {"source.txt": "original\n"}, self.root, timeout)
        self.assertEqual(list(self.root.iterdir()), [], "case directory must be cleaned")
        return result

    def test_manifest_validates(self):
        gate.validate(self.manifest)

    def test_rejects_unsafe_files_duplicates_and_empty_suite(self):
        for mutation in (lambda m: m["files"].update({"../escape": "text"}),
                         lambda m: m["cases"].append(m["cases"][0]),
                         lambda m: m.update(cases=[]),
                         lambda m: m.update(full_cli_conformance=True)):
            manifest = copy.deepcopy(self.manifest)
            mutation(manifest)
            with self.assertRaises(ValueError):
                gate.validate(manifest)

    def test_real_success_and_exact_raw_output(self):
        result = self.run_script("print('hello')", {"exit_code": 0, "stdout_contains": ["hello"]})
        self.assertTrue(result["passed"])
        self.assertEqual(result["raw"]["stdout"]["base64"], "aGVsbG8K")

    def test_wrong_exit_and_mutated_input_are_both_failures(self):
        result = self.run_script("from pathlib import Path; Path('source.txt').write_text('changed')",
            {"exit_code": 2})
        self.assertEqual(set(result["errors"]), {"filesystem_changed", "exit_code"})

    def test_invalid_json_is_not_version_success(self):
        result = self.run_script("print('version 1')", {"exit_code": 0, "stdout_json": {"schema": "version"}})
        self.assertIn("invalid_json", result["errors"])

    def test_timeout_and_cleanup(self):
        result = self.run_script("import time; time.sleep(60)", {"exit_code": 0}, timeout=0.05)
        self.assertIn("timeout", result["errors"])

    def test_excessive_output_is_bounded_and_fails(self):
        result = self.run_script("print('x' * 300000)", {"exit_code": 0})
        self.assertIn("output_budget", result["errors"])
        self.assertTrue(result["raw"]["stdout"]["truncated"])
        self.assertLessEqual(len(result["stdout"]), gate.OUTPUT_LIMIT)
        if os.name == "posix":
            self.assertLessEqual(result["raw"]["stdout"]["byte_length"], gate.OUTPUT_LIMIT + 1)

    @unittest.skipUnless(os.name == "posix", "POSIX child resource limits")
    def test_child_and_grandchild_inherit_disabled_cores_and_file_limit(self):
        expected = {"core": [0, 0], "file": [gate.OUTPUT_LIMIT + 1] * 2}
        probe = "import resource,json; print(json.dumps({'core':resource.getrlimit(resource.RLIMIT_CORE),'file':resource.getrlimit(resource.RLIMIT_FSIZE)}))"
        for script in (probe, "import subprocess,sys; subprocess.run([sys.executable,'-c'," + repr(probe) + "],check=True)"):
            result = self.run_script(script, {"exit_code": 0, "stdout_json": expected})
            self.assertTrue(result["passed"], result["errors"])

    @unittest.skipUnless(os.name == "posix", "POSIX child resource limits")
    def test_side_file_growth_is_limited_and_cleanup_remains_exact(self):
        result = self.run_script("from pathlib import Path; Path('extra').write_bytes(b'x' * 1000000)",
                                 {"exit_code": 0})
        self.assertIn("filesystem_changed", result["errors"])
        self.assertIn("exit_code", result["errors"])
        self.assertLessEqual(result["after"]["extra"]["size"], gate.OUTPUT_LIMIT + 1)

    def test_low_disk_rejects_before_process_or_scratch_creation(self):
        with patch.object(gate.shutil, "disk_usage", return_value=SimpleNamespace(free=0)), \
                patch.object(gate.subprocess, "Popen") as process:
            with self.assertRaisesRegex(RuntimeError, "disk reserve"):
                self.run_script("print('must not run')", {"exit_code": 0})
            process.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
