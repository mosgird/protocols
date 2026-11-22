# What other parties can observe (v0.1)

**Status:** draft.

There is no server. What others can observe depends on who they are and on the transport ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)).

**A contact's device, while exchanging messages directly, can observe:**

- The other device's onion address and I2P destination, and that both belong to the same device. Over Tor and I2P, it does not learn the other device's network address. Over a local link, it learns the local link address.
- When the other device is online and reachable.
- The size and timing of each message, and how often the sender retries.
- The one-time prekeys the other device gives it for two-party messages in groups ([decision 0019](../decisions/0019-two-party-component-for-dcgka.md)), and when it uses up the ones it gave.
- The other device's identity KEM key, and the ephemeral keys and encapsulations of each handshake ([decision 0012](../decisions/0012-mosgird-session-protocol.md)). These are what the contact needs to derive the session keys. Nothing in them is signed, so they prove nothing to a third party.
- When each connection starts, because every connection runs a new handshake.

**A contact, from the device lists it receives ([decision 0016](../decisions/0016-user-identity-and-linked-devices.md)), can observe:**

- The user key, and every device of the user: how many there are, their public keys and addresses, and that they belong to one person.
- When the user links or removes a device, from the list's version and content.
- That the list is signed by the user key and agreed to by each device. These signatures can be shown to a third party, so who owns which devices is not deniable. Messages stay deniable.
- Each device's signed prekey, and when the device replaces it, which shows roughly when the device was online ([decision 0019](../decisions/0019-two-party-component-for-dcgka.md)). The prekey is signed under the device's key, so it shows a third party that the device published it.
- Members of a group observe the same about the devices that are members of that group.

Which devices a user approves, holds, or distrusts is stored only on that user's devices and is never sent.

**At first contact ([decision 0014](../decisions/0014-first-contact-by-invite.md)):**

- Anyone who sees an invite link or QR code, including every service it passes through, learns the inviting device's addresses and key fingerprint. Until the invite is used or expires, they can use it to send a contact request in the invited user's place.
- The inviting device learns the requesting device's addresses and identity keys, and the text of the contact request, even if its user declines.
- A device that does not hold a valid invite gets no answer, so it does not learn the inviting device's identity key or whether that device is online.

**Members of a channel or group chat can observe:**

- The membership of the group, which member sent each message, who added or removed whom, and when each member updates their keys. DCGKA does not hide this from members ([decision 0006](../decisions/0006-dcgka-for-groups.md)).
- The size and timing of each message, and the onion addresses and I2P destinations of the members they talk to directly.
- When other members were online, and which group messages each member was missing, because members pass missing messages on to each other ([decision 0017](../decisions/0017-retry-expiry-and-relaying.md), [decision 0018](../decisions/0018-deniable-signatures-for-group-messages.md)). Each member stores the group's control and application messages until every member has acknowledged them or they expire.
- Which short-lived signing key each member device uses in each epoch, and from the key lists, which pairs of member devices have met in each epoch ([decision 0018](../decisions/0018-deniable-signatures-for-group-messages.md)). A member can show other members who wrote an application message. Whether it can show an outsider depends on the deniability of decision 0012's sessions, which is **[open]** ([open question 18](open-questions.md#18-post-quantum-deniable-authentication)).
- Community and channel structure: names, roles, membership, and moderation actions. Whether non-members can learn any of this is **[open]** ([open question 7](open-questions.md#7-community-and-channel-structure-visibility)).

**Network observers and transport relays can observe:**

- That a device uses Tor or I2P, when, and how much traffic it sends. A device's internet provider, and the first Tor relay it connects to, see its network address. Tor bridges can hide Tor use from the provider. When and how is open ([open question 12](open-questions.md#12-transport-and-addressing)).
- An I2P router's network address, which is listed in I2P's network database unless the router runs in hidden or firewalled mode.
- Timing and volume patterns. An observer who can watch large parts of the network may correlate the two ends of a conversation by timing. Neither Tor nor I2P is designed to prevent this ([open question 10](open-questions.md#10-metadata-minimization)).
- Lookups of an onion service descriptor or an I2P lease set, by the directory relays or routers that serve them. The details are set by each network.
- Near a device that uses local links: that it broadcasts or connects, and when. Discovery must not reveal stable identifiers to non-contacts. How is open.

**Someone holding a copy of a device's storage, without its key store or passphrase ([decision 0015](../decisions/0015-protection-of-stored-data.md)), can observe:**

- The number and size of stored records, and when they changed. The content is encrypted.
- That the device holds other members' group control and application messages, for up to the expiry time, and from the hashes it keeps, how many messages its groups had ([decision 0017](../decisions/0017-retry-expiry-and-relaying.md), [decision 0018](../decisions/0018-deniable-signatures-for-group-messages.md)).

**No one other than the intended participants can observe:**

- Plaintext message content.
- Private identity keys, session keys, or group secrets.
- Plaintext of attachments, if attachments are added in v0.1. Attachment handling is **[open]**.
