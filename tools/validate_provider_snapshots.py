#!/usr/bin/env python3
"""Validate Slice 1029 observed Ruby provider snapshots."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SLICE = ROOT / "diagnostics" / "slice-1029-provider-contract-snapshot-manifest"
MANIFEST_PATH = SLICE / "manifest.json"
REQUIRED_TARGETS = {
    "snapshot.tslp.json",
    "snapshot.prism.ruby",
    "snapshot.psych.yaml",
    "snapshot.rbs.native",
    "snapshot.markdown.markly",
    "snapshot.toml.tslp",
    "snapshot.yaml.tslp",
}
NATIVE_TARGETS = {
    "snapshot.prism.ruby",
    "snapshot.psych.yaml",
    "snapshot.rbs.native",
    "snapshot.markdown.markly",
}
NORMALIZED_SCHEMAS = {
    "structuredmerge.parse-result/v1",
    "structuredmerge.analysis-result/v1",
}


def main() -> int:
    errors: list[str] = []
    manifest = load_json(MANIFEST_PATH, errors)
    if not isinstance(manifest, dict):
        return report(errors)

    rows = manifest.get("rows", [])
    row_ids = [row.get("snapshot_id") for row in rows if isinstance(row, dict)]
    if set(row_ids) != REQUIRED_TARGETS or len(row_ids) != len(REQUIRED_TARGETS):
        errors.append("manifest must contain each required snapshot exactly once")
    if set(manifest.get("required_targets", [])) != REQUIRED_TARGETS:
        errors.append("required_targets does not match the Slice 1029 matrix")

    for row in rows:
        if isinstance(row, dict):
            validate_row(row, errors)
        else:
            errors.append("manifest row is not an object")

    validate_summary(manifest, rows, errors)
    if errors:
        return report(errors)

    print(f"validated {len(rows)} observed provider snapshots")
    return 0


def validate_row(row: dict[str, Any], errors: list[str]) -> None:
    snapshot_id = str(row.get("snapshot_id", "<missing>"))
    context = f"row {snapshot_id}"
    if row.get("state") != "observed":
        errors.append(f"{context}: state must be observed")
    admission = row.get("admission", {})
    if admission.get("satisfies_required_target") is not True:
        errors.append(f"{context}: admission does not satisfy required target")
    if admission.get("review_state") != "admitted" or not admission.get("reviewer"):
        errors.append(f"{context}: admission review is incomplete")

    artifacts = row.get("artifacts", [])
    if len(artifacts) != 1:
        errors.append(f"{context}: exactly one observed artifact is required")
        return
    artifact_entry = artifacts[0]
    artifact_path = safe_local_path(artifact_entry.get("path"), context, errors)
    if artifact_path is None or not artifact_path.is_file():
        errors.append(f"{context}: observed artifact does not exist")
        return
    artifact_bytes = artifact_path.read_bytes()
    artifact_digest = hashlib.sha256(artifact_bytes).hexdigest()
    if artifact_entry.get("byte_length") != len(artifact_bytes):
        errors.append(f"{context}: artifact byte length mismatch")
    if artifact_entry.get("sha256") != artifact_digest:
        errors.append(f"{context}: artifact SHA-256 mismatch")
    if artifact_entry.get("canonicalization") != "exact_bytes":
        errors.append(f"{context}: artifact must retain exact bytes")

    artifact = load_json(artifact_path, errors)
    if not isinstance(artifact, dict):
        return
    if artifact.get("schema") != "structuredmerge.provider-snapshot/v1":
        errors.append(f"{context}: unexpected artifact schema")
    if artifact.get("snapshot_id") != snapshot_id:
        errors.append(f"{context}: artifact snapshot ID mismatch")
    if artifact.get("workflow_provider") != row.get("workflow_provider"):
        errors.append(f"{context}: workflow provider identity mismatch")
    if artifact.get("parser_backend") != row.get("parser_backend"):
        errors.append(f"{context}: parser backend identity mismatch")
    if artifact.get("workflow_provider", {}).get("provider_id") == artifact.get("parser_backend", {}).get("id"):
        errors.append(f"{context}: workflow provider and parser backend are conflated")
    for identity_name in ("workflow_provider", "parser_backend"):
        identity = artifact.get(identity_name, {})
        if not identity.get("package") or not identity.get("package_version"):
            errors.append(f"{context}: {identity_name} package identity is incomplete")

    validate_producer(row, artifact, context, errors)
    validate_captures(row, artifact, context, errors)
    validate_replays(row, artifact, artifact_digest, context, errors)


def validate_producer(
    row: dict[str, Any], artifact: dict[str, Any], context: str, errors: list[str]
) -> None:
    producer = artifact.get("producer", {})
    required = {
        "ruby_gm_release",
        "ruby_gm_source_sha",
        "clean_source_state",
        "dependency_versions",
        "ruby",
        "environment_sha256",
        "capture_adapter",
    }
    missing = sorted(required - producer.keys())
    if missing:
        errors.append(f"{context}: producer missing {', '.join(missing)}")
    if producer.get("clean_source_state") is not True:
        errors.append(f"{context}: producer source state is not clean")
    if not producer.get("dependency_versions"):
        errors.append(f"{context}: dependency versions are empty")
    adapter = producer.get("capture_adapter", {})
    if not adapter.get("id") or not adapter.get("version") or not adapter.get("source_sha256"):
        errors.append(f"{context}: capture adapter identity is incomplete")

    row_producer = row.get("producer", {})
    for key in ("ruby_gm_release", "ruby_gm_source_sha", "clean_source_state", "capture_adapter"):
        if row_producer.get(key) != producer.get(key):
            errors.append(f"{context}: row producer {key} does not match artifact")
    metadata = artifact.get("metadata", {})
    if row_producer.get("capture_command") != metadata.get("capture_command"):
        errors.append(f"{context}: capture command mismatch")
    if row_producer.get("fixture_repository_revision") != metadata.get("fixture_repository_revision"):
        errors.append(f"{context}: fixture revision mismatch")
    if not row_producer.get("captured_at"):
        errors.append(f"{context}: capture timestamp is missing")
    if row_producer.get("producer_manifest_sha256") != canonical_digest(producer):
        errors.append(f"{context}: producer manifest digest mismatch")


def validate_captures(
    row: dict[str, Any], artifact: dict[str, Any], context: str, errors: list[str]
) -> None:
    captures = artifact.get("captures", [])
    if not captures:
        errors.append(f"{context}: no captures found")
        return
    required_schemas = set(row.get("capture_requirements", {}).get("normalized_schemas", []))
    if required_schemas != NORMALIZED_SCHEMAS:
        errors.append(f"{context}: normalized schema requirements are incomplete")
    expected_extensions = {
        extension.get("schema")
        for extension in row.get("capture_requirements", {}).get("extension_requirements", [])
    }
    if row.get("snapshot_id") in NATIVE_TARGETS and not expected_extensions:
        errors.append(f"{context}: native target has no extension requirement")
    inputs = row.get("inputs", [])
    if len(inputs) != len(captures):
        errors.append(f"{context}: input and capture counts differ")

    for index, capture in enumerate(captures):
        capture_context = f"{context} capture {index}"
        parse_request = capture.get("parse_request", {})
        parse_result = capture.get("parse_result", {})
        analysis_result = capture.get("analysis_result", {})
        if parse_request.get("schema") != "structuredmerge.parse-request/v1":
            errors.append(f"{capture_context}: parse request schema mismatch")
        if parse_result.get("schema") != "structuredmerge.parse-result/v1":
            errors.append(f"{capture_context}: parse result schema mismatch")
        if analysis_result.get("schema") != "structuredmerge.analysis-result/v1":
            errors.append(f"{capture_context}: analysis result schema mismatch")
        if not parse_result.get("nodes"):
            errors.append(f"{capture_context}: normalized nodes are empty")
        source = parse_request.get("source", {})
        content = source.get("content", "")
        encoded = content.encode("utf-8")
        if source.get("byte_length") != len(encoded):
            errors.append(f"{capture_context}: source byte length mismatch")
        if source.get("sha256") != hashlib.sha256(encoded).hexdigest():
            errors.append(f"{capture_context}: source SHA-256 mismatch")
        if index < len(inputs):
            validate_input(inputs[index], source, capture_context, errors)
        extension_schemas = {extension.get("schema") for extension in parse_result.get("extensions", [])}
        if not expected_extensions.issubset(extension_schemas):
            errors.append(f"{capture_context}: required extension evidence is missing")
        for extension in parse_result.get("extensions", []):
            if not extension.get("opaque_forwarding_replay_sha256"):
                errors.append(f"{capture_context}: extension forwarding digest is missing")
            requirement = next(
                (item for item in row["capture_requirements"]["extension_requirements"]
                 if item.get("schema") == extension.get("schema")),
                None,
            )
            if requirement and not set(requirement.get("capabilities", [])).issubset(
                set(extension.get("capabilities", []))
            ):
                errors.append(f"{capture_context}: required extension capabilities are missing")
        if parse_result.get("extensions") != analysis_result.get("extensions"):
            errors.append(f"{capture_context}: parse and analysis extensions diverge")


def validate_input(
    manifest_input: dict[str, Any], captured_source: dict[str, Any],
    context: str, errors: list[str]
) -> None:
    expected = {key: value for key, value in captured_source.items() if key != "content"}
    actual = {key: value for key, value in manifest_input.items() if key not in {"kind", "origin"}}
    if actual != expected:
        errors.append(f"{context}: manifest source descriptor differs from capture")
    origin = manifest_input.get("origin", {})
    kind = origin.get("kind")
    if kind == "inline_source":
        content = origin.get("content", "").encode("utf-8")
        validate_bytes(content, origin, f"{context} inline origin", errors)
    elif kind in {"local_fixture", "embedded_source"}:
        relative_path = origin.get("path") or origin.get("artifact_path")
        path = safe_local_path(relative_path, f"{context} origin", errors)
        if path is None or not path.is_file():
            errors.append(f"{context}: source origin does not exist")
        elif kind == "local_fixture":
            validate_bytes(path.read_bytes(), origin, f"{context} fixture origin", errors)
        else:
            document = load_json(path, errors)
            candidates = list(string_values(document))
            matching = [value for value in candidates if digest_text(value) == origin.get("sha256")]
            if not matching or len(matching[0].encode("utf-8")) != origin.get("byte_length"):
                errors.append(f"{context}: embedded source origin was not found")
    else:
        errors.append(f"{context}: unsupported source origin kind {kind!r}")


def validate_replays(
    row: dict[str, Any], artifact: dict[str, Any], artifact_digest: str,
    context: str, errors: list[str]
) -> None:
    replay = row.get("replay", {})
    if replay.get("process_count", 0) < 2 or replay.get("deterministic") is not True:
        errors.append(f"{context}: two-process deterministic replay is required")
    if replay.get("excluded_fields") != []:
        errors.append(f"{context}: replay fields must not be excluded")
    if replay.get("artifact_sha256") != [artifact_digest, artifact_digest]:
        errors.append(f"{context}: exact replay artifact digests do not match")

    differential = artifact.get("differential_replays", [])
    if not differential:
        errors.append(f"{context}: differential operation replay is missing")
    for evidence in differential:
        if evidence.get("equivalent") is not True or evidence.get("output_bytes_equal") is not True:
            errors.append(f"{context}: serialized operation changed provider output")
        if evidence.get("original_sha256") != evidence.get("replay_sha256"):
            errors.append(f"{context}: differential result digest mismatch")
        if evidence.get("original_request") != evidence.get("transported_request"):
            errors.append(f"{context}: transported request differs from original")
        if evidence.get("original_result") != evidence.get("transported_result"):
            errors.append(f"{context}: transported result differs from original")
        if evidence.get("original_sha256") != canonical_digest(evidence.get("original_result")):
            errors.append(f"{context}: original result digest is invalid")
    compact = [
        {key: evidence.get(key) for key in (
            "operation", "equivalent", "original_sha256", "replay_sha256", "output_bytes_equal"
        )}
        for evidence in differential
    ]
    if replay.get("differential_replays") != compact:
        errors.append(f"{context}: manifest differential summary differs from artifact")
    operations = row.get("capture_requirements", {}).get("operation_artifacts", [])
    if "merge2" not in operations:
        errors.append(f"{context}: merge2 operation evidence is not required")


def validate_summary(
    manifest: dict[str, Any], rows: list[Any], errors: list[str]
) -> None:
    summary = manifest.get("summary", {})
    observed = sum(isinstance(row, dict) and row.get("state") == "observed" for row in rows)
    expected = {
        "required_target_count": len(REQUIRED_TARGETS),
        "row_count": len(REQUIRED_TARGETS),
        "observed_count": len(REQUIRED_TARGETS),
        "provisional_count": 0,
        "pending_count": 0,
        "rejected_count": 0,
        "native_target_count": len(NATIVE_TARGETS),
        "tree_sitter_target_count": len(REQUIRED_TARGETS - NATIVE_TARGETS),
        "matrix_complete": observed == len(REQUIRED_TARGETS),
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"summary {key} must be {value!r}")


def safe_local_path(value: Any, context: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str):
        errors.append(f"{context}: artifact path is missing")
        return None
    candidate = (ROOT / value).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{context}: artifact path escapes fixture repository")
        return None
    return candidate


def validate_bytes(
    content: bytes, descriptor: dict[str, Any], context: str, errors: list[str]
) -> None:
    if descriptor.get("byte_length") != len(content):
        errors.append(f"{context}: byte length mismatch")
    if descriptor.get("sha256") != hashlib.sha256(content).hexdigest():
        errors.append(f"{context}: SHA-256 mismatch")


def string_values(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from string_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from string_values(item)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path}: {error}")
        return None


def report(errors: list[str]) -> int:
    for error in errors:
        print(error, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
