import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
