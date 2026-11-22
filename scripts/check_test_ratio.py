#!/usr/bin/env python3
"""Check the test-to-code ratio of a Mosgird implementation repository.

The rule (AGENTS.md, "Test-driven development"): at least 3 lines of test
code for every line of production code, counted in non-blank, non-comment
lines, for the whole repository, for each unit (Cargo crate, Gradle module,
or other package with its own manifest), and for each production file.

Test code is all verification code:
- whole files under a test path: the defaults below plus the repository's
  `test_paths` in `test-ratio.toml` (fuzz targets, test tools, scripts);
- in Rust production files, items compiled only for verification: under
  `#[test]`, `#[<path>::test]`, `#[kani::...]`, or a `#[cfg(...)]` that is
  false when `test`, `kani`, `hax` and `miri` are all off.

A whole test file names the production files it tests in a comment near
its top, `covers: path/a.rs, path/b.rs`; its lines are split evenly between
them. `covers: *` counts toward the repository total only.

The ratio is fixed here, so a repository cannot lower it. Usage:

    python3 check_test_ratio.py [ROOT] [--all] [--no-git]
"""

import argparse
import math
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

RATIO = 3
CONFIG_NAME = "test-ratio.toml"
CONFIG_KEYS = ("test_paths", "ignore")

C_LIKE = {"rs", "kt", "kts", "java", "c", "h", "cc", "cpp", "hpp", "swift", "m",
          "go", "js", "mjs", "ts", "tsx", "jsx", "cs", "zig", "scala", "dart"}
HASH = {"sh", "bash"}
PYTHON = {"py"}
DOCSTRING_START = re.compile(r"[rRuU]?(\"\"\"|''')")

DEFAULT_TEST_PATHS = (
    "**/tests/**",
    "**/src/test/**",
    "**/src/androidTest/**",
    "fuzz/**",
    "**/test_*.py",
    "**/*_test.py",
    "**/*_test.go",
)
UNIT_MANIFESTS = ("Cargo.toml", "build.gradle", "build.gradle.kts", "package.json",
                  "go.mod", "pyproject.toml")
SKIPPED_DIRS = {".git", "target", "build", "node_modules", ".gradle", "__pycache__"}
VERIFICATION_CFGS = {"test", "kani", "hax", "miri"}
COVERS_HEAD = 40

CHAR_LITERAL = re.compile(r"'(?:\\.|[^\\'])'")
COVERS = re.compile(r"^\s*(?://+|#+|/?\*+)\s*covers:\s*(.*?)\s*(?:\*/)?\s*$")
CFG_TOKEN = re.compile(r'\s*(?:(\w+)|("(?:\\.|[^"\\])*")|([=(),]))')


class ConfigError(Exception):
    """test-ratio.toml is missing a valid shape."""


@dataclass(frozen=True)
class Config:
    test_paths: tuple
    ignore: tuple


@dataclass
class FileCount:
    production: int
    test: float


@dataclass(frozen=True)
class Failure:
    kind: str
    name: str
    production: int
    test: float

    @property
    def missing(self):
        return math.ceil(RATIO * self.production - self.test)


@dataclass
class Report:
    files: dict = field(default_factory=dict)
    units: dict = field(default_factory=dict)
    repo_prod: int = 0
    repo_test: float = 0
    errors: list = field(default_factory=list)
    failures: list = field(default_factory=list)


def load_config(root):
    path = Path(root) / CONFIG_NAME
    if not path.exists():
        return Config(DEFAULT_TEST_PATHS, ())
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        raise ConfigError(f"{CONFIG_NAME}: {err}") from err
    unknown = sorted(set(data) - set(CONFIG_KEYS))
    if unknown:
        raise ConfigError(f"{CONFIG_NAME}: unknown keys {', '.join(unknown)}; "
                          f"the ratio is fixed at {RATIO}:1")
    for key in CONFIG_KEYS:
        value = data.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ConfigError(f"{CONFIG_NAME}: {key} must be a list of strings")
    return Config(DEFAULT_TEST_PATHS + tuple(data.get("test_paths", [])),
                  tuple(data.get("ignore", [])))


def _glob_regex(pattern):
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def matches(path, patterns):
    return any(_glob_regex(p).match(path) for p in patterns)


def language(path):
    name = path.rsplit("/", 1)[-1]
    if "." not in name:
        return None
    ext = name.rsplit(".", 1)[-1]
    if ext in C_LIKE:
        return "c"
    if ext in HASH:
        return "hash"
    if ext in PYTHON:
        return "python"
    return None


