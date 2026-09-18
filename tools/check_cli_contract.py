#!/usr/bin/env python3
"""Run portable discovery/argument cases against one real CLI; never claim full conformance."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "conformance/cli-v1/manifest.json"
RESERVE = 20 * 1024**3
OUTPUT_LIMIT = 256 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


def validate(manifest):
    if manifest.get("schema") != "structuredmerge.cli-conformance/v1" or manifest.get("full_cli_conformance") is not False:
        raise ValueError("unsupported manifest or full-conformance claim")
    files = manifest["files"]
    if not isinstance(files, dict) or not files:
        raise ValueError("expected source fixtures")
    for name, value in files.items():
        if not isinstance(name, str) or name in ("", ".", "..", "stdout.capture", "stderr.capture") or "/" in name or "\\" in name:
            raise ValueError("unsafe fixture filename")
        if not isinstance(value, str) or len(value.encode()) > 4096:
            raise ValueError("expected small UTF-8 fixture")
    ids = set()
    for case in manifest["cases"]:
        if not isinstance(case["id"], str) or not case["id"] or case["id"] in ids:
            raise ValueError("missing or duplicate case id")
        ids.add(case["id"])
        if not isinstance(case["argv"], list) or not all(isinstance(value, str) and "\0" not in value for value in case["argv"]):
            raise ValueError("invalid argument vector")
        expected = case["expect"]
        allowed = {"exit_code", "stderr_empty", "stderr_nonempty", "stdout_empty", "stdout_contains", "stdout_json", "stdout_json_strings"}
        if set(expected) - allowed or type(expected.get("exit_code")) is not int or expected["exit_code"] not in range(4):
            raise ValueError("unknown expectation or exit code")
        for name in ("stdout_empty", "stderr_empty", "stderr_nonempty"):
            if name in expected and type(expected[name]) is not bool:
                raise ValueError("expected Boolean assertion")
        for name in ("stdout_contains", "stdout_json_strings"):
            if name in expected and (not isinstance(expected[name], list) or not all(isinstance(value, str) for value in expected[name])):
                raise ValueError("expected string assertions")
        if "stdout_json" in expected and not isinstance(expected["stdout_json"], dict):
            raise ValueError("expected JSON field assertions")
    if not ids:
        raise ValueError("empty conformance suite")


def snapshot(directory):
    result = {}
    for path in directory.rglob("*"):
        if path.name in ("stdout.capture", "stderr.capture"):
            continue
        name = path.relative_to(directory).as_posix()
        if path.is_symlink():
            result[name] = {"symlink": os.readlink(path)}
        elif path.is_file():
            size = path.stat().st_size
            # Seed files are at most 4 KiB; oversized replacements already fail.
            result[name] = {"sha256": file_digest(path) if size <= OUTPUT_LIMIT else None, "size": size}
        elif path.is_dir():
            result[name] = {"directory": True}
    return result


def run_case(command, case, files, scratch, timeout=10):
    with tempfile.TemporaryDirectory(prefix="case-", dir=scratch) as directory:
        directory = Path(directory)
        for name, text in files.items():
            (directory / name).write_bytes(text.encode("utf-8"))
        before = snapshot(directory)
        stdout_path, stderr_path = directory / "stdout.capture", directory / "stderr.capture"
        failure = None
        started = time.monotonic()
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen([*command, *case["argv"]], cwd=directory,
                stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                start_new_session=os.name != "nt")
            try:
                while process.poll() is None:
                    if time.monotonic() - started > timeout:
                        failure = "timeout"
                    elif stdout_path.stat().st_size + stderr_path.stat().st_size > OUTPUT_LIMIT:
                        failure = "output_budget"
                    elif shutil.disk_usage(scratch).free < RESERVE:
                        failure = "disk_reserve"
                    if failure:
                        break
                    time.sleep(0.01)
            finally:
                if os.name == "nt":
                    if process.poll() is None:
                        process.kill()
                else:
                    # Also retire descendants if their leader has already exited.
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                process.wait()
        after = snapshot(directory)
        outputs = {}
        raw = {}
        if stdout_path.stat().st_size + stderr_path.stat().st_size > OUTPUT_LIMIT:
            failure = failure or "output_budget"
        for key, path in (("stdout", stdout_path), ("stderr", stderr_path)):
            with path.open("rb") as stream:
                data = stream.read(OUTPUT_LIMIT + 1)
            if len(data) > OUTPUT_LIMIT:
                failure = failure or "output_budget"
            outputs[key] = data[:OUTPUT_LIMIT].decode("utf-8", errors="replace")
            raw[key] = {"base64": base64.b64encode(data[:OUTPUT_LIMIT]).decode("ascii"),
                "captured_sha256": digest(data[:OUTPUT_LIMIT]), "byte_length": path.stat().st_size,
                "truncated": len(data) > OUTPUT_LIMIT}
        errors = [failure] if failure else []
        if before != after:
            errors.append("filesystem_changed")
        expected = case["expect"]
        if process.returncode != expected["exit_code"]:
            errors.append("exit_code")
        for key in ("stdout", "stderr"):
            if expected.get(key + "_empty") and outputs[key]:
                errors.append(key + "_not_empty")
            if expected.get(key + "_nonempty") and not outputs[key]:
                errors.append(key + "_empty")
        for token in expected.get("stdout_contains", []):
            if token not in outputs["stdout"]:
                errors.append("missing_stdout_token:" + token)
        if "stdout_json" in expected:
            try:
                value = json.loads(outputs["stdout"])
                if not isinstance(value, dict):
                    raise ValueError("expected object")
                for key, item in expected["stdout_json"].items():
                    if value.get(key) != item:
                        errors.append("json_field:" + key)
                for key in expected.get("stdout_json_strings", []):
                    if not isinstance(value.get(key), str) or not value[key]:
                        errors.append("json_identity:" + key)
            except ValueError:
                errors.append("invalid_json")
        return {"id": case["id"], "argv": case["argv"], "passed": not errors,
            "exit_code": process.returncode, "errors": errors, **outputs,
            "raw": raw, "before": before, "after": after}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    executable = args.executable.resolve(strict=True)
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    validate(manifest)
    scratch = ROOT / "tmp"
    scratch.mkdir(exist_ok=True)
    if shutil.disk_usage(scratch).free < RESERVE + 1024**3:
        raise RuntimeError("requires 20 GiB reserve plus 1 GiB working budget")
    report_dir = Path(tempfile.mkdtemp(prefix="cli-conformance-", dir=scratch))
    report = {"schema": "structuredmerge.cli-conformance-report/v1", "executable": str(executable),
        "executable_sha256": file_digest(executable), "manifest_sha256": digest(manifest_bytes),
        "scope": manifest["scope"], "full_cli_conformance": False, "publication_gate": False,
        "passed": False, "cases": []}
    try:
        for case in manifest["cases"]:
            result = run_case([str(executable)], case, manifest["files"], report_dir)
            report["cases"].append(result)
            print(case["id"] + ": " + ("passed" if result["passed"] else ", ".join(result["errors"])), flush=True)
        report["passed"] = all(case["passed"] for case in report["cases"])
    except BaseException as error:
        report["error"] = type(error).__name__ + ": " + str(error)
        raise
    finally:
        (report_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Report: " + str(report_dir / "report.json"), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
