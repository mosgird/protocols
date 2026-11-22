# 0010. A shared core library in mosgird/core

**Status:** Proposed

## Context

[Decision 0004](0004-separate-implementation-repositories.md) puts implementations in their own repositories, `mosgird/desktop` and `mosgird/android`. Without a shared library, each of them would implement the cryptography, the protocol, key storage, and the Tor, I2P, and local-link connections on its own. Two implementations of the same security-critical code double the review work, and they can differ in behavior.

The team wants the same code on every platform: Linux, the BSDs, Windows, macOS, Android, and iOS. It also wants a new user to be able to create an identity and start talking to a contact almost immediately, with no manual setup.

## Decision

- A new repository, `mosgird/core`, holds a library that implements everything except the user interface:
  - the cryptographic primitives and the protocol's key agreement, ratchets, and group key handling;
  - the Mosgird protocol: sessions, direct messages, groups, communities, moderation, contact requests, delivery, retries, and acknowledgments;
  - storage of key material and protocol state on the device;
  - the transports of [decision 0009](0009-tor-and-i2p-with-local-links.md): Tor, I2P, and local links.
- `mosgird/desktop` and `mosgird/android`, and any later application, use `mosgird/core` and add only the user interface and platform integration. They do not implement protocol behavior themselves.
- The library is written in Rust. It offers bindings for Kotlin and Swift, and a C interface for other languages.
- `mosgird/core` follows decision 0004 like the other implementations. It names the specification version it follows, keeps its own documentation, uses this repository's agent and contributor rules, and runs this repository's contribution checker at a pinned commit.
- The libraries `mosgird/core` depends on are chosen and documented in that repository, within the requirements of this specification. The planned starting set is:
  - libsodium, for classical primitives and ML-KEM;
  - libcrux, for ML-KEM-1024 and other primitives libsodium lacks;
  - Arti, for Tor;
  - i2pd, used through its SAMv3 interface, for I2P.

## Consequences

- The security-critical code is written and reviewed once, and it behaves the same on every platform.
- The applications depend on the core library's releases. A protocol change follows this order: the specification, then `mosgird/core`, then each application. That adds a third pull request to the order in decision 0004.
- The automatic first-use flow is implemented once, in the core library: create an identity, show a contact link or QR code, and connect. Its limits still apply: first contact needs the contact's link or QR code ([open question 13](../v0.1/open-questions.md#13-first-contact-without-a-directory)), delivery is online-only (decision 0005), and joining Tor or I2P takes time on first start.
- Rust's support differs by platform. Linux, Windows, macOS, Android, iOS, and FreeBSD are well supported. OpenBSD and some other BSDs are supported only on a best-effort basis by the Rust project.
- i2pd is written in C++ and runs as a separate router, so the core library needs a way to bundle or reach it on each platform. Whether i2pd runs on iOS is not confirmed. A Rust I2P router such as emissary could replace it later. emissary is young and marked unstable.
- Arti is the Tor Project's Rust implementation. The Tor Project has not yet said that hosting onion services with Arti is ready for production. If that does not change in time, the library may need C tor instead.
- The existing repositories keep their own build, release, and accessibility details. `mosgird/android` and `mosgird/desktop` lose most protocol code they would otherwise have.

## Alternatives considered

- **No shared library; each application implements the protocol.** Rejected. It duplicates security-critical code and allows behavior to differ between platforms.
- **A shared library for cryptography and protocol only, with transports in each application.** Not chosen. Tor, I2P, and local-link handling would be duplicated, and the first-use flow would differ by platform.
- **A shared library in C or C++.** Not chosen. Rust gives memory safety for code that parses data from untrusted peers, and Arti is already written in Rust.
- **Keep the library inside `mosgird/desktop`.** Rejected. The Android application would then depend on another application's repository, and the separation in decision 0004 would be lost.
