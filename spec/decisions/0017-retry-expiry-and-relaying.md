# 0017. Retry, expiry and relaying: sender retry for direct messages, member relaying for groups

**Status:** Proposed

## Context

Delivery is online-only ([decision 0005](0005-serverless-online-only-delivery.md)). A message reaches a device only while the sender and that device can reach each other. [Open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery) asked how long a sending device keeps and retries an undelivered message, what the sender is told, and whether anyone other than the sender may carry it.

Four facts constrain the answer:

- Sessions last one connection ([decision 0012](0012-mosgird-session-protocol.md)). A message cannot be encrypted in advance for a device that is offline. It waits in the device's encrypted store ([decision 0015](0015-protection-of-stored-data.md)) until a connection exists.
- A direct message is encrypted separately for each approved device of the recipient ([decision 0016](0016-user-identity-and-linked-devices.md), point 11). A device that the sender holds or distrusts receives nothing. This protects against a stolen primary device that adds an attacker's device to its list.
- DCGKA needs every member to process every causally prior control message ([decision 0006](0006-dcgka-for-groups.md)). If only the original sender can re-send, a group stalls for a member whenever that member and the sender are never online together.
- Group protocol messages are signed under their sender's key (decision 0006). Any member can check such a message no matter who passed it on.

The team chose relaying by group members (option C of question 14), an expiry of 30 days that the user can change, and a per-device and per-member delivery view for the sender.

The relaying follows a published design: M. Kleppmann and H. Howard, "Byzantine Eventual Consistency and the Fundamental Limits of Peer-to-Peer Databases", arXiv:2012.00472, 2020. Each update names the hashes of its causal predecessors. Two replicas that meet exchange the updates one of them is missing, using those hashes. The paper shows that all correct replicas reach the same set of updates even when some replicas are malicious. That guarantee assumes that correct replicas never delete updates and are eventually connected to each other. Expiry (point 8) gives up the first assumption, so here the guarantee holds only for messages that some member still keeps.

## Decision

1. **Pending messages.** A device keeps each message it has not yet delivered in its encrypted store (decision 0015). It tries to deliver whenever a connection to the target device comes up.
2. **Message identifiers.** The sender gives each message a 256-bit random identifier, the same in every copy. For a direct message, the identifier travels inside the session, which authenticates it. For a group message, the sender's signature covers it (point 5). A device drops a direct message whose identifier it already has, and a group message whose hash it already has, and acknowledges it again.
3. **Direct messages: the sender retries (option A).** Only the sending device delivers a direct message, to each approved device of the recipient and to each of the sender's own other devices (decision 0016, point 11). Devices of the recipient do not pass direct messages to each other. That would deliver to devices that the sender holds or distrusts.
4. **Acknowledgments for direct messages.** Inside the session, the receiving device acknowledges the identifiers it received. The sender deletes a stored message once every device it was meant for has acknowledged it, or once it expires. A device that the sender holds (decision 0016, point 10) is one that the message is meant for: the message waits for it, and expires like any other if the user has not approved the device in time. The wire encoding is not defined in v0.1, like every other format.
5. **Group control messages: members relay (option C).**
   - Relaying covers the group's control messages: the messages that DCGKA sends by authenticated causal broadcast (decision 0006), including acknowledgments (point 6). The two-party messages that DCGKA sends with a control message are carried with it, still encrypted for their recipient, and are relayed with it.
   - Every control message names the hashes of its causal predecessors. Among them is always the hash of the previous control message that the same sender device sent in that group.
   - The sender's signature covers the group, the identifier, the content, and the predecessor hashes. So a member cannot move a message into another group, relabel it, change it, or change its place in the causal order.
   - Every member device keeps the control messages it has received. When it is connected to another member device of the same group, the two exchange the messages one of them is missing, by the reconciliation of Kleppmann and Howard. A device passes on only messages the other device lacks.
   - A device accepts a relayed message only if the original sender's signature verifies. The member that passed it on is not trusted for anything.
   - This implements the causal broadcast that decision 0006 assumes. DCGKA itself is unchanged.
   - Application messages are not relayed by this decision. Whether they are signed is open: signing lets members check them and relay them, but removes their deniability within the group. Until that is decided, only their sender retries them, as in point 3.
6. **Acknowledgments for groups.** A member's signed control message acknowledges every message its predecessor hashes cover. A member that has received messages but sent nothing for a while sends a short acknowledgment message that carries its current predecessor hashes. A member stops relaying a message once every member device has acknowledged it, or once it expires.
7. **Relaying and decision 0005.** Decision 0005 says that no third party holds messages for an offline device. A group member relays only control messages of groups it belongs to, which it can check and process itself. It is an intended participant, not a third party. This is how this decision reads decision 0005. Decision 0005 is not changed.
8. **Expiry.**
   - A message expires after 30 days by default. The user can choose any value from 1 to 90 days. The setting applies to what the user's own devices keep.
   - The clock starts when this device first stored the message. The creation time a sender writes into a message is shown to users but plays no part in expiry, so a sender cannot make a message expire early or late by its clock.
   - A message is passed on only to a device that lacks it, so a message stops travelling once every member device has it.
   - A message that a device has not yet processed, because a predecessor is missing, does not expire. Nor does any message that such a message names as a predecessor.
   - When a processed message expires, it is deleted. Its identifier and hash are kept, so that it is not requested again during reconciliation.
