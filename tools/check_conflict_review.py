#!/usr/bin/env python3
"""Run exact-byte conflict-review fixtures against any installed full CLI."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from check_cli_contract import ROOT, RESERVE, digest, file_digest, run_case, validate

MANIFEST = ROOT / "conformance/cli-v1/conflict-review.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def review_errors(case, text):
    try:
        report = json.loads(text)
        expected = case["expected"]
        require(report["schema"] == "structuredmerge.cli-report/v1" and report["command"] == "conflicts.diff", "report identity")
        require(report["outcome"] == expected["outcome"] and report["exit_code"] == expected["exit"], "report outcome")
        require(report["cli"]["cli_contract"] == "structuredmerge.cli/v1", "CLI contract")
        for key in ("executable", "package", "version", "kernel_version"):
            require(isinstance(report["cli"][key], str) and report["cli"][key], "CLI identity")
        for key in ("operation_result", "availability", "git_install"):
            require(report[key] is None, "conflict review cannot claim " + key)
        require(report["output_commit_verified"] is False, "output commit claim")
        review = report["conflict_review"]
        if expected["exit"] == 2:
            require(review is None, "partial review on error")
            diagnostic = report["diagnostics"][0]
            require(diagnostic["schema"] == "structuredmerge.diagnostic/v1"
                    and diagnostic["code"] == expected["code"] and diagnostic["blocking"] is True,
                    "error diagnostic")
            return []
        require(report["diagnostics"] == [], "unexpected diagnostic")
        source = case["source"].encode()
        require(review["schema"] == "structuredmerge.conflict-review/v1", "review schema")
        require(review["source"]["byte_length"] == len(source)
                and review["source"]["sha256"] == hashlib.sha256(source).hexdigest(), "source integrity")
        descriptor = review["source"]
        require(descriptor["encoding"] == "utf8" and descriptor["role"] == "source"
                and descriptor["bom"] == source.startswith(b"\xef\xbb\xbf")
                and descriptor["final_newline"] == source.endswith((b"\r", b"\n")), "source metadata")
        crlf = source.count(b"\r\n")
        require(descriptor["line_endings"] == {"crlf": crlf, "lf": source.count(b"\n") - crlf,
                "bare_cr": source.count(b"\r") - crlf}, "line-ending metadata")
        require(review["semantic_conflicts_verified"] is False, "unproven semantic claim")
        require(review["marker_size"] == case.get("marker_size", 7), "marker width")
        require(len(review["regions"]) == len(expected["regions"]), "region count")
        previous = 0
        for region, wanted in zip(review["regions"], expected["regions"]):
            start, end = region["range"]["start_byte"], region["range"]["end_byte"]
            require(type(start) is int and type(end) is int and previous <= start < end <= len(source), "region ordering/range")
            previous = end
            previous_role_end = start
            for role in ("ours", "base", "theirs"):
                if wanted[role] is None:
                    require(region[role] is None, "fabricated base role")
                else:
                    first, last = region[role]["start_byte"], region[role]["end_byte"]
                    require(type(first) is int and type(last) is int and previous_role_end <= first <= last <= end, "role range")
                    previous_role_end = last
                    require(source[first:last] == wanted[role].encode(), "role source bytes")
        return []
    except (ValueError, KeyError, TypeError, IndexError) as error:
        return ["conflict_review:" + str(error)]


def case_inputs(case):
    argv = ["conflicts", "diff", "--json"]
    if case["exit_code"]:
        argv.append("--exit-code")
    argv.extend(["--", "--source.txt"])
    expected = case["expected"]
    invocation = {"id": case["id"], "argv": argv, "expect": {"exit_code": expected["exit"],
        "stderr_empty" if expected["exit"] != 2 else "stderr_nonempty": True}}
    files = {"--source.txt": case["source"], ".gitattributes": "*.txt conflict-marker-size=" + str(case.get("marker_size", 7)) + "\n"}
    validate({"schema": "structuredmerge.cli-conformance/v1", "full_cli_conformance": False,
              "files": files, "cases": [invocation]})
    return invocation, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    executable = args.executable.resolve(strict=True)
    raw = MANIFEST.read_bytes()
    manifest = json.loads(raw)
    require(manifest["schema"] == "structuredmerge.cli-conflict-review-cases/v1"
            and manifest["full_cli_conformance"] is False and 0 < len(manifest["cases"]) <= 100, "fixture schema/count")
    for case in manifest["cases"]:
        case_inputs(case)
    root = ROOT / "tmp"
    root.mkdir(exist_ok=True)
    require(shutil.disk_usage(root).free >= RESERVE + 1024**3, "requires 20 GiB reserve plus 1 GiB budget")
    stage = Path(tempfile.mkdtemp(prefix="cli-conflict-review-", dir=root))
    report = {"schema": "structuredmerge.cli-conflict-review-gate/v1", "executable": str(executable),
        "executable_sha256": file_digest(executable), "fixture_sha256": digest(raw),
        "full_cli_conformance": False, "publication_gate": False, "passed": False, "cases": []}
    try:
        for case in manifest["cases"]:
            invocation, files = case_inputs(case)
            result = run_case([str(executable)], invocation, files, stage)
            result["errors"].extend(review_errors(case, result["stdout"]))
            result["passed"] = not result["errors"]
            report["cases"].append(result)
            print(case["id"] + ": " + ("passed" if result["passed"] else str(result["errors"])))
        report["passed"] = all(case["passed"] for case in report["cases"])
    finally:
        (stage / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print("Report: " + str(stage / "report.json"))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
