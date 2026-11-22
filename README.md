# Mosgird protocols

This repository is the source of truth for the Mosgird protocol: an end-to-end encrypted chat platform with communities, channels, direct messages, roles, and moderation, which runs without servers.

It contains the specification, the decision records behind it, the test vectors that implementations must pass, and the rules for contributing to this repository. It contains no implementation code. Implementations live in their own repositories and follow this specification.

**Status:** specification in draft (v0.1). Not released.

**License:** Mulan Permissive Software License, Version 2 (Mulan PSL v2). See [LICENSE.md](LICENSE.md).

## Implementations

| Repository | Role |
|------------|------|
| [mosgird/core](https://github.com/mosgird/core) | Shared library: protocol, cryptography, storage, and transports ([decision 0010](spec/decisions/0010-shared-core-library.md)). |
| [mosgird/desktop](https://github.com/mosgird/desktop) | Desktop client application |
| [mosgird/android](https://github.com/mosgird/android) | Android application |

The protocol has no server. Devices deliver messages to each other directly ([decision 0005](spec/decisions/0005-serverless-online-only-delivery.md)).

Each implementation names the version of this specification it implements. When an implementation and this specification disagree, the specification is correct and the implementation has a bug, or the specification needs a change proposed here.

Users and developers should read the specification here before relying on any behavior of an implementation.

## Contents

| Path | Description |
|------|-------------|
| [spec/v0.1/overview.md](spec/v0.1/overview.md) | Goals, non-goals, and a list of the v0.1 documents |
| [spec/v0.1/architecture.md](spec/v0.1/architecture.md) | Components and trust model |
| [spec/v0.1/metadata.md](spec/v0.1/metadata.md) | What parties other than the intended participants can observe |
| [spec/v0.1/terminology.md](spec/v0.1/terminology.md) | Terms used throughout the specification |
| [spec/v0.1/message-flow.md](spec/v0.1/message-flow.md) | How direct and group messages travel |
| [spec/v0.1/references.md](spec/v0.1/references.md) | Published designs the protocol builds on |
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
| [.github/rulesets/main.json](.github/rulesets/main.json) | Branch ruleset for `main` |
| [.github/rulesets/tags.json](.github/rulesets/tags.json) | Ruleset that protects release tags |
| [scripts/check_semver_tag.py](scripts/check_semver_tag.py) | Release tag check: SemVer name, tagged commit on `main` |
| [.github/workflows/](.github/workflows/) | CI workflows that run the checks above |
| [.github/CODEOWNERS](.github/CODEOWNERS) | Code owners for automation, scripts, and policy files |
