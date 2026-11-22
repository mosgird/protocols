# Versioning

Mosgird uses [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) for the specification and for each implementation (`mosgird/core`, `mosgird/desktop`, and `mosgird/android`). This document says how the rules apply to each of them.

## Specification

### Version numbers

A specification version is `MAJOR.MINOR.PATCH`. Its documents live in `spec/vMAJOR.MINOR/`.

The public API of the specification is everything an implementation depends on:

- the wire format: message and envelope encodings, field names, and their meanings;
- every procedure whose output a test vector checks, such as key agreement, ratchet steps, and group key updates;
- every requirement written with MUST, MUST NOT, or SHALL.

Changes to editorial text, examples, links, and open-question notes that do not change any of the above do not require a release of their own. They are included in the next release, whatever its level.

### Bumping the version

- **PATCH** (`0.1.0` to `0.1.1`): backward-compatible corrections. A release that contains only editorial changes is a PATCH. A test vector whose expected output disagreed with the referenced document is corrected in a PATCH, because an implementation that follows the document already produces the corrected output.
- **MINOR** (`0.1.0` to `0.2.0`): backward-compatible additions. A new optional behavior that an implementation may ignore, a new message type that old implementations can safely drop, or a new test vector for a new section.
- **MAJOR** (`1.0.0` to `2.0.0`): any change that breaks an implementation written to the previous version. Changing a MUST, changing a wire field, or changing a procedure so that it produces a different output from the same input is breaking, and so is the test vector change that follows from it.

A security fix that changes wire or procedural behavior is breaking if the old behavior was allowed. It takes the MAJOR bump, or the MINOR bump while the version is `0.y.z`.

### Before 1.0.0

SemVer section 4 says that a version `0.y.z` is for initial development, and anything may change. The specification uses that freedom, with two conventions:

- Breaking changes bump the MINOR version, so `0.1.x` to `0.2.0` is the breaking step.
- Every breaking change is listed in the release notes.

The specification becomes `1.0.0` when the open questions that affect the wire format are settled and the test vectors for the core sections exist and pass.

### Releases

A release is an annotated git tag named `v` followed by a SemVer version, for example `v0.1.0`. The tag points to a commit on `main`. A tag is never moved, deleted, or reused. `scripts/check_semver_tag.py` checks the name and the ancestry, and a ruleset protects the tags.

A release is made only when:

1. the documents in the version directory are final for that version;
2. the test vectors for that version exist and pass the checks;
3. the release notes list each change since the previous tag and mark each one as breaking or not.

## Implementations

Each implementation follows SemVer for its own releases, with the same tag format and the same tag protection.

Its public API is the library interface that other code calls, the behavior a user can observe, and the local storage format it writes.

An implementation release states the specification version it implements, in its README and its release notes. For example: "Implements mosgird/protocols `v0.1.0`."

Implementation versions and specification versions are separate. A client `1.4.2` may implement specification `0.1.0`. An implementation adopts a newer specification by its own pull request, which must pass the test vectors for that specification version. Adopting a breaking specification version is a breaking change for the implementation, so it takes a MAJOR bump, or a MINOR bump while the implementation is `0.y.z`.

## Build metadata

SemVer build metadata (the `+` suffix) is allowed in a tag name but ignored for precedence. Releases should not use it.
