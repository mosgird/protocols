# Overview (v0.1)

**Status:** draft.

This document describes the goals and non-goals of v0.1 of the protocol, and lists the documents that specify it. Items marked **[open]** are not decided. Each one is listed with options in [open-questions.md](open-questions.md). Proposed decisions are recorded in [../decisions/](../decisions/). None is accepted yet.

## 1. Goals

- **Security and privacy as the primary constraint.** Every component, feature, and deployment mode is designed under this requirement. None is exempt. Where another goal conflicts with security or privacy, the conflict is recorded as an open question. It is not resolved by weakening the requirement.
- **No servers and no domain names.** Devices deliver messages to each other directly. No server stores, forwards, or orders anything for the protocol, and nothing depends on DNS (see [decision 0005](../decisions/0005-serverless-online-only-delivery.md)). This includes push services such as FCM, APNs, and UnifiedPush ([decision 0008](../decisions/0008-no-push-services.md)).
- **Minimal metadata.** Reduce what parties other than the intended participants learn about who communicates, when, and from where. The current gaps are listed in [metadata.md](metadata.md) and tracked in [open question 10](open-questions.md#10-metadata-minimization).
- **Private messaging.** Message content is readable only by the intended participants and their devices.
- **Communities and channels.** A community contains channels, members and roles, and has moderation against bad-faith members ([decision 0007](../decisions/0007-communities.md)). A channel is a multi-party conversation whose membership can change over time, and its keys follow membership changes.
- **Self-held identity.** A user's identity key material is generated and held by the user's devices. No one issues identities. A substituted key is detected only if contacts verify keys ([open question 4](open-questions.md#4-key-verification-method)). The identifier format is **[open]**.
- **Readable specification.** Each mechanism is described well enough that an independent implementer can build an interoperable client.

## 2. Non-goals (v0.1)

- **Voice and video.** Not specified in v0.1.
- **Monetization.** Not addressed by the protocol.
- **Content policy.** The protocol does not define which content is permitted. Mechanisms for handling reports are an open question (see [open question 6](open-questions.md#6-abuse-handling-for-an-encrypted-service)). Policy itself is out of scope.
- **Delivery to offline devices.** A message is delivered only while both devices are reachable at the same time. No third party stores messages for an offline device (see [decision 0005](../decisions/0005-serverless-online-only-delivery.md)). The sender keeps them. Group members pass on group messages they already hold: control messages ([decision 0017](../decisions/0017-retry-expiry-and-relaying.md)) and application messages ([decision 0018](../decisions/0018-deniable-signatures-for-group-messages.md)). No push service wakes an offline device ([decision 0008](../decisions/0008-no-push-services.md)). How phones stay reachable is **[open]** ([open question 17](open-questions.md#17-mobile-reachability-without-push-services)).

## 3. Documents

- [architecture.md](architecture.md): the components and the trust model.
- [metadata.md](metadata.md): what parties other than the intended participants can observe.
- [terminology.md](terminology.md): the terms used throughout the specification.
- [message-flow.md](message-flow.md): how a direct message and a group message travel.
- [references.md](references.md): the published designs and specifications the protocol builds on.
- [open-questions.md](open-questions.md): what is not yet decided.
- [models/](models/README.md): the formal models.
- [../decisions/](../decisions/): the decision records.
