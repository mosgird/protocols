# 0019. The two-party component of DCGKA: the authors' protocol with X-Wing, and prekeys from sessions

**Status:** Proposed

## Context

DCGKA sends some secrets to one member at a time: the seed secret of a key update, and the state a new member needs. It encrypts them with a two-party secure messaging (2SM) protocol (DCGKA paper, section 5.3). Which one was [open question 15](../v0.1/open-questions.md#15-two-party-component-for-dcgka).

What the paper requires, checked against its CCS 2021 text:

- **2SM must reach members who are offline.** 2SM "must use a Public Key Infrastructure (PKI) or key server to map these IDs to public keys", and that infrastructure "should include ephemeral prekeys … This allows users to send messages to a new group member, even if that member is currently offline" (section 5.3).
- **2SM must heal with every message.** The Signal protocol "does not suffice for our purposes because it heals from a compromise only after several rounds of communication, not with each message sent" (section 5.3). The paper uses a protocol with optimal forward secrecy and post-compromise security.
- **What 2SM may assume.** The 2SM security game assumes authentic, in-order delivery, which DCGKA's authenticated causal broadcast provides, and asks for IND-CPA security (appendix B). Schemes that meet it are described by Jost, Maurer and Mularczyk, and by Durak and Vaudenay (appendix B).
- **What the authors use.** The authors' implementation uses "a protocol described informally by Jost et al. [section 2.2] as a simplification of their full protocol" (section 8.2). Their extended version, IACR ePrint 2020/1281, describes it formally (section 5.3, appendix B). Their code is `TwoPartyProtocol.java` in `trvedata/key-agreement`. In it, each message carries the payload, the secret key of a new key pair, and the public key of another new key pair, all encrypted with public-key encryption.

In this project, DCGKA's two-party messages travel inside control messages, and members relay control messages ([decision 0017](0017-retry-expiry-and-relaying.md)). A two-party message can therefore reach its recipient days after it was written, through a third member. Decision 0012's sessions need both devices online for one connection, and their keys last one connection ([decision 0012](0012-mosgird-session-protocol.md)). They cannot carry such a message.

The team chose option A of question 15, with prekeys handed out in sessions and a signed prekey on each device as a fallback.

## Decision

1. **The 2SM protocol.** DCGKA's two-party messages use the protocol the DCGKA authors use: Jost, Maurer, Mularczyk, "Efficient Ratcheting: Almost-Optimal Guarantees for Secure Messaging", EUROCRYPT 2019, section 2.2, as the extended DCGKA paper describes it formally (ePrint 2020/1281). This specification references that description. It does not restate or change it.
2. **Public-key encryption.** The protocol needs only public-key encryption. It uses an X-Wing encapsulation followed by XChaCha20-Poly1305 under the shared secret, so the post-quantum level is that of [decision 0011](0011-cryptographic-suite-and-security-level.md). X-Wing is IND-CCA secure, which covers the IND-CPA security that the 2SM game asks for. The exact construction (HPKE as RFC 9180 defines it with X-Wing, or a form that derives the key with BLAKE2b) is **[open]**, as question 15 records.
3. **One-time prekeys from sessions.** Whenever two devices that share a group hold a decision 0012 session, each gives the other a small number of one-time X-Wing prekeys, reserved for that one device. A device deletes the private part of a one-time prekey when it first decrypts with it. Group members meet in sessions anyway, to exchange short-lived signing keys ([decision 0018](0018-deniable-signatures-for-group-messages.md), point 3).
4. **A signed prekey as fallback.** Each device also keeps one *signed prekey*: an X-Wing public key, its creation time, and the device identifier, signed with the device's own signature keys (the hybrid signature of decision 0011).
   - The signed prekey travels with the device list ([decision 0016](0016-user-identity-and-linked-devices.md), point 9) to everyone who receives that list, but it is not part of the list. The device signs it itself, so a device can replace it without the primary device.
   - A device replaces its signed prekey every 7 days. It keeps the old private part for 90 days after that, the longest expiry a user can set under decision 0017, and then deletes it.
5. **Which prekey is used.** The first two-party message from one device to another uses a one-time prekey of the recipient if the sender holds one, and the recipient's signed prekey if not. Every later message uses the keys that earlier messages carried, as the protocol of point 1 defines.
6. **Direct messages are unchanged.** They keep decision 0012's sessions and ratchet.

This closes [open question 15](../v0.1/open-questions.md#15-two-party-component-for-dcgka), except for the open details listed there.

## Consequences

- **The paper's analysis applies to the protocol as published.** The authors' 2SM is the one their proof covers. Two changes need checking: the encryption of point 2 replaces the authors' choice, and point 4's prekeys are this project's arrangement.
- **The record rests on a description it has not seen.** The extended version (ePrint 2020/1281) could not be fetched when this record was written. The record cites the CCS paper and the authors' code. Someone must check point 1 against the extended version before this decision leaves Proposed.
- **What a leaked signed prekey exposes.** If a device's signed prekey leaks while its private part is still kept, the attacker can read every two-party message that was encrypted to that prekey. It can also read every later message from the same sender until the device replies, because each message carries the key for the next. The model's negative control shows this. Those messages carry seed secrets, so the group messages those secrets protect are exposed until the sender's next key update. A one-time prekey has no such window.
- **A message that arrives after its prekey is deleted cannot be read.** Unprocessed control messages never expire (decision 0017, point 8), but a signed prekey's private part is deleted 90 days after it is replaced. A device that receives a control message after that misses the seed secret and cannot read that sender's group messages. How it recovers is part of the catch-up after expiry in [open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery).
- **Two two-party protocols.** Implementations need decision 0012's sessions and this 2SM, with separate tests.
- **Size.** Each two-party message carries an X-Wing public key (1,216 bytes), an X-Wing secret key (32 bytes), an X-Wing ciphertext (1,120 bytes), and the AEAD nonce and tag (40 bytes): about 2.4 KB beyond its payload. A key update in a group of n member devices sends n − 1 of them, about 300 KB for 128 devices. The paper measured 39.6 kB for a 128-member key update with Curve25519. Over Tor and I2P, key updates in large groups will be slow.
- **More for contacts and members to observe.** Everyone who receives a device's list sees its signed prekey and when it is replaced, and so roughly when the device was last online. Two devices see each other's one-time prekeys. This is added to [the list of what other parties can observe](../v0.1/metadata.md). The signed prekey is signed under the device's long-term key, so it proves to anyone that the device published it, like the device list itself.
- **Nothing becomes less deniable.** Two-party messages travel inside control messages, which were already signed under long-term keys (decision 0006).
- **Formal model.** Decision 0013 requires a model of the group protocol. `two_party.pv` covers one bounded exchange between honest devices: a first message under a one-time prekey, a second before the reply, the reply, and an answer. With authentic in-order delivery, all four payloads stay secret even when both devices' remaining keys are revealed afterwards. The model does not cover recovery after compromise, messages sent by both sides at once, the signed prekey's lifetime, or computational security. That last point is what the paper's proof covers.

## Alternatives considered

- **Decision 0012's session protocol as 2SM** (question 15, option B). Not chosen. Its sessions need both devices online, and its keys last one connection, so it cannot carry a message relayed days later. The paper also states that a ratchet that heals only on a change of direction does not suffice.
- **The 2SM protocol for direct messages too** (question 15, option C). Not chosen. It would supersede part of decision 0012, and restart the analysis of direct-message deniability ([open question 18](../v0.1/open-questions.md#18-post-quantum-deniable-authentication)) and its model.
- **Signal's PQXDH with the Double Ratchet as 2SM.** Not chosen. The paper states that the Signal protocol does not suffice.
- **Durak and Vaudenay's protocol.** Not chosen. The DCGKA authors name it as meeting their game, but they built and measured the protocol of point 1.
- **One-time prekeys only.** Not chosen. A member could not send a seed secret to a device it has never met in a session, so key updates would stall for members who are rarely online together.
- **The device's identity X-Wing key as the fallback.** Not chosen. A first message under it would be exposed for as long as the device exists if that key leaked, not only until a 7-day rotation and 90-day deletion.
- **The signed prekey inside the device list.** Not chosen. The primary device signs the list (decision 0016), so every device's weekly rotation would need the primary device online.
