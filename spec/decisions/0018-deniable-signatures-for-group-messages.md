# 0018. Deniable signatures for group application messages, with short-lived keys as in multi-party OTR

**Status:** Proposed

## Context

[Decision 0017](0017-retry-expiry-and-relaying.md) lets group members relay control messages, because those are signed and any member can check them. It left open whether group application messages, the messages users write, are signed ([open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery)). Until that is decided, only their sender can re-send them.

The choice has three parts:

- **Encryption alone does not show who wrote a message.** It keeps outsiders from reading or changing it. But with more than two parties, a key that every member holds does not show which member used it. Goldberg, Ustaoglu, Van Gundy and Chen state this for message authentication codes: they "do not provide origin authentication when used by more than two parties" (mpOTR, section 1). DCGKA has this property: every member keeps a copy of every member's ratchet, and that ratchet gives the key for each application message (DCGKA paper, section 4, Figures 1 and 3). So an unsigned message could have been written by any member.
- **DCGKA signs every message under the sender's identity key.** Its authenticated causal broadcast "requires a signature to authenticate the sender of each message" (sections 5.1 and 8.1), application messages included ([decision 0006](0006-dcgka-for-groups.md)). As published, group application messages are therefore not deniable.
- **A signature under the user's long-term key proves authorship to anyone.** A member can forward a signed message to someone outside the group, and that person can check it. This ends deniability for group messages. The team requires deniability ([decision 0011](0011-cryptographic-suite-and-security-level.md)), and direct messages are designed to have it ([decision 0012](0012-mosgird-session-protocol.md)).
- **Relaying needs a signature that members can check.** Without one, a relaying member could change or invent a message (decision 0017).

A published design aims for both authorship among members and deniability of what was said towards everyone else: I. Goldberg, B. Ustaoglu, M. D. Van Gundy, H. Chen, "Multi-party Off-the-Record Messaging", ACM CCS 2009 (mpOTR). In mpOTR:

- Each participant makes a new signing key for each session.
- It sends that key to each other participant over a deniable two-party key agreement (section 4.2.1, Algorithm 4).
- Messages are encrypted and then signed with that key (section 4.3, Algorithms 5 and 6).
- Members can convince each other who wrote a message, so a member can add messages it missed from another member's copy (sections 2.3 and 4.4).
- Nothing ties the short-lived key to the person, except the deniable two-party exchange (sections 2.5 and 4.2.1).

mpOTR needs that two-party exchange to be deniable even against a judge who learns the long-term secrets (section 3.2.3). It notes that SKEME, an exchange authenticated by encryption to long-term keys, does not meet this (section 4.2.1). Whether decision 0012's sessions, which are authenticated by key encapsulation, meet it is **[open]** ([open question 18](../v0.1/open-questions.md#18-post-quantum-deniable-authentication)). This decision is only as deniable as those sessions.

The team chose this design.

## Decision

1. **Epochs.**
   - An epoch of a member device starts with a control message that the device processes: a change of the group's membership, or its own DCGKA key update.
   - The epoch identifier is the hash of that control message. Every member that processes the same control message computes the same identifier. It takes the place of mpOTR's session identifier (Algorithm 2).
   - Concurrent control messages start several epochs. A device makes one key for each epoch it starts.
2. **Short-lived signing keys.**
   - For each epoch, a member device makes a new signing key pair and uses it only in that group and that epoch.
   - The key uses the hybrid Ed25519 and ML-DSA-87 signature of decision 0011.
3. **Handing out a key.**
   - A device sends its short-lived public key to each other member device inside a decision 0012 session, following mpOTR's two-party signature key exchange (Algorithm 4). Each side sends its key, together with the group, the epoch identifier and both identities, encrypted inside the session.
   - Each side then signs the other's key, the group, the epoch identifier and both identities with its own short-lived key, and sends the signature back. This shows that each side holds the private key it announced.
   - A device accepts a short-lived key for another device only through this exchange, never from a third member.
   - A device does not run the exchange, in either direction, with a device it holds or distrusts ([decision 0016](0016-user-identity-and-linked-devices.md), point 10). It accepts no application message from such a device.
4. **Keeping long-term signatures away from short-lived keys.**
   - Short-lived keys, key fingerprints and key lists never appear in a control message or a device list. Those are signed under long-term keys, and would tie the key to the user.
   - Control messages never name an application message as a predecessor, and never acknowledge one. A member's long-term key therefore signs nothing that covers an application message.
5. **Agreeing on keys.** As in mpOTR's multi-party signature key exchange (section 4.2.1, with footnote 9), each member device sends the group a hash of the keys it has accepted in an epoch, listed by device. It sends this as an application message: encrypted, and signed with its short-lived key. A device that sees a different hash learns that some member was shown a different key, but not which. mpOTR then aborts the session; here the response is part of [open question 6](../v0.1/open-questions.md#6-abuse-handling-for-an-encrypted-service), as for an equivocating sender in decision 0017. When the hash is sent, given that pairs of members meet at different times, is open.
6. **Signed application messages.**
   - Each application message names the epoch identifier, the fingerprint of the short-lived key that signs it, and the hashes of the application messages before it from the same group. Application messages form their own hash graph, separate from the graph of control messages.
   - The message is encrypted as before. Then the sender signs the group, the identifier, the epoch identifier, the key fingerprint, the predecessor hashes and the ciphertext with its short-lived key. This is mpOTR's encrypt-then-sign construction (section 4.3), with decision 0017's fields added. Signing the epoch identifier does what signing the session identifier does in mpOTR.
   - A member device accepts the message only if the signature verifies under the key it accepted from that sender for that epoch, and only if the epoch's control message does not causally follow the sender's removal.
   - A device keeps a short-lived public key until every message of its epoch has expired under decision 0017.
