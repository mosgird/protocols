# Overview (v0.1)

**Status:** draft.

This document describes goals, non-goals, architecture, terminology and the message flow for v0.1 of the protocol. Items marked **[open]** are not decided. Each one is listed with options in [open-questions.md](open-questions.md). Decisions already taken are recorded in [../decisions/](../decisions/).

## 1. Goals

- **Security and privacy as the primary constraint.** Every component, feature, and deployment mode is designed under this requirement. None is exempt. Where another goal conflicts with security or privacy, the conflict is recorded as an open question. It is not resolved by weakening the requirement.
- **Minimal metadata.** Reduce what the relay server learns about who communicates, when, and from where. The current gaps are listed in section 3.3 and tracked in [open question 10](open-questions.md#10-metadata-minimization).
- **Private messaging.** Message content is readable only by the intended participants and their devices. The relay server cannot read it.
- **Group channels.** Servers contain channels. A channel is a multi-party conversation whose membership can change over time, and its keys follow membership changes.
- **Server-independent identity.** A user's identity key material is generated and held by the user's devices. The server does not issue identities and cannot replace one without the user's devices detecting it. The identifier format is **[open]**.
- **Readable specification.** Each mechanism is described well enough that an independent implementer can build an interoperable client or server.

## 2. Non-goals (v0.1)

- **Voice and video.** Not specified in v0.1.
- **Monetization.** Not addressed by the protocol.
- **Content policy.** The protocol does not define which content is permitted. Mechanisms for handling reports are an open question (see [open-questions.md](open-questions.md)). Policy itself is out of scope.
- **Peer-to-peer message delivery.** Messages are delivered through the relay server. Peer-to-peer transports may be specified later for calls and file transfer (see [decision 0001](../decisions/0001-relay-based-e2ee.md)).
- **Federation.** Not decided. v0.1 assumes a single official instance. Federation is an open question, not an assumed property.

## 3. Architecture

### 3.1 Components

- **Client.** Software running on a user's device. It generates and stores key material, encrypts outgoing messages, decrypts incoming messages, and manages local state.
- **Relay server.** Stores and forwards ciphertext. It also stores public key material that clients need in order to start encrypted sessions, such as pre-key bundles. It never receives private keys or plaintext.
- **Official instance.** The single deployment in v0.1. A client connects to one relay server.

### 3.2 Trust model

- Clients trust their own key material. Each device keeps its private keys locally.
- The relay server is not trusted with message confidentiality. It is trusted to deliver messages and to serve public keys, but a dishonest server could serve false public keys. Detection of this is covered by key verification ([open](open-questions.md#4-key-verification-method)).

### 3.3 What the server can and cannot observe

**The server can observe:**

- Ciphertext of every message, and the approximate size of each message.
- Timing: when messages are sent, when they are delivered, and when devices come online.
- Sender and recipient identifiers as they appear on the wire (user and device identifiers).
- IP addresses of connecting clients.
- Which devices are members of a channel or group chat, to the extent that delivery requires this. Whether the server learns more than this is **[open]**.
- Server and channel structure, such as the existence of a server and its channels. Whether names and roles are visible to the server is **[open]**.

**The server cannot observe:**

- Plaintext message content.
- Private identity keys, session keys, or group secrets.
- Plaintext of attachments, if attachments are added in v0.1. Attachment handling is **[open]**.

## 4. Terminology

- **User.** A person's identity in the system. A user is identified by an identifier derived from or bound to identity key material. The identifier format is **[open]**.
- **Device.** One installation of a client, holding its own key material. A device belongs to exactly one user. A user may have several devices.
- **Session.** The cryptographic state shared by two devices for direct messages, as defined by the Double Ratchet (see [decision 0002](../decisions/0002-signal-for-direct-messages.md)). In group contexts, membership is tracked by MLS group state, not by pairwise sessions (see [decision 0003](../decisions/0003-mls-for-groups.md)).
- **Channel.** A named conversation inside a server. Each channel is an MLS group. Membership is determined by the server's roles and permissions model, which is not specified in this document.
- **Direct message.** A conversation between two users, encrypted with pairwise sessions.
- **Group chat.** A conversation with more than two participants that is not part of a server. It is an MLS group.
- **Event.** A unit that the server stores and forwards. An event consists of an encrypted payload and the routing metadata the server needs to deliver it. Event types (messages, membership changes, key updates) are **[open]** in their full list.

## 5. Message flow

This section describes the flow in plain language. Exact message formats are not defined in v0.1.

### 5.1 Direct message

1. The sender's device asks the relay server for the recipient's public pre-key bundle.
2. The sender's device uses the bundle to run the X3DH key agreement and derive a shared secret. It does not need the recipient to be online.
3. The sender's device encrypts the message with the Double Ratchet, using keys derived from that shared secret. Each message uses a new key, which gives forward secrecy.
4. The sender's device sends the ciphertext to the relay server, addressed to the recipient's device.
5. The relay server stores the ciphertext until the recipient's device fetches it, then forwards it. It does not decrypt it.
6. The recipient's device runs its half of X3DH, derives the same secret, and decrypts the message with the Double Ratchet.

### 5.2 Channel or group chat

1. The group has a current MLS epoch. Each member device holds the epoch's secrets.
2. When membership changes, a member device creates an MLS commit. The commit updates the group's keys so that removed devices cannot read later messages, and added devices receive what they need to join.
3. The sending device encrypts the message under the current epoch's keys.
4. The relay server delivers the ciphertext to each member device, which is the role of the MLS Delivery Service.
5. Each member device decrypts the message with the keys for that epoch.

Commit ordering, handling of concurrent commits, and the exact delivery semantics are defined by RFC 9420 and must be checked against it when the spec is written in full. Details that depend on the relay's behavior are **[open]**.

## 6. References

- RFC 9420, The Messaging Layer Security (MLS) Protocol.
- The Signal Protocol documents: X3DH Key Agreement and the Double Ratchet Algorithm, published by Signal.
- libsodium, for cryptographic primitives. No cryptographic constructions are invented in this specification.
