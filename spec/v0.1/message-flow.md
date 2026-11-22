# Message flow (v0.1)

**Status:** draft.

This document describes the flow in plain language. Exact message formats are not defined in v0.1.

## 1. Direct message

The session protocol is defined in [decision 0012](../decisions/0012-mosgird-session-protocol.md).

1. The sender's device holds the recipient device's address and identity KEM key. At first contact, it got them from an invite link or QR code and a contact request that the recipient accepted ([decision 0014](../decisions/0014-first-contact-by-invite.md)). The steps below run once for each approved device of the recipient, and once for each of the sender's own other devices ([decision 0016](../decisions/0016-user-identity-and-linked-devices.md)).
2. The sender's device keeps the message in its local storage until it can reach the recipient's device, for up to 30 days by default ([decision 0017](../decisions/0017-retry-expiry-and-relaying.md)). The message is not encrypted in advance under an earlier session. Only the sender's device delivers it.
3. When the devices can reach each other, they run a new handshake. Each side encapsulates secrets to the other's identity KEM key and to fresh ephemeral keys, and both derive the same session keys. Nothing is signed.
4. The sender's device encrypts each message with a new key from the ratchet and sends it. No other party stores it.
5. The recipient's device decrypts the message and deletes its key. It acknowledges the message's identifier so that the sender can delete the stored message (decision 0017). The wire encoding is not defined in v0.1.
6. When the connection closes, both devices delete the session.

## 2. Channel or group chat

The group protocol is DCGKA ([decision 0006](../decisions/0006-dcgka-for-groups.md)). The steps below summarize the paper. The paper is the reference.

1. Each member device holds DCGKA state for the group, including a ratchet for each member.
2. To add or remove a member, or to update its own keys, a member device sends a control message to all members by authenticated causal broadcast. Each control message is signed under the sender's identity key. Secrets meant for one member travel in a direct message encrypted with the two-party component of [decision 0019](../decisions/0019-two-party-component-for-dcgka.md), under keys that earlier messages carried or under a prekey of the recipient.
3. Each member device processes a message only after every message that causally precedes it. Members may change membership concurrently, and they reach the same membership from the causal order. No member or server decides a single order.
4. To send an application message, a device encrypts it with the next key from its own ratchet, signs it with its short-lived signing key for the current epoch, and delivers it directly to each member device it can reach. It hands that short-lived key to each other member device in a direct session ([decision 0018](../decisions/0018-deniable-signatures-for-group-messages.md)).
5. Each group message names the hashes of the messages of its own kind before it: control messages and application messages form two separate graphs, so that no long-term signature covers an application message. Members acknowledge messages, and any member that holds a message passes it on to a member that is missing it. A relayed message is accepted only with its sender's signature: under the identity key for a control message ([decision 0017](../decisions/0017-retry-expiry-and-relaying.md)), and under the short-lived key the sender handed over for an application message (decision 0018).
