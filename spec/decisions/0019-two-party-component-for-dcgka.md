# 0019. The two-party component of DCGKA: the authors' protocol with X-Wing, and prekeys from sessions

**Status:** Proposed

## Context

DCGKA sends some secrets to one member at a time: the seed secret of a key update, and the state a new member needs. It encrypts them with a two-party secure messaging (2SM) protocol (DCGKA paper, section 5.3). Which one was [open question 15](../v0.1/open-questions.md#15-two-party-component-for-dcgka).

What the paper requires, checked against its CCS 2021 text:

- **2SM must reach members who are offline.** 2SM "must use a Public Key Infrastructure (PKI) or key server to map these IDs to public keys", and that infrastructure "should include ephemeral prekeys … This allows users to send messages to a new group member, even if that member is currently offline" (section 5.3).
- **2SM must heal with every message.** The Signal protocol "does not suffice for our purposes because it heals from a compromise only after several rounds of communication, not with each message sent" (section 5.3). The paper uses a protocol with optimal forward secrecy and post-compromise security.
- **What 2SM may assume, and what it must give.** The 2SM security game assumes authentic, in-order delivery, which DCGKA's authenticated causal broadcast provides. It asks for IND-CPA security, and for forward secrecy in the sense that compromising a party after it received a message reveals nothing about that message (appendix B, Figures 11 and 12). Schemes that meet it are described by Jost, Maurer and Mularczyk, and by Durak and Vaudenay (appendix B).
- **What the authors use.** The authors' implementation uses "a protocol described informally by Jost et al. [section 2.2] as a simplification of their full protocol" (section 8.2). Their extended version, IACR ePrint 2020/1281, describes it formally (section 5.3, appendix B). In their code (`TwoPartyProtocol.java` and `PreKeySecret.java` in `trvedata/key-agreement`):
  - each message carries the payload, the secret key of a new key pair, and the public key of another new key pair, all encrypted with public-key encryption;
  - the first message to a device is encrypted instead with a key agreed by X3DH, from the sender's identity key, the recipient's signed prekey and one-time prekey, and an ephemeral key;
  - each group keeps its own 2SM state for each other member (DCGKA paper, section 6.2, `γ.2sm[ID]`).

In this project, DCGKA's two-party messages travel inside control messages, and members relay control messages ([decision 0017](0017-retry-expiry-and-relaying.md)). A two-party message can therefore reach its recipient days after it was written, through a third member. Decision 0012's sessions need both devices online for one connection, and their keys last one connection ([decision 0012](0012-mosgird-session-protocol.md)). They cannot carry such a message.

The team chose option A of question 15, with prekeys handed out in sessions and a signed prekey on each device as a fallback.

## Decision

1. **The 2SM protocol.** DCGKA's two-party messages use the protocol the DCGKA authors use: Jost, Maurer, Mularczyk, "Efficient Ratcheting: Almost-Optimal Guarantees for Secure Messaging", EUROCRYPT 2019, section 2.2, as the extended DCGKA paper describes it formally (ePrint 2020/1281). This specification references that description. Points 2 and 6 are the only changes.
2. **Public-key encryption.** The protocol needs public-key encryption. It uses an X-Wing encapsulation followed by XChaCha20-Poly1305, the KEM-then-AEAD hybrid (R. Cramer, V. Shoup, "Design and analysis of practical public-key encryption schemes secure against adaptive chosen ciphertext attack", SIAM Journal on Computing, 2003; the same structure as HPKE, RFC 9180). The post-quantum level is that of [decision 0011](0011-cryptographic-suite-and-security-level.md). How the AEAD key is derived from the X-Wing shared secret is **[open]** (question 15).
3. **One state per group and pair of devices.** As in DCGKA, each device keeps a separate 2SM state for each group and each other member device. Causal broadcast orders messages only within a group, so a state shared between groups would receive messages out of order.
4. **One-time prekeys from sessions.**
   - Whenever two devices that share a group hold a decision 0012 session, each gives the other a few one-time X-Wing prekeys, reserved for that one device. Group members meet in sessions anyway, to exchange short-lived signing keys ([decision 0018](0018-deniable-signatures-for-group-messages.md), point 3). How many is **[open]**.
   - A sender uses each one-time prekey for one first message, in one group, and then forgets it.
   - The device that made a one-time prekey deletes its private part when it first decrypts with it, or 30 days after handing it out if it is unused. The other device forgets an unused one after 30 days as well.
5. **A signed prekey as fallback.**
   - Each device keeps one *signed prekey*: an X-Wing public key, its creation time, and the device's identity KEM public key, signed with the device's own signature keys (the hybrid signature of decision 0011).
   - The signed prekey travels with the device list ([decision 0016](0016-user-identity-and-linked-devices.md), point 9) to everyone who receives that list, but it is not part of the list. The device signs it itself, so a device can replace it without the primary device.
   - A device replaces its signed prekey every 7 days. It keeps the old private part for 90 days after that, and then deletes it.
   - A sender uses a signed prekey only if its creation time is later than that of every signed prekey it has seen for that device, and at most 14 days old. Otherwise it waits for a newer one or a one-time prekey. Anyone who relays device lists could otherwise replay an old prekey whose private part has leaked.
6. **The first message.** The first two-party message from one device to another in a group is encrypted under the recipient's prekeys: a one-time prekey if the sender holds one, and the signed prekey if not. Every later message uses the keys that earlier messages carried. The authors derive the first key with X3DH, which needs Diffie–Hellman identity keys that devices here do not have. The post-quantum replacement is **[open]** (question 15). Until it is settled, the first message is encrypted to one prekey with the encryption of point 2.
7. **Held and distrusted devices.** DCGKA sends each seed secret to every member device. Whether a device also sends its seed secrets to member devices it holds or distrusts under decision 0016 is **[open]** (question 15). Sending them lets such a device read this member's group messages, which goes further than decision 0016's "a held device receives nothing". Leaving them out changes DCGKA, which decision 0006 does not allow without a new record. Devices exchange no one-time prekeys with them, because they hold no sessions with them (decision 0018, point 3).
8. **Direct messages are unchanged.** They keep decision 0012's sessions and ratchet, with no prekeys.

This closes [open question 15](../v0.1/open-questions.md#15-two-party-component-for-dcgka), except for the open details listed there.

## Consequences

- **Whether the paper's analysis applies is [open].** The authors' 2SM is the one their proof covers. Three changes need checking: the encryption of point 2, the first message of point 6, and the signed prekey of point 5. The extended version (ePrint 2020/1281) could not be fetched when this record was written, and the record cites the CCS paper and the authors' code. Someone must check this record against the extended version before it leaves Proposed.
- **The signed prekey falls short of the 2SM game's forward secrecy.** Its private part is kept for up to 97 days and serves every sender in every group. If it leaks in that time, the attacker reads every first message that was encrypted to it. Each message carries the key for the sender's next one, so the attacker also reads every later message from that sender in that group, until the sender processes a reply from the recipient. Relaying can make that take days. The model's negative control shows this. Those messages carry seed secrets, so the group messages those secrets protect are exposed until the sender's next key update. AGENTS.md does not allow weakening a requirement for another goal, so this conflict is recorded in question 15 with its options. A one-time prekey has the same exposure while it is unused, or while its message is in transit, and at most 30 days.
- **A two-party message that cannot be read breaks that pair for that group.** Every later message from the sender is encrypted under keys that the lost message carried. This happens when a message arrives after its prekey was deleted: unprocessed control messages never expire, and the expiry clock starts again on each device that stores a message (decision 0017, point 8). The recipient then cannot read that sender's group messages, and DCGKA has no step that restarts a 2SM state. How to restart it is **[open]** (question 15), together with the catch-up after expiry of [open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery).
- **Two two-party protocols.** Implementations need decision 0012's sessions and this 2SM, with separate tests.
- **Size.** Each two-party message carries an X-Wing public key (1,216 bytes), an X-Wing secret key (32 bytes), an X-Wing ciphertext (1,120 bytes), and the AEAD nonce and tag (40 bytes): about 2.4 KB beyond its payload.
  - A key update in a group of n member devices carries n − 1 of them in one control message, about 306 KB for 128 devices.
  - Members relay the whole control message to every member (decision 0017), so each of the 128 devices receives and stores about 306 KB, about 39 MB across the group.
  - The 127 acknowledgments add about 4.7 KB of signature each, about 0.6 MB in all, each also received by every member.
  - The paper measured 39.6 kB for a whole 128-member key update with Curve25519 and no relaying. That figure is not comparable.
  - Each signed prekey adds 1,216 bytes of key and about 4.7 KB of signature.
  - Over Tor and I2P, key updates in large groups will be slow, and they count against decision 0017's storage limit.
- **More for contacts and members to observe.** This is added to [the list of what other parties can observe](../v0.1/metadata.md).
  - Everyone who receives a device's list sees its signed prekey and when it is replaced, and so roughly when the device was online. The signed prekey proves to anyone that the device published it, like the device list itself.
  - Two devices see each other's one-time prekeys, and the device that gave one learns when it is used.
  - Every group member, and anyone who later reads a member's device, sees each two-party message inside the relayed control messages. They see whether each first message used a one-time or a signed prekey, which shows whether that pair of devices had met in a session. From the cleartext key indexes, they see how many messages each pair exchanged and in which direction. Whether to encrypt or pad these fields is **[open]**.
- **Nothing becomes less deniable.** Two-party messages travel inside control messages, which were already signed under long-term keys (decision 0006).
- **Formal model.** Decision 0013 requires a model of the group protocol. `two_party.pv` covers one bounded exchange between honest devices: a first message under a one-time prekey, a second before the reply, the reply, and an answer. With authentic in-order delivery, all four payloads stay secret even when both devices' remaining keys are revealed afterwards. The model does not cover recovery after compromise, messages sent by both sides at once, the signed prekey path, the first-message key agreement of point 6, or computational security.

## Alternatives considered

- **Decision 0012's session protocol as 2SM** (question 15, option B). Not chosen. Its sessions need both devices online, and its keys last one connection, so it cannot carry a message relayed days later. The paper also states that a ratchet that heals only on a change of direction does not suffice.
- **The 2SM protocol for direct messages too** (question 15, option C). Not chosen. It would supersede part of decision 0012, and restart the analysis of direct-message deniability ([open question 18](../v0.1/open-questions.md#18-post-quantum-deniable-authentication)) and its model.
- **Signal's PQXDH with the Double Ratchet as 2SM.** Not chosen. The paper states that the Signal protocol does not suffice. PQXDH remains a candidate for the first message alone (point 6).
- **Durak and Vaudenay's protocol.** Not chosen. The DCGKA authors name it as meeting their game, but they built and measured the protocol of point 1.
- **One-time prekeys only.** Not chosen. A member could not send a seed secret to a device it has never met in a session, so key updates would stall for members who are rarely online together.
- **The device's identity X-Wing key as the fallback.** Not chosen. A first message under it would be exposed for as long as the device exists if that key leaked, not only for 97 days.
- **The signed prekey inside the device list.** Not chosen. The primary device signs the list (decision 0016), so every device's weekly rotation would need the primary device online.
