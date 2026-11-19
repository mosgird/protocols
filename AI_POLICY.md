# AI policy

This document sets the rules for using generative AI tools when contributing to this repository. It applies to code, specification text, decision records, issues, pull request descriptions, and review comments.

## Position

Maintainers are critical of generative AI. The concerns include energy and water use, effects on workers and on the people whose work was used in training, and the concentration of compute and capital in a few companies. These concerns are the reason for the rules below.

We accept AI-assisted contributions because the work of this project is large and our time is limited. We treat AI tools as a way to work faster on tasks that are already understood. We do not treat them as a source of design decisions or of understanding. We expect our reliance on them to fall as the project matures, and this policy will be revised in pull requests as that happens.

## What you may do

- Use AI tools to draft, reword, summarize, or check text you have written.
- Use AI tools to write code or test cases, provided you read, understand, and test all of it.
- Use AI tools to search for or explain published material, provided you verify what they cite.

## What you must do

- **Disclose use.** Complete the "AI use" section of the pull request template. Say which tool was used and how: brainstorming, drafted text, generated code, or review only. Disclosure goes in the pull request description. Do not add tool footers or attribution lines to commits.
- **Understand what you submit.** You must be able to explain and defend every line in your contribution. If you cannot, do not submit it.
- **Run the checks.** Run `python3 scripts/check_spec.py` and any tests that apply, and report the result honestly.
- **Verify citations.** Check every reference, RFC number, section number, and quotation against the source. Models invent these.

## What you may not do

- **Do not use AI-generated designs for cryptography or for key handling.** The project references published designs (X3DH, the Double Ratchet, RFC 9420, libsodium primitives) and does not invent constructions. AI-assisted edits to these areas must be written or line-by-line reviewed by a human who can check them against the source.
- **Do not paste secrets, private keys, unpublished code, or personal data into an AI tool.**
- **Do not submit output you have not checked.** Unreviewed generated text in the specification is rejected.

## Review

- Maintainers may ask for a change to be rewritten by hand, or decline an AI-heavy contribution, without a detailed reason. Ask if you want one.
- Pull requests opened by AI agents are reviewed exactly like any other. Agents do not merge (see [AGENTS.md](AGENTS.md)).
- Changes to this policy go through a pull request and need owner approval.
