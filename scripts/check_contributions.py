#!/usr/bin/env python3
"""Contribution policy checks for pull requests. See AI_POLICY.md.

Usage:
    python3 scripts/check_contributions.py BASE HEAD PR_BODY_FILE

BASE and HEAD are commit SHAs (or refs). PR_BODY_FILE holds the pull request
description. Reads commit messages with git. Standard library only.

Checks:
  1. The pull request description and every commit in BASE..HEAD contain no
     session links and no credential-like strings.
  2. The pull request description answers the "AI use" section: exactly one
     "Extent" line with ticked boxes.
  3. If AI use is disclosed, every non-merge commit has a Co-authored-by
     trailer with a name and an address, and a Task trailer that is short
     and non-empty.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Links to hosted AI sessions or conversations from any vendor, session
# identifiers, "<tool>-session:" lines, and "generated with/by <tool>" footers.
# Session identifiers must contain a digit and be at least 16 characters, so
# ordinary words such as "session-handling" do not match.
AI_TOOL = r"(?:claude|codex|chatgpt|gpt|gemini|deepseek|copilot|cursor|aider|perplexity)"
SESSION_LINK = re.compile(
    r"(?:claude\.ai|chatgpt\.com|chat\.openai\.com|gemini\.google\.com|chat\.deepseek\.com"
    r"|copilot\.microsoft\.com|perplexity\.ai)/\S*"
    r"|\bsession[_-](?=[0-9A-Za-z]*\d)[0-9A-Za-z]{16,}"
    rf"|\b{AI_TOOL}-session\s*:"
    rf"|generated (?:with|by)\s*\[?{AI_TOOL}",
    re.IGNORECASE,
)
CREDENTIAL = re.compile(
    r"BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|sk-[A-Za-z0-9]{20,}"
)
CO_AUTHOR = re.compile(r"^[^<>\n]+ <[^<>\s]+@[^<>\s]+>$")
TASK_MAX = 120


def commits(base: str, head: str) -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "log", "--no-merges", "--format=%H%x00%B%x1e", f"{base}..{head}"],
        capture_output=True, text=True, check=True,
    ).stdout
    result = []
    for record in out.split("\x1e"):
        if record.strip():
            sha, _, body = record.partition("\x00")
            result.append((sha.strip(), body.strip()))
    return result


def trailers(message: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for line in message.splitlines():
        match = re.match(r"^([A-Za-z-]+):\s*(.+)$", line)
        if match:
            found.setdefault(match.group(1).lower(), []).append(match.group(2).strip())
    return found


def ai_disclosure(body: str) -> bool | None:
    """True if AI use is disclosed, False if 'none', None if unanswered."""
    if "## AI use" not in body:
        return None
    section = body.split("## AI use", 1)[1].split("\n## ", 1)[0]
    extent = [line for line in section.splitlines() if line.lstrip("- ").startswith("Extent:")]
    if not extent:
        return None
    ticked = re.findall(r"\[[xX]\]\s*([A-Za-z ]+?)(?=\s{2,}|\s*\[|$)", extent[0])
    ticked = [t.strip().lower() for t in ticked]
    if not ticked:
        return None
    return ticked != ["none"]


def asset_attestation(body: str) -> bool | None:
    """True if the 'AI-generated assets' line ticks 'none', False if it does not, None if absent."""
    for line in body.splitlines():
        if line.lstrip("- ").startswith("AI-generated assets"):
            return bool(re.search(r"\[[xX]\]\s*none", line))
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__)
        return 2
    base, head, body_file = argv[1], argv[2], Path(argv[3])
    body = body_file.read_text(encoding="utf-8") if body_file.exists() else ""
    errors: list[str] = []

    if SESSION_LINK.search(body):
        errors.append("pull request description contains a session link")
    if CREDENTIAL.search(body):
        errors.append("pull request description contains a credential-like string")

    disclosure = ai_disclosure(body)
    if disclosure is None:
        errors.append("pull request description must answer the 'AI use' section (tick one Extent box)")

    attestation = asset_attestation(body)
    if attestation is None:
        errors.append("pull request description must include the 'AI-generated assets' line")
    elif not attestation:
        errors.append("AI-generated assets are permanently prohibited; tick 'none' in the 'AI-generated assets' line")

    for sha, message in commits(base, head):
        short = sha[:10]
        if SESSION_LINK.search(message):
            errors.append(f"{short}: commit message contains a session link")
        if CREDENTIAL.search(message):
            errors.append(f"{short}: commit message contains a credential-like string")
        if disclosure:
            found = trailers(message)
            if not any(CO_AUTHOR.match(v) for v in found.get("co-authored-by", [])):
                errors.append(f"{short}: missing 'Co-authored-by: <name> <address>' trailer (AI use disclosed)")
            tasks = found.get("task", [])
            if not tasks:
                errors.append(f"{short}: missing 'Task: <short description>' trailer (AI use disclosed)")
            elif len(tasks[0]) > TASK_MAX:
                errors.append(f"{short}: Task trailer longer than {TASK_MAX} characters")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} error(s)")
        return 1
    print("contribution policy: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
