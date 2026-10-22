#!/usr/bin/env python3
"""Run the merge-driver v1 conformance subset against an installed smorg* CLI.

Usage:
    python3 tools/check_merge_driver_conformance.py --executable /path/to/smorg-rb

Exit status is 0 when every case passes, 1 otherwise. This is a partial
conformance suite: it always reports full_cli_conformance: false.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "conformance" / "merge-driver-v1" / "manifest.json"
CHILD_TIMEOUT_SECONDS = 60


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", required=True, help="Absolute path to the smorg* CLI to exercise")
    parser.add_argument("--json", action="store_true", help="Emit the full report as JSON")
    return parser.parse_args()


def run_case(executable, case):
    with tempfile.TemporaryDirectory(prefix="smorg-merge-driver-conformance-") as sandbox:
        root = Path(sandbox)
        for name, content in case.get("files", {}).items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        completed = subprocess.run(
            [executable, *case["argv"]],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=CHILD_TIMEOUT_SECONDS,
        )

        report = {}
        report_path = root / "report.json"
        if report_path.is_file():
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                report = {}

        output_path = root / "merged.out"
        output = output_path.read_text(encoding="utf-8") if output_path.is_file() else None

    return check_expectations(case, completed, report, output)


def check_expectations(case, completed, report, output):
    expect = case["expect"]
    failures = []

    if completed.returncode != expect["exit_code"]:
        failures.append(
            f"exit_code: expected {expect['exit_code']}, got {completed.returncode} "
            f"(stderr: {completed.stderr.strip()[:200]})"
        )

    if "report_ok" in expect and report.get("ok") != expect["report_ok"]:
        failures.append(f"report_ok: expected {expect['report_ok']}, got {report.get('ok')!r}")

    if "conflict_count" in expect:
        actual = len(report.get("conflicts") or [])
        if actual != expect["conflict_count"]:
            failures.append(f"conflict_count: expected {expect['conflict_count']}, got {actual}")

    if "output_source" in expect and output != expect["output_source"]:
        failures.append(
            "output_source mismatch:\n"
            f"  expected: {expect['output_source']!r}\n"
            f"  actual:   {output!r}"
        )

    if "output_json_value" in expect:
        try:
            actual_value = json.loads(output) if output is not None else None
        except json.JSONDecodeError:
            actual_value = None
        if actual_value != expect["output_json_value"]:
            failures.append(
                f"output_json_value: expected {expect['output_json_value']!r}, got {actual_value!r}"
            )

    diagnostics_text = json.dumps(report.get("diagnostics") or [])
    for needle in expect.get("diagnostics_contain", []):
        if needle not in diagnostics_text:
            failures.append(f"diagnostics_contain: {needle!r} not found in {diagnostics_text[:300]}")

    conflict_categories = [entry.get("category") for entry in (report.get("conflicts") or [])]
    for needle in expect.get("conflicts_category_contain", []):
        if needle not in conflict_categories:
            failures.append(f"conflicts_category_contain: {needle!r} not found in {conflict_categories}")

    return {"id": case["id"], "ok": not failures, "failures": failures}


def main():
    args = parse_args()
    executable = str(Path(args.executable).resolve())
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    results = [run_case(executable, case) for case in manifest["cases"]]
    passed = sum(1 for result in results if result["ok"])
    summary = {
        "schema": manifest["schema"],
        "full_cli_conformance": False,
        "executable": executable,
        "manifest": str(MANIFEST),
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for result in results:
            status = "PASS" if result["ok"] else "FAIL"
            print(f"{status} {result['id']}")
            for failure in result["failures"]:
                print(f"     {failure}")
        print(f"{passed}/{len(results)} cases passed (full_cli_conformance: false)")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
