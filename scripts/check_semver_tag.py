#!/usr/bin/env python3
"""Check a release tag name and its ancestry. See spec/VERSIONING.md.

Usage:
    python3 scripts/check_semver_tag.py TAG

Run from inside a git checkout whose HEAD is the tagged commit. The check
fails unless:
  1. TAG is 'v' followed by a version that matches the official SemVer 2.0.0
     regular expression (https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string);
  2. HEAD is an ancestor of, or equal to, origin/main, so releases come from main.

Standard library only; uses git to read history.
"""

from __future__ import annotations

import re
import subprocess
import sys

# Official regular expression from https://semver.org/ (SemVer 2.0.0).
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def check_name(tag: str) -> list[str]:
    if not tag.startswith("v"):
        return [f"tag {tag!r} must start with 'v'"]
    version = tag[1:]
    if not SEMVER.match(version):
        return [f"tag {tag!r}: {version!r} is not a valid SemVer 2.0.0 version"]
    if "+" in version:
        return [f"tag {tag!r}: build metadata ('+') is not used for releases"]
    return []


def check_ancestry() -> list[str]:
    fetched = subprocess.run(
        ["git", "fetch", "--no-tags", "origin", "main"],
        capture_output=True, text=True,
    )
    if fetched.returncode != 0:
        return [f"could not fetch origin/main: {fetched.stderr.strip()}"]
    is_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "HEAD", "FETCH_HEAD"],
        capture_output=True, text=True,
    )
    if is_ancestor.returncode != 0:
        return ["the tagged commit is not on main"]
    return []


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    tag = argv[1]
    errors = check_name(tag)
    if not errors:
        errors = check_ancestry()
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"release tag {tag}: valid SemVer name, on main")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
