# AI policy

This document sets the rules for using generative AI tools when contributing to this repository. It applies to code, specification text, decision records, issues, pull request descriptions, and review comments.

## Position

Maintainers are critical of generative AI, and that critique shapes the rules below. The concerns are:

- **Energy and water.** Training and running large models uses large amounts of electricity and cooling water.
- **Labor and consent.** Models are trained on work that was made without the consent of its authors or payment to them. Their output can replace the work of the people they learned from.
- **Concentration.** Training and serving large models depends on a few companies with large amounts of capital and compute.
- **Understanding.** Generated output can look correct while being wrong. Relying on it can replace learning the subject.

We still use AI tools in a few bounded tasks where doing the work by hand is costly and the output is easy to check. The current uses are:

- **Documentation:** drafting prose that a maintainer then rewrites or edits.
- **Boilerplate code:** repetitive code such as test scaffolding, configuration, and serialization glue. The author reads, tests, and owns it.
- **Wording:** suggesting alternative phrasing, or pointing out unclear sentences, in text the author wrote.
- **Translations:** a first draft of translated text. A fluent speaker who is not the drafter must review it before it is merged.

We do not accept AI as the source of design decisions, of cryptographic constructions, or of factual claims in the specification. We expect our reliance on these tools to fall as the project matures. This policy will be revised in pull requests as that happens.

## What you may do

- Use AI tools for the uses listed under Position: documentation drafts, boilerplate code, wording suggestions, and translation drafts.
- Use AI tools to search for or explain published material, provided you verify what they cite.
- Use AI tools to check text you have written, provided you decide what changes to make.

## What you must do

- **Disclose use.** Complete the "AI use" section of the pull request template. Say which tool was used and how: brainstorming, drafted text, generated code, or review only. Disclosure goes in the pull request description. Do not add tool footers or attribution lines to commits.
- **Understand what you submit.** You must be able to explain and defend every line in your contribution. If you cannot, do not submit it.
- **Run the checks.** Run `python3 scripts/check_spec.py` and any tests that apply, and report the result honestly.
- **Verify citations.** Check every reference, RFC number, section number, and quotation against the source. Models invent these.

## Commit trailers and session links

- **Session links are banned** in commit messages and in pull request descriptions, both local and remote. This covers links to AI session pages (for example, `claude.ai/code/...`), `session_...` identifiers, and `claude-session:` lines.
- **If you disclose AI use in a pull request**, every non-merge commit in that pull request must carry two trailers:
  - `Co-authored-by: <tool name> <address>`, naming the tool that contributed.
  - `Task: <short description>`, at most 120 characters, saying what the tool was asked to do. Do not put secrets, personal data, or private material in it.
- `scripts/check_contributions.py` checks these rules. The `contribution-policy` check runs on every pull request.

## What you may not do

- **Do not use AI-generated designs for cryptography or for key handling.** The project references published designs (X3DH, the Double Ratchet, RFC 9420, libsodium primitives) and does not invent constructions. AI-assisted edits to these areas must be written or line-by-line reviewed by a human who can check them against the source.
- **Do not paste secrets, private keys, unpublished code, or personal data into an AI tool.**
- **Do not submit output you have not checked.** Unreviewed generated text in the specification is rejected.

## Review

- Maintainers may ask for a change to be rewritten by hand, or decline an AI-heavy contribution, without a detailed reason. Ask if you want one.
- Pull requests opened by AI agents are reviewed exactly like any other. Agents do not merge (see [AGENTS.md](AGENTS.md)).
- Changes to this policy go through a pull request and need owner approval.
