# Contributing

Thank you for helping with this protocol. This page is the short guide for people. The rules themselves live in two documents, and this page only points to them:

- [AI_POLICY.md](AI_POLICY.md): when and how AI tools may be used, and what is never accepted (AI-generated assets are prohibited permanently).
- [AGENTS.md](AGENTS.md): workflow, security and privacy requirements, and writing rules. It applies to humans and agents alike.

## Before you start

1. Read both documents above.
2. For a substantial change, open an issue or a draft pull request first so the direction can be agreed.

## Making a change

1. Create a branch from `main`. Do not commit to `main` directly; it is protected.
2. Keep each pull request to one decision, one specification section, or one tooling change.
3. Run the consistency check locally:

   ```sh
   python3 scripts/check_spec.py
   ```

4. Push the branch and open a pull request. Fill in the template completely, including the AI use and security and privacy sections.
5. Both required checks must pass before merging: `spec-consistency` and `contribution-policy`.

## Commits and AI disclosure

- If AI tools contributed to a pull request, every commit in it carries a `Co-authored-by` trailer naming the tool, and a `Task` trailer describing what it was asked to do. The details are in [AI_POLICY.md](AI_POLICY.md).
- Do not put links to AI sessions or conversations in commit messages or pull request descriptions.
- Commits do not need to be signed.

## Specification changes

- Decisions go in `spec/decisions/` as numbered records. An accepted record is superseded, not edited in substance.
- Uncertain points go in `spec/v0.1/open-questions.md`, with options and costs. Do not state them as settled.
- Every pull request states its security and privacy impact. Any new information the relay server can observe is recorded in `spec/v0.1/overview.md` section 3.3.

## Outside contributors

Workflows for pull requests from forks wait for maintainer approval before they run. This protects the repository from untrusted code running in CI.

## Licensing

This project is licensed under the Mulan Permissive Software License, Version 2 (see [LICENSE.md](LICENSE.md)). Unless you state otherwise, your contributions are submitted under that license.

## Reporting security problems

Do not open a public issue for a security or privacy problem. Report it to the maintainers privately. A dedicated contact method has not been set up yet; until one is, contact a maintainer directly.