9. **What the sender sees.** Each message shows one of three states: pending, delivered, or expired. On request, the sender sees delivery per device ("delivered to 2 of 3 devices") or per member ("delivered to 4 of 6 members"). An expired message is shown as not delivered to the devices or members that never acknowledged it. Held devices are listed apart from approved ones.
10. **Storage limit.**
    - Pending and relayed messages share a limit of 256 MiB per device by default. Attachments are not counted here ([open question 8](../v0.1/open-questions.md#8-attachments-and-file-transfer)).
    - When the limit is reached, a device drops messages it holds for others, starting with the sender whose messages take the most space, oldest first.
    - It never drops a message it has not yet processed, or one that such a message needs.
    - It never drops a user's own undelivered message silently: the user is told, and chooses what to delete.
11. **Retry timing.** Besides trying on every connection, a device retries on a schedule chosen by the implementation. The schedule must back off between failed attempts and must not use a fixed period, because a fixed period would make a device recognisable by its timing. How a phone retries without push services is [open question 17](../v0.1/open-questions.md#17-mobile-reachability-without-push-services).

This closes [open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery), except for the open details listed there.

## Consequences

- **Groups do not stall on one sender.** Any member that holds a control message can pass it on, so a member catches up when it meets any other member that still holds what it needs.
- **A relaying member cannot forge or change a message.** The sender's signature covers the group, the identifier, the content, and the predecessor hashes. A draft ProVerif model checks this ([formal models](../v0.1/models/README.md), `group_relay.pv`).
- **A relaying member can withhold.** It can decline to pass a message on. Reconciliation with any other member that holds the message repairs this.
- **A sender that equivocates becomes visible.** Each control message names the sender device's previous one. If a sender signs two messages of which neither comes after the other, and shows each to different members, reconciliation gives both to every member that meets holders of both. Members then hold two signed messages from one sender that fork. What a client does then is part of [open question 6](../v0.1/open-questions.md#6-abuse-handling-for-an-encrypted-service).
- **One member can still cost the group storage.** Eviction by the largest sender limits this, but a member that sends many large control messages takes space on every member device.
- **Members learn more about each other.** From reconciliation, a member learns when other members were online and which messages each was missing. Members store each other's control messages until every member acknowledges them or they expire. Someone who takes a device finds other members' group messages, encrypted, for up to the expiry time, and the kept hashes show how many messages a group had. This is added to [the list of what other parties can observe](../v0.1/metadata.md).
- **A member offline for too long cannot catch up alone.** If every copy of a control message has expired before a member comes back, that member can never process the messages after it, because DCGKA processes them in causal order. This stays an open detail of question 14.
- **Direct and application messages still need both devices online together.** A recipient's device that is rarely online gets them only when the sender's device is online at the same time.
- **More traffic and storage.** Predecessor hashes, acknowledgments, and reconciliation rounds add traffic to every group. Acknowledgment messages are control messages too, so they join the causal order.
- **Formal model.** Decision 0013 requires the group protocol's model to change with it. No model of DCGKA exists yet. The new model covers only the authenticity of relayed messages under one signing key. Key rotation, reconciliation, expiry, and equivocation are not modelled.

## Alternatives considered

- **Sender-only retry for groups.** Not chosen. A group stalls for a member whenever that member and the original sender are never online together, and DCGKA cannot skip a control message.
- **Relaying as an option each group turns on.** Not chosen. Two behaviours to specify, model, and test, and groups without it stall as above.
- **Relaying direct messages through the recipient's own devices** (option B of question 14). Not chosen. A device of the recipient would pass messages to devices that the sender holds or distrusts, which removes the protection of decision 0016 against a stolen primary device. It stays an open detail of question 14.
- **Per-sender sequence numbers.** Not chosen. Members would compare counters such as "message 41 from Alice". A sender could give two members two different messages with the same number, and neither would notice.
- **Sending every recent group message at each meeting.** Not chosen. It costs much more traffic over Tor and I2P, and tells members more about each other's online times.
- **Expiry counted from the sender's creation time.** Not chosen. A sender could backdate a message so that every device treats it as expired at once and nobody relays it, which would cut off any member that missed it.
- **No expiry.** Not chosen. Storage, and the data exposed to someone who takes a device ([decision 0015](0015-protection-of-stored-data.md)), would grow without bound.
- **A fixed expiry of 7 days**, as for invites ([decision 0014](0014-first-contact-by-invite.md)). Not chosen. Messages to someone away for a week would fail.
