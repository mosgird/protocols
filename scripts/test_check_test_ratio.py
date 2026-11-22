"""Tests for check_test_ratio.py.

Run from the repository root:

    python3 -m unittest discover -s scripts -p 'test_*.py'
"""

# covers: scripts/check_test_ratio.py

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_test_ratio as ctr  # noqa: E402


def make_repo(files):
    """Write files (path -> text) into a new temporary directory and return it."""
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp, root


def rust_lines(n, prefix="let x"):
    """Return n distinct lines of Rust production code."""
    return "".join(f"{prefix}{i} = {i};\n" for i in range(n))


def run_main(args):
    """Run main() and return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = ctr.main(args)
    return code, out.getvalue(), err.getvalue()


class CodeLinesCLike(unittest.TestCase):
    def lines(self, text):
        return ctr.code_lines(text, "c")

    def test_blank_lines_are_not_code(self):
        self.assertEqual(self.lines("\n   \n\t\n"), [])

    def test_line_comment_is_not_code(self):
        self.assertEqual(self.lines("// a comment\n"), [])

    def test_doc_comments_are_not_code(self):
        self.assertEqual(self.lines("/// outer doc\n//! inner doc\n"), [])

    def test_indented_comment_is_not_code(self):
        self.assertEqual(self.lines("    // indented\n"), [])

    def test_block_comment_on_one_line_is_not_code(self):
        self.assertEqual(self.lines("/* block */\n"), [])

    def test_block_comment_over_lines_is_not_code(self):
        self.assertEqual(self.lines("/*\n * one\n * two\n */\n"), [])

    def test_code_after_block_comment_end_is_code(self):
        self.assertEqual(self.lines("/* a\n b */ let x = 1;\n"), ["let x = 1;"])

    def test_code_before_block_comment_start_is_code(self):
        self.assertEqual(self.lines("let x = 1; /* start\n end */\n"), ["let x = 1;"])

    def test_trailing_line_comment_is_removed(self):
        self.assertEqual(self.lines("let x = 1; // note\n"), ["let x = 1;"])

    def test_code_line_is_kept_stripped(self):
        self.assertEqual(self.lines("    let x = 1;\n"), ["let x = 1;"])

    def test_comment_marker_inside_string_is_code(self):
        self.assertEqual(self.lines('let u = "http://x";\n'), ['let u = "";'])

    def test_braces_inside_string_are_removed(self):
        self.assertEqual(self.lines('let s = "{[(";\n'), ['let s = "";'])

    def test_escaped_quote_inside_string(self):
        self.assertEqual(self.lines('let s = "a\\"{";\n'), ['let s = "";'])

    def test_char_literal_brace_is_removed(self):
        self.assertEqual(self.lines("let c = '{';\n"), ["let c = ' ';"])

    def test_escaped_char_literal_is_removed(self):
        self.assertEqual(self.lines("let c = '\\'';\n"), ["let c = ' ';"])

    def test_lifetimes_are_kept(self):
        self.assertEqual(self.lines("fn f<'a, 'b>(x: &'a u8) {}\n"),
                         ["fn f<'a, 'b>(x: &'a u8) {}"])

    def test_counts_each_code_line(self):
        self.assertEqual(len(self.lines("a;\n\n// c\nb;\n/* d */\nc;\n")), 3)


class CodeLinesHash(unittest.TestCase):
    def lines(self, text):
        return ctr.code_lines(text, "hash")

    def test_hash_comment_is_not_code(self):
        self.assertEqual(self.lines("# comment\n  # indented\n"), [])

    def test_shebang_is_not_code(self):
        self.assertEqual(self.lines("#!/bin/sh\necho hi\n"), ["echo hi"])

    def test_code_line_is_kept(self):
        self.assertEqual(self.lines("x = 1\n"), ["x = 1"])

    def test_blank_lines_are_not_code(self):
        self.assertEqual(self.lines("\n\n"), [])

    def test_trailing_comment_keeps_the_code(self):
        self.assertEqual(self.lines("x = 1  # note\n"), ["x = 1  # note"])


class CodeLinesPython(unittest.TestCase):
    def lines(self, text):
        return ctr.code_lines(text, "python")

    def test_one_line_docstring_is_not_code(self):
        self.assertEqual(self.lines('"""Docs."""\nx = 1\n'), ["x = 1"])

    def test_multi_line_docstring_is_not_code(self):
        text = 'def f():\n    """Docs.\n\n    More.\n    """\n    return 1\n'
        self.assertEqual(self.lines(text), ["def f():", "return 1"])

    def test_single_quoted_docstring_is_not_code(self):
        self.assertEqual(self.lines("'''Docs\nmore'''\nx = 1\n"), ["x = 1"])

    def test_raw_docstring_is_not_code(self):
        self.assertEqual(self.lines('r"""Docs\\d."""\nx = 1\n'), ["x = 1"])

    def test_assigned_triple_quoted_string_is_code(self):
        text = 'X = """\na\n"""\n'
        self.assertEqual(self.lines(text), ['X = """', "a", '"""'])

    def test_docstring_closing_with_code_after_is_not_split(self):
        text = '"""Docs\nend"""\ny = 2\n'
        self.assertEqual(self.lines(text), ["y = 2"])

    def test_hash_comment_is_not_code(self):
        self.assertEqual(self.lines("# c\nx = 1\n"), ["x = 1"])

    def test_hash_inside_docstring_does_not_end_it(self):
        text = '"""Docs\n# not a comment\n"""\nx = 1\n'
        self.assertEqual(self.lines(text), ["x = 1"])

    def test_python_files_use_python_rules(self):
        self.assertEqual(ctr.language("a.py"), "python")


class Language(unittest.TestCase):
    def test_c_like_extensions(self):
        for name in ("a.rs", "b.kt", "c.kts", "d.java", "e.c", "f.h", "g.swift",
                     "h.go", "i.ts", "j.js", "k.cpp"):
            self.assertEqual(ctr.language(name), "c", name)

    def test_hash_extensions(self):
        for name in ("b.sh", "c.bash"):
            self.assertEqual(ctr.language(name), "hash", name)

    def test_non_code_extensions(self):
        for name in ("README.md", "Cargo.toml", "x.json", "y.yml", "Cargo.lock",
                     "LICENSE", "a.fst", "Makefile"):
            self.assertIsNone(ctr.language(name), name)

    def test_extension_in_directory_name_is_ignored(self):
        self.assertIsNone(ctr.language("dir.rs/README"))


