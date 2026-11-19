#!/usr/bin/env python3
"""Consistency checks for the protocol specification repository.

Standard library only. Exits 0 when all checks pass, 1 otherwise.

Usage:
    python3 scripts/check_spec.py [REPO_ROOT]

Checks:
  1. Required files and directories exist.
  2. Decision records follow the naming and section format in AGENTS.md.
  3. Every relative Markdown link resolves to an existing file, and every
     anchor resolves to a heading in the target file.
  4. Open questions are numbered 1..N in order, with no gaps or duplicates.
  5. LICENSE is the Mulan PSL v2 text and contains no template markup.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_PATHS = [
    "AGENTS.md",
    "AI_POLICY.md",
    "README.md",
    "LICENSE",
    "spec/v0.1/overview.md",
    "spec/v0.1/open-questions.md",
    "spec/decisions",
    "test-vectors/README.md",
    "client/.gitkeep",
    "server/.gitkeep",
]

DECISION_NAME = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
DECISION_STATUSES = {"Proposed", "Accepted", "Rejected", "Superseded", "Deprecated"}
DECISION_SECTIONS = ["Context", "Decision", "Consequences", "Alternatives considered"]

LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
OPEN_QUESTION_HEADING = re.compile(r"^## (\d+)\. ", re.MULTILINE)
EXTERNAL = re.compile(r"^(https?:|mailto:)")


def github_slug(heading: str) -> str:
    """Approximate GitHub's heading-to-anchor rule."""
    text = heading.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def heading_slugs(text: str) -> set[str]:
    return {github_slug(m.group(2)) for m in HEADING.finditer(text)}


def markdown_files(root: Path) -> list[Path]:
    skip = {".git", ".claude"}
    return sorted(
        p
        for p in root.rglob("*.md")
        if not any(part in skip for part in p.relative_to(root).parts)
    )


def check_required(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            errors.append(f"missing required path: {rel}")


def check_decisions(root: Path, errors: list[str]) -> None:
    decisions = root / "spec" / "decisions"
    if not decisions.is_dir():
        return
    for path in sorted(decisions.glob("*")):
        rel = path.relative_to(root)
        if path.name == ".gitkeep":
            continue
        if not DECISION_NAME.match(path.name):
            errors.append(f"{rel}: name must match NNNN-kebab-slug.md")
            continue
        text = path.read_text(encoding="utf-8")
        status = re.search(r"^\*\*Status:\*\*\s*(\S+)", text, re.MULTILINE)
        if not status or status.group(1) not in DECISION_STATUSES:
            errors.append(f"{rel}: missing or invalid '**Status:**' line")
        found = [m.group(1) for m in re.finditer(r"^## (.+?)\s*$", text, re.MULTILINE)]
        positions = []
        for section in DECISION_SECTIONS:
            if section not in found:
                errors.append(f"{rel}: missing section '## {section}'")
            else:
                positions.append(found.index(section))
        if positions != sorted(positions):
            errors.append(f"{rel}: sections out of order")


def check_links(root: Path, errors: list[str]) -> None:
    slug_cache: dict[Path, set[str]] = {}

    def slugs_for(target: Path) -> set[str]:
        if target not in slug_cache:
            slug_cache[target] = heading_slugs(target.read_text(encoding="utf-8"))
        return slug_cache[target]

    for source in markdown_files(root):
        text = source.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            target_str = match.group(2)
            if EXTERNAL.match(target_str):
                continue
            path_part, _, anchor = target_str.partition("#")
            rel_source = source.relative_to(root)
            if path_part == "":
                target = source
            else:
                target = (source.parent / path_part).resolve()
                try:
                    target.relative_to(root.resolve())
                except ValueError:
                    errors.append(f"{rel_source}: link leaves the repository: {target_str}")
                    continue
                if not target.exists():
                    errors.append(f"{rel_source}: broken link: {target_str}")
                    continue
            if anchor and target.suffix == ".md":
                if anchor not in slugs_for(target):
                    errors.append(f"{rel_source}: missing anchor #{anchor} in {target_str.split('#')[0] or rel_source}")


def check_open_questions(root: Path, errors: list[str]) -> None:
    path = root / "spec" / "v0.1" / "open-questions.md"
    if not path.exists():
        return
    numbers = [int(n) for n in OPEN_QUESTION_HEADING.findall(path.read_text(encoding="utf-8"))]
    if numbers != list(range(1, len(numbers) + 1)):
        errors.append(f"{path.relative_to(root)}: open questions must be numbered 1..N in order, found {numbers}")


def check_license(root: Path, errors: list[str]) -> None:
    path = root / "LICENSE"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for needle in ["Mulan Permissive Software License", "END OF THE TERMS AND CONDITIONS"]:
        if needle not in text:
            errors.append(f"LICENSE: expected text not found: {needle!r}")
    if "<<" in text or ">>" in text:
        errors.append("LICENSE: contains template markup ('<<' or '>>')")


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent.parent
    errors: list[str] = []
    check_required(root, errors)
    check_decisions(root, errors)
    check_links(root, errors)
    check_open_questions(root, errors)
    check_license(root, errors)
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} error(s)")
        return 1
    print("spec consistency: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
