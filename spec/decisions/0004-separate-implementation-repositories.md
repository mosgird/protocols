# 0004. Separate repositories for implementations

**Status:** Proposed

## Context

This repository started as a specification with placeholder directories for the client and the server. Implementations have a different life from the specification: they depend on platforms, build tools, and release schedules that do not affect the protocol. Their documentation covers platforms and build details, and their rules for accessibility and security differ in scope. Keeping them together makes the specification harder to read and the implementation history harder to follow.

## Decision

- Implementations live in their own repositories: `mosgird/client` and `mosgird/server`. Further implementations get their own repositories too.
- This repository is the source of truth for the protocol. It holds the specification, decision records, test vectors, and the rules that apply to all repositories.
- Each implementation names the specification tag it follows (see [VERSIONING.md](../VERSIONING.md)). It documents its own platforms, build steps, and accessibility and security details.
- Shared rules are kept once. The implementation repositories point to this repository's agent and contributor documents, and their contribution check runs this repository's checker at a pinned commit.
- Changes that touch both the specification and an implementation are made as two pull requests, one in each repository, with the specification change merged first.

## Consequences

- A protocol change needs coordination across repositories. The specification change is merged and tagged before an implementation moves to it.
- Each repository has its own ruleset, code owners, and automation. The rule set in this repository is the reference for the others.
- The contribution check in each implementation depends on a pinned commit of this repository. That pin is updated by its own pull request.
- Test vectors live here, so every implementation runs the same tests.

## Alternatives considered

- **Keep implementations here under `client/` and `server/`.** Rejected. It mixes platform and build detail with the specification, and it couples implementation releases to specification releases.
- **Create implementation repositories before any code exists, and keep them empty.** Considered. Accepted in part: the repositories exist now, with their rules in place, so the shared rules are tested before code arrives.