class CfgEvaluation(unittest.TestCase):
    def only_verification(self, attr):
        return ctr.is_verification_attr(attr)

    def test_cfg_test(self):
        self.assertTrue(self.only_verification("#[cfg(test)]"))

    def test_cfg_kani(self):
        self.assertTrue(self.only_verification("#[cfg(kani)]"))

    def test_cfg_hax(self):
        self.assertTrue(self.only_verification("#[cfg(hax)]"))

    def test_cfg_miri(self):
        self.assertTrue(self.only_verification("#[cfg(miri)]"))

    def test_not_hax_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(not(hax))]"))

    def test_any_of_verification_atoms(self):
        self.assertTrue(self.only_verification("#[cfg(any(miri, kani))]"))

    def test_all_with_negated_verification_is_production(self):
        self.assertFalse(self.only_verification(
            "#[cfg(all(unix, not(any(miri, kani))))]"))

    def test_any_with_feature_is_production(self):
        self.assertFalse(self.only_verification('#[cfg(any(test, feature = ""))]'))

    def test_all_with_test_is_verification(self):
        self.assertTrue(self.only_verification("#[cfg(all(test, unix))]"))

    def test_target_os_is_production(self):
        self.assertFalse(self.only_verification('#[cfg(target_os = "")]'))

    def test_platform_atom_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(windows)]"))

    def test_nested_double_negation(self):
        self.assertTrue(self.only_verification("#[cfg(not(not(test)))]"))

    def test_empty_any_is_never_compiled(self):
        self.assertTrue(self.only_verification("#[cfg(any())]"))

    def test_empty_all_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(all())]"))

    def test_unparsable_cfg_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(any(test,]"))

    def test_spaces_inside_attribute(self):
        self.assertTrue(self.only_verification("#[ cfg ( test ) ]"))

    def test_test_attribute(self):
        self.assertTrue(self.only_verification("#[test]"))

    def test_path_test_attribute(self):
        self.assertTrue(self.only_verification("#[tokio::test]"))

    def test_kani_proof_attribute(self):
        self.assertTrue(self.only_verification("#[kani::proof]"))

    def test_kani_unwind_attribute(self):
        self.assertTrue(self.only_verification("#[kani::unwind(5)]"))

    def test_derive_is_production(self):
        self.assertFalse(self.only_verification("#[derive(Debug)]"))

    def test_cfg_attr_is_production(self):
        self.assertFalse(self.only_verification("#[cfg_attr(test, derive(Debug))]"))

    def test_attribute_named_like_test_is_production(self):
        self.assertFalse(self.only_verification("#[testing_helper]"))


class SplitRust(unittest.TestCase):
    def split(self, text):
        return ctr.split_rust(ctr.code_lines(text, "c"))

    def test_plain_code_is_production(self):
        self.assertEqual(self.split("fn f() {\n    1\n}\n"), (3, 0))

    def test_test_module_is_test_code(self):
        text = ("fn f() {}\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    #[test]\n"
                "    fn t() {\n"
                "        assert!(true);\n"
                "    }\n"
                "}\n")
        self.assertEqual(self.split(text), (1, 7))

    def test_code_after_test_module_is_production(self):
        text = "#[cfg(test)]\nmod tests {\n}\nfn after() {}\n"
        self.assertEqual(self.split(text), (1, 3))

    def test_kani_module_with_nested_proofs(self):
        text = ("#[cfg(kani)]\n"
                "mod proofs {\n"
                "    #[kani::proof]\n"
                "    fn p() {\n"
                "        let x: u8 = kani::any();\n"
                "        assert!(x <= 255);\n"
                "    }\n"
                "}\n")
        self.assertEqual(self.split(text), (0, 8))

    def test_test_function_outside_module(self):
        text = "#[test]\nfn t() {\n    assert!(true);\n}\nfn prod() {}\n"
        self.assertEqual(self.split(text), (1, 4))

    def test_single_line_hax_statement(self):
        text = ("fn f(out: &mut [u8]) {\n"
                "    #[cfg(hax)]\n"
                "    hax_lib::loop_invariant!(|_: usize| out.len() == n);\n"
                "    out[0] = 1;\n"
                "}\n")
        self.assertEqual(self.split(text), (3, 2))

    def test_multi_line_hax_statement(self):
        text = ("fn f() {\n"
                "    #[cfg(hax)]\n"
                "    hax_lib::loop_invariant!(\n"
                "        |_: usize| true\n"
                "    );\n"
                "    g();\n"
                "}\n")
        self.assertEqual(self.split(text), (3, 4))

    def test_attribute_and_item_on_one_line(self):
        text = "#[cfg(test)] use std::fmt;\nfn f() {}\n"
        self.assertEqual(self.split(text), (1, 1))

    def test_attribute_and_module_on_one_line(self):
        text = "#[cfg(test)] mod tests {\n    fn t() {}\n}\nfn f() {}\n"
        self.assertEqual(self.split(text), (1, 3))

    def test_not_hax_is_production(self):
        text = "#[cfg(not(hax))]\nfn f() {\n    1\n}\n"
        self.assertEqual(self.split(text), (4, 0))

    def test_derive_attribute_is_production(self):
        text = "#[derive(Debug)]\nstruct S;\n"
        self.assertEqual(self.split(text), (2, 0))

    def test_derive_before_test_cfg(self):
        text = "#[derive(Debug)]\n#[cfg(test)]\nstruct S;\n"
        self.assertEqual(self.split(text), (1, 2))

    def test_external_test_module_declaration(self):
        text = "#[cfg(test)]\nmod tests;\nfn f() {}\n"
        self.assertEqual(self.split(text), (1, 2))

    def test_braces_in_strings_inside_test_module(self):
        text = ('#[cfg(test)]\n'
                'mod tests {\n'
                '    const S: &str = "}}}";\n'
                '    const C: char = \'}\';\n'
                '}\n'
                'fn f() {}\n')
        self.assertEqual(self.split(text), (1, 5))

    def test_multi_line_attribute(self):
        text = ("#[cfg(any(\n"
                "    miri,\n"
                "    kani\n"
                "))]\n"
                "fn stub() {}\n"
                "fn f() {}\n")
        self.assertEqual(self.split(text), (1, 5))

    def test_multi_line_production_attribute(self):
        text = ("#[cfg(all(\n"
                "    unix,\n"
                "    not(any(miri, kani))\n"
                "))]\n"
                "fn real() {}\n")
        self.assertEqual(self.split(text), (5, 0))

    def test_function_signature_over_lines(self):
        text = ("#[test]\n"
                "fn t(\n"
                ") {\n"
                "    assert!(true);\n"
                "}\n"
                "fn f() {}\n")
        self.assertEqual(self.split(text), (1, 5))

    def test_where_clause_and_generics(self):
        text = ("#[cfg(test)]\n"
                "fn helper<T>(x: T) -> Vec<T>\n"
                "where\n"
                "    T: Clone,\n"
                "{\n"
                "    vec![x]\n"
                "}\n"
                "fn f() {}\n")
        self.assertEqual(self.split(text), (1, 7))

    def test_test_block_statement_inside_function(self):
        text = ("fn f() {\n"
                "    #[cfg(kani)]\n"
                "    {\n"
                "        check();\n"
                "    }\n"
                "    run();\n"
                "}\n")
        self.assertEqual(self.split(text), (3, 4))

    def test_two_adjacent_test_items(self):
        text = "#[test]\nfn a() {}\n#[test]\nfn b() {}\n"
        self.assertEqual(self.split(text), (0, 4))

    def test_unterminated_test_item_runs_to_end(self):
        text = "#[cfg(test)]\nmod tests {\n    fn t() {}\n"
        self.assertEqual(self.split(text), (0, 3))

    def test_comments_inside_test_module_are_not_counted(self):
        text = "#[cfg(test)]\nmod tests {\n    // note\n\n    fn t() {}\n}\n"
        self.assertEqual(self.split(text), (0, 4))


class GlobMatching(unittest.TestCase):
    def test_double_star_matches_nested(self):
        self.assertTrue(ctr.matches("a/b/tests/c/d.rs", ["**/tests/**"]))

    def test_double_star_matches_at_root(self):
        self.assertTrue(ctr.matches("tests/d.rs", ["**/tests/**"]))

    def test_single_star_does_not_cross_directories(self):
        self.assertFalse(ctr.matches("a/b/c.rs", ["a/*.rs"]))

    def test_single_star_within_directory(self):
        self.assertTrue(ctr.matches("a/c.rs", ["a/*.rs"]))

    def test_question_mark_matches_one_character(self):
        self.assertTrue(ctr.matches("a1.rs", ["a?.rs"]))
        self.assertFalse(ctr.matches("a12.rs", ["a?.rs"]))

    def test_dots_are_literal(self):
        self.assertFalse(ctr.matches("axrs", ["a.rs"]))

    def test_whole_path_must_match(self):
        self.assertFalse(ctr.matches("x/tests_more.rs", ["tests"]))

    def test_no_patterns_match_nothing(self):
        self.assertFalse(ctr.matches("a.rs", []))

    def test_default_test_paths(self):
        defaults = ctr.DEFAULT_TEST_PATHS
        for path in ("crates/a/tests/t.rs", "tests/t.rs",
                     "app/src/test/java/a/FooTest.kt",
                     "app/src/androidTest/java/a/FooTest.kt",
                     "fuzz/fuzz_targets/f.rs", "scripts/test_x.py", "pkg/x_test.py",
                     "pkg/x_test.go"):
            self.assertTrue(ctr.matches(path, defaults), path)

    def test_default_test_paths_leave_production_alone(self):
        defaults = ctr.DEFAULT_TEST_PATHS
        for path in ("crates/a/src/lib.rs", "app/src/main/java/a/Foo.kt",
                     "src/testing.rs", "scripts/check.py", "src/contest.rs"):
            self.assertFalse(ctr.matches(path, defaults), path)


class Covers(unittest.TestCase):
    def test_single_target(self):
        self.assertEqual(ctr.covers("// covers: src/a.rs\n"), ["src/a.rs"])

    def test_comma_separated_targets(self):
        self.assertEqual(ctr.covers("// covers: src/a.rs, src/b.rs\n"),
                         ["src/a.rs", "src/b.rs"])

    def test_space_separated_targets(self):
        self.assertEqual(ctr.covers("// covers: src/a.rs src/b.rs\n"),
                         ["src/a.rs", "src/b.rs"])

    def test_several_lines(self):
        self.assertEqual(ctr.covers("// covers: a.rs\n// covers: b.rs\n"),
                         ["a.rs", "b.rs"])

    def test_hash_comment(self):
        self.assertEqual(ctr.covers("# covers: a.py\n"), ["a.py"])

    def test_block_comment(self):
        self.assertEqual(ctr.covers("/* covers: a.kt */\n"), ["a.kt"])

    def test_star_for_whole_repository(self):
        self.assertEqual(ctr.covers("# covers: *\n"), ["*"])

    def test_no_covers_line(self):
        self.assertEqual(ctr.covers("fn t() {}\n"), [])

    def test_covers_in_code_is_ignored(self):
        self.assertEqual(ctr.covers('let s = "covers: a.rs";\n'), [])

    def test_only_the_head_of_the_file_is_read(self):
        text = "x\n" * 40 + "// covers: late.rs\n"
        self.assertEqual(ctr.covers(text), [])

    def test_line_forty_is_read(self):
        text = "x\n" * 39 + "// covers: a.rs\n"
        self.assertEqual(ctr.covers(text), ["a.rs"])


class Config(unittest.TestCase):
    def test_defaults_without_file(self):
        tmp, root = make_repo({})
        with tmp:
            config = ctr.load_config(root)
        self.assertEqual(config.test_paths, ctr.DEFAULT_TEST_PATHS)
        self.assertEqual(config.ignore, ())

    def test_extra_test_paths_are_added_to_defaults(self):
        tmp, root = make_repo({"test-ratio.toml": 'test_paths = ["tools/**"]\n'})
        with tmp:
            config = ctr.load_config(root)
        self.assertEqual(config.test_paths, ctr.DEFAULT_TEST_PATHS + ("tools/**",))

    def test_ignore_paths(self):
        tmp, root = make_repo({"test-ratio.toml": 'ignore = ["gen/**"]\n'})
        with tmp:
            config = ctr.load_config(root)
        self.assertEqual(config.ignore, ("gen/**",))

    def test_ratio_cannot_be_configured(self):
        tmp, root = make_repo({"test-ratio.toml": "ratio = 1\n"})
        with tmp, self.assertRaises(ctr.ConfigError) as caught:
            ctr.load_config(root)
        self.assertIn("ratio", str(caught.exception))
        self.assertIn("3:1", str(caught.exception))

    def test_unknown_key_is_an_error(self):
        tmp, root = make_repo({"test-ratio.toml": "exclude = []\n"})
        with tmp, self.assertRaises(ctr.ConfigError):
            ctr.load_config(root)

    def test_wrong_type_is_an_error(self):
        tmp, root = make_repo({"test-ratio.toml": 'test_paths = "tools/**"\n'})
        with tmp, self.assertRaises(ctr.ConfigError):
            ctr.load_config(root)

    def test_non_string_entry_is_an_error(self):
        tmp, root = make_repo({"test-ratio.toml": "ignore = [1]\n"})
        with tmp, self.assertRaises(ctr.ConfigError):
            ctr.load_config(root)

    def test_invalid_toml_is_an_error(self):
        tmp, root = make_repo({"test-ratio.toml": "test_paths = [\n"})
        with tmp, self.assertRaises(ctr.ConfigError):
            ctr.load_config(root)


class Measure(unittest.TestCase):
    def measure(self, files, config_text=None):
        if config_text is not None:
            files = dict(files, **{"test-ratio.toml": config_text})
        tmp, root = make_repo(files)
        with tmp:
            config = ctr.load_config(root)
            return ctr.measure(root, sorted(files), config)

    def kinds(self, report):
        return [(f.kind, f.name) for f in report.failures]

    def test_exactly_three_to_one_passes(self):
        report = self.measure({
            "src/a.rs": rust_lines(2),
            "tests/a.rs": "// covers: src/a.rs\n" + rust_lines(6),
        })
        self.assertEqual(report.failures, [])
        self.assertEqual(report.errors, [])

    def test_just_below_three_to_one_fails(self):
        report = self.measure({
            "src/a.rs": rust_lines(2),
            "tests/a.rs": "// covers: src/a.rs\n" + rust_lines(5),
        })
        self.assertIn(("file", "src/a.rs"), self.kinds(report))
        self.assertIn(("repository", "."), self.kinds(report))

    def test_failure_reports_counts(self):
        report = self.measure({"src/a.rs": rust_lines(4)})
        failure = report.failures[0]
        self.assertEqual((failure.production, failure.test), (4, 0))
        self.assertEqual(failure.missing, 12)

    def test_in_file_tests_count_for_the_file(self):
        text = rust_lines(1) + "#[cfg(test)]\nmod tests {\n    fn t() {}\n}\n"
        report = self.measure({"src/a.rs": text})
        self.assertEqual(report.failures, [])
        self.assertEqual(report.files["src/a.rs"].test, 4)

    def test_attribution_is_split_between_targets(self):
        report = self.measure({
            "src/a.rs": rust_lines(1),
            "src/b.rs": rust_lines(1),
            "tests/ab.rs": "// covers: src/a.rs, src/b.rs\n" + rust_lines(6),
        })
        self.assertEqual(report.files["src/a.rs"].test, 3)
        self.assertEqual(report.files["src/b.rs"].test, 3)
        self.assertEqual(report.failures, [])

    def test_uneven_split_is_fractional(self):
        report = self.measure({
            "src/a.rs": rust_lines(1),
            "src/b.rs": rust_lines(1),
            "tests/ab.rs": "// covers: src/a.rs, src/b.rs\n" + rust_lines(5),
        })
        self.assertEqual(report.files["src/a.rs"].test, 2.5)
        self.assertIn(("file", "src/a.rs"), self.kinds(report))

    def test_repository_wide_tests_count_only_for_the_repository(self):
        report = self.measure({
            "src/a.rs": rust_lines(1),
            "scripts/test_all.py": "# covers: *\n" + "x = 1\n" * 3,
        })
        self.assertIn(("file", "src/a.rs"), self.kinds(report))
        self.assertNotIn(("repository", "."), self.kinds(report))
        self.assertEqual(report.repo_test, 3)

    def test_star_mixed_with_paths_is_an_error(self):
        report = self.measure({
            "src/a.rs": rust_lines(1),
            "tests/a.rs": "// covers: *, src/a.rs\n" + rust_lines(3),
        })
        self.assertTrue(any("tests/a.rs" in e for e in report.errors))

    def test_test_file_without_covers_is_an_error(self):
        report = self.measure({"tests/a.rs": rust_lines(3)})
        self.assertTrue(any("tests/a.rs" in e and "covers" in e for e in report.errors))

    def test_covers_unknown_file_is_an_error(self):
        report = self.measure({"tests/a.rs": "// covers: src/gone.rs\n" + rust_lines(3)})
        self.assertTrue(any("src/gone.rs" in e for e in report.errors))

    def test_covers_a_test_file_is_an_error(self):
        report = self.measure({
            "tests/a.rs": "// covers: tests/b.rs\n" + rust_lines(3),
            "tests/b.rs": "// covers: *\n" + rust_lines(3),
        })
        self.assertTrue(any("tests/b.rs" in e for e in report.errors))

    def test_ignored_files_are_skipped(self):
        report = self.measure({"gen/a.rs": rust_lines(9)}, 'ignore = ["gen/**"]\n')
        self.assertEqual(report.failures, [])
        self.assertEqual(report.repo_prod, 0)

    def test_configured_test_paths(self):
        report = self.measure({
            "src/a.rs": rust_lines(1),
            "tools/check/main.rs": "// covers: src/a.rs\n" + rust_lines(3),
        }, 'test_paths = ["tools/**"]\n')
        self.assertEqual(report.failures, [])

    def test_non_code_files_are_skipped(self):
        report = self.measure({"README.md": "text\n" * 50, "Cargo.toml": "[package]\n"})
        self.assertEqual(report.failures, [])
        self.assertEqual(report.repo_prod, 0)

    def test_no_production_code_passes(self):
        report = self.measure({})
        self.assertEqual(report.failures, [])
        self.assertEqual(report.errors, [])

    def test_comment_only_production_file_passes(self):
        report = self.measure({"src/lib.rs": "//! Docs only.\n"})
        self.assertEqual(report.failures, [])

    def test_units_follow_the_nearest_manifest(self):
        report = self.measure({
            "Cargo.toml": "[workspace]\n",
            "crates/good/Cargo.toml": "[package]\n",
            "crates/good/src/lib.rs": rust_lines(1),
            "crates/good/tests/t.rs": "// covers: crates/good/src/lib.rs\n" + rust_lines(3),
            "crates/bad/Cargo.toml": "[package]\n",
            "crates/bad/src/lib.rs": rust_lines(1),
        })
        self.assertIn(("unit", "crates/bad"), self.kinds(report))
        self.assertNotIn(("unit", "crates/good"), self.kinds(report))
        self.assertEqual(report.units["crates/good"], (1, 3))

    def test_unit_without_manifest_is_the_root(self):
        report = self.measure({"src/a.rs": rust_lines(1)})
        self.assertIn(("unit", "."), self.kinds(report))

    def test_gradle_module_is_a_unit(self):
        report = self.measure({
            "app/build.gradle.kts": "plugins {}\n",
            "app/src/main/java/a/Foo.kt": "class Foo {\n}\n",
            "app/src/test/java/a/FooTest.kt":
                "// covers: app/src/main/java/a/Foo.kt\n" + "val x = 1\n" * 6,
        }, 'ignore = ["**/build.gradle.kts"]\n')
        self.assertEqual(report.units["app"], (2, 6))
        self.assertEqual(report.failures, [])

    def test_kotlin_production_has_no_in_file_tests(self):
        report = self.measure({"src/Foo.kt": "@Test\nfun t() {}\n"})
        self.assertEqual(report.files["src/Foo.kt"].production, 2)

    def test_python_production_is_counted(self):
        report = self.measure({"tool/run.py": "import os\nprint(os.name)\n"})
        self.assertEqual(report.files["tool/run.py"].production, 2)

    def test_repository_totals(self):
        report = self.measure({
            "src/a.rs": rust_lines(2),
            "tests/a.rs": "// covers: src/a.rs\n" + rust_lines(6),
            "scripts/test_x.py": "# covers: *\n" + "x = 1\n" * 4,
        })
        self.assertEqual((report.repo_prod, report.repo_test), (2, 10))

    def test_failures_are_sorted_file_unit_repository(self):
        report = self.measure({"src/b.rs": rust_lines(1), "src/a.rs": rust_lines(1)})
        self.assertEqual(self.kinds(report), [
            ("file", "src/a.rs"), ("file", "src/b.rs"), ("unit", "."), ("repository", ".")])

    def test_missing_rounds_up(self):
        report = self.measure({
            "src/a.rs": rust_lines(1),
            "src/b.rs": rust_lines(1),
            "tests/ab.rs": "// covers: src/a.rs, src/b.rs\n" + rust_lines(5),
        })
        failure = report.failures[0]
        self.assertEqual(failure.missing, 1)


class ListFiles(unittest.TestCase):
    def test_walk_skips_build_output(self):
        tmp, root = make_repo({
            "src/a.rs": "x\n",
            "target/debug/b.rs": "x\n",
            "build/c.kt": "x\n",
            "node_modules/d.js": "x\n",
            ".git/e.rs": "x\n",
        })
        with tmp:
            files = ctr.list_files(root, use_git=False)
        self.assertEqual(files, ["src/a.rs"])

    def test_walk_returns_posix_paths_sorted(self):
        tmp, root = make_repo({"b/x.rs": "x\n", "a/y.rs": "x\n"})
        with tmp:
            files = ctr.list_files(root, use_git=False)
        self.assertEqual(files, ["a/y.rs", "b/x.rs"])


class Main(unittest.TestCase):
    def run_in(self, files, *args):
        tmp, root = make_repo(files)
        with tmp:
            return run_main([str(root), "--no-git", *args])

    def test_passing_repository_exits_zero(self):
        code, out, _ = self.run_in({
            "src/a.rs": rust_lines(1),
            "tests/a.rs": "// covers: src/a.rs\n" + rust_lines(3),
        })
        self.assertEqual(code, 0)
        self.assertIn("OK", out)
        self.assertIn("3.00:1", out)

    def test_failing_repository_exits_one(self):
        code, out, _ = self.run_in({"src/a.rs": rust_lines(2)})
        self.assertEqual(code, 1)
        self.assertIn("FAIL file src/a.rs", out)
        self.assertIn("2 production", out)
        self.assertIn("6 more test lines", out)

    def test_errors_exit_one(self):
        code, out, _ = self.run_in({"tests/a.rs": rust_lines(3)})
        self.assertEqual(code, 1)
        self.assertIn("ERROR", out)

    def test_bad_config_exits_two(self):
        code, _, err = self.run_in({"test-ratio.toml": "ratio = 1\n"})
        self.assertEqual(code, 2)
        self.assertIn("ratio", err)

    def test_all_lists_passing_files(self):
        code, out, _ = self.run_in({
            "src/a.rs": rust_lines(1),
            "tests/a.rs": "// covers: src/a.rs\n" + rust_lines(3),
        }, "--all")
        self.assertEqual(code, 0)
        self.assertIn("src/a.rs", out)

    def test_without_all_passing_files_are_not_listed(self):
        code, out, _ = self.run_in({
            "src/a.rs": rust_lines(1),
            "tests/a.rs": "// covers: src/a.rs\n" + rust_lines(3),
        })
        self.assertNotIn("src/a.rs", out)

    def test_empty_repository_passes(self):
        code, out, _ = self.run_in({})
        self.assertEqual(code, 0)
        self.assertIn("no production code", out)


class ScanCEdgeCases(unittest.TestCase):
    def lines(self, text):
        return ctr.code_lines(text, "c")

    def test_block_comment_marker_inside_string_is_code(self):
        self.assertEqual(self.lines('let s = "/*";\nlet t = 1;\n'),
                         ['let s = "";', "let t = 1;"])

    def test_unclosed_string_ends_at_line_end(self):
        self.assertEqual(self.lines('let s = "abc\nlet t = 1;\n'),
                         ['let s = ""', "let t = 1;"])

    def test_two_strings_on_one_line(self):
        self.assertEqual(self.lines('f("{", "}");\n'), ['f("", "");'])

    def test_empty_string(self):
        self.assertEqual(self.lines('let s = "";\n'), ['let s = "";'])

    def test_escaped_backslash_before_quote_ends_string(self):
        self.assertEqual(self.lines('let s = "a\\\\"; let t = "{";\n'),
                         ['let s = ""; let t = "";'])

    def test_newline_char_literal(self):
        self.assertEqual(self.lines("let c = '\\n';\n"), ["let c = ' ';"])

    def test_two_block_comments_on_one_line(self):
        self.assertEqual(self.lines("a /* x */ b /* y */ c\n"), ["a   b   c"])

    def test_line_comment_after_block_comment(self):
        self.assertEqual(self.lines("/* x */ // y\n"), [])

    def test_block_comment_start_inside_line_comment_is_ignored(self):
        self.assertEqual(self.lines("// a /* b\nlet x = 1;\n"), ["let x = 1;"])

    def test_star_lines_in_block_comment(self):
        self.assertEqual(self.lines("/**\n * Docs.\n * More.\n */\nfn f() {}\n"),
                         ["fn f() {}"])

    def test_kotlin_code(self):
        text = "package a\n\n// c\nclass Foo {\n    fun bar() = 1\n}\n"
        self.assertEqual(len(self.lines(text)), 4)

    def test_windows_line_endings(self):
        self.assertEqual(self.lines("a;\r\n// c\r\nb;\r\n"), ["a;", "b;"])


class CodeLinesPythonEdgeCases(unittest.TestCase):
    def lines(self, text):
        return ctr.code_lines(text, "python")

    def test_function_docstring_after_signature(self):
        text = ('def f(x):\n'
                '    """Return x."""\n'
                '    return x\n')
        self.assertEqual(self.lines(text), ["def f(x):", "return x"])

    def test_class_docstring_over_lines(self):
        text = ('class C:\n'
                '    """A class.\n'
                '\n'
                '    Details.\n'
                '    """\n'
                '\n'
                '    x = 1\n')
        self.assertEqual(self.lines(text), ["class C:", "x = 1"])

    def test_assigned_single_quoted_triple_string(self):
        text = "X = '''\none\ntwo\n'''\ny = 1\n"
        self.assertEqual(self.lines(text), ["X = '''", "one", "two", "'''", "y = 1"])

    def test_triple_string_closed_on_same_line_is_one_line(self):
        self.assertEqual(self.lines('X = """a"""\ny = 1\n'), ['X = """a"""', "y = 1"])

    def test_blank_lines_inside_assigned_string_are_not_code(self):
        text = 'X = """\n\nb\n"""\n'
        self.assertEqual(self.lines(text), ['X = """', "b", '"""'])

    def test_unicode_prefixed_docstring(self):
        self.assertEqual(self.lines('u"""Docs."""\nx = 1\n'), ["x = 1"])

    def test_unclosed_docstring_runs_to_end(self):
        self.assertEqual(self.lines('x = 1\n"""Docs\nmore\n'), ["x = 1"])

    def test_indented_comment(self):
        self.assertEqual(self.lines("def f():\n    # c\n    return 1\n"),
                         ["def f():", "return 1"])


class CfgEdgeCases(unittest.TestCase):
    def only_verification(self, attr):
        return ctr.is_verification_attr(attr)

    def test_any_of_two_verification_cfgs(self):
        self.assertTrue(self.only_verification("#[cfg(any(test, kani))]"))

    def test_all_of_two_verification_cfgs(self):
        self.assertTrue(self.only_verification("#[cfg(all(kani, hax))]"))

    def test_not_any_test_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(not(any(test)))]"))

    def test_all_not_test_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(all(not(test)))]"))

    def test_any_including_negation_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(any(not(test), test))]"))

    def test_key_value_named_test_is_production(self):
        self.assertFalse(self.only_verification('#[cfg(test = "")]'))

    def test_bare_feature_atom_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(feature)]"))

    def test_not_with_two_arguments_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(not(test, kani))]"))

    def test_unknown_function_is_production(self):
        self.assertFalse(self.only_verification("#[cfg(xor(test))]"))

    def test_trailing_tokens_are_production(self):
        self.assertFalse(self.only_verification("#[cfg(test, kani)]"))

    def test_trailing_comma_in_any(self):
        self.assertTrue(self.only_verification("#[cfg(any(test, kani,))]"))

    def test_empty_cfg_is_production(self):
        self.assertFalse(self.only_verification("#[cfg()]"))

    def test_attribute_split_over_lines(self):
        self.assertTrue(self.only_verification("#[cfg(any( miri, kani ))]"))

    def test_test_case_attribute_is_production(self):
        self.assertFalse(self.only_verification("#[test_case(1)]"))

    def test_should_panic_is_production(self):
        self.assertFalse(self.only_verification("#[should_panic]"))

    def test_allow_is_production(self):
        self.assertFalse(self.only_verification("#[allow(dead_code)]"))

    def test_kani_stub_attribute(self):
        self.assertTrue(self.only_verification("#[kani::stub(a, b)]"))

    def test_nested_path_test_attribute(self):
        self.assertTrue(self.only_verification("#[a::b::test]"))