def _scan_c(line, in_block):
    """Return the code of one line, without comments and string contents."""
    out, i, n = [], 0, len(line)
    while i < n:
        if in_block:
            end = line.find("*/", i)
            if end < 0:
                return "".join(out), True
            i, in_block = end + 2, False
            out.append(" ")
        elif line.startswith("//", i):
            break
        elif line.startswith("/*", i):
            i, in_block = i + 2, True
        elif line[i] == '"':
            j = i + 1
            while j < n and line[j] != '"':
                j += 2 if line[j] == "\\" else 1
            out.append('""')
            i = j + 1
        elif line[i] == "'" and CHAR_LITERAL.match(line, i):
            out.append("' '")
            i = CHAR_LITERAL.match(line, i).end()
        else:
            out.append(line[i])
            i += 1
    return "".join(out), in_block


def _python_lines(text):
    """Code lines of Python; standalone triple-quoted strings are documentation."""
    result, closing, in_doc = [], None, False
    for raw in text.splitlines():
        line = raw.strip()
        if closing:
            if not in_doc and line:
                result.append(line)
            if closing in line:
                closing = None
            continue
        if not line or line.startswith("#"):
            continue
        doc = DOCSTRING_START.match(line)
        if doc:
            if doc.group(1) not in line[doc.end():]:
                closing, in_doc = doc.group(1), True
            continue
        result.append(line)
        for quote in ('"""', "'''"):
            if line.count(quote) % 2:
                closing, in_doc = quote, False
    return result


def code_lines(text, lang):
    """Return each line that holds code, stripped, without comments."""
    if lang == "python":
        return _python_lines(text)
    result, in_block = [], False
    for raw in text.splitlines():
        if lang == "hash":
            line = raw.strip()
            if line and not line.startswith("#"):
                result.append(line)
            continue
        code, in_block = _scan_c(raw, in_block)
        if code.strip():
            result.append(code.strip())
    return result


def _eval_cfg(text):
    """Evaluate a cfg predicate with verification cfgs off: True, False, or None."""
    tokens = [m.group(1) or m.group(2) or m.group(3) for m in CFG_TOKEN.finditer(text)]
    pos = 0

    def take():
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError("end of predicate")
        pos += 1
        return tokens[pos - 1]

    def expr():
        name = take()
        if pos < len(tokens) and tokens[pos] == "(":
            take()
            args = []
            while tokens[pos:pos + 1] != [")"]:
                args.append(expr())
                if tokens[pos:pos + 1] == [","]:
                    take()
            take()
            if name == "not" and len(args) == 1:
                return None if args[0] is None else not args[0]
            if name == "any":
                return True if True in args else (None if None in args else False)
            if name == "all":
                return False if False in args else (None if None in args else True)
            raise ValueError(name)
        if pos < len(tokens) and tokens[pos] == "=":
            take()
            take()
            return None
        if not re.fullmatch(r"\w+", name):
            raise ValueError(name)
        return False if name in VERIFICATION_CFGS else None

    try:
        value = expr()
    except (ValueError, IndexError):
        return None
    return value if pos == len(tokens) else None


def is_verification_attr(attr):
    """True if the item under this Rust attribute exists only for verification."""
    body = re.sub(r"\s+", "", attr)[2:-1]
    if re.fullmatch(r"(?:\w+::)*test", body) or body.startswith("kani::"):
        return True
    cfg = re.fullmatch(r"cfg\((.*)\)", body)
    return bool(cfg) and _eval_cfg(cfg.group(1)) is False


def _read_attr(lines, i):
    """Read the attribute starting lines[i]; return (text, end line, rest of line)."""
    depth, parts = 0, []
    for k in range(i, len(lines)):
        line = lines[k]
        for pos, ch in enumerate(line):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    parts.append(line[:pos + 1])
                    return " ".join(parts), k, line[pos + 1:]
        parts.append(line)
    return " ".join(parts), len(lines) - 1, ""


def _item_end(lines, k, rest):
    """Index of the last line of the item that starts with `rest` on line k."""
    depth, text = 0, rest
    if not text.strip():
        k, text = k + 1, lines[k + 1] if k + 1 < len(lines) else ""
    while k < len(lines):
        for ch in text:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
                if depth == 0 and ch == "}":
                    return k
            elif ch == ";" and depth == 0:
                return k
        k += 1
        text = lines[k] if k < len(lines) else ""
    return len(lines) - 1


