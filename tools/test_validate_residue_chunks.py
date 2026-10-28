#!/usr/bin/env python3
"""Tests for validate_residue_chunks (slice 1055 residue interleaving)."""

import copy
import json
import unittest
from pathlib import Path

import validate_residue_chunks as v

ROOT = Path(__file__).resolve().parents[1]
CORPUS = json.loads(
    (ROOT / "diagnostics/slice-1055-residue-interleaving/contract.json").read_text(encoding="utf-8")
)


class ResidueCorpus(unittest.TestCase):
    def test_every_case_meets_its_expectation(self):
        outcomes = []
        for case in CORPUS["cases"]:
            expect_error = (case.get("expect") or {}).get("error")
            try:
                v.verify(case, CORPUS)
                outcome = None
            except v.Invalid as error:
                outcome = str(error)
            if expect_error:
                self.assertEqual(outcome, expect_error, case["name"])
            else:
                self.assertIsNone(outcome, case["name"])
            outcomes.append(case["name"])
        self.assertEqual(len(outcomes), 8)

    def test_corpus_has_the_designed_case_set(self):
        names = {case["name"] for case in CORPUS["cases"]}
        self.assertIn("jsonc-comment-only-edit-preserves-owned-identity", names)
        self.assertIn("comment-only-edit-changes-one-residue-chunk", names)
        self.assertIn("trailing-comment-attaches-to-last-surface", names)
        self.assertIn("string-containing-comment-syntax-is-not-residue", names)
        self.assertIn("undetected-residue-falls-back-to-plain-tier", names)
        self.assertEqual(
            {c["name"] for c in CORPUS["cases"] if c.get("expect")},
            {
                "residue-silent-drop-rejected",
                "residue-missing-parent-address-rejected",
                "residue-edit-changing-owned-hash-rejected",
            },
        )


class ResidueValidatorRules(unittest.TestCase):
    def setUp(self):
        self.base = next(
            c for c in CORPUS["cases"]
            if c["name"] == "jsonc-comment-only-edit-preserves-owned-identity"
        )

    def test_tampered_residue_text_rejects_on_hash(self):
        case = copy.deepcopy(self.base)
        chunk = case["output"]["residue"][0]
        chunk["text"] = chunk["text"] + " tampered"
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "hash")

    def test_unknown_parent_address_rejects_on_attachment(self):
        case = copy.deepcopy(self.base)
        case["output"]["residue"][0]["parent_address"] = "/json/paths/missing"
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "attachment")

    def test_missing_surface_kind_rejects_on_fields(self):
        case = copy.deepcopy(self.base)
        del case["output"]["residue"][0]["surface_kind"]
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "fields")

    def test_variant_referencing_unknown_case_rejects(self):
        case = copy.deepcopy(self.base)
        case["variant_of"] = "no-such-case"
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "variant")


