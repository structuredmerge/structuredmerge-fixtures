#!/usr/bin/env python3
"""Slice 1045 local contract verifier. No authentication, runtime or remote I/O."""
import base64
import binascii
import hashlib
import json
from pathlib import Path


class Invalid(ValueError):
    """A verification failure authorizes no effects."""


def require(condition, code):
    if not condition:
        raise Invalid(code)


def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def text(value):
    return isinstance(value, str) and bool(value)


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()), "fields")


def verify_bytes(value, domain, resources):
    require(isinstance(value, dict), "bytes")
    transport = set(value) & {"inline_base64", "ref"}
    require(len(transport) == 1, "bytes")
    require(set(value) == {"domain", "byte_length", "digest"} | transport, "bytes")
    require(value["domain"] == domain, "bytes")
    require(type(value["byte_length"]) is int and value["byte_length"] >= 0, "bytes")
    try:
        encoded = value.get("inline_base64")
        if "ref" in value:
            require(text(value["ref"]) and value["ref"] in resources, "unavailable_bytes")
            encoded = resources[value["ref"]]
        require(isinstance(encoded, str), "bytes")
        data = base64.b64decode(encoded, validate=True)
        require(base64.b64encode(data).decode("ascii") == encoded, "bytes")
    except Invalid:
        raise
    except (ValueError, binascii.Error, UnicodeError):
        raise Invalid("bytes") from None
    require(value["byte_length"] == len(data) and value["digest"] == digest(data), "bytes")
    return data


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "json")
            result[key] = value
        return result

    def invalid_number(_):
        raise Invalid("json")

    try:
        raw = data.decode("utf-8") if isinstance(data, bytes) else data
        raw.encode("utf-8")
        result = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_number)
        # Encoding decoded strings also rejects escaped unpaired surrogates.
        json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")
        return result
    except (ValueError, TypeError, UnicodeError) as error:
        if isinstance(error, Invalid):
            raise
        raise Invalid("json") from None


def compact(rows):
    require(isinstance(rows, list), "delta")
    result = []
    for row in rows:
        require(isinstance(row, dict), "delta")
        item = {key: row.get(key) for key in ("id", "ordinal", "content_hash")}
        require(text(item["id"]) and type(item["ordinal"]) is int
                and item["ordinal"] >= 0 and valid_digest(item["content_hash"]), "delta")
        result.append(item)
    require(len({r["id"] for r in result}) == len(result), "delta")
    require(len({r["ordinal"] for r in result}) == len(result), "delta")
    return result


def valid_digest(value):
    return (isinstance(value, str) and value.startswith("sha256:")
            and len(value) == 71 and all(c in "0123456789abcdef" for c in value[7:]))


def id_list(value, code="delta"):
    require(isinstance(value, list) and all(text(i) for i in value), code)
    require(len(set(value)) == len(value), code)
    return set(value)


def jsonl(value):
    require(isinstance(value, str), "dialect")
    return [strict_json(line) for line in value.splitlines() if line.strip()]