7. **Acknowledging and relaying application messages.**
   - A member acknowledges application messages with a short acknowledgment that is itself an application message, signed with its short-lived key. Members stop relaying an application message once every member device has acknowledged it, or once it expires.
   - Members relay application messages by the reconciliation of decision 0017, over the application graph.
   - A member device relays only application messages it has verified.
   - A device that has not yet accepted the sender's key holds a received application message until it does. It cannot get the key from anyone but the sender. A held message expires under decision 0017, point 8, even though it has not been processed. When storage is short, held messages are dropped first, and they count against the member that passed them on (decision 0017, point 10). The rules of decision 0017 that keep unprocessed messages apply only to control messages.
8. **Old private keys are not published.** mpOTR lets each participant publish its short-lived private key when a session ends, so that anyone can edit an old transcript (section 4.4). This decision does not do so. mpOTR states that its protocol is deniable without it, and a key published before every member has finished lets anyone impersonate the sender. Whether to add it later is open.
9. **mpOTR's shutdown step is replaced.** mpOTR checks at the end of a session that all participants hold the same transcript (Algorithm 7). Here, the hash graph and reconciliation of decision 0017 take that role, as the paper allows (section 4.4: the network layer may choose how to reach consensus). This is a change to the structure of mpOTR, and it needs the cryptographer's review below.
10. **Control messages are unchanged; application messages change.** DCGKA signs control messages under the member's identity key (decision 0006), and this decision keeps that. For application messages, the short-lived signature of point 6 replaces DCGKA's identity-key signature. DCGKA's security analysis treats authenticated causal broadcast as a module that authenticates the sender (section 5.1). Whether the short-lived signature satisfies that module's requirements, including that a member's signing key changes on every key update, needs the cryptographer's review below.

This settles the open detail of question 14 on signing group application messages.

## Consequences

- **Members cannot write messages in another member's name.** A message is accepted only under the short-lived key that its sender handed over in a session.
- **Members can relay application messages.** Once a member holds the sender's short-lived key, it can take that sender's messages from any member.
- **What stays deniable, and what does not.**
  - What a member said is deniable towards outsiders, if decision 0012's sessions are deniable in mpOTR's sense (open question 18). mpOTR argues its deniability but does not formally prove it (section 5).
  - That a member took part in a group is not deniable towards outsiders. Control messages carry long-term signatures (decision 0006, open question 18).
  - Among members, a member that accepted Alice's key is convinced that Alice wrote a message, and can show this to other members who accepted the same key. This is the intent of mpOTR (section 2.3).
- **Every pair of members must meet once per epoch.** A member device reads a sender's messages only after a direct session with that sender in the current epoch. A member that is rarely online at the same time as a sender may hold that sender's messages unread until they expire. Each membership change or key update starts a new epoch for every member, so a busy group may never reach a state in which every pair has met. The setup of mpOTR assumes that all participants are online together. Adapting it to devices that come online at different times needs a cryptographer's review.
- **Held and distrusted devices.** A member exchanges no keys with them and shows nothing from them. They can still decrypt group ciphertext that other members relay, because DCGKA gives them the group's keys, as decision 0016 already records.
- **Larger messages.** Each application message carries a hybrid signature of 4,691 bytes (4,627 for ML-DSA-87, 64 for Ed25519). Each key exchange carries a 2,624-byte public key. Over Tor and I2P, this adds noticeable latency for short messages.
- **New observations for members.** Members see which short-lived key each member device uses in each epoch, from the key lists when two members last met, and which application messages each member was missing. Members and seized devices also hold other members' application messages until they are acknowledged or expire. This is added to [the list of what other parties can observe](../v0.1/metadata.md).
- **Formal model.** Decision 0013 requires the group model to change with the protocol. `group_relay.pv` now also covers application messages signed under short-lived keys. It assumes the key travels over an ideal private channel and that both members are honest, so its result follows closely from that assumption. It does not tie a key to a group or epoch, does not model a dishonest member or a leaked key, and does not check deniability. In particular, it does not check point 4.

## Alternatives considered

- **No signatures.** Not chosen. DCGKA's keys let any member compute another member's message keys, so members could not be sure who wrote a message, and could not relay application messages. It would also drop the sender authentication that DCGKA's analysis assumes.
- **DCGKA as published, with identity-key signatures on application messages.** Not chosen, for the reason given for long-term signatures below.
- **Signing with the user's long-term key.** Not chosen. Any message forwarded outside the group would prove authorship to anyone. That gives up the team's deniability requirement for group messages, and AGENTS.md forbids weakening a requirement to reach another goal.
- **Application messages in the control-message graph.** Not chosen. Control messages are signed under long-term keys, so naming or acknowledging an application message in one would tie the sender's long-term key to it.
- **A message authentication code for each recipient**, using the keys of decision 0012 sessions. Not chosen. Those keys last one connection, so a code could be checked only by a member connected to the sender at the time. Members also could not relay messages to each other, because a code for one member convinces no other member.
- **Designated-verifier or ring signatures** (open question 18, option C). Not chosen. They are research designs with no production library.
- **Publishing old private keys** (mpOTR, section 4.4). Deferred, as point 8 explains.
