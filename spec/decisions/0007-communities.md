# 0007. Communities replace "servers" in the product sense

**Status:** Proposed

## Context

The initial brief grouped channels into units it called "servers". After [decision 0005](0005-serverless-online-only-delivery.md) the protocol has no servers, so the same word named two different things, and the overview did not define the product meaning. The team decided to keep the concept, to rename it "community", and that communities need a moderation system to act against members who act in bad faith.

## Decision

- A **community** is a named set of channels, with members and roles. It is not a machine, and no server hosts it.
- The specification does not use "server" for a community. "Server" means only what decision 0005 excludes.
- Each channel in a community is one DCGKA group ([decision 0006](0006-dcgka-for-groups.md)).
- Communities have moderation: members who hold a moderating role can act against members who act in bad faith, at least by removing them from the community's channels. There is no operator, so moderation actions are protocol operations that every member's client checks and applies. The mechanism is open (see [open question 16](../v0.1/open-questions.md#16-community-moderation-without-an-operator)).
- Roles and permissions are part of the community state that members hold. How they are represented and checked is open (open questions [7](../v0.1/open-questions.md#7-community-and-channel-structure-visibility) and 16).

## Consequences

- Removal is enforced by the group protocol. A removed member loses access to later messages in each channel, and the paper states that a member cannot prevent their own removal (decision 0006). Other moderation actions, such as muting, are enforced only by clients that follow the protocol. A modified client can ignore them for its own user.
- Removing a member from a community means removing them from each channel's group. Each removal costs O(n) in the size of that group.
- Without a server, members must agree on who may remove whom. Two moderators can act at the same time, for example each removing the other. The result must be the same for every member, using only the causal order. This is open in question 16.
- Without a registry, new identities cost nothing to create. A ban on one identity does not stop its owner from returning under another. Admission control, such as invitations, matters more (questions 6 and 16).
- Community size is limited by DCGKA's linear cost (open question 9).
- Moderation can conflict with privacy. For example, moderators may need evidence that only disclosed plaintext provides (question 6, option A). Such conflicts are recorded as open questions, not resolved by weakening privacy.

## Alternatives considered

- **Drop communities and keep only direct messages and group chats.** Not chosen by the team.
- **Keep the name "server".** Rejected. After decision 0005 it is ambiguous.
- **Moderation by a trusted operator.** Not possible after decision 0005: there is no operator.