def legacy_inventory(legacy, dialect, prior):
    require(isinstance(legacy, dict), "dialect")
    previous = {row["ordinal"]: row for row in prior}
    if dialect == "hosted-rag-v1":
        exports = legacy.get("exports")
        require(isinstance(exports, dict), "dialect")
        rows = jsonl(exports.get("chunks_jsonl"))
        upserts = jsonl(exports.get("upserts_jsonl"))
        deletes = jsonl(exports.get("deletes_jsonl"))
        current = compact(legacy.get("chunks"))
        require(compact(rows) == current, "delta")
        manifest = legacy.get("manifest")
        require(isinstance(manifest, dict) and manifest.get("chunks") == current, "delta")
        added, updated, touched, removed = set(), set(), set(), set()
        for row in current:
            old = previous.get(row["ordinal"])
            if old is None:
                added.add(row["id"])
            elif old == row:
                touched.add(row["id"])
            else:
                updated.add(row["id"])
                removed.add(old["id"])
        ordinals = {r["ordinal"] for r in current}
        removed.update(r["id"] for r in prior if r["ordinal"] not in ordinals)
        for key, expected in (("added", added), ("updated", updated),
                              ("touched", touched), ("removed", removed)):
            require(id_list(manifest.get(key)) == expected, "delta")
        require(compact(upserts) == [r for r in current if r["id"] in added | updated], "delta")
    elif dialect == "ur-brain-delta-v1":
        require(legacy.get("schema") == "ur_brain.structuredmerge_delta.v1", "dialect")
        rows, deletes = legacy.get("pgvector_queue"), legacy.get("deletes_jsonl")
        require(isinstance(rows, list) and isinstance(deletes, list), "dialect")
        current = compact([{**r, "ordinal": r.get("metadata", {}).get("ordinal")}
                           for r in rows if isinstance(r, dict)])
        require(len(current) == len(rows), "delta")
        removed = {r["id"] for r in prior} - {r["id"] for r in current}
    else:
        raise Invalid("dialect")
    require(all(isinstance(r, dict) and text(r.get("id")) for r in deletes), "delta")
    deleted = id_list([r["id"] for r in deletes])
    require(deleted == removed and not deleted & {r["id"] for r in current}, "delta")
    return current, deleted


def occurrence_entries(refs, code):
    require(isinstance(refs, list), code)
    entries = []
    for ref in refs:
        require(isinstance(ref, dict), code)
        fields(ref, "id ordinal")
        require(text(ref["id"]) and type(ref["ordinal"]) is int
                and ref["ordinal"] >= 0, code)
        entries.append((ref["id"], ref["ordinal"]))
    require(len(set(entries)) == len(entries), code)
    return entries


def verify_incorporation(incorporation, prior, current, payload_evidence):
    require(isinstance(incorporation, list), "incorporation")
    prior_refs = {(row["id"], row["ordinal"]) for row in prior}
    current_refs = {(row["id"], row["ordinal"]) for row in current}
    declared_evidence = set(payload_evidence)
    decision_ids = set()
    for record in incorporation:
        require(isinstance(record, dict), "incorporation")
        fields(record, "decision_id authority_ref source_refs subject_refs outcome evidence_refs")
        require(text(record["decision_id"]) and text(record["authority_ref"]), "incorporation")
        require(record["decision_id"] not in decision_ids, "incorporation")
        decision_ids.add(record["decision_id"])
        require(record["outcome"] in ("accepted", "rejected", "edited", "ignored", "unknown"),
                "incorporation")
        source = occurrence_entries(record["source_refs"], "incorporation")
        subject = occurrence_entries(record["subject_refs"], "incorporation")
        require(all(ref in prior_refs for ref in source), "incorporation")
        require(all(ref in current_refs for ref in subject), "incorporation")
        if record["outcome"] in ("accepted", "rejected", "edited"):
            require(subject, "incorporation")
        require(isinstance(record["evidence_refs"], list)
                and set(record["evidence_refs"]) <= declared_evidence, "incorporation")


