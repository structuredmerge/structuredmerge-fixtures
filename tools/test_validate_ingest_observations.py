"""Executable, stdlib-only tests for the opt-in companion, not a runtime adapter."""
import base64
import copy
import hashlib
import json
import unittest
from pathlib import Path

import validate_ingest_observations as v


def descriptor(data, domain="original-source-bytes"):
    return {"domain": domain, "byte_length": len(data),
            "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
            "inline_base64": base64.b64encode(data).decode("ascii")}


class DescriptorTests(unittest.TestCase):
    def test_exact_original_bytes_not_normalized(self):
        raw = b" Alpha\r\n\r\nBeta \r\n"
        self.assertEqual(v.verify_bytes(descriptor(raw), "original-source-bytes", {}), raw)
        broken = descriptor(raw)
        broken["inline_base64"] = base64.b64encode(raw.strip()).decode()
        with self.assertRaisesRegex(v.Invalid, "bytes"):
            v.verify_bytes(broken, "original-source-bytes", {})


CORPORA = [
    Path(__file__).resolve().parents[1] / "diagnostics/slice-1045-ingest-observation-deletion-authority/contract.json",
    Path(__file__).resolve().parents[1] / "diagnostics/slice-1046-document-identity-occurrence-scoping/contract.json",
    Path(__file__).resolve().parents[1] / "diagnostics/slice-1047-revision-ancestry-merge-roles/contract.json",
    Path(__file__).resolve().parents[1] / "diagnostics/slice-1048-temporal-dedupe-preconditions/contract.json",
    Path(__file__).resolve().parents[1] / "diagnostics/slice-1049-embedding-contract-handoff/contract.json",
    Path(__file__).resolve().parents[1] / "diagnostics/slice-1050-tombstones-atomicity-compatibility/contract.json",
]