class SplitRustEdgeCases(unittest.TestCase):
    def split(self, text):
        return ctr.split_rust(ctr.code_lines(text, "c"))

    def test_inner_attribute_is_production(self):
        self.assertEqual(self.split("#![forbid(unsafe_code)]\nfn f() {}\n"), (2, 0))

    def test_test_impl_block(self):
        text = ("#[cfg(test)]\n"
                "impl S {\n"
                "    fn helper(&self) {}\n"
                "}\n"
                "impl S {}\n")
        self.assertEqual(self.split(text), (1, 4))

    def test_test_enum(self):
        text = "#[cfg(test)]\nenum E {\n    A,\n    B,\n}\n"
        self.assertEqual(self.split(text), (0, 5))

    def test_test_const_array(self):
        text = "#[cfg(test)]\nconst V: [u8; 3] = [\n    1, 2, 3,\n];\nconst W: u8 = 0;\n"
        self.assertEqual(self.split(text), (1, 4))

    def test_two_attributes_on_a_test(self):
        text = "#[test]\n#[should_panic]\nfn t() {\n    panic!();\n}\nfn f() {}\n"
        self.assertEqual(self.split(text), (1, 5))

    def test_allow_before_test_module(self):
        text = "#[allow(dead_code)]\n#[cfg(test)]\nmod tests {\n}\n"
        self.assertEqual(self.split(text), (1, 3))

    def test_attribute_with_brackets_in_string(self):
        text = '#[doc = "[x]"]\nfn f() {}\n'
        self.assertEqual(self.split(text), (2, 0))

    def test_closure_inside_test_item(self):
        text = ("#[test]\n"
                "fn t() {\n"
                "    let f = |x: u8| { x + 1 };\n"
                "    assert_eq!(f(1), 2);\n"
                "}\n"
                "fn g() {}\n")
        self.assertEqual(self.split(text), (1, 5))

    def test_kani_harness_in_production_function_body(self):
        text = ("fn f() {\n"
                "    #[cfg(kani)]\n"
                "    kani::assume(true);\n"
                "    #[cfg(not(kani))]\n"
                "    run();\n"
                "}\n")
        self.assertEqual(self.split(text), (4, 2))

    def test_macro_rules_under_test(self):
        text = ("#[cfg(test)]\n"
                "macro_rules! check {\n"
                "    ($e:expr) => { assert!($e) };\n"
                "}\n"
                "fn f() {}\n")
        self.assertEqual(self.split(text), (1, 4))

    def test_unterminated_attribute_counts_to_end(self):
        self.assertEqual(self.split("#[cfg(test\nfn f() {}\n"), (2, 0))

    def test_empty_file(self):
        self.assertEqual(self.split(""), (0, 0))

    def test_test_attribute_on_last_line(self):
        self.assertEqual(self.split("fn f() {}\n#[test]\n"), (1, 1))


