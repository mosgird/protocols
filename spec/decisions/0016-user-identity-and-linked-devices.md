# 0016. User identity and linked devices: a user key on the primary device

**Status:** Proposed

## Context

Every key in the protocol so far belongs to a device. Each device holds an identity KEM key ([decision 0012](0012-mosgird-session-protocol.md)) and two signature keys ([decision 0011](0011-cryptographic-suite-and-security-level.md)), and an invite names one device ([decision 0014](0014-first-contact-by-invite.md)). What a *user* is, and how one user's devices belong together, was left to [open question 2](../v0.1/open-questions.md#2-identity-format) and [open question 3](../v0.1/open-questions.md#3-multi-device-key-handling).

Two facts constrain the answer:

- In groups, every key update gives a member a new signature key, signed by the old one ([decision 0006](0006-dcgka-for-groups.md)). A user identifier cannot be a hash of a key that changes this often.
- There is no server ([decision 0005](0005-serverless-online-only-delivery.md)), so nothing can hold a recovery copy of a key or publish device lists.

The team wants a person who uses Mosgird on a phone and a desktop to appear to contacts as one contact, with messages reaching both devices. The team chose:

- a user key that lives on one device, the *primary device*, and signs the list of the user's devices (option A of question 2, applied to a user key, and options A and C of question 3);
- no recovery key: a device that is lost or stolen is treated as compromised;
- per-device trust held by each contact: a contact's new device receives nothing until the user approves it, and any device or user can be distrusted.

The design follows published, deployed designs, not a new construction:

- **WhatsApp multi-device** (WhatsApp Encryption Overview, technical whitepaper; "How WhatsApp enables multi-device capability", Meta Engineering, 2021-07-14). Each device has its own identity key. A primary device signs a companion device's key (the "Account Signature"), the companion signs the primary's key (the "Device Signature"), and the primary signs the device list. Senders encrypt once per device ("client fan-out").
- **OMEMO** (XEP-0384, version 0.9.1, section 8). "Clients MUST NOT use a newly built session (or any other session) to transmit data without ensuring trust first", because otherwise "an attacker could publish a fake device for this user, which would then receive copies of all messages".
- **Automatic Trust Management** (XEP-0450) defines manual distrust of a single device's key.

## Decision

1. **User key.** When a user creates an identity, the first device generates a *user key*: a hybrid signature key pair, Ed25519 and ML-DSA-87 ([decision 0011](0011-cryptographic-suite-and-security-level.md)). The private part never leaves that device, except in a handover (point 7). That device is the user's *primary device*.
2. **User identifier.** A user is identified by a 256-bit fingerprint of the user key's two public parts: keyed BLAKE2b, as for the fingerprint in decision 0014, with its own key for domain separation. The identifier does not change when devices are added, removed, or update their group keys. Display names are labels chosen by each user. They are never identifiers and are not unique.
3. **Device keys stay per device.** Each device keeps its own identity KEM key and signature keys, as decisions 0012 and 0014 define. No private key is shared between devices, apart from the user key during a handover.
4. **Device list.** The primary device signs a *device list* with the user key. It holds:
   - the user identifier and a version number that increases with every change;
   - for each device: its identity KEM public key, its two signature public keys, its onion address and I2P destination hash ([decision 0009](0009-tor-and-i2p-with-local-links.md)), as in an invite;
   - for each device, a *device signature*: the device's own signature over the user identifier. It shows that the device agreed to belong to this user, so that no one can list another user's device as their own. It plays the role of WhatsApp's Device Signature, which a companion device makes over the primary device's key.

   A device accepts a list only if the user key's signature and every device signature verify, and its version is higher than the version it holds for that user. A lower or equal version is ignored.
5. **Linking a new device.**
   - The new device generates its own keys. The primary device shows a QR code in the format of a decision 0014 invite, and the new device scans it. The two devices run decision 0014's handshake. In place of a contact request, the new device sends a *link request* that carries its device signature.
   - The user confirms the link on the primary device. The primary device signs a new device list that includes the new device, and sends the new device the list, the user's contacts, their device lists, and the trust state of each of their devices. Message history is not sent ([open question 5](../v0.1/open-questions.md#5-message-history-sync)).
   - The user's other devices accept the new list without asking, because it is signed by their own user key.
6. **Removing a device.** The primary device signs a list without the device. Contacts apply a removal without asking. The removed device can no longer be reached as part of this user, but it is not erased. A stolen device must be treated as compromised.
7. **Handover of the primary role.** While the primary device still works, the user can move the user key to another of their devices over a session between the two. The receiving device becomes the primary device, and the old one deletes its copy. The user identifier does not change.
8. **No recovery.** If the primary device is lost, stolen, or broken, the user key is gone. The user's other devices keep working with the last list, but no device can be added or removed. To change devices, the user creates a new identity, and contacts accept a new invite.
9. **Exchanging device lists.**
   - After a contact request is accepted (decision 0014, step 5), the two devices send each other their device lists over the session that already exists. The list must contain the device the handshake ran with, and with the same identity KEM key. If it does not, the contact is not stored. From then on, the contact is recorded under the user identifier.
   - Later, devices send their current list whenever the other side holds an older version. A list can come from any device of the user. Its signature, not the sender, makes it valid.
   - The handshake of decision 0014 is not changed.