class ContractTests(unittest.TestCase):
    def base_case(self):
        return copy.deepcopy(json.loads(CORPORA[0].read_text())["cases"][0])

    def mutate(self, change):
        case = self.base_case()
        payload = json.loads(case["envelope"]["payload_json"])
        change(payload)
        raw = json.dumps(payload, separators=(",", ":"))
        case["envelope"]["payload_json"] = raw
        case["envelope"]["payload_digest"] = v.digest(raw.encode())
        return case

    def test_malformed_nested_types_reject_without_effects(self):
        mutations = [
            lambda p: p["legacy_result"].update(dialect=[]),
            lambda p: p.update(scan=[]),
            lambda p: p.update(processing=None),
            lambda p: p["deletion"].update(authority_ref=[]),
        ]
        for mutation in mutations:
            case = self.mutate(mutation)
            state = {}
            with self.subTest(mutation=mutation), self.assertRaises(v.Invalid):
                v.verify(case["envelope"], case["context"], state)
            self.assertEqual(state, {})

    def test_tampered_retry_digest_is_rejected_before_replay(self):
        case = self.base_case()
        state = {}
        v.verify(case["envelope"], case["context"], state)
        before = copy.deepcopy(state)
        case["envelope"]["payload_json"] += " "
        with self.assertRaisesRegex(v.Invalid, "payload_digest"):
            v.verify(case["envelope"], case["context"], state)
        self.assertEqual(state, before)

    def test_unknown_schema_is_rejected_even_for_retry(self):
        case = self.base_case()
        state = {}
        v.verify(case["envelope"], case["context"], state)
        before = copy.deepcopy(state)
        case["envelope"]["schema"] = "unknown/v2"
        with self.assertRaisesRegex(v.Invalid, "schema"):
            v.verify(case["envelope"], case["context"], state)
        self.assertEqual(state, before)

    def test_strict_json_rejects_duplicate_keys_nonfinite_and_surrogates(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}', r'"\ud800"', b'\xff'):
            with self.subTest(raw=raw), self.assertRaises(v.Invalid):
                v.strict_json(raw)

    def test_timestamp_calendar_and_lexical_validation(self):
        for value in ("2026-02-30T00:00:00Z", "2026-10-26 00:00:00Z",
                      "2026-10-26T00:00:00+00:00", "2026-10-26T00:00:00.Z", None):
            self.assertFalse(v.valid_time(value))
        self.assertTrue(v.valid_time("2026-10-26T00:00:00.123Z"))

    def test_used_parser_proof_and_initial_inventory(self):
        case = self.base_case()
        payload = json.loads(case["envelope"]["payload_json"])
        payload["expected_prior_revision_ref"] = None
        payload["prior_inventory"] = None
        legacy = json.loads(v.verify_bytes(payload["legacy_result"]["bytes"], "legacy-result-json", {}))
        legacy["manifest"]["added"] = [row["id"] for row in legacy["chunks"]]
        legacy["manifest"]["touched"] = []
        legacy["exports"]["upserts_jsonl"] = legacy["exports"]["chunks_jsonl"]
        payload["legacy_result"]["bytes"] = descriptor(json.dumps(legacy).encode(), "legacy-result-json")
        processing = json.loads(v.verify_bytes(payload["processing"]["descriptor"], "processing-json", {}))
        processing["parser"] = {"status": "used", "id": "designed-parser", "version": "1",
                                "backend": "designed", "grammar": "text", "grammar_version": "1",
                                "contract_ref": "fixture:parser"}
        proof = descriptor(json.dumps(processing).encode(), "processing-json")
        payload["processing"] = {"descriptor": proof, "fingerprint": proof["digest"]}
        raw = json.dumps(payload)
        case["envelope"].update(payload_json=raw, payload_digest=v.digest(raw.encode()))
        case["context"]["head_revision_ref"] = None
        self.assertEqual(v.verify(case["envelope"], case["context"], {})["authorized_delete_ids"], [])

    def test_descriptor_rejects_invalid_base64(self):
        value = descriptor(b"source")
        value["inline_base64"] = "!!!"
        with self.assertRaisesRegex(v.Invalid, "bytes"):
            v.verify_bytes(value, "original-source-bytes", {})

    def test_payload_rejects_unpaired_surrogate(self):
        case = self.base_case()
        case["envelope"]["payload_json"] = chr(0xD800)
        with self.assertRaisesRegex(v.Invalid, "utf8"):
            v.verify(case["envelope"], case["context"], {})

    def test_unknown_dialect_rejected(self):
        with self.assertRaisesRegex(v.Invalid, "dialect"):
            v.legacy_inventory({}, "unknown", [])

    def test_invalid_timestamp_separators_and_calendar(self):
        for value in ("2026-10-26T00:00:00.aZ", "2026-10-26T00:00:00Zextra",
                      "2026-13-01T00:00:00Z", "x026-10-26T00:00:00Z"):
            self.assertFalse(v.valid_time(value))

    def check_case(self, case, context, state):
        before = copy.deepcopy(state)
        original = copy.deepcopy(case["envelope"])
        expected = case["expect"]
        if "error" in expected:
            with self.assertRaisesRegex(v.Invalid, "^" + expected["error"] + "$"):
                v.verify(case["envelope"], context, state)
            self.assertEqual(state, before, "failure must have no effects")
        else:
            decision = v.verify(case["envelope"], context, state)
            self.assertEqual(decision["authorized_delete_ids"], expected["authorized_delete_ids"])
            self.assertEqual(decision["replay"], expected["replay"])
            if "tombstones" in expected:
                self.assertEqual(decision["tombstones"], expected["tombstones"])
        self.assertEqual(case["envelope"], original, "legacy and companion bytes must not be rewritten")

    def run_corpus(self, corpus_path):
        corpus = json.loads(corpus_path.read_text())
        self.assertTrue(corpus["cases"])
        names = [case["name"] for case in corpus["cases"]]
        self.assertEqual(len(names), len(set(names)))
        for case in corpus["cases"]:
            with self.subTest(case=case["name"]):
                self.check_case(case, case["context"], {})
        for sequence in corpus["sequences"]:
            state = {}
            for step in sequence["steps"]:
                with self.subTest(sequence=sequence["name"], step=step["name"]):
                    self.check_case(step, step.get("context") or sequence["context"], state)

    def test_shared_positive_and_negative_cases(self):
        for corpus_path in CORPORA:
            with self.subTest(corpus=corpus_path.parent.name):
                self.run_corpus(corpus_path)


if __name__ == "__main__":
    unittest.main()
