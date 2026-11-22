# Terminology (v0.1)

**Status:** draft.

- **User.** A person's identity in the system. A user is identified by the *user identifier*, a 256-bit fingerprint of the user key ([decision 0016](../decisions/0016-user-identity-and-linked-devices.md)).
- **User key.** A user's long-term hybrid signature key pair, Ed25519 and ML-DSA-87. It lives only on the primary device and signs the device list.
- **Primary device.** The device that holds the user key: the first device, unless the role was handed over to another of the user's devices.
- **Device list.** The list of a user's devices, with their public keys and addresses, signed by the user key and carrying a version number.
- **Device.** One installation of a client, holding its own key material. A device belongs to exactly one user. A user may have several devices. A contact's device is *approved*, *held*, or *distrusted* on each of the user's own devices (decision 0016).
- **Address.** What the transport needs to reach a device. It is derived from key material, never from a domain name. Over the internet, a device has two addresses: a Tor onion address and an I2P destination ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)). Addresses belong to devices, not to users, and are listed in the device list.
- **Identity KEM key.** A device's long-term X-Wing key pair. Other devices encapsulate secrets to it during a handshake, which authenticates the device without a signature ([decision 0012](../decisions/0012-mosgird-session-protocol.md)).
- **Invite.** A one-time link or QR code that lets one device send a contact request to another. It carries the inviting device's addresses, a fingerprint of its identity keys, and a secret ([decision 0014](../decisions/0014-first-contact-by-invite.md)).
- **Handshake.** The interactive exchange that starts every connection between two devices. It follows the Post-Quantum Noise framework.
- **Session.** The cryptographic state that two devices share for the length of one connection: the handshake result and the ratchet that follows it (decision 0012). It is deleted when the connection closes. In group contexts, membership is tracked by DCGKA group state, not by pairwise sessions (see [decision 0006](../decisions/0006-dcgka-for-groups.md)).
- **Group.** A set of member devices that share DCGKA state. Each member keeps a ratchet for every member, and message keys come from the sender's ratchet.
- **Causal order.** The order in which one message depends on another: a message sent after its sender processed another message comes after it. A member processes a group message only after all messages that come before it in causal order.
- **Community.** A named set of channels, with members and roles ([decision 0007](../decisions/0007-communities.md)). It is not a machine. The brief called this a "server"; the specification does not.
- **Role.** A set of permissions that a community grants to some members. The roles and permissions model is **[open]** ([open question 16](open-questions.md#16-community-moderation-without-an-operator)).
- **Moderation action.** An action that a member with a moderating role takes against another member, such as removal. Every member's client checks and applies it.
- **Channel.** A named conversation inside a community. Each channel is one group. Membership follows the community's roles and permissions.
- **Direct message.** A conversation between two users, encrypted with pairwise sessions.
- **Group chat.** A conversation with more than two participants that is not part of a community. It is one group.
- **Event.** A unit that one device sends to another. An event consists of an encrypted payload and the metadata the transport needs to deliver it. Event types (messages, membership changes, key updates, acknowledgments) are **[open]** in their full list.
