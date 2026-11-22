# 0013. Formal verification in layers

**Status:** Proposed

## Context

The Mosgird session protocol ([decision 0012](0012-mosgird-session-protocol.md)) combines published designs in a structure of its own. No published proof covers that combination: Post-Quantum Noise handshakes with X-Wing, and a double ratchet built on X-Wing. The core library ([decision 0010](0010-shared-core-library.md)) will implement it, and bugs in such code usually come from the implementation, not from the primitives.

The team wants the cryptography proven with mathematical tools, where that is possible. Tools exist for three layers:

- **Protocol design.** Symbolic provers, Tamarin and ProVerif, check secrecy and authentication against an attacker who controls the network. Computational provers, CryptoVerif and EasyCrypt, give game-based proofs.
- **Primitive implementations.** HACL\* (written in F\*) and libcrux (Rust checked with the hax toolchain) prove functional correctness and memory safety of primitive code. HACL\* also proves its code free of secret-dependent branches and memory access.
- **Protocol code.** hax translates Rust into F\* or ProVerif, so the code that ships can be checked against the model.

## Decision

- **Protocol proofs are required before acceptance.**
  - The session protocol of decision 0012 is modelled in Tamarin or ProVerif before 0012 is accepted. The model covers the handshake patterns at first contact and between contacts, and the ratchet.
  - It states and proves: secrecy of message keys, mutual authentication, forward secrecy, and recovery after a key leak.
  - Every later change to the session protocol, the group protocol, or the first-contact flow updates the model in the same pull request.
- **The models live in this repository**, next to the specification text they describe. The checks that run them are added to CI once the first model exists. The first models are in [spec/v0.1/models](../v0.1/models/README.md) and run with `scripts/check_models.py`.
- **Verified primitive implementations come first.** For each primitive of [decision 0011](0011-cryptographic-suite-and-security-level.md), the core library uses a formally verified implementation (libcrux, or HACL\* through libcrux) where one exists. It uses libsodium where none exists. Which library provides each primitive is listed in `mosgird/core`, with the reason.
- **The core library's protocol code is checked against the model with hax** where hax supports the code. Code it cannot check, such as the transports, is listed as unverified in `mosgird/core`.
- **Rust stays the implementation language.** Proof languages are used for the models and through hax, not as a replacement for the core library.
- **Models and proofs are cryptographic content** under [AI_POLICY.md](../../AI_POLICY.md). An AI tool may draft them. A human with the expertise must write or review them line by line before they count as a proof.

## Consequences

- Decision 0012 stays Proposed until its model and proofs are merged and reviewed. That needs a person with experience in Tamarin or ProVerif, from the team or from outside.
- **Deniability is not covered by these tools in their usual form.** Tamarin and ProVerif check secrecy and authentication; deniability needs a separate argument, written or tool-assisted. This is recorded in the open detail of [open question 18](../v0.1/open-questions.md#18-post-quantum-deniable-authentication).
- **Proofs cover their model, not everything.** Side channels in compiled code, hardware, the operating system, and the transports (Arti, i2pd) stay outside them. Code review, testing, and audits remain necessary. Verified code has had bugs: ePrint 2026/192 reports thirteen vulnerabilities in libcrux and hpke-rs that escaped formal verification. Verified libraries must be kept up to date.
- **Two primitive libraries.**
  - libcrux is tested mainly on x64 and Arm64. Other platforms are best effort, and may need libsodium instead.
  - Some primitives of decision 0011 may have no verified implementation, for example XChaCha20 and BLAKE2b. Each must be checked; where none exists, libsodium is used and the gap is listed.
  - X-Wing is built from ML-KEM-768, X25519, and SHA3-256. If no library implements X-Wing itself with verified code, the core library composes it exactly as the X-Wing draft specifies, from verified parts, and tests it against the draft's test vectors.
- hax checks only the subset of Rust it supports. The protocol code has to be written in that subset, which shapes how `mosgird/core` is written.
- The group protocol (DCGKA, decision 0006) needs a model too, before it is accepted. DCGKA has a published game-based proof, but Mosgird's choice of two-party component ([decision 0019](0019-two-party-component-for-dcgka.md)) changes what must be shown.

## Alternatives considered

- **Protocol proofs only.** Not chosen. The code would remain unchecked, and implementation bugs are the more common failure.
- **The whole core library in a proof language, such as F\* compiled to C as HACL\* is.** Not chosen. It would take years of specialist work, and the transports would remain unverified anyway.
- **Haskell, with or without refinement types (Liquid Haskell).** Not chosen. Its runtime makes constant-time code hard to guarantee, deployment on Android and iOS is difficult, and its type system alone does not prove cryptographic security. Tamarin, which is written in Haskell, is used as a tool instead.
- **No formal verification; review and audits only.** Not chosen by the team.
