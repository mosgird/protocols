#!/usr/bin/env python3
"""Run the formal models in spec/v0.1/models and check every result.

ProVerif: every query must be proved true, except reachability
("sanity") queries of the form `query ...; event(...)`, which ProVerif
reports as `not event(...) is false` when the event is reachable. A
sanity query reported true means the model is vacuous and fails.

Tamarin: every lemma in each theory must be verified.

Usage: python3 scripts/check_models.py [--proverif] [--tamarin]
With no option, both run. The tools must be on PATH.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS = ROOT / "spec" / "v0.1" / "models"
RESULT = re.compile(r"^RESULT (.*) is (true|false|cannot be proved)\.$")
LEMMA = re.compile(r"^\s+(\w+) \((all-traces|exists-trace)\): (verified|falsified|analysis incomplete)")


def run(cmd: list[str], cwd: pathlib.Path) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout + proc.stderr)
        raise SystemExit(f"error: {' '.join(cmd)} exited with {proc.returncode}")
    return proc.stdout + proc.stderr


def check_proverif() -> list[str]:
    errors = []
    directory = MODELS / "proverif"
    for model in sorted(directory.glob("*.pv")):
        out = run(["proverif", "-lib", "common.pvl", model.name], directory)
        results = [m.groups() for m in map(RESULT.match, out.splitlines()) if m]
        if not results:
            errors.append(f"{model.name}: no results")
        for query, verdict in results:
            sanity = query.startswith("not event(")
            expected = "false" if sanity else "true"
            status = "ok" if verdict == expected else "FAIL"
            print(f"{status:4} {model.name}: {query} is {verdict}")
            if verdict != expected:
                errors.append(f"{model.name}: {query} is {verdict}, expected {expected}")
    return errors


def check_tamarin() -> list[str]:
    errors = []
    for theory in sorted((MODELS / "tamarin").glob("*.spthy")):
        out = run(["tamarin-prover", "--prove", theory.name, "+RTS", "-N4", "-M3g", "-RTS"], theory.parent)
        lemmas = [m.groups() for m in map(LEMMA.match, out.splitlines()) if m]
        if not lemmas:
            errors.append(f"{theory.name}: no lemma results")
        for name, kind, verdict in lemmas:
            status = "ok" if verdict == "verified" else "FAIL"
            print(f"{status:4} {theory.name}: {name} ({kind}) {verdict}")
            if verdict != "verified":
                errors.append(f"{theory.name}: {name} {verdict}")
    return errors


def main(argv: list[str]) -> int:
    selected = set(argv) or {"--proverif", "--tamarin"}
    errors = []
    if "--proverif" in selected:
        errors += check_proverif()
    if "--tamarin" in selected:
        errors += check_tamarin()
    if errors:
        print("\nformal models: FAILED")
        for e in errors:
            print(f"  {e}")
        return 1
    print("\nformal models: all results as expected")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
