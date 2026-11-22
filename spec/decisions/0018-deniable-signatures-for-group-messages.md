# 0018. Deniable signatures for group application messages, with short-lived keys as in multi-party OTR

**Status:** Proposed

## Context

[Decision 0017](0017-retry-expiry-and-relaying.md) lets group members relay control messages, because those are signed and any member can check them. It left open whether group application messages, the messages users write, are signed ([open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery)). Until that is decided, only their sender can re-send them.

The choice has three parts:

- **Encryption alone does not show who wrote a message.** It keeps outsiders from reading or changing it. But with more than two parties, a key that every member holds does not show which member used it. Goldberg, Ustaoglu, Van Gundy and Chen state this for message authentication codes: they "do not provide origin authentication when used by more than two parties" (mpOTR, section 1). Whether DCGKA's own message keys let one member compute another member's keys is **[open]**: it needs checking against the paper ([decision 0006](0006-dcgka-for-groups.md)) before a record relies on it. If they do, an unsigned message could have been written by any member.
- **A signature under the user's long-term key proves authorship to anyone.** A member can forward a signed message to someone outside the group, and that person can check it. This ends deniability for group messages. The team requires deniability ([decision 0011](0011-cryptographic-suite-and-security-level.md)), and direct messages have it ([decision 0012](0012-mosgird-session-protocol.md)).
- **Relaying needs a signature that members can check.** Without one, a relaying member could change or invent a message (decision 0017).

A published design gives both authorship among members and deniability towards everyone else: I. Goldberg, B. Ustaoglu, M. D. Van Gundy, H. Chen, "Multi-party Off-the-Record Messaging", ACM CCS 2009 (mpOTR). In mpOTR:

- Each participant makes a new signing key for each session.
- It sends that key to each other participant over a deniable two-party key agreement (section 4.2.1, Algorithm 4).
- Messages are encrypted and then signed with that key (section 4.3, Algorithms 5 and 6).
- Members can convince each other who wrote a message, so a member can add messages it missed from another member's copy (sections 2.3 and 4.4).
- Nothing ties the short-lived key to the person, except the deniable two-party exchange. So a transcript proves nothing to an outsider (sections 2.5 and 4.2.1).

Decision 0012's sessions are deniable two-party key agreements of the kind mpOTR assumes.

The team chose this design.

## Decision

1. **Short-lived signing keys.**
   - Each member device makes a new signing key pair for each group epoch. It uses that key only in that group.
   - An epoch ends when the device processes a change of the group's membership, or updates its own DCGKA keys.
   - The key uses the hybrid Ed25519 and ML-DSA-87 signature of decision 0011.
2. **Handing out a key.**
   - A device sends its short-lived public key to each other member device inside a decision 0012 session, following mpOTR's two-party signature key exchange (Algorithm 4). Each side sends its key, together with the group, the epoch, and both identities, encrypted inside the session.
   - Each side then signs the other's key, the group, the epoch and both identities with its own short-lived key, and sends the signature back. This shows that each side holds the private key it announced.
   - The short-lived key is never put in a control message or a device list. Those are signed under long-term keys, which would tie the key to the user.
   - A member device accepts a short-lived key for another device only through this exchange, never from a third member.
3. **Agreeing on keys.** As in mpOTR's attestation step (Algorithm 3), each member device sends the group a hash of the keys it has accepted, listed by device, signed with its own short-lived key. A device that sees a different hash learns that some member was shown a different key, and treats it like an equivocating sender under decision 0017.
4. **Signed application messages.**
   - Each application message names the hashes of its causal predecessors, like a control message (decision 0017, point 5). It also names the fingerprint of the short-lived key that signs it.
   - The message is encrypted as before. Then the sender signs the group, the identifier, the predecessor hashes, the key fingerprint and the ciphertext with its short-lived key. This is mpOTR's encrypt-then-sign construction (section 4.3), with decision 0017's fields added.
   - A member device accepts the message only if the signature verifies under the key it accepted from that sender for that epoch.
5. **Relaying application messages.**
   - Members relay application messages by the same reconciliation as control messages (decision 0017, point 5).
   - A member device that has not yet accepted the sender's short-lived key holds the message until it does. It cannot get the key from anyone but the sender.
   - A member processes later control messages without waiting for a missing application message. A held application message expires under decision 0017, point 8, even though it has not been processed. The rule there that unprocessed messages do not expire applies only to control messages.
6. **Old private keys are not published.** mpOTR lets each participant publish its short-lived private key when a session ends, so that anyone can edit an old transcript (section 4.4). This decision does not do so. mpOTR states that its protocol is deniable without it, and a key published before every member has finished lets anyone impersonate the sender. Whether to add it later is open.
7. **Control messages are unchanged.** DCGKA signs them under the member's identity key (decision 0006), so membership changes stay non-deniable towards other members, as [open question 18](../v0.1/open-questions.md#18-post-quantum-deniable-authentication) records.

This settles the open detail of question 14 on signing group application messages.

## Consequences

- **Members cannot write messages in another member's name.** A message is accepted only under the short-lived key that its sender handed over in a deniable session.
- **Members can relay application messages.** The relaying of decision 0017 now covers all group messages, once a member holds the sender's short-lived key.
- **Deniable towards outsiders.** A signed message proves only that the holder of a short-lived key wrote it. Nothing ties that key to a user, except a decision 0012 session, and that proves nothing to a third party. This rests on mpOTR's argument, which the paper does not formally prove (section 5). The argument has to be checked for Mosgird, as for decision 0012 (open question 18).
- **Not deniable among members.** A member that accepted Alice's key is convinced that Alice wrote a message, and can show it to other members who accepted the same key. This is the intent of mpOTR (section 2.3). Each such member can still deny it in front of an outsider.
- **Every pair of members must meet once per epoch.** A member device reads a sender's messages only after a direct session with that sender in the current epoch. A member that is rarely online at the same time as a sender may hold that sender's messages unread until the next meeting, or until they expire. The setup of mpOTR assumes that all participants are online together. Adapting it to devices that come online at different times needs a cryptographer's review.
- **Larger messages.** Each application message carries a hybrid signature of 4,691 bytes (4,627 for ML-DSA-87, 64 for Ed25519). Each key exchange carries a 2,624-byte public key. Over Tor and I2P, this adds noticeable latency for short messages.
- **New observations for members.** Members see which short-lived key each member device uses in each epoch, and when two members last held a session. This is added to [the list of what other parties can observe](../v0.1/metadata.md).
- **Formal model.** Decision 0013 requires the group model to change with the protocol. `group_relay.pv` now also covers application messages signed under short-lived keys handed over through a private channel. It checks only authenticity. Deniability cannot be checked in ProVerif's usual form.

## Alternatives considered

- **No signatures.** Not chosen. Members could not be sure who wrote a message, if DCGKA's keys allow one member to compute another's, and members could not relay application messages.
- **Signing with the user's long-term key.** Not chosen. Any message forwarded outside the group would prove authorship to anyone. That gives up the team's deniability requirement for group messages, and AGENTS.md forbids weakening a requirement to reach another goal.
- **A message authentication code for each recipient**, using the keys of decision 0012 sessions. Not chosen. Those keys last one connection, so a code could be checked only by a member connected to the sender at the time. Members also could not relay messages to each other, because a code for one member convinces no other member.
- **Designated-verifier or ring signatures** (open question 18, option C). Not chosen. They are research designs with no production library.
- **Publishing old private keys** (mpOTR, section 4.4). Deferred, as point 6 explains.