def split_rust(lines):
    """Split a Rust file's code lines into (production, test) counts."""
    prod = test = i = 0
    while i < len(lines):
        if lines[i].startswith("#["):
            attr, end, rest = _read_attr(lines, i)
            if is_verification_attr(attr):
                last = _item_end(lines, end, rest)
                test += last - i + 1
                i = last + 1
            else:
                prod += end - i + 1
                i = end + 1
        else:
            prod += 1
            i += 1
    return prod, test


def covers(text):
    targets = []
    for line in text.splitlines()[:COVERS_HEAD]:
        match = COVERS.match(line)
        if match:
            targets += [t for t in re.split(r"[,\s]+", match.group(1)) if t]
    return targets


def unit_of(root, path):
    parent = Path(path).parent
    while True:
        if any((root / parent / m).exists() for m in UNIT_MANIFESTS):
            return parent.as_posix()
        if parent == Path("."):
            return "."
        parent = parent.parent


def list_files(root, use_git=True):
    if use_git:
        result = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return sorted(p for p in result.stdout.split("\0") if p)
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIPPED_DIRS]
        for name in filenames:
            files.append(Path(dirpath, name).relative_to(root).as_posix())
    return sorted(files)


def measure(root, paths, config):
    root, report, attributions = Path(root), Report(), []
    for path in sorted(paths):
        lang = language(path)
        if lang is None or matches(path, config.ignore):
            continue
        text = (root / path).read_text(encoding="utf-8", errors="replace")
        lines = code_lines(text, lang)
        if matches(path, config.test_paths):
            report.repo_test += len(lines)
            attributions.append((path, covers(text), len(lines)))
            continue
        prod, test = split_rust(lines) if path.endswith(".rs") else (len(lines), 0)
        report.files[path] = FileCount(prod, test)
        report.repo_prod += prod
        report.repo_test += test
    for path, targets, count in attributions:
        if not targets:
            report.errors.append(f"{path}: test file without a 'covers:' line")
        elif "*" in targets:
            if targets != ["*"]:
                report.errors.append(f"{path}: 'covers: *' cannot be mixed with paths")
        else:
            for target in targets:
                if target in report.files:
                    report.files[target].test += count / len(targets)
                else:
                    report.errors.append(f"{path}: covers {target}, "
                                         "which is not a production file")
    for path, count in report.files.items():
        unit = unit_of(root, path)
        prod, test = report.units.get(unit, (0, 0))
        report.units[unit] = (prod + count.production, test + count.test)
    for path, count in sorted(report.files.items()):
        if count.test < RATIO * count.production:
            report.failures.append(Failure("file", path, count.production, count.test))
    for unit, (prod, test) in sorted(report.units.items()):
        if test < RATIO * prod:
            report.failures.append(Failure("unit", unit, prod, test))
    if report.repo_test < RATIO * report.repo_prod:
        report.failures.append(Failure("repository", ".", report.repo_prod, report.repo_test))
    return report


def _num(value):
    return str(int(value)) if value == int(value) else f"{value:.1f}"


def _describe(production, test):
    ratio = test / production if production else math.inf
    return f"{production} production, {_num(test)} test lines ({ratio:.2f}:1)"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--all", action="store_true", help="list every production file")
    parser.add_argument("--no-git", action="store_true",
                        help="walk the directory instead of asking git for tracked files")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        config = load_config(root)
    except ConfigError as err:
        print(f"test-ratio: {err}", file=sys.stderr)
        return 2
    report = measure(root, list_files(root, use_git=not args.no_git), config)
    if args.all:
        for path, count in sorted(report.files.items()):
            print(f"  {path}: {_describe(count.production, count.test)}")
    for error in report.errors:
        print(f"ERROR {error}")
    for f in report.failures:
        print(f"FAIL {f.kind} {f.name}: {_describe(f.production, f.test)}; "
              f"{f.missing} more test lines needed")
    if report.repo_prod == 0:
        summary = "no production code"
    else:
        summary = f"repository {_describe(report.repo_prod, report.repo_test)}"
    failed = bool(report.errors or report.failures)
    print(f"test-ratio: {'FAILED' if failed else 'OK'}, {summary}; "
          f"required {RATIO}:1 per file, unit and repository")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