class GlobEdgeCases(unittest.TestCase):
    def test_trailing_double_star_matches_direct_child(self):
        self.assertTrue(ctr.matches("fuzz/a.rs", ["fuzz/**"]))

    def test_trailing_double_star_needs_the_directory(self):
        self.assertFalse(ctr.matches("fuzzy/a.rs", ["fuzz/**"]))

    def test_leading_double_star_alone_matches_everything(self):
        self.assertTrue(ctr.matches("a/b/c.rs", ["**"]))

    def test_regex_characters_are_literal(self):
        self.assertTrue(ctr.matches("a+(b).rs", ["a+(b).rs"]))
        self.assertFalse(ctr.matches("aa(b).rs", ["a+(b).rs"]))

    def test_any_pattern_can_match(self):
        self.assertTrue(ctr.matches("b.rs", ["a.rs", "b.rs"]))

    def test_star_in_middle_of_name(self):
        self.assertTrue(ctr.matches("src/fooTest/a.kt", ["src/*Test/**"]))


class CoversEdgeCases(unittest.TestCase):
    def test_extra_spaces(self):
        self.assertEqual(ctr.covers("//   covers:    a.rs  \n"), ["a.rs"])

    def test_no_targets(self):
        self.assertEqual(ctr.covers("// covers:\n"), [])

    def test_keyword_is_case_sensitive(self):
        self.assertEqual(ctr.covers("// Covers: a.rs\n"), [])

    def test_block_comment_continuation_line(self):
        self.assertEqual(ctr.covers("/*\n * covers: a.kt\n */\n"), ["a.kt"])

    def test_doc_comment_style(self):
        self.assertEqual(ctr.covers("//! covers: a.rs\n"), [])

    def test_after_module_docstring(self):
        text = '"""Tests."""\n\n# covers: scripts/a.py\n'
        self.assertEqual(ctr.covers(text), ["scripts/a.py"])


