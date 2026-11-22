# 0006. DCGKA for group chats and channels

**Status:** Proposed

Supersedes [decision 0003](0003-mls-for-groups.md).

## Context

Decision 0003 chose MLS (RFC 9420) for groups. MLS relies on a Delivery Service so that members agree on the order of commits. [Decision 0005](0005-serverless-online-only-delivery.md) removes every server, so no Delivery Service exists.

The team chose decentralized continuous group key agreement (DCGKA), from M. Weidner, M. Kleppmann, D. Hugenroth, and A. R. Beresford, "Key Agreement for Decentralized Secure Group Messaging with Strong Security Guarantees", ACM CCS 2021, doi:10.1145/3460120.3484542. The extended version is IACR ePrint 2020/1281. The paper adapts secure group messaging to networks with no central authority, and claims forward secrecy and post-compromise security after device compromise.

## Decision

- Group chats and channels use the DCGKA protocol as specified in the paper. This specification references the paper for the algorithm. It does not restate or modify it. Any deviation is a new decision record.
- Each channel is one DCGKA group. Each group chat is one DCGKA group. A community with several channels therefore has several groups ([decision 0007](0007-communities.md)).
- Group protocol messages are sent by authenticated causal broadcast, as the paper defines it (section 5.1). Each message is signed under the sender's identity key. A member processes a message only after every message that causally precedes it. Over the transport, a broadcast is sent to each member device directly, and missing messages are re-sent.
- The two-party secure messaging (2SM) component that DCGKA uses is open (see [open question 15](../v0.1/open-questions.md#15-two-party-component-for-dcgka)).
- The concrete primitives and the group size limit are open (see [open question 9](../v0.1/open-questions.md#9-group-protocol-primitives-and-group-size-limits)).
- The public key infrastructure that the paper assumes, by which members get correct public keys for each other, is provided by identity, verification and first contact: open questions [2](../v0.1/open-questions.md#2-identity-format), [4](../v0.1/open-questions.md#4-key-verification-method), and [13](../v0.1/open-questions.md#13-first-contact-without-a-directory).

## Consequences

- DCGKA is not an IETF standard. Its references are a peer-reviewed paper and a research prototype in Java (`trvedata/key-agreement`). It has fewer independent implementations and reviews than MLS.
- No published test vectors exist for DCGKA. The rule in [test-vectors](../../test-vectors/README.md), that vectors are derived from the referenced documents and not copied from an implementation, needs a method for this case. That method is an open detail of open question 9.
- Membership changes and key updates cost O(n) in the number of members, against O(log n) for MLS. The paper reports, for a group of 128 members, 70 ms of CPU time per client and 40 kB of network traffic for one key update. It calls the protocol impractical for groups of tens of thousands of members (section 2.1).
- A member keeps some state for each key update until every member acknowledges it. If a member never acknowledges, the state grows without bound (section 2.1). Under online-only delivery, members that are rarely online make this more likely.
- Members may change membership concurrently. Members reach the same membership from the causal order, not from a total order (section 5.2).
- A removed member can keep sending to members who have not yet processed the removal. The paper states that such messages cannot violate confidentiality (section 2.1).
- The paper assumes that members follow the protocol. A member can send malformed messages that make others disagree on keys, which denies service. A member cannot prevent their own removal, or the removal of members they added (sections 2.1 and 7). This matters for moderation.
- On every key update, a member generates a new identity key pair and broadcasts it, signed by the old one (section 5.1). The key that signs a member's group messages therefore changes often. Identity format and key verification must account for this.
- DCGKA does not hide group metadata from members, such as who added whom. The paper leaves metadata privacy for future work (section 2.1).
- Every member must eventually receive every causally prior message. Under online-only delivery, retransmission can come only from the sender or from other members (see [open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery)).
- Clients must store group state, and it must survive app restarts. Whether it survives the loss of a device depends on [message history sync](../v0.1/open-questions.md#5-message-history-sync).

## Alternatives considered

- **MLS, RFC 9420 (decision 0003).** Superseded. MLS relies on a Delivery Service to order commits, and decision 0005 removes it. Decentralized variants of MLS exist only as drafts.
- **Pairwise Double Ratchet sessions for every member.** Not chosen. Each message is encrypted once per member device, and membership changes need separate logic.
- **Sender Keys, and TreeKEM variants that need only causal order.** Not chosen. The paper's comparison (Table 1) reports weaker forward secrecy or post-compromise security for them under concurrent updates.
- **A custom group scheme.** Rejected. The project does not invent cryptography.
