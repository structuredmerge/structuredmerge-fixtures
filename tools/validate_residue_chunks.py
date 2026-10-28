#!/usr/bin/env python3
"""Parser-free conformance validator for residue-interleaved chunk outputs.

Checks the contract rules of RAG_INGESTION_ADAPTER_CONTRACT.md
"Residue Interleaving" against designed cases: hash semantics, tier
metadata, attachment direction, declared-drop coverage, and the
owned-identity invariant across variant cases. The validator never
parses source documents; cases declare spans.
"""

from __future__ import annotations

import hashlib
import json


class Invalid(Exception):
    """Raised with the named rejection reason when a rule fails."""


def _sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load(text: str):
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise Invalid("payload") from error
    if not isinstance(value, dict):
        raise Invalid("payload")
    return value


def validate_chunk_fields(chunk: dict) -> None:
    if not isinstance(chunk, dict):
        raise Invalid("fields")
    for key in ("address", "content_hash", "text", "start_byte", "end_byte"):
        if key not in chunk:
            raise Invalid("fields")
    if not isinstance(chunk["text"], str) or not chunk["text"]:
        raise Invalid("fields")
    if not isinstance(chunk["start_byte"], int) or not isinstance(chunk["end_byte"], int):
        raise Invalid("fields")
    if chunk["start_byte"] < 0 or chunk["end_byte"] <= chunk["start_byte"]:
        raise Invalid("spans")


def validate_residue_chunk(chunk: dict) -> None:
    validate_chunk_fields(chunk)
    kind = chunk.get("surface_kind")
    parser = chunk.get("residue_parser")
    if not isinstance(kind, str) or not kind.endswith("_residue"):
        raise Invalid("fields")
    if not isinstance(parser, str) or not parser or parser == "owned":
        raise Invalid("fields")
    if chunk.get("content_hash") != _sha256(chunk["text"]):
        raise Invalid("hash")


def validate_attachment(chunk: dict, owned: list[dict]) -> None:
    parent = chunk.get("parent_address")
    if not isinstance(parent, str) or not parent:
        raise Invalid("attachment")
    addresses = {surface["address"] for surface in owned}
    if parent not in addresses:
        raise Invalid("attachment")
    following = [s for s in owned if s["start_byte"] >= chunk["end_byte"]]
    if following:
        expected = min(following, key=lambda s: s["start_byte"])["address"]
        span_precedes = chunk["end_byte"] <= owned_start(owned, expected)
    else:
        expected = max(owned, key=lambda s: s["end_byte"])["address"]
        span_precedes = chunk["start_byte"] >= owned_end(owned, expected)
    if parent != expected or not span_precedes:
        raise Invalid("attachment")


def owned_start(owned: list[dict], address: str) -> int:
    return next(s["start_byte"] for s in owned if s["address"] == address)


def owned_end(owned: list[dict], address: str) -> int:
    return next(s["end_byte"] for s in owned if s["address"] == address)


def validate_coverage(case: dict, output: dict) -> None:
    residue = output.get("residue", [])
    dropped = output.get("dropped", [])
    if not isinstance(dropped, list):
        raise Invalid("fields")
    for entry in dropped:
        if not isinstance(entry, dict) or not entry.get("reason"):
            raise Invalid("fields")
    covered = [(c["start_byte"], c["end_byte"]) for c in residue]
    covered += [(d["start_byte"], d["end_byte"]) for d in dropped if isinstance(d.get("start_byte"), int)]
    for span in case.get("uncovered_spans", []):
        start, end = span
        if not any(cs <= start and end <= ce for cs, ce in covered):
            raise Invalid("coverage")


def validate_output(case: dict, output: dict) -> None:
    if not isinstance(output, dict):
        raise Invalid("fields")
    owned = output.get("owned")
    residue = output.get("residue", [])
    if not isinstance(owned, list) or not owned or not isinstance(residue, list):
        raise Invalid("fields")
    addresses = set()
    ordinals = set()
    for surface in owned:
        validate_chunk_fields(surface)
        if surface["address"] in addresses:
            raise Invalid("fields")
        addresses.add(surface["address"])
    for chunk in residue:
        validate_residue_chunk(chunk)
        if chunk["address"] in addresses:
            raise Invalid("fields")
        addresses.add(chunk["address"])
        if "ordinal" in chunk:
            if chunk["ordinal"] in ordinals:
                raise Invalid("ordinal")
            ordinals.add(chunk["ordinal"])
        validate_attachment(chunk, owned)
    validate_coverage(case, output)


def verify(case: dict, corpus: dict) -> dict:
    """Verify one designed case; returns the checked output."""
    output = case.get("output")
    if not isinstance(output, dict):
        raise Invalid("fields")
    variant_of = case.get("variant_of")
    validate_output(case, output)
    if variant_of:
        base = next((c for c in corpus["cases"] if c["name"] == variant_of), None)
        if base is None:
            raise Invalid("variant")
        base_owned = sorted(
            (s["address"], s["content_hash"]) for s in base["output"]["owned"]
        )
        case_owned = sorted(
            (s["address"], s["content_hash"]) for s in output["owned"]
        )
        if base_owned != case_owned:
            raise Invalid("identity")
    return output


def main_with_args(argv: list[str]) -> int:
    path = argv[0] if argv else "diagnostics/slice-1055-residue-interleaving/contract.json"
    corpus = _load(open(path, encoding="utf-8").read())
    failures = 0
    for case in corpus["cases"]:
        expect_error = (case.get("expect") or {}).get("error")
        try:
            verify(case, corpus)
            outcome = None
        except Invalid as error:
            outcome = str(error)
        if expect_error:
            if outcome != expect_error:
                print(f"FAIL {case['name']}: expected rejection {expect_error}, got {outcome}")
                failures += 1
            else:
                print(f"ok   {case['name']} (rejected: {outcome})")
        elif outcome:
            print(f"FAIL {case['name']}: unexpected rejection {outcome}")
            failures += 1
        else:
            print(f"ok   {case['name']}")
    return 1 if failures else 0


def main() -> int:
    import sys

    return main_with_args(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