class ResidueValidatorBranches(unittest.TestCase):
    def setUp(self):
        self.base = next(
            c for c in CORPUS["cases"]
            if c["name"] == "jsonc-comment-only-edit-preserves-owned-identity"
        )

    def test_load_rejects_invalid_json_and_non_object(self):
        with self.assertRaises(v.Invalid):
            v._load("not json {")
        with self.assertRaises(v.Invalid):
            v._load("[1, 2]")

    def test_missing_output_rejects_on_fields(self):
        with self.assertRaises(v.Invalid) as caught:
            v.verify({"name": "x"}, CORPUS)
        self.assertEqual(str(caught.exception), "fields")

    def test_owned_not_list_or_empty_rejects(self):
        case = copy.deepcopy(self.base)
        case["output"]["owned"] = []
        with self.assertRaises(v.Invalid):
            v.verify(case, CORPUS)
        case = copy.deepcopy(self.base)
        case["output"]["owned"] = "nope"
        with self.assertRaises(v.Invalid):
            v.verify(case, CORPUS)

    def test_owned_address_collision_rejects(self):
        case = copy.deepcopy(self.base)
        case["output"]["owned"][1]["address"] = case["output"]["owned"][0]["address"]
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "fields")

    def test_residue_address_colliding_with_owned_rejects(self):
        case = copy.deepcopy(self.base)
        case["output"]["residue"][0]["address"] = "/json/paths/limit"
        with self.assertRaises(v.Invalid):
            v.verify(case, CORPUS)

    def test_duplicate_residue_ordinal_rejects(self):
        case = copy.deepcopy(self.base)
        case["output"]["residue"][1]["ordinal"] = case["output"]["residue"][0]["ordinal"]
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "ordinal")

    def test_invalid_span_rejects(self):
        case = copy.deepcopy(self.base)
        case["output"]["owned"][0]["end_byte"] = case["output"]["owned"][0]["start_byte"]
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "spans")

    def test_dropped_without_reason_rejects(self):
        case = copy.deepcopy(self.base)
        case["output"]["dropped"] = [{"start_byte": 2, "end_byte": 8}]
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "fields")

    def test_declared_drop_covers_uncovered_span(self):
        case = copy.deepcopy(self.base)
        span = case["output"]["residue"][0]
        case["uncovered_spans"] = [[span["start_byte"], span["end_byte"]]]
        case["output"]["dropped"] = [
            {"start_byte": span["start_byte"], "end_byte": span["end_byte"], "reason": "test drop"}
        ]
        del case["output"]["residue"][0]
        v.verify(case, CORPUS)

    def test_comment_attaching_to_wrong_surface_rejects(self):
        case = copy.deepcopy(self.base)
        # First comment precedes both surfaces; pointing it at the second
        # (not nearest following) surface violates attachment.
        case["output"]["residue"][0]["parent_address"] = "/json/paths/enabled"
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "attachment")

    def test_chunk_shape_guards_reject_on_fields(self):
        for mutate in (
            lambda chunk: chunk.update({"text": None}),
            lambda chunk: chunk.update({"text": ""}),
            lambda chunk: chunk.update({"start_byte": "zero"}),
            lambda chunk: chunk.pop("content_hash"),
        ):
            case = copy.deepcopy(self.base)
            mutate(case["output"]["owned"][0])
            with self.assertRaises(v.Invalid) as caught:
                v.verify(case, CORPUS)
            self.assertEqual(str(caught.exception), "fields", mutate)

    def test_non_dict_chunk_rejects_on_fields(self):
        case = copy.deepcopy(self.base)
        case["output"]["owned"][0] = "not-a-chunk"
        with self.assertRaises(v.Invalid):
            v.verify(case, CORPUS)

    def test_empty_residue_parser_rejects_on_fields(self):
        case = copy.deepcopy(self.base)
        case["output"]["residue"][0]["residue_parser"] = ""
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "fields")

    def test_dropped_not_a_list_rejects_on_fields(self):
        case = copy.deepcopy(self.base)
        case["output"]["dropped"] = "nope"
        with self.assertRaises(v.Invalid) as caught:
            v.verify(case, CORPUS)
        self.assertEqual(str(caught.exception), "fields")

    def test_main_reports_unexpected_rejection_of_verified_case(self):
        import contextlib
        import io

        corpus = copy.deepcopy(CORPUS)
        corpus["cases"][0]["output"]["residue"][0]["text"] = "tampered"
        broken = ROOT / "tmp/broken-residue-corpus.json"
        broken.parent.mkdir(exist_ok=True)
        broken.write_text(json.dumps(corpus), encoding="utf-8")
        try:
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                code = v.main_with_args([str(broken)])
            self.assertEqual(code, 1)
            self.assertIn("unexpected rejection", captured.getvalue())
        finally:
            broken.unlink()


    def test_main_reports_rejection_reason_mismatch(self):
        import contextlib
        import io

        corpus = copy.deepcopy(CORPUS)
        # A designed rejection case that actually verifies: expected reason
        # never materializes.
        corpus["cases"][0]["expect"] = {"error": "coverage"}
        mismatched = ROOT / "tmp/mismatched-residue-corpus.json"
        mismatched.parent.mkdir(exist_ok=True)
        mismatched.write_text(json.dumps(corpus), encoding="utf-8")
        try:
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                code = v.main_with_args([str(mismatched)])
            self.assertEqual(code, 1)
            self.assertIn("expected rejection coverage", captured.getvalue())
        finally:
            mismatched.unlink()


class ResidueValidatorMain(unittest.TestCase):
    def test_main_passes_on_the_corpus(self):
        path = str(ROOT / "diagnostics/slice-1055-residue-interleaving/contract.json")
        self.assertEqual(v.main_with_args([path]), 0)

    def test_main_fails_when_a_case_is_broken(self):
        corpus = copy.deepcopy(CORPUS)
        corpus["cases"][0]["output"]["residue"][0]["text"] = "tampered"
        broken = ROOT / "tmp/broken-residue-corpus.json"
        broken.parent.mkdir(exist_ok=True)
        broken.write_text(json.dumps(corpus), encoding="utf-8")
        try:
            self.assertEqual(v.main_with_args([str(broken)]), 1)
        finally:
            broken.unlink()


if __name__ == "__main__":
    unittest.main()
