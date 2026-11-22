# 0005. No servers, no domain names, online-only delivery

**Status:** Proposed

Supersedes [decision 0001](0001-relay-based-e2ee.md).

## Context

Decision 0001 put a relay server between clients. The relay stored ciphertext for offline devices, held the pre-key bundles that start direct-message sessions, and acted as the MLS Delivery Service for groups. The team has decided that the platform runs without servers and without domain names. This record states that decision and what it removes.

## Decision

- **No servers.** No part of the protocol is a server. No server stores, forwards, orders, or indexes messages, keys, or group state for the protocol. Devices deliver messages to each other directly.
- **No domain names.** Nothing in the protocol depends on DNS or on any name that an operator or registry assigns. Identifiers and addresses are derived from key material. The identifier format is still open (see [open question 2](../v0.1/open-questions.md#2-identity-format)).
- **Online-only delivery.** A message is delivered only while the sending device and the receiving device can reach each other at the same time. Until then, the sending device keeps the ciphertext and retries. No third party holds messages for an offline device.
- **Encryption is unchanged.** All encryption and decryption happens in clients, as before. The transport that carries ciphertext between devices is not trusted with content.
- **The transport is open.** How a device finds and reaches another device is not decided (see [open question 12](../v0.1/open-questions.md#12-transport-and-addressing)). Later chosen in [decision 0009](0009-tor-and-i2p-with-local-links.md).

## Consequences

- If two devices are never reachable at the same time, a message between them is never delivered. Mobile operating systems limit background networking, which makes this more likely on phones. Retry, expiry, and the storage of undelivered ciphertext on the sending device are open (see [open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery)).
- There is no pre-key directory. The asynchronous session setup in [decision 0002](0002-signal-for-direct-messages.md) needs the recipient's pre-key bundle, which must now come from the recipient's device or out of band (see [open question 13](../v0.1/open-questions.md#13-first-contact-without-a-directory)).
- There is no MLS Delivery Service. [Decision 0003](0003-mls-for-groups.md) assumed one to deliver and order commits. [Decision 0006](0006-dcgka-for-groups.md) replaces MLS with DCGKA, which needs only causal order and no Delivery Service.
- Devices that talk directly can see each other's network addresses, unless the transport hides them. Decision 0001 rejected peer-to-peer delivery partly for this reason. This cost is recorded in [overview section 3.3](../v0.1/overview.md#33-what-other-parties-can-observe) and in [open question 10](../v0.1/open-questions.md#10-metadata-minimization). It is not accepted by default. Decision 0009 chooses transports that hide network addresses from contacts.
- Some candidate transports, such as Tor, I2P, and mixnets, carry traffic through relays that other people run. Those relays are not part of this protocol and see only transport-encrypted traffic. Whether depending on them fits this decision was part of open question 12. Decision 0009 treats the Tor and I2P networks as part of the transport, because they never store Mosgird messages.
- Options in the open questions that need a server no longer apply. They are marked in place: federation ([open question 1](../v0.1/open-questions.md#1-federation), closed by this record), the server-run key transparency log (4D), encrypted server-side backup (5C), server-enforced abuse controls (6B and 6D), server-held structure (7A), relay-stored attachments (8A), and sealed sender (10A).
- Clients must still handle duplicate and out-of-order delivery. A retrying sender can deliver the same ciphertext twice.
- The `mosgird/server` repository is removed. Implementations are listed in [decision 0004](0004-separate-implementation-repositories.md).

## Alternatives considered

- **Keep the relay server (decision 0001).** Rejected by the team, which decided that the platform runs without servers.
- **Mailboxes run by users.** A user's always-on device holds ciphertext for them, as in Briar Mailbox. Not chosen for v0.1. Someone must run always-on hardware, and it is a store-and-forward role that this decision excludes. A user's own additional device that is simply online more often is a different case, covered by open question 14.
- **Storage in a distributed hash table.** Ciphertext is stored across peers. Not chosen. Storing peers see sizes and timing, storage is unreliable, and it is store-and-forward by third parties.
