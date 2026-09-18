import copy
import hashlib
import json
import unittest

from check_conflict_review import MANIFEST, case_inputs, review_errors


class ConflictReviewGateTest(unittest.TestCase):
    def test_all_shared_inputs_validate(self):
        manifest = json.loads(MANIFEST.read_text())
        for case in manifest["cases"]:
            case_inputs(case)

    def test_clean_report_and_unproven_claims(self):
        case = {"source": "雪\r\n", "expected": {"exit": 0, "outcome": "clean", "regions": []}}
        report = {"schema": "structuredmerge.cli-report/v1", "command": "conflicts.diff",
            "cli": {"cli_contract": "structuredmerge.cli/v1", "executable": "smorg", "package": "smorg", "version": "test", "kernel_version": "test"},
            "outcome": "clean", "exit_code": 0, "operation_result": None, "availability": None,
            "git_install": None, "output_commit_verified": False, "diagnostics": [],
            "conflict_review": {"schema": "structuredmerge.conflict-review/v1", "marker_size": 7,
                "source": {"byte_length": len(case["source"].encode()), "sha256": hashlib.sha256(case["source"].encode()).hexdigest(),
                    "encoding": "utf8", "role": "source", "bom": False, "final_newline": True,
                    "line_endings": {"crlf": 1, "lf": 0, "bare_cr": 0}},
                "semantic_conflicts_verified": False, "regions": []}}
        self.assertEqual(review_errors(case, json.dumps(report)), [])
        for mutate in [lambda r: r.update(availability={"available": True}),
                       lambda r: r["conflict_review"].update(semantic_conflicts_verified=True),
                       lambda r: r["conflict_review"]["source"].update(sha256="guessed"),
                       lambda r: r["conflict_review"].update(regions=[{}])]:
            changed = copy.deepcopy(report)
            mutate(changed)
            self.assertTrue(review_errors(case, json.dumps(changed)))
        self.assertTrue(review_errors(case, "not-json"))

    def test_error_cannot_return_partial_review(self):
        case = {"expected": {"exit": 2, "outcome": "error", "code": "conflict.invalid_markers"}}
        report = {"schema": "structuredmerge.cli-report/v1", "command": "conflicts.diff",
            "cli": {"cli_contract": "structuredmerge.cli/v1", "executable": "smorg", "package": "smorg", "version": "test", "kernel_version": "test"},
            "outcome": "error", "exit_code": 2, "operation_result": None, "availability": None,
            "git_install": None, "output_commit_verified": False, "conflict_review": None,
            "diagnostics": [{"schema": "structuredmerge.diagnostic/v1", "code": "conflict.invalid_markers", "blocking": True}]}
        self.assertEqual(review_errors(case, json.dumps(report)), [])
        report["conflict_review"] = {"regions": []}
        self.assertTrue(review_errors(case, json.dumps(report)))
