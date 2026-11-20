# Specification versioning

This document says how versions of the specification are numbered, released, and referenced by implementations.

## Version numbers

Specification versions have the form `MAJOR.MINOR.PATCH`, and the directory `spec/vMAJOR.MINOR/` holds the documents for a minor version.

- **PATCH** changes correct wording, fix broken links, or clarify text without changing behavior.
- **MINOR** changes add behavior that existing implementations can ignore, or change text in a way that could change an implementation's conformance.
- **MAJOR** changes break compatibility: an implementation written to the previous major version cannot interoperate without changes.

Before 1.0.0, the specification is a draft. Any version may change incompatibly, and each implementation must name the exact tag it follows.

## Releases

A release is a git tag on `main`, of the form `vMAJOR.MINOR.PATCH` (for example `v0.1.0`). A tag is never moved or reused. A release does not exist until its tag does.

A release is made when:

1. every document in the version directory is final for that version, with no open question that changes the wire format or the security properties;
2. the test vectors for that version exist and pass the reference checks;
3. the release notes list each change since the previous tag.

## Implementations

An implementation states the specification version it follows, by tag, in its README. For example: "Implements mosgird/protocols `v0.1.0`."

An implementation moves to a newer tag by its own pull request, which must pass the test vectors for the new tag. An implementation may follow a draft (untagged) state of `main` only for development, and must not describe itself as following a version it does not implement.

## Compatibility notes

Each release lists, for each implementation-visible change, whether it is compatible with the previous minor version. An unlisted change is treated as incompatible until the release notes say otherwise.
