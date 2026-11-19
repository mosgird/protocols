# 0002. Signal protocol design for direct messages

**Status:** Proposed

## Context

Direct messages need asynchronous session setup (the recipient may be offline), forward secrecy, and post-compromise recovery. The project must not invent new cryptographic constructions. Published designs exist for these properties.

## Decision

- Direct messages use the protocol design published by Signal:
  - **X3DH** (Extended Triple Diffie-Hellman) for asynchronous session setup from a published pre-key bundle.
  - **Double Ratchet** for per-message keys, forward secrecy, and recovery after key compromise.
- This specification references the Signal documents for these algorithms. It does not restate or modify them. Any deviation is a new decision record.
- Cryptographic primitives (key agreement, signatures, AEAD, hashing) are provided by libsodium. No primitive is implemented from scratch.
- Each device maintains pairwise sessions with the devices of its direct message contacts.

## Consequences

- The server stores pre-key bundles and hands them out. One-time pre-keys can run out, so clients must replenish them. The exhaustion behavior must be specified (see [open question 3](../v0.1/open-questions.md#3-multi-device-key-handling)).
- Pairwise sessions multiply with the number of devices. Multi-device behavior depends on the open question about device identity.
- libsodium does not implement X3DH or the Double Ratchet. Those are protocol-level designs implemented on top of its primitives. The implementation must follow the referenced documents exactly, and test vectors are needed (see [test-vectors](../../test-vectors/README.md)).
- Identity keys used by X3DH are tied to the identity format, which is an open question.

## Alternatives considered

- **MLS for direct messages as well.** Not chosen for v0.1. Using one group design for both cases would simplify the protocol, but this record has not evaluated whether MLS meets the asynchronous setup and forward secrecy requirements for two-party conversations at the same level of review as the Signal design. Revisit if that evaluation is done.
- **A custom ratchet or key agreement.** Rejected. The project does not invent cryptography.
