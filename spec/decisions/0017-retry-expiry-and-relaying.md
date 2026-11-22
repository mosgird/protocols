# 0017. Retry, expiry and relaying: sender retry for direct messages, member relaying for groups

**Status:** Proposed

## Context

Delivery is online-only ([decision 0005](0005-serverless-online-only-delivery.md)). A message reaches a device only while the sender and that device can reach each other. [Open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery) asked how long a sending device keeps and retries an undelivered message, what the sender is told, and whether anyone other than the sender may carry it.

Four facts constrain the answer:

- Sessions last one connection ([decision 0012](0012-mosgird-session-protocol.md)). A message cannot be encrypted in advance for a device that is offline. It waits in the device's encrypted store ([decision 0015](0015-protection-of-stored-data.md)) until a connection exists.
- A direct message is encrypted separately for each approved device of the recipient ([decision 0016](0016-user-identity-and-linked-devices.md), point 11). A device that the sender holds or distrusts receives nothing. This protects against a stolen primary device that adds an attacker's device to its list.
- DCGKA needs every member to process every causally prior group message ([decision 0006](0006-dcgka-for-groups.md)). If only the original sender can re-send, a group stalls for a member whenever that member and the sender are never online together.
- Every group protocol message is signed under its sender's key (decision 0006). Any member can check a message no matter who passed it on.

The team chose relaying by group members (option C of question 14), an expiry of 30 days that the user can change, and a per-device and per-member delivery view for the sender.

The relaying follows a published design: M. Kleppmann and H. Howard, "Byzantine Eventual Consistency and the Fundamental Limits of Peer-to-Peer Databases", arXiv:2012.00472, 2020. Each message names the hashes of its causal predecessors. Two replicas that meet exchange the messages one of them is missing, using those hashes. The paper shows that this reaches the same set of messages on all correct replicas even when some replicas are malicious, including a sender that shows different replicas different messages.

## Decision

1. **Pending messages.** A device keeps each message it has not yet delivered in its encrypted store (decision 0015). It tries to deliver whenever a connection to the target device comes up.
2. **Message identifiers.** The sender gives each message a 256-bit random identifier. It is the same in every copy of the message. A device that receives an identifier it already has drops the copy, and acknowledges it again.
3. **Direct messages: the sender retries (option A).** Only the sending device delivers a direct message, to each approved device of the recipient and to each of the sender's own other devices (decision 0016, point 11). Devices of the recipient do not pass direct messages to each other. That would deliver to devices that the sender holds or distrusts.
4. **Acknowledgments for direct messages.** Inside the session, the receiving device acknowledges the identifiers it received. The sender deletes a stored message once every device it was meant for has acknowledged it, or once it expires. The wire encoding is not defined in v0.1, like every other format.
5. **Groups: members relay (option C).**
   - Every message sent by authenticated causal broadcast (decision 0006) names the hashes of its causal predecessors.
   - Every member device keeps the group messages it has received. When it is connected to another member device of the same group, the two exchange the messages one of them is missing, by the reconciliation of Kleppmann and Howard.
   - A device accepts a relayed message only if the original sender's signature verifies over its content and its predecessor hashes. The member that passed it on is not trusted for anything.
   - This implements the causal broadcast that decision 0006 assumes. DCGKA itself is unchanged.
6. **Acknowledgments for groups.** A member's signed group message acknowledges every message its predecessor hashes cover. A member that has received messages but sent nothing for a while sends a short acknowledgment message that carries its current predecessor hashes. A member stops relaying a message once every member has acknowledged it, or once it expires.
7. **Relaying is not store-and-forward.** A group member relays only messages of groups it belongs to, which it can read itself. It is an intended participant, not a third party in the sense of decision 0005. Decision 0005 is not changed.
8. **Expiry.**
   - A message expires after 30 days by default. The user can choose any value from 1 to 90 days. The setting applies to what the user's own devices keep.
   - The clock starts at the earlier of two times: the creation time that the sender signed into the message, and the time this device first stored it. So a message that passes between members does not live longer, and a creation time in the future gives it no extra time.
   - An expired message is deleted. Its identifier and hash are kept, so that it is not requested again during reconciliation.
   - A device accepts and processes a message of any age. It keeps the message for relaying only within its own expiry time.