class Units(unittest.TestCase):
    def unit(self, files, path):
        tmp, root = make_repo(files)
        with tmp:
            return ctr.unit_of(root, path)

    def test_nearest_manifest_wins(self):
        files = {"Cargo.toml": "", "crates/a/Cargo.toml": "", "crates/a/src/x/y.rs": ""}
        self.assertEqual(self.unit(files, "crates/a/src/x/y.rs"), "crates/a")

    def test_root_manifest(self):
        self.assertEqual(self.unit({"Cargo.toml": "", "src/a.rs": ""}, "src/a.rs"), ".")

    def test_no_manifest_is_root(self):
        self.assertEqual(self.unit({"src/a.rs": ""}, "src/a.rs"), ".")

    def test_manifest_beside_file(self):
        self.assertEqual(self.unit({"tool/pyproject.toml": "", "tool/a.py": ""},
                                   "tool/a.py"), "tool")

    def test_each_manifest_kind(self):
        for manifest in ctr.UNIT_MANIFESTS:
            files = {f"m/{manifest}": "", "m/src/a.x": ""}
            self.assertEqual(self.unit(files, "m/src/a.x"), "m", manifest)

    def test_file_at_root(self):
        self.assertEqual(self.unit({"a.rs": ""}, "a.rs"), ".")