def verify_lineage(lineage, prior, current):
    require(isinstance(lineage, list), "lineage")
    prior_refs = {(row["id"], row["ordinal"]): row for row in prior}
    current_refs = {(row["id"], row["ordinal"]): row for row in current}
    for assertion in lineage:
        require(isinstance(assertion, dict), "lineage")
        fields(assertion, "kind from to provenance status")
        require(assertion["kind"] in ("move", "copy", "split", "join", "reorder"), "lineage")
        require(assertion["status"] in ("asserted", "ambiguous", "unknown"), "lineage")
        sides = {}
        for side in ("from", "to"):
            refs = assertion[side]
            require(isinstance(refs, list), "lineage")
            entries = []
            for ref in refs:
                require(isinstance(ref, dict), "lineage")
                fields(ref, "id ordinal")
                require(text(ref["id"]) and type(ref["ordinal"]) is int
                        and ref["ordinal"] >= 0, "lineage")
                entries.append((ref["id"], ref["ordinal"]))
            require(len(set(entries)) == len(entries), "lineage")
            sides[side] = entries
        provenance = assertion["provenance"]
        require(isinstance(provenance, dict), "lineage")
        fields(provenance, "basis authority_ref algorithm confidence")
        require(provenance["basis"] in ("authored", "algorithmic", "unknown"), "lineage")
        if provenance["basis"] == "authored":
            require(text(provenance["authority_ref"]) and provenance["algorithm"] is None, "lineage")
        elif provenance["basis"] == "algorithmic":
            algorithm = provenance["algorithm"]
            require(provenance["authority_ref"] is None and isinstance(algorithm, dict), "lineage")
            fields(algorithm, "id version")
            require(text(algorithm["id"]) and text(algorithm["version"]), "lineage")
        else:
            require(provenance["authority_ref"] is None and provenance["algorithm"] is None, "lineage")
        confidence = provenance["confidence"]
        require(confidence is None or (isinstance(confidence, (int, float))
                and 0 <= confidence <= 1), "lineage")
        if assertion["status"] == "asserted":
            require(sides["from"] and sides["to"], "lineage")
            require(all(ref in prior_refs for ref in sides["from"]), "lineage")
            require(all(ref in current_refs for ref in sides["to"]), "lineage")
            if assertion["kind"] == "reorder":
                from_hashes = sorted(prior_refs[ref]["content_hash"] for ref in sides["from"])
                to_hashes = sorted(current_refs[ref]["content_hash"] for ref in sides["to"])
                require(from_hashes == to_hashes, "lineage")


