# 0008. No push services

**Status:** Proposed

## Context

Mobile operating systems limit what an app can do in the background. Most messaging apps work around this with a push service: a server sends a short message to the operating system's push channel, which wakes the app. Examples are Firebase Cloud Messaging (FCM) on Android, the Apple Push Notification service (APNs) on iOS, and UnifiedPush, which lets the user choose who runs the push server.

A push service is a server in the delivery path, and it learns information that is missing from [the list of what other parties can observe](../v0.1/metadata.md). At a minimum, it learns which device has the app installed (through a device token), and when a message arrives for that device. With FCM or APNs, that information goes to Google or Apple. Sending an empty push that carries no message content still reveals the device and the timing.

[Decision 0005](0005-serverless-online-only-delivery.md) already excludes servers. The team decided that the protocol must not use a push service when it compromises the end user's privacy, and asked for this to be stated on its own.

## Decision

- Clients do not use push services, including FCM, APNs, and UnifiedPush servers, whether self-hosted or not. This holds even when the push message carries no content.
- A client may use a way to wake itself or stay reachable only if both of these hold:
  - it reveals nothing beyond what `metadata.md` lists;
  - no server takes part in it.
- How a mobile device stays reachable under these limits is open (see [open question 17](../v0.1/open-questions.md#17-mobile-reachability-without-push-services)).
- A future mechanism that wakes a device without revealing more than `metadata.md` lists needs its own decision record. That record must show that the mechanism meets the requirement above.

## Consequences

- Mobile devices will often be unreachable while the app is not in use. Under online-only delivery (decision 0005), this means more messages wait on the sender's device, or are never delivered.
- On iOS, apps generally cannot run in the background or keep a connection open without APNs. An iOS client may only be reachable while it is in the foreground. This must be checked against Apple's current documentation before an iOS client is planned.
- On Android, an app can stay reachable by running a foreground service, which shows a persistent notification and costs battery. The platform restricts foreground service types and their durations by version. This must be checked against current Android documentation (question 17).
- No Google or Apple account and no Google Play services are needed for delivery.
- Users see no prompt to allow notifications from a push service, because none is used. Local notifications that the app shows itself, after it receives a message over the transport, are not affected.

## Alternatives considered

- **FCM or APNs with empty, content-free pushes.** Rejected. Google or Apple still learns the device and the arrival times, and someone must run a server that sends the pushes.
- **UnifiedPush with a server the user runs.** Rejected. It is still a server, which decision 0005 excludes. Whoever runs it learns arrival times. Most users would rely on a public server that someone else runs.
- **Push only as an option the user turns on.** Rejected. Every user who turns it on exposes their own arrival times. It also exposes the times at which their contacts send to them, and those contacts did not choose this.