class ListFilesWithGit(unittest.TestCase):
    def git(self, root, *args):
        import subprocess
        subprocess.run(["git", "-C", str(root), *args], check=True,
                       capture_output=True)

    def test_only_tracked_files_are_listed(self):
        tmp, root = make_repo({"src/a.rs": "x\n", "src/untracked.rs": "x\n"})
        with tmp:
            self.git(root, "init", "-q")
            self.git(root, "add", "src/a.rs")
            files = ctr.list_files(root)
        self.assertEqual(files, ["src/a.rs"])

    def test_outside_git_falls_back_to_walking(self):
        tmp, root = make_repo({"src/a.rs": "x\n"})
        with tmp:
            os.environ["GIT_CEILING_DIRECTORIES"] = str(root.parent)
            try:
                files = ctr.list_files(root)
            finally:
                del os.environ["GIT_CEILING_DIRECTORIES"]
        self.assertEqual(files, ["src/a.rs"])


class MeasureEdgeCases(unittest.TestCase):
    def measure(self, files, config_text=None):
        if config_text is not None:
            files = dict(files, **{"test-ratio.toml": config_text})
        tmp, root = make_repo(files)
        with tmp:
            return ctr.measure(root, sorted(files), ctr.load_config(root))

    def test_ignore_wins_over_test_paths(self):
        report = self.measure({"tests/gen.rs": rust_lines(3)}, 'ignore = ["tests/gen.rs"]\n')
        self.assertEqual(report.errors, [])
        self.assertEqual(report.repo_test, 0)

    def test_shell_script_outside_test_paths_is_production(self):
        report = self.measure({"tool/run.sh": "#!/bin/sh\necho hi\n"})
        self.assertEqual(report.files["tool/run.sh"].production, 1)

    def test_kotlin_test_file(self):
        report = self.measure({
            "app/src/main/java/Foo.kt": "class Foo\n",
            "app/src/test/java/FooTest.kt":
                "// covers: app/src/main/java/Foo.kt\n" + "val a = 1\n" * 3,
        })
        self.assertEqual(report.failures, [])

    def test_in_file_tests_count_toward_the_repository(self):
        text = rust_lines(1) + "#[test]\nfn t() {}\n"
        report = self.measure({"src/a.rs": text})
        self.assertEqual((report.repo_prod, report.repo_test), (1, 2))

    def test_file_with_only_in_file_tests_passes(self):
        report = self.measure({"src/a.rs": "#[test]\nfn t() {}\n"})
        self.assertEqual(report.failures, [])

    def test_attribution_crosses_units(self):
        report = self.measure({
            "a/Cargo.toml": "",
            "a/src/lib.rs": rust_lines(1),
            "b/Cargo.toml": "",
            "b/tests/t.rs": "// covers: a/src/lib.rs\n" + rust_lines(3),
        })
        self.assertEqual(report.units["a"], (1, 3))
        self.assertEqual(report.failures, [])

    def test_same_target_twice_counts_fully(self):
        report = self.measure({
            "src/a.rs": rust_lines(1),
            "tests/a.rs": "// covers: src/a.rs, src/a.rs\n" + rust_lines(3),
        })
        self.assertEqual(report.files["src/a.rs"].test, 3)

    def test_unit_totals_add_files(self):
        report = self.measure({
            "Cargo.toml": "",
            "src/a.rs": rust_lines(1),
            "src/b.rs": rust_lines(2),
        })
        self.assertEqual(report.units["."], (3, 0))

    def test_one_failing_file_fails_a_passing_unit(self):
        report = self.measure({
            "src/a.rs": rust_lines(1),
            "src/b.rs": rust_lines(1) + "#[cfg(test)]\nmod t {\n" + rust_lines(6) + "}\n",
        })
        kinds = [(f.kind, f.name) for f in report.failures]
        self.assertEqual(kinds, [("file", "src/a.rs")])

    def test_file_read_with_invalid_utf8(self):
        tmp, root = make_repo({})
        with tmp:
            (root / "a.rs").write_bytes(b"let x = 1;\n\xff\xfe\n")
            report = ctr.measure(root, ["a.rs"], ctr.load_config(root))
        self.assertEqual(report.files["a.rs"].production, 2)

    def test_report_defaults_are_empty(self):
        report = ctr.Report()
        self.assertEqual((report.files, report.units, report.errors, report.failures),
                         ({}, {}, [], []))
        self.assertEqual((report.repo_prod, report.repo_test), (0, 0))


