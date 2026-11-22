# 0001. Relay server with end-to-end encryption

**Status:** Superseded

Superseded by [decision 0005](0005-serverless-online-only-delivery.md). The text below is kept as it was proposed.

## Context

The platform needs to deliver messages between users who may not be online at the same time. Clients on mobile networks often change IP address and may sleep. Direct client-to-client connections therefore cannot be the only delivery path. The platform must also prevent the operator from reading message content.

## Decision

- Messages are delivered through a relay server. The server stores and forwards ciphertext. It does not decrypt messages.
- All encryption and decryption happens in clients.
- The server stores public key material needed to start sessions. It does not store private keys.
- Peer-to-peer connections (for example WebRTC) may be specified later for calls and file transfer. They are not used for message delivery in v0.1.

## Consequences

- The server sees ciphertext, timing, sender and recipient identifiers, and IP addresses (see [overview section 3.3](../v0.1/overview.md#33-what-other-parties-can-observe), which now describes the design without a server).
- Message availability depends on the relay. A stored-and-forward queue is needed, with a retention policy that is not yet defined.
- Clients must handle offline delivery, duplicate delivery, and out-of-order delivery.
- A dishonest server can serve false public keys. Key verification is required to detect this (see [open question 4](../v0.1/open-questions.md#4-key-verification-method)).

## Alternatives considered

- **Peer-to-peer delivery only.** Rejected for v0.1. Requires both clients to be online together or a separate store-and-forward service, and it exposes IP addresses to contacts.
- **Server-side decryption with transport encryption only.** Rejected. The operator could read all messages, which is inconsistent with the goal of private messaging.