10. **Trust in a contact's devices.** Each device keeps a trust state for every device of every contact:
    - **Approved.** It receives messages. The device a contact was accepted through is approved when the contact is accepted.
    - **Held.** Every other device of a contact, including the other devices in the first list, starts here. A held device receives nothing. Messages for it wait on the sending device ([open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery)). Messages from it are not shown. The user sees the device and its fingerprint, and approves or distrusts it.
    - **Distrusted.** It receives nothing, and what it sends is dropped. Distrust is bound to the device's keys, not to a list version: a later list that includes the device again does not bring it back.

    A user can also **distrust a user key**. That blocks every device of that identity, present and future. If the person starts a new identity, they come back only through a new invite.

    Trust states are local. They are never sent to the contact or to anyone else.
11. **Fan-out.** A direct message is encrypted separately, in its own session, for each approved device of the recipient, and for each of the sender's own other devices, so that all of a user's devices show the conversation. This is WhatsApp's client fan-out.
12. **Groups.** Every device is a DCGKA member, as before (decision 0006). To add a user to a group, a member adds that user's devices that the member has approved. When a user's device list adds or removes a device, the user's own devices add or remove it in each group they share.

This closes [open question 2](../v0.1/open-questions.md#2-identity-format) and [open question 3](../v0.1/open-questions.md#3-multi-device-key-handling), except for the open details listed there.

## Consequences

- **One contact per person.** Contacts see one identity for all of a user's devices. A phone and a desktop both receive messages, so a desktop that is online more often can help with delivery ([open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery), option B, and [open question 17](../v0.1/open-questions.md#17-mobile-reachability-without-push-services), option D).
- **A stolen non-primary device cannot add devices.** It holds no user key. Once the primary device removes it, contacts stop sending to it.
- **A stolen primary device is the weak point.** Its holder can sign lists that add their own devices, and the real user cannot revoke them. Holding new devices until approval means contacts do not send to an added device without their own decision. A contact who learns of the theft can distrust the user key.
- **Approval costs effort.** Every contact approves every new device of a user, and messages for that device wait until they do. After linking a device, a user should tell contacts to expect it. Safety codes ([open question 4](../v0.1/open-questions.md#4-key-verification-method)) help a contact decide.
- **Losing the primary loses the identity.** This matches [decision 0015](0015-protection-of-stored-data.md), which has no backups.
- **Device lists are signed, so they are not deniable.** A contact can show a third party that the listed devices belong to the holder of one user key. Messages stay deniable (decision 0012). Group control messages were already signed (decision 0006).
- **More for contacts to observe.** A contact learns how many devices a user has, every device's addresses and public keys, that they belong to one person, and when devices are linked or removed. Group members learn the same for the devices in their groups. This is added to [the list of what other parties can observe](../v0.1/metadata.md).
- **Groups: approval and distrust are partial.** DCGKA gives every member device the keys it needs to read the group's messages. Whether one member can also compute the keys another member sends with is **[open]** ([decision 0018](0018-deniable-signatures-for-group-messages.md)). A device that one member has not approved, or has distrusted, still receives group messages if other members added it. That member's client can only decline to process its messages, warn its user, and refuse to add it. Removing a device for everyone is a group-wide action, governed by the permission rules that are still open ([open question 16](../v0.1/open-questions.md#16-community-moderation-without-an-operator)).
- **Size.** One list entry is about 8.6 KB: an X-Wing key of 1,216 bytes, signature keys of 32 and 2,592 bytes, two 32-byte addresses, and a device signature of about 4.7 KB (64 bytes of Ed25519 and 4,627 of ML-DSA-87). The list's own signature adds about 4.7 KB. Lists travel over the transport, never in invites.
- **Depends on the hybrid signature.** The user key, the list signature, and the device signatures need the published binding of Ed25519 and ML-DSA-87 that [open question 18](../v0.1/open-questions.md#18-post-quantum-deniable-authentication) leaves open. This decision cannot be implemented before that is settled.
- **Formal model.** [Decision 0013](0013-formal-verification.md) requires a model. The current models cover the handshakes and the contact request, not linking or device lists. A model of linking, device-list exchange, and the check in point 9 is needed before this decision leaves Proposed.

## Alternatives considered

- **One device per identity** (as Briar does). Not chosen. A phone and a desktop would be two contacts, and the delivery options that rely on a user's other device would not exist.
- **The user key on every linked device** (close to Matrix cross-signing with its keys shared to every device). Not chosen. Any device could manage the device list, so the compromise of any one device could add an attacker's device.
- **Devices that sign each other in a chain, with no user key.** Not chosen. The identifier would stay tied to the first device after it is gone. Concurrent changes from two devices would need merge rules that no published design here provides.
- **One identity key copied to every device** (question 3, option B). Not chosen. No published design does this, and one compromised device exposes the whole identity.
- **A recovery key written down by the user.** Not chosen. The team treats a lost or stolen device as compromised, and a written key would be a second secret that can be stolen.
- **Trusting a contact's new device at once, with a notice** (OMEMO's "blind trust before verification"). Not chosen. A stolen primary device's added device would receive messages until someone noticed. XEP-0384 forbids sending to a device before trust is established.
- **Approval only for contacts the user has verified.** Not chosen for now. It adds states to explain, and unverified contacts would get no protection.
- **Human-readable names bound by signature** (question 2, option C). Not chosen as identifiers. Without a registry, names are not unique. Display names remain labels.