class FailureMissing(unittest.TestCase):
    def test_exact_shortfall(self):
        self.assertEqual(ctr.Failure("file", "a", 10, 20).missing, 10)

    def test_fractional_shortfall_rounds_up(self):
        self.assertEqual(ctr.Failure("file", "a", 1, 2.1).missing, 1)

    def test_no_tests(self):
        self.assertEqual(ctr.Failure("file", "a", 5, 0).missing, 15)


class MainOutput(unittest.TestCase):
    def run_in(self, files, *args):
        tmp, root = make_repo(files)
        with tmp:
            return run_main([str(root), "--no-git", *args])

    def test_summary_line(self):
        _, out, _ = self.run_in({
            "src/a.rs": rust_lines(1),
            "tests/a.rs": "// covers: src/a.rs\n" + rust_lines(3),
        })
        self.assertEqual(out.strip().splitlines()[-1],
                         "test-ratio: OK, repository 1 production, 3 test lines (3.00:1); "
                         "required 3:1 per file, unit and repository")

    def test_failure_line(self):
        _, out, _ = self.run_in({"src/a.rs": rust_lines(1)})
        self.assertIn("FAIL file src/a.rs: 1 production, 0 test lines (0.00:1); "
                      "3 more test lines needed", out)

    def test_fractional_test_lines_are_shown(self):
        _, out, _ = self.run_in({
            "src/a.rs": rust_lines(1),
            "src/b.rs": rust_lines(1),
            "tests/ab.rs": "// covers: src/a.rs, src/b.rs\n" + rust_lines(5),
        })
        self.assertIn("2.5 test lines", out)

    def test_all_shows_files_without_production(self):
        _, out, _ = self.run_in({"src/a.rs": "#[test]\nfn t() {}\n"}, "--all")
        self.assertIn("src/a.rs: 0 production, 2 test lines (inf:1)", out)

    def test_errors_come_before_failures(self):
        _, out, _ = self.run_in({"src/a.rs": rust_lines(1), "tests/x.rs": rust_lines(1)})
        lines = out.splitlines()
        first_error = next(i for i, l in enumerate(lines) if l.startswith("ERROR"))
        first_fail = next(i for i, l in enumerate(lines) if l.startswith("FAIL"))
        self.assertLess(first_error, first_fail)

    def test_errors_alone_fail_the_summary(self):
        _, out, _ = self.run_in({"tests/x.rs": rust_lines(1)})
        self.assertIn("test-ratio: FAILED, no production code", out)

    def test_default_root_is_current_directory(self):
        tmp, root = make_repo({"src/a.rs": rust_lines(1)})
        with tmp:
            cwd = os.getcwd()
            os.chdir(root)
            try:
                code, out, _ = run_main(["--no-git"])
            finally:
                os.chdir(cwd)
        self.assertEqual(code, 1)
        self.assertIn("src/a.rs", out)

    def test_help_describes_the_check(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit):
            ctr.main(["--help"])
        self.assertIn("test-to-code ratio", out.getvalue())


class ConfigEdgeCases(unittest.TestCase):
    def test_empty_file_gives_defaults(self):
        tmp, root = make_repo({"test-ratio.toml": ""})
        with tmp:
            config = ctr.load_config(root)
        self.assertEqual(config, ctr.Config(ctr.DEFAULT_TEST_PATHS, ()))

    def test_both_keys(self):
        tmp, root = make_repo({"test-ratio.toml":
                               'test_paths = ["t/**"]\nignore = ["g/**"]\n'})
        with tmp:
            config = ctr.load_config(root)
        self.assertEqual(config.test_paths[-1], "t/**")
        self.assertEqual(config.ignore, ("g/**",))

    def test_root_as_string(self):
        tmp, root = make_repo({"test-ratio.toml": 'ignore = ["g/**"]\n'})
        with tmp:
            config = ctr.load_config(str(root))
        self.assertEqual(config.ignore, ("g/**",))

    def test_error_names_the_file(self):
        tmp, root = make_repo({"test-ratio.toml": "x = 1\n"})
        with tmp, self.assertRaises(ctr.ConfigError) as caught:
            ctr.load_config(root)
        self.assertIn("test-ratio.toml", str(caught.exception))

    def test_ratio_constant_is_three(self):
        self.assertEqual(ctr.RATIO, 3)


