import subprocess
import unittest
from unittest.mock import patch

import validate_provider_snapshots as validator


class HistoricalFixtureTests(unittest.TestCase):
    def test_reads_pinned_object_not_worktree(self):
        revision = "a" * 40
        path = validator.ROOT / "yaml" / "case.json"
        errors = []
        with patch.object(validator.subprocess, "run") as run:
            run.return_value.stdout = b"historical bytes"
            self.assertEqual(
                validator.historical_fixture_bytes(path, revision, "test", errors),
                b"historical bytes",
            )
        self.assertEqual(run.call_args.args[0], ["git", "show", f"{revision}:yaml/case.json"])
        self.assertEqual(errors, [])

    def test_rejects_unpinned_revisions_without_git(self):
        for revision in (None, "main", "--help", "g" * 40):
            with self.subTest(revision=revision), patch.object(validator.subprocess, "run") as run:
                errors = []
                self.assertIsNone(validator.historical_fixture_bytes(
                    validator.ROOT / "fixture.json", revision, "test", errors))
                self.assertTrue(errors)
                run.assert_not_called()

    def test_missing_history_fails_closed_without_fallback(self):
        errors = []
        with patch.object(validator.subprocess, "run", side_effect=subprocess.CalledProcessError(128, "git")):
            self.assertIsNone(validator.historical_fixture_bytes(
                validator.ROOT / "README.md", "a" * 40, "test", errors))
        self.assertTrue(errors)

    def test_wrong_digest_still_fails(self):
        errors = []
        validator.validate_bytes(b"changed", {"byte_length": 7, "sha256": "0" * 64}, "test", errors)
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
