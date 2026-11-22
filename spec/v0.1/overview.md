# Overview (v0.1)

**Status:** draft.

This document describes goals, non-goals, architecture, terminology and the message flow for v0.1 of the protocol. Items marked **[open]** are not decided. Each one is listed with options in [open-questions.md](open-questions.md). Proposed decisions are recorded in [../decisions/](../decisions/). None is accepted yet.

## 1. Goals

- **Security and privacy as the primary constraint.** Every component, feature, and deployment mode is designed under this requirement. None is exempt. Where another goal conflicts with security or privacy, the conflict is recorded as an open question. It is not resolved by weakening the requirement.
- **No servers and no domain names.** Devices deliver messages to each other directly. No server stores, forwards, or orders anything for the protocol, and nothing depends on DNS (see [decision 0005](../decisions/0005-serverless-online-only-delivery.md)). This includes push services such as FCM, APNs, and UnifiedPush ([decision 0008](../decisions/0008-no-push-services.md)).
- **Minimal metadata.** Reduce what parties other than the intended participants learn about who communicates, when, and from where. The current gaps are listed in section 3.3 and tracked in [open question 10](open-questions.md#10-metadata-minimization).
- **Private messaging.** Message content is readable only by the intended participants and their devices.
- **Communities and channels.** A community contains channels, members and roles, and has moderation against bad-faith members ([decision 0007](../decisions/0007-communities.md)). A channel is a multi-party conversation whose membership can change over time, and its keys follow membership changes.
- **Self-held identity.** A user's identity key material is generated and held by the user's devices. No one issues identities. A substituted key is detected only if contacts verify keys ([open question 4](open-questions.md#4-key-verification-method)). The identifier format is **[open]**.
- **Readable specification.** Each mechanism is described well enough that an independent implementer can build an interoperable client.

## 2. Non-goals (v0.1)

- **Voice and video.** Not specified in v0.1.
- **Monetization.** Not addressed by the protocol.
- **Content policy.** The protocol does not define which content is permitted. Mechanisms for handling reports are an open question (see [open question 6](open-questions.md#6-abuse-handling-for-an-encrypted-service)). Policy itself is out of scope.
- **Delivery to offline devices.** A message is delivered only while both devices are reachable at the same time. Nothing stores messages for an offline device (see [decision 0005](../decisions/0005-serverless-online-only-delivery.md)), and no push service wakes one ([decision 0008](../decisions/0008-no-push-services.md)). How phones stay reachable is **[open]** ([open question 17](open-questions.md#17-mobile-reachability-without-push-services)).

## 3. Architecture

### 3.1 Components

- **Client.** Software running on a user's device. It generates and stores key material, encrypts outgoing messages, decrypts incoming messages, delivers ciphertext to other devices, keeps undelivered messages in protected local storage until it can deliver them, and manages local state. The protocol, cryptography, storage, and transports are implemented once in the shared library `mosgird/core`. The applications `mosgird/client` and `mosgird/android` add the user interface ([decision 0010](../decisions/0010-shared-core-library.md)).
- **Transport.** The means by which one device finds and reaches another, using an address derived from key material. It carries ciphertext and is not trusted with content. Over the internet, the transports are Tor onion services and I2P. Local links (Bluetooth, Wi-Fi Direct, the local network) are a fallback for when the internet is unavailable. Every link is encrypted and authenticated, and no client connects directly over the internet ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)).

The protocol has no server component. Implementations are not part of this specification. Their repositories name the version of the specification they follow (see [VERSIONING.md](../VERSIONING.md)).

### 3.2 Trust model

- Clients trust their own key material. Each device keeps its private keys locally.
- A contact's device is trusted with the messages addressed to it, and with nothing else.
- The transport and the network are not trusted. They may observe, delay, drop, replay, or reorder traffic. They cannot read or forge content without breaking the end-to-end encryption.
- A device can present false key material for someone else, for example when passing on a contact's identity KEM key or contact link. Detection depends on key verification ([open question 4](open-questions.md#4-key-verification-method)).

### 3.3 What other parties can observe

There is no server. What others can observe depends on who they are and on the transport ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)).

**A contact's device, while exchanging messages directly, can observe:**

- The other device's onion address and I2P destination, and that both belong to the same device. Over Tor and I2P, it does not learn the other device's network address. Over a local link, it learns the local link address.
- When the other device is online and reachable.
- The size and timing of each message, and how often the sender retries.
- The other device's identity KEM key, and the ephemeral keys and encapsulations of each handshake ([decision 0012](../decisions/0012-mosgird-session-protocol.md)). These are what the contact needs to derive the session keys. Nothing in them is signed, so they prove nothing to a third party.
- When each connection starts, because every connection runs a new handshake.

**Members of a channel or group chat can observe:**

- The membership of the group, which member sent each message, who added or removed whom, and when each member updates their keys. DCGKA does not hide this from members ([decision 0006](../decisions/0006-dcgka-for-groups.md)).
- The size and timing of each message, and the onion addresses and I2P destinations of the members they talk to directly.
- Community and channel structure: names, roles, membership, and moderation actions. Whether non-members can learn any of this is **[open]** ([open question 7](open-questions.md#7-community-and-channel-structure-visibility)).

**Network observers and transport relays can observe:**

- That a device uses Tor or I2P, when, and how much traffic it sends. A device's internet provider, and the first Tor relay it connects to, see its network address. Tor bridges can hide Tor use from the provider. When and how is open ([open question 12](open-questions.md#12-transport-and-addressing)).
- An I2P router's network address, which is listed in I2P's network database unless the router runs in hidden or firewalled mode.
- Timing and volume patterns. An observer who can watch large parts of the network may correlate the two ends of a conversation by timing. Neither Tor nor I2P is designed to prevent this ([open question 10](open-questions.md#10-metadata-minimization)).
- Lookups of an onion service descriptor or an I2P lease set, by the directory relays or routers that serve them. The details are set by each network.
- Near a device that uses local links: that it broadcasts or connects, and when. Discovery must not reveal stable identifiers to non-contacts. How is open.

**No one other than the intended participants can observe:**

- Plaintext message content.
- Private identity keys, session keys, or group secrets.
- Plaintext of attachments, if attachments are added in v0.1. Attachment handling is **[open]**.

## 4. Terminology

- **User.** A person's identity in the system. A user is identified by an identifier derived from or bound to identity key material. The identifier format is **[open]**.
- **Device.** One installation of a client, holding its own key material. A device belongs to exactly one user. A user may have several devices.
- **Address.** What the transport needs to reach a device. It is derived from key material, never from a domain name. Over the internet, a device has two addresses: a Tor onion address and an I2P destination ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)). How addresses relate to the user identifier is **[open]**.
- **Identity KEM key.** A device's long-term X-Wing key pair. Other devices encapsulate secrets to it during a handshake, which authenticates the device without a signature ([decision 0012](../decisions/0012-mosgird-session-protocol.md)).
- **Handshake.** The interactive exchange that starts every connection between two devices. It follows the Post-Quantum Noise framework.
- **Session.** The cryptographic state that two devices share for the length of one connection: the handshake result and the ratchet that follows it (decision 0012). It is deleted when the connection closes. In group contexts, membership is tracked by DCGKA group state, not by pairwise sessions (see [decision 0006](../decisions/0006-dcgka-for-groups.md)).
- **Group.** A set of member devices that share DCGKA state. Each member keeps a ratchet for every member, and message keys come from the sender's ratchet.
- **Causal order.** The order in which one message depends on another: a message sent after its sender processed another message comes after it. A member processes a group message only after all messages that come before it in causal order.
- **Community.** A named set of channels, with members and roles ([decision 0007](../decisions/0007-communities.md)). It is not a machine. The brief called this a "server"; the specification does not.
- **Role.** A set of permissions that a community grants to some members. The roles and permissions model is **[open]** ([open question 16](open-questions.md#16-community-moderation-without-an-operator)).
- **Moderation action.** An action that a member with a moderating role takes against another member, such as removal. Every member's client checks and applies it.
- **Channel.** A named conversation inside a community. Each channel is one group. Membership follows the community's roles and permissions.
- **Direct message.** A conversation between two users, encrypted with pairwise sessions.
- **Group chat.** A conversation with more than two participants that is not part of a community. It is one group.
- **Event.** A unit that one device sends to another. An event consists of an encrypted payload and the metadata the transport needs to deliver it. Event types (messages, membership changes, key updates, acknowledgments) are **[open]** in their full list.

## 5. Message flow

This section describes the flow in plain language. Exact message formats are not defined in v0.1.

### 5.1 Direct message

The session protocol is defined in [decision 0012](../decisions/0012-mosgird-session-protocol.md).

1. The sender's device holds the recipient device's address and identity KEM key. How it got them at first contact is **[open]** ([open question 13](open-questions.md#13-first-contact-without-a-directory)).
2. The sender's device keeps the message in its local storage until it can reach the recipient's device ([open question 14](open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery)). The message is not encrypted in advance under an earlier session.
3. When the devices can reach each other, they run a new handshake. Each side encapsulates secrets to the other's identity KEM key and to fresh ephemeral keys, and both derive the same session keys. Nothing is signed.
4. The sender's device encrypts each message with a new key from the ratchet and sends it. No other party stores it.
5. The recipient's device decrypts the message and deletes its key. It acknowledges delivery so that the sender can delete the stored message. The acknowledgment format is **[open]**.
6. When the connection closes, both devices delete the session.

### 5.2 Channel or group chat

The group protocol is DCGKA ([decision 0006](../decisions/0006-dcgka-for-groups.md)). The steps below summarize the paper. The paper is the reference.

1. Each member device holds DCGKA state for the group, including a ratchet for each member.
2. To add or remove a member, or to update its own keys, a member device sends a control message to all members by authenticated causal broadcast. Each control message is signed under the sender's identity key. Secrets meant for one member travel in a direct message encrypted with the two-party component ([open question 15](open-questions.md#15-two-party-component-for-dcgka)).
3. Each member device processes a message only after every message that causally precedes it. Members may change membership concurrently, and they reach the same membership from the causal order. No member or server decides a single order.
4. To send an application message, a device encrypts it with the next key from its own ratchet and delivers the ciphertext directly to each member device it can reach.
5. Members acknowledge control messages. A member that is missing a message asks for it again. Who can re-send it under online-only delivery is **[open]** ([open question 14](open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery)).

## 6. References

- M. Weidner, M. Kleppmann, D. Hugenroth, A. R. Beresford. Key Agreement for Decentralized Secure Group Messaging with Strong Security Guarantees. ACM CCS 2021, doi:10.1145/3460120.3484542. Extended version: IACR ePrint 2020/1281.
- Y. Angel, B. Dowling, A. Hülsing, P. Schwabe, F. Weber. Post Quantum Noise. ACM CCS 2022.
- J. Alwen, S. Coretti, Y. Dodis. The Double Ratchet: Security Notions, Proofs, and Modularization for the Signal Protocol. EUROCRYPT 2019. IACR ePrint 2018/1037.
- X-Wing: the hybrid KEM in the IETF draft draft-connolly-cfrg-xwing-kem.
- The Tor Project's specifications for version 3 onion services, and the I2P project's specifications, including the network database and SAM version 3.
- The Noise Protocol Framework, by T. Perrin, as a candidate for the handshake on local links.
- libsodium, for cryptographic primitives. No cryptographic constructions are invented in this specification.