def verify(envelope, context, state):
    """Verify designed evidence against trusted local context; mutate only on success."""
    fields(envelope, "schema payload_json payload_digest")
    require(envelope["schema"] == "structuredmerge.ingest-observation/v1", "schema")
    require(isinstance(envelope["payload_json"], str), "json")
    try:
        encoded = envelope["payload_json"].encode("utf-8")
    except UnicodeError:
        raise Invalid("utf8") from None
    require(digest(encoded) == envelope["payload_digest"], "payload_digest")
    payload = strict_json(encoded)
    base_fields = ("producer scope observation_id revision_ref source_revision_ref "
                   "expected_prior_revision_ref prior_inventory legacy_result original normalized "
                   "processing times scan deletion evidence_refs extensions").split()
    allowed = set(base_fields)
    if "revision_parents" in payload:
        allowed.add("revision_parents")
    if "source_time_start" in payload or "source_time_end" in payload:
        allowed.update({"source_time_start", "source_time_end"})
        require("source_time_start" in payload and "source_time_end" in payload, "time")
    if "embedding_contract" in payload:
        allowed.add("embedding_contract")
    if "lineage" in payload:
        allowed.add("lineage")
    if "incorporation" in payload:
        allowed.add("incorporation")
    require(isinstance(payload, dict) and set(payload) == allowed, "fields")
    producer, scope = payload["producer"], payload["scope"]
    fields(producer, "id version contract_ref")
    require(all(text(v) for v in producer.values()), "producer")
    fields(scope, "workspace_id source_id document_id enumeration")
    require(all(text(v) for v in scope.values()) and scope["enumeration"] == "document-chunks", "scope")
    require(scope == context["scope"] and producer["id"] == context["producer_id"], "scope")
    require(text(payload["observation_id"]) and text(payload["revision_ref"]), "identity")
    for key in ("source_revision_ref", "expected_prior_revision_ref"):
        require(payload[key] is None or text(payload[key]), "identity")
    declared_parents = payload.get("revision_parents")
    if declared_parents is not None:
        require(isinstance(declared_parents, list)
                and all(text(parent) for parent in declared_parents), "ancestry")
        require(len(set(declared_parents)) == len(declared_parents), "ancestry")
        require(payload["revision_ref"] not in declared_parents, "ancestry")
        if declared_parents:
            expected_prior = payload["expected_prior_revision_ref"]
            require(
                expected_prior is None
                or expected_prior == payload["revision_ref"]
                or expected_prior in declared_parents,
                "ancestry",
            )
        else:
            require(payload["expected_prior_revision_ref"] is None, "ancestry")
    require(isinstance(payload["extensions"], dict)
            and all(":" in k for k in payload["extensions"]), "fields")
    key = (producer["id"], json.dumps(scope, sort_keys=True), payload["observation_id"])
    if key in state.get("accepted", {}):
        previous = state["accepted"][key]
        require(previous["digest"] == envelope["payload_digest"], "conflicting_retry")
        return {**previous["decision"], "replay": True}
    head = state.get("head", context["head_revision_ref"])
    require(payload["expected_prior_revision_ref"] == head, "precondition")
    resources = context["resources"]
    prior = []
    if head is None:
        require(payload["prior_inventory"] is None, "prior")
    else:
        prior_bytes = verify_bytes(payload["prior_inventory"], "prior-inventory-json", resources)
        prior_object = strict_json(prior_bytes)
        fields(prior_object, "scope revision_ref chunks")
        require(prior_object["scope"] == scope and prior_object["revision_ref"] == head, "prior")
        require(digest(prior_bytes) == context["prior_inventory_digest"], "prior")
        prior = compact(prior_object["chunks"])
    verify_bytes(payload["original"], "original-source-bytes", resources)
    normalized = verify_bytes(payload["normalized"], "normalized-input-utf8", resources)
    try:
        normalized.decode("utf-8")
    except UnicodeError:
        raise Invalid("utf8") from None
    legacy_ref = payload["legacy_result"]
    fields(legacy_ref, "dialect schema_ref bytes")
    schemas = {"hosted-rag-v1": "RAG_INGESTION_ADAPTER_CONTRACT.md#initial-private",
               "ur-brain-delta-v1": "ur_brain.structuredmerge_delta.v1"}
    require(text(legacy_ref["dialect"]) and schemas.get(legacy_ref["dialect"]) == legacy_ref["schema_ref"], "dialect")
    legacy = strict_json(verify_bytes(legacy_ref["bytes"], "legacy-result-json", resources))
    processing = payload["processing"]
    fields(processing, "descriptor fingerprint")
    proof = verify_bytes(processing["descriptor"], "processing-json", resources)
    require(processing["fingerprint"] == digest(proof), "processing")
    config = strict_json(proof)
    fields(config, "schema normalizer chunker hash parser legacy_schema_ref")
    require(config["schema"] == "structuredmerge.ingest-processing/v1"
            and config["legacy_schema_ref"] == legacy_ref["schema_ref"], "processing")
    for name in ("normalizer", "chunker"):
        fields(config[name], "id version config")
        require(text(config[name]["id"]) and text(config[name]["version"])
                and isinstance(config[name]["config"], dict), "processing")
    require(config["hash"] == {"algorithm": "sha256", "domain": "chunk-text-utf8"}, "processing")
    parser = config["parser"]
    require(isinstance(parser, dict), "processing")
    if parser.get("status") == "used":
        fields(parser, "status id version backend grammar grammar_version contract_ref")
        require(all(text(v) for v in parser.values()), "processing")
    else:
        require(parser == {"status": "not_applicable"}, "processing")
    times = payload["times"]
    fields(times, "source_at observed_at processed_at")
    for name, value in times.items():
        if name == "source_at" and value is None:
            continue
        require(valid_time(value), "time")
    if "source_time_start" in payload:
        require(valid_time(payload["source_time_start"]), "time")
        require(valid_time(payload["source_time_end"]), "time")
        require(payload["source_time_start"] <= payload["source_time_end"], "time")
    contract = payload.get("embedding_contract")
    if contract is not None:
        fields(contract, "owner model_ref model_revision dimensions normalization instruction_profile")
        require(text(contract["owner"]) and text(contract["model_ref"]), "embedding")
        for key in ("model_revision", "normalization", "instruction_profile"):
            require(contract[key] is None or text(contract[key]), "embedding")
        dimensions = contract["dimensions"]
        require(dimensions is None or (type(dimensions) is int and dimensions > 0), "embedding")
    scan = payload["scan"]
    fields(scan, "status enumerated_scope checkpoint_ref finalization_ref")
    require(scan["status"] in ("complete", "partial", "interrupted", "unknown"), "scan")
    require(scan["enumerated_scope"] == scope, "scope")
    final = scan["finalization_ref"]
    require((text(final) if scan["status"] == "complete" else final is None), "scan")
    require(isinstance(payload["evidence_refs"], list)
            and all(text(v) for v in payload["evidence_refs"]), "evidence")
    for ref in [scan["checkpoint_ref"], final, *payload["evidence_refs"]]:
        require(ref is None or (text(ref) and ref in context["evidence_refs"]), "evidence")
    current, deleted = legacy_inventory(legacy, legacy_ref["dialect"], prior)
    lineage = payload.get("lineage")
    if lineage is not None:
        verify_lineage(lineage, prior, current)
    incorporation = payload.get("incorporation")
    if incorporation is not None:
        verify_incorporation(incorporation, prior, current, payload["evidence_refs"])
    deletion = payload["deletion"]
    fields(deletion, "mode authority_ref targets")
    mode = deletion["mode"]
    targets = id_list(deletion["targets"], "deletion")
    if mode == "none":
        require(deletion["authority_ref"] is None and not targets, "deletion")
    else:
        require(mode in ("absence", "explicit_source"), "deletion")
        require(targets == deleted and targets <= {r["id"] for r in prior}, "deletion")
        if mode == "absence":
            require(scan["status"] == "complete", "deletion")
        else:
            require(not current and targets == {r["id"] for r in prior}, "deletion")
        authority = context["authorities"].get(deletion["authority_ref"])
        require(isinstance(authority, dict), "authority")
        require(authority.get("producer_id") == producer["id"] and authority.get("scope") == scope
                and authority.get("mode") == mode and authority.get("finalization_ref") == final
                and id_list(authority.get("targets"), "authority") == targets, "authority")
    revision_key = (producer["id"], json.dumps(scope, sort_keys=True), payload["revision_ref"])
    projection_evidence = digest(
        payload["legacy_result"]["bytes"]["digest"].encode()
        + payload["original"]["digest"].encode()
        + payload["normalized"]["digest"].encode()
        + payload["processing"]["fingerprint"].encode()
    )
    retained = state.get("revisions", {}).get(revision_key)
    if retained is None:
        state.setdefault("revisions", {})[revision_key] = {"projection": projection_evidence}
    else:
        # Re-referencing a retained revision is valid only as a fresh
        # observation of the same projection: evidence must agree, and the
        # head does not advance.
        require(retained.get("projection") == projection_evidence, "revision")
    descriptors = [payload["prior_inventory"], payload["legacy_result"]["bytes"],
                   payload["original"], payload["normalized"], payload["processing"]["descriptor"]]
    retained_evidence = []
    for item in descriptors:
        if item is None:
            continue
        entry = {"domain": item["domain"], "digest": item["digest"],
                 "via": "ref" if "ref" in item else "inline_base64"}
        if "ref" in item:
            entry["ref"] = item["ref"]
        retained_evidence.append(entry)
    decision = {
        "authorized_delete_ids": deletion["targets"],
        "retained_evidence": retained_evidence,
        "tombstones": [
            {
                "target": target,
                "prior_revision_ref": head,
                "cause": mode,
                "observation_id": payload["observation_id"],
                "revision_ref": payload["revision_ref"],
                "authority_ref": deletion["authority_ref"],
            }
            for target in deletion["targets"]
        ],
        "replay": False,
    }
    # Commit local model state only after every proof has passed. This is not a runtime store.
    state.setdefault("accepted", {})[key] = {"digest": envelope["payload_digest"], "decision": decision}
    state["head"] = payload["revision_ref"]
    return decision


def valid_time(value):
    from datetime import datetime
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    # RFC3339 lexical validation has no source AST: require exact separators/digits,
    # then delegate calendar validation to datetime (no permissive ISO alternatives).
    date, separator, fraction = value[:-1].partition(".")
    if len(date) != 19 or any(date[i] != c for i, c in ((4, "-"), (7, "-"), (10, "T"), (13, ":"), (16, ":"))):
        return False
    if not all(c in "0123456789" for i, c in enumerate(date) if i not in (4, 7, 10, 13, 16)):
        return False
    if separator and (not fraction or any(c not in "0123456789" for c in fraction)):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    import unittest
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), "test_validate_ingest_observations.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
