#!/usr/bin/env python3
"""Validate compact ruleset fixtures.

This script validates the minimal line-oriented ruleset syntax described in the
informational draft and verifies that every merge fixture with template,
destination, and expected output has a mirrored `.smrules` contract.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULESETS = ROOT / "rulesets"
REQUIRED_DIRECTIVES = {"format", "owners", "match", "read", "attach"}
SINGLETON_DIRECTIVES = {
    "format",
    "owners",
    "match",
    "read",
    "attach",
    "comment_style",
    "render",
    "render_strategy",
}
REPEATABLE_KEYED_DIRECTIVES = {
    "backend",
    "node_role",
    "atomic",
    "child_group",
    "capability",
    "logical_owner",
    "repair",
    "surface",
    "delegate",
}
KNOWN_DIRECTIVES = SINGLETON_DIRECTIVES | REPEATABLE_KEYED_DIRECTIVES
READ_VALUES = {
    "source_augmented_portable_write",
    "native_read_portable_write",
    "native_mutation",
}
ATTACH_VALUES = {
    "layout_only",
    "tracker_layout_merge",
    "augmenter_preferred_tracker_layout",
    "normalize_tracked_layout_merge",
}
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")
TOKEN = re.compile(r"^[\x21\x24-\x7e]+$")


def main() -> int:
    errors: list[str] = []
    merge_fixtures = discover_merge_fixtures()

    for fixture in merge_fixtures:
        ruleset = ruleset_path_for(fixture)
        if not ruleset.exists():
            errors.append(f"missing ruleset for {relative(fixture)}: {relative(ruleset)}")

    for ruleset in sorted(RULESETS.rglob("*.smrules")):
        errors.extend(validate_ruleset(ruleset))
        fixture = fixture_path_for(ruleset)
        if not fixture.exists():
            errors.append(f"ruleset has no matching fixture: {relative(ruleset)}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"validated {len(merge_fixtures)} merge fixture rulesets")
    return 0


def discover_merge_fixtures() -> list[Path]:
    fixtures: list[Path] = []
    for path in sorted(ROOT.rglob("*.json")):
        if ignored(path):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if (
            isinstance(data, dict)
            and isinstance(data.get("template"), str)
            and isinstance(data.get("destination"), str)
            and isinstance(data.get("expected"), dict)
            and isinstance(data["expected"].get("output"), str)
        ):
            fixtures.append(path)
    return fixtures


def ignored(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    return bool(parts and parts[0] in {".git", "rulesets"})


def validate_ruleset(path: Path) -> list[str]:
    errors: list[str] = []
    seen_singletons: dict[str, int] = {}
    seen_repeatable_keys: set[tuple[str, str]] = set()
    seen_directives: set[str] = set()

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        directive, args = parts[0], parts[1:]
        context = f"{relative(path)}:{line_number}"

        if not IDENTIFIER.match(directive):
            errors.append(f"{context}: invalid directive token {directive!r}")
            continue
        if directive not in KNOWN_DIRECTIVES:
            errors.append(f"{context}: unknown directive {directive!r}")
            continue
        if not args:
            errors.append(f"{context}: directive {directive!r} requires at least one argument")
            continue
        for arg in args:
            if arg not in {"true", "false"} and not IDENTIFIER.match(arg) and not TOKEN.match(arg):
                errors.append(f"{context}: invalid argument token {arg!r}")

        seen_directives.add(directive)
        if directive in SINGLETON_DIRECTIVES:
            if directive in seen_singletons:
                errors.append(
                    f"{context}: repeated singleton directive {directive!r}; "
                    f"first seen on line {seen_singletons[directive]}"
                )
            seen_singletons[directive] = line_number

        if directive in REPEATABLE_KEYED_DIRECTIVES:
            keyed = repeatable_key(directive, args)
            if keyed in seen_repeatable_keys:
                errors.append(f"{context}: repeated {directive!r} key {args[0]!r}")
            seen_repeatable_keys.add(keyed)

        if directive == "read" and args[0] not in READ_VALUES:
            errors.append(f"{context}: unknown read value {args[0]!r}")
        if directive == "attach" and args[0] not in ATTACH_VALUES:
            errors.append(f"{context}: unknown attach value {args[0]!r}")

    missing = REQUIRED_DIRECTIVES - seen_directives
    if missing:
        errors.append(f"{relative(path)}: missing required directives: {', '.join(sorted(missing))}")

    return errors


def repeatable_key(directive: str, args: list[str]) -> tuple[str, ...]:
    if directive == "child_group" and len(args) > 1:
        return (directive, args[0], args[1])
    return (directive, args[0])


def ruleset_path_for(fixture: Path) -> Path:
    relative_fixture = fixture.relative_to(ROOT)
    return RULESETS / relative_fixture.with_suffix(".smrules")


def fixture_path_for(ruleset: Path) -> Path:
    relative_ruleset = ruleset.relative_to(RULESETS)
    return ROOT / relative_ruleset.with_suffix(".json")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
