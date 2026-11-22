# 0003. MLS (RFC 9420) for group chats and channels

**Status:** Superseded

Superseded by [decision 0006](0006-dcgka-for-groups.md). The text below is kept as it was proposed.

## Context

Group chats and channels have many members whose membership changes over time. Pairwise sessions do not scale well to large groups: the sender would encrypt once per member device, and membership changes would require re-keying in ad hoc ways. The project must not invent a group key scheme.

## Decision

- Group chats and channels use the Messaging Layer Security protocol, as specified in RFC 9420.
- Each channel is one MLS group. Each group chat is one MLS group. Whether a server is one group or several is an open question (see [open questions, section 11](../v0.1/open-questions.md#11-ambiguities-in-the-initial-brief)).
- Membership changes are made with MLS commits. Each commit advances the group epoch.
- The relay server acts as the MLS Delivery Service. It delivers handshake and application messages. It does not participate in key derivation.
- The ciphersuite and group size limits are open (see [open question 9](../v0.1/open-questions.md#9-group-protocol-primitives-and-group-size-limits), which now covers DCGKA).

## Consequences

- Removing a member and adding a member both advance the epoch. Removed devices cannot decrypt later epochs.
- The server must order commits for each group. Concurrent commits must be handled as RFC 9420 defines. The server's role in ordering must be specified against the RFC.
- Clients must store MLS group state, which must survive app restarts and device loss. Its backup and recovery interact with [message history sync](../v0.1/open-questions.md#5-message-history-sync).
- The server learns group membership to the extent that delivery needs it. Whether more than that is visible is an open question.

## Alternatives considered

- **Pairwise sessions for every group member.** Rejected. Fan-out cost grows with group size, and membership changes need separate re-keying logic.
- **A shared group key distributed by the server.** Rejected. The server would hold group secrets, which contradicts [decision 0001](0001-relay-based-e2ee.md).
- **A custom group scheme.** Rejected. The project does not invent cryptography.
