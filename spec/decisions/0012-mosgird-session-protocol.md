# 0012. Mosgird session protocol: interactive, KEM-authenticated, ratcheted

**Status:** Proposed

Supersedes [0002](0002-signal-for-direct-messages.md).

## Context

[Decision 0002](0002-signal-for-direct-messages.md) used Signal's X3DH and Double Ratchet for direct messages. X3DH is built for a recipient who is offline: the sender starts a session from pre-keys the recipient published earlier. Three later decisions changed the situation:

- Delivery is online-only ([decision 0005](0005-serverless-online-only-delivery.md)), so both devices are online whenever a session starts.
- The suite in [decision 0011](0011-cryptographic-suite-and-security-level.md) requires post-quantum key exchange at 192 bits or more. X3DH and the classical Double Ratchet use only X25519.
- The team wants Mosgird's own protocol structure, not Signal's protocol as-is. It wants it built from published concepts, without inventing cryptographic constructions.

The team chose:

- an interactive handshake;
- authentication by key encapsulation from the start, so that sessions are post-quantum and deniable;
- both a continuous ratchet within each connection and a new handshake on every connection.

## Decision

The **Mosgird session protocol** protects all traffic between two devices. It has three layers. Each layer follows a published design, and the primitives are those of decision 0011.

1. **Handshake: a new one on every connection.** Each time two devices connect, they run an interactive handshake from the Post-Quantum Noise framework (Angel, Dowling, Hülsing, Schwabe, Weber, "Post Quantum Noise", ACM CCS 2022). That framework replaces Noise's Diffie-Hellman operations with key encapsulation. The KEM is X-Wing. The other operations are those of decision 0011.
   - Between known contacts, both devices already know each other's long-term key, and they use the paper's mutually known-key pattern (the KEM form of Noise `KK`).
   - At first contact, the devices use the KEM form of Noise `XX` with a one-time invite secret as a pre-shared key, as [decision 0014](0014-first-contact-by-invite.md) defines. (An earlier draft of this record named `IK`; decision 0014 explains the change.)
   - The exact patterns and their parameters are written in the specification text, with test vectors. They follow the paper without changing its structure.
2. **Authentication: no signatures.** Each device holds a long-term X-Wing key pair, its *identity KEM key*. A device proves its identity by decapsulating secrets that the other device encapsulated to that key. Nothing in the handshake or in messages is signed. The Ed25519 + ML-DSA-87 signatures of decision 0011 are used only where proof is wanted, such as community roles and moderation.
3. **Ratchet within a connection.** After the handshake, messages are protected by a double ratchet in the generic form given by Alwen, Coretti, and Dodis ("The Double Ratchet: Security Notions, Proofs, and Modularization for the Signal Protocol", EUROCRYPT 2019). Its key agreement step ("continuous key agreement") is built from a KEM, here X-Wing. Each change of sending direction carries a new X-Wing public key and an encapsulation to the other side's latest key.
   - Symmetric key chains use keyed BLAKE2b, and messages use XChaCha20-Poly1305 with a fresh key each.
   - Message keys are deleted once used.
   - Ratchet state, and any keys kept for messages that arrived out of order, exist only for the length of a connection. They are deleted when it closes.

Messages waiting for delivery are not encrypted in advance under an old session. The device keeps them in its local storage and encrypts them under the new session when the next connection opens. Protection of that local storage is open ([open question 19](../v0.1/open-questions.md#19-protection-of-data-stored-on-the-device)).

This closes [open question 18](../v0.1/open-questions.md#18-post-quantum-deniable-authentication) with option B.

## Consequences

- **Post-quantum confidentiality and authentication.** Both hold from the first message, while ML-KEM-768 holds. X25519 inside X-Wing protects against a break of ML-KEM.
- **Forward secrecy.** Every message has its own key. Ephemeral keys from both sides protect even the first message of a connection.
- **Recovery after a key leak** happens on every reply within a connection, and at the latest on the next connection.
- **No pre-keys.** No pre-key bundles, signed pre-keys, or one-time pre-keys exist. The open detail about one-time pre-keys in question 13 no longer applies.
- **Deniability needs confirmation.** Either party can compute every secret of a session, so a transcript proves nothing to a third party. This is expected to give deniability comparable to Diffie-Hellman handshakes. The deniability properties of KEM-based Noise patterns must be confirmed by a cryptographer against the paper before this record is accepted. [Decision 0013](0013-formal-verification.md) also requires a Tamarin or ProVerif model and proof of this protocol before acceptance.
- **No audited production library implements Post-Quantum Noise.** The core library implements it from the paper, on libsodium's X-Wing, BLAKE2b, and XChaCha20-Poly1305. That code needs a cryptographer's review and independent test vectors.
- **Bandwidth.** An X-Wing public key is 1,216 bytes and a ciphertext 1,120 bytes:
  - A handshake carries several of each, a few kilobytes in total, once per connection.
  - Each ratchet step adds about 2.3 KB to the first message after a change of direction.
  - Long one-way bursts add nothing beyond the symmetric chain.
  - Battery and data cost is to be measured later.
- **Groups.** Whether this protocol can serve as DCGKA's two-party component is part of [open question 15](../v0.1/open-questions.md#15-two-party-component-for-dcgka). The paper requires specific properties of that component, and they must be checked against this design.
- **Identity.** The identity KEM key and the signature keys are separate key pairs. How they are bound to one user identifier is part of [open question 2](../v0.1/open-questions.md#2-identity-format).
- **Signal's protocol is no longer referenced** for direct messages. Its ideas remain in the cited papers, which analyze the double ratchet in general form.

## Alternatives considered

- **Keep X3DH and the Double Ratchet (decision 0002), adding PQXDH and SPQR.** Rejected by the team, which wants Mosgird's own structure. It is also built for offline recipients, which Mosgird does not support.
- **Classical Diffie-Hellman authentication with post-quantum confidentiality** (question 18, option A). Not chosen. The team wants post-quantum authentication from the start.
- **A new handshake per connection without a ratchet inside it.** Not chosen. Recovery after a leak would wait until the next connection.
- **A sparse post-quantum ratchet (Signal's SPQR).** Not chosen. It needs an incremental ML-KEM interface that libsodium's X-Wing does not provide. It could replace the per-step encapsulation later to save bandwidth, by a new decision.
- **Signing the handshake.** Rejected. It would make sessions provable to third parties.