9. **What the sender sees.** Each message shows one of three states: pending, delivered, or expired. On request, the sender sees delivery per device ("delivered to 2 of 3 devices") or per member ("delivered to 4 of 6 members"). An expired message is shown as not delivered to the devices or members that never acknowledged it.
10. **Storage limit.** Pending and relayed messages share a limit of 256 MiB per device by default. When the limit is reached, messages held for other members are dropped first, oldest first. A user's own undelivered messages are never dropped silently: the user is told, and chooses what to delete. Attachments are not counted here ([open question 8](../v0.1/open-questions.md#8-attachments-and-file-transfer)).
11. **Retry timing.** Besides trying on every connection, a device retries on a schedule chosen by the implementation. The schedule must back off between failed attempts and must not use a fixed period, because a fixed period would make a device recognisable by its timing. How a phone retries without push services is [open question 17](../v0.1/open-questions.md#17-mobile-reachability-without-push-services).

This closes [open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery), except for the open details listed there.

## Consequences

- **Groups do not stall on one sender.** Any member that holds a message can pass it on, so a member catches up when it meets any other member.
- **A relaying member cannot forge or change a message.** The sender's signature covers the content and the predecessor hashes. A draft ProVerif model checks this ([formal models](../v0.1/models/README.md), `group_relay.pv`).
- **A relaying member can withhold.** It can decline to pass a message on. Reconciliation with any other member that holds the message repairs this.
- **A sender that equivocates is detected.** If a sender signs two different messages and shows each to different members, reconciliation gives both to every correct member. They see two messages from the same sender with the same predecessors. What a client does then is part of [open question 6](../v0.1/open-questions.md#6-abuse-handling-for-an-encrypted-service).
- **Members learn more about each other.** From reconciliation, a member learns when other members were online and which messages each was missing. Members store each other's group messages until every member acknowledges them or they expire. This is added to [overview section 3.3](../v0.1/overview.md#33-what-other-parties-can-observe).
- **A member offline for too long cannot catch up alone.** If every copy of a message has expired before a member comes back, that member can never process the messages after it, because DCGKA processes messages in causal order. The proposed remedy is to remove the member and add it again. This stays an open detail of question 14.
- **Direct messages still need both devices online together.** A recipient's device that is rarely online gets direct messages only when the sender's device is online at the same time.
- **More traffic and storage.** Predecessor hashes, acknowledgments, and reconciliation rounds add traffic to every group. Every member device stores group messages for up to the expiry time, within the storage limit.
- **Formal model.** Decision 0013 requires the group protocol's model to change with it. No model of DCGKA exists yet. The new model covers only the authenticity of relayed messages. Reconciliation, expiry, and equivocation detection are not modelled.

## Alternatives considered

- **Sender-only retry for groups.** Not chosen. A group stalls for a member whenever that member and the original sender are never online together, and DCGKA cannot skip a message.
- **Relaying as an option each group turns on.** Not chosen. Two behaviours to specify, model, and test, and groups without it stall as above.
- **Relaying direct messages through the recipient's own devices** (option B of question 14). Not chosen. A device of the recipient would pass messages to devices that the sender holds or distrusts, which removes the protection of decision 0016 against a stolen primary device. It stays an open detail of question 14.
- **Per-sender sequence numbers.** Not chosen. Members would compare counters such as "message 41 from Alice". A sender could give two members two different messages with the same number, and neither would notice.
- **Sending every recent group message at each meeting.** Not chosen. It costs much more traffic over Tor and I2P, and tells members more about each other's online times.
- **No expiry.** Not chosen. Storage, and the data exposed to someone who takes a device ([decision 0015](0015-protection-of-stored-data.md)), would grow without bound.
- **A fixed expiry of 7 days**, as for invites ([decision 0014](0014-first-contact-by-invite.md)). Not chosen. Messages to someone away for a week would fail.
