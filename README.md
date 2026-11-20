# Mosgird protocols

This repository is the source of truth for the Mosgird protocol: an end-to-end encrypted chat platform with servers, channels, direct messages, and roles.

It contains the specification, the decision records behind it, the test vectors that implementations must pass, and the rules for contributing to this repository. It contains no implementation code. Implementations live in their own repositories and follow this specification.

**Status:** specification in draft (v0.1). Not released.

**License:** Mulan Permissive Software License, Version 2 (Mulan PSL v2). See [LICENSE.md](LICENSE.md).

## Implementations

| Repository | Role |
|------------|------|
| [mosgird/client](https://github.com/mosgird/client) | Client application |
| [mosgird/server](https://github.com/mosgird/server) | Relay server |

Each implementation names the version of this specification it implements. When an implementation and this specification disagree, the specification is correct and the implementation has a bug, or the specification needs a change proposed here.

## Where implementation details come from

This repository is the reference for implementation details. Users and developers should read the specification here before relying on any behavior of an implementation. Implementations follow it: if one disagrees, the specification is correct and the implementation is the thing to fix.

## Contents

| Path | Description |
|------|-------------|
| [spec/v0.1/overview.md](spec/v0.1/overview.md) | Goals, non-goals, architecture, terminology, message flow |
| [spec/v0.1/open-questions.md](spec/v0.1/open-questions.md) | Unresolved decisions, with options and trade-offs |
| [spec/VERSIONING.md](spec/VERSIONING.md) | How specification versions are numbered, released, and referenced |
| [spec/decisions/](spec/decisions/) | Decision records |
| [test-vectors/README.md](test-vectors/README.md) | Test vectors that implementations must pass |
| [AGENTS.md](AGENTS.md) | Rules for AI agents and contributors |
| [AI_POLICY.md](AI_POLICY.md) | Rules for using generative AI tools when contributing |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to propose a change: branches, pull requests, checks |
| [SECURITY.md](SECURITY.md) | How to report a security or privacy problem privately |
| [ACCESSIBILITY.md](ACCESSIBILITY.md) | Accessibility goals for the documents and for implementers |
| [scripts/check_spec.py](scripts/check_spec.py) | Consistency checks for the specification |
| [scripts/check_contributions.py](scripts/check_contributions.py) | Pull request checks: session links, AI-use disclosure, commit trailers, asset attestation |
| [.github/rulesets/main.json](.github/rulesets/main.json) | Branch rule set for `main` |
| [.github/CODEOWNERS](.github/CODEOWNERS) | Code owners for automation, scripts, and policy files |