CORE_LIKE_BASE32 = """\
//! Base32 without padding.

use crate::Error;

/// Encode `input` into `out`.
pub fn encode(input: &[u8], out: &mut [u8]) -> Result<usize, Error> {
    let out_len = out.len();
    for blk in 0..input.len() / 5 {
        #[cfg(hax)]
        hax_lib::loop_invariant!(|_: usize| out.len() == out_len);
        out[blk] = input[blk];
    }
    Ok(out_len)
}

#[cfg(not(hax))]
fn table() -> &'static [u8; 32] {
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty() {
        let mut out = [0u8; 0];
        assert_eq!(encode(&[], &mut out), Ok(0));
    }
}

#[cfg(kani)]
mod proofs {
    use super::*;

    #[kani::proof]
    #[kani::unwind(3)]
    fn never_panics() {
        let input: [u8; 5] = kani::any();
        let mut out = [0u8; 8];
        let _ = encode(&input, &mut out);
    }
}
"""

CORE_LIKE_SECURE_MEM = """\
#[cfg(any(miri, kani))]
fn lock(_p: *mut u8, _n: usize) -> bool {
    true
}

#[cfg(all(unix, not(any(miri, kani))))]
fn lock(p: *mut u8, n: usize) -> bool {
    unsafe { libc::mlock(p.cast(), n) == 0 }
}
"""


class CoreLikeRepository(unittest.TestCase):
    """A small copy of mosgird/core's layout, with known counts."""

    def setUp(self):
        self.tmp, self.root = make_repo({
            "Cargo.toml": "[workspace]\n",
            "test-ratio.toml": 'test_paths = ["tools/**", "scripts/**"]\n',
            "crates/protocol/Cargo.toml": "[package]\n",
            "crates/protocol/src/lib.rs": "pub mod base32;\n",
            "crates/protocol/src/base32.rs": CORE_LIKE_BASE32,
            "crates/core/Cargo.toml": "[package]\n",
            "crates/core/src/secure_mem.rs": CORE_LIKE_SECURE_MEM,
            "fuzz/Cargo.toml": "[package]\n",
            "fuzz/fuzz_targets/round_trip.rs":
                "// covers: crates/protocol/src/base32.rs\n" + rust_lines(10),
            "tools/ct-check/Cargo.toml": "[package]\n",
            "tools/ct-check/src/main.rs":
                "// covers: crates/protocol/src/base32.rs, crates/core/src/secure_mem.rs\n"
                + rust_lines(8),
            "scripts/ct_check.sh": "#!/bin/sh\n# covers: *\nvalgrind \"$1\"\n",
            "README.md": "# core\n",
        })
        config = ctr.load_config(self.root)
        self.report = ctr.measure(self.root, ctr.list_files(self.root, use_git=False), config)

    def tearDown(self):
        self.tmp.cleanup()

    def test_base32_production_lines(self):
        # use, fn encode, let, for, out[blk], }, Ok, }, plus 4 lines of
        # #[cfg(not(hax))] fn table: 12.
        self.assertEqual(self.report.files["crates/protocol/src/base32.rs"].production, 12)

    def test_base32_test_lines(self):
        # hax invariant 2, tests module 9, proofs module 11, fuzz 10, tool 4.
        self.assertEqual(self.report.files["crates/protocol/src/base32.rs"].test, 36)

    def test_base32_is_exactly_three_to_one(self):
        kinds = [(f.kind, f.name) for f in self.report.failures]
        self.assertNotIn(("file", "crates/protocol/src/base32.rs"), kinds)

    def test_secure_mem_split(self):
        count = self.report.files["crates/core/src/secure_mem.rs"]
        self.assertEqual((count.production, count.test), (4, 8))

    def test_lib_has_no_tests(self):
        count = self.report.files["crates/protocol/src/lib.rs"]
        self.assertEqual((count.production, count.test), (1, 0))

    def test_test_tools_are_not_production_files(self):
        self.assertNotIn("tools/ct-check/src/main.rs", self.report.files)
        self.assertNotIn("fuzz/fuzz_targets/round_trip.rs", self.report.files)
        self.assertNotIn("scripts/ct_check.sh", self.report.files)

    def test_units(self):
        self.assertEqual(self.report.units["crates/protocol"], (13, 36))
        self.assertEqual(self.report.units["crates/core"], (4, 8))

    def test_repository_totals(self):
        # Test lines: in-file 22 + 4, fuzz 10, tool 8, script 1.
        self.assertEqual((self.report.repo_prod, self.report.repo_test), (17, 45))

    def test_failures(self):
        kinds = [(f.kind, f.name) for f in self.report.failures]
        self.assertEqual(kinds, [
            ("file", "crates/core/src/secure_mem.rs"),
            ("file", "crates/protocol/src/lib.rs"),
            ("unit", "crates/core"),
            ("unit", "crates/protocol"),
            ("repository", "."),
        ])

    def test_no_errors(self):
        self.assertEqual(self.report.errors, [])

    def test_backfilled_repository_passes(self):
        extra = {
            "crates/protocol/tests/base32.rs":
                "// covers: crates/protocol/src/base32.rs\n" + rust_lines(2),
            "crates/protocol/tests/lib.rs":
                "// covers: crates/protocol/src/lib.rs\n" + rust_lines(3),
            "crates/core/tests/secure_mem.rs":
                "// covers: crates/core/src/secure_mem.rs\n" + rust_lines(4),
        }
        for rel, text in extra.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        config = ctr.load_config(self.root)
        report = ctr.measure(self.root, ctr.list_files(self.root, use_git=False), config)
        self.assertEqual(report.failures, [])
        self.assertEqual(report.errors, [])


class AndroidLikeRepository(unittest.TestCase):
    """A Gradle layout: unit tests, instrumented tests, build scripts ignored."""

    def setUp(self):
        self.tmp, self.root = make_repo({
            "settings.gradle.kts": 'include(":app")\n',
            "test-ratio.toml": 'ignore = ["**/*.gradle.kts"]\n',
            "app/build.gradle.kts": "plugins {\n}\n",
            "app/src/main/java/org/m/Chat.kt":
                "package org.m\n\n/** A chat. */\nclass Chat(val id: Int) {\n"
                "    fun title() = \"#$id\"\n}\n",
            "app/src/test/java/org/m/ChatTest.kt":
                "// covers: app/src/main/java/org/m/Chat.kt\n" + "val a = 1\n" * 8,
            "app/src/androidTest/java/org/m/ChatUiTest.kt":
                "// covers: app/src/main/java/org/m/Chat.kt\n" + "val b = 1\n" * 4,
        })
        config = ctr.load_config(self.root)
        self.report = ctr.measure(self.root, ctr.list_files(self.root, use_git=False), config)

    def tearDown(self):
        self.tmp.cleanup()

    def test_production_lines(self):
        self.assertEqual(self.report.files["app/src/main/java/org/m/Chat.kt"].production, 4)

    def test_unit_and_instrumented_tests_both_count(self):
        self.assertEqual(self.report.files["app/src/main/java/org/m/Chat.kt"].test, 12)

    def test_build_scripts_are_ignored(self):
        self.assertEqual(list(self.report.files), ["app/src/main/java/org/m/Chat.kt"])

    def test_module_is_the_unit(self):
        self.assertEqual(self.report.units, {"app": (4, 12)})

    def test_passes(self):
        self.assertEqual((self.report.failures, self.report.errors), ([], []))


if __name__ == "__main__":
    unittest.main()
