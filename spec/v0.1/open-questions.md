# Open questions (v0.1)

Each question lists options and what each option costs. A question is closed when a decision record is added under [../decisions/](../decisions/) and this file is updated to point to it.

Options that needed a server no longer apply after [decision 0005](../decisions/0005-serverless-online-only-delivery.md). They are kept and marked "Not applicable after decision 0005", so the reasoning stays visible.

---

## 1. Federation

**Status:** closed by [decision 0005](../decisions/0005-serverless-online-only-delivery.md). There are no servers, so there is nothing to federate. The concern behind option C still applies: identifiers must not embed an operator or domain name, and decision 0005 forbids domain names.

**Question:** Do independent servers interoperate with each other, or does each deployment stand alone?

**Options:**

- **A. No federation.** One official instance. Users on one server cannot reach users on another.
  - Cost: simplest trust model and key directory. Users cannot choose their operator. Growth depends on a single deployment.
- **B. Federation with server-to-server protocol.** Servers relay events to one another and each server holds its own users.
  - Cost: a second protocol to specify and secure. Key directory consistency must cross operators. Metadata is shared with more parties. Abuse handling must work across operators.
- **C. Defer, but keep identifiers operator-neutral.** Do not specify federation in v0.1. Avoid designs that make a later federation protocol impossible, such as identifiers that embed the server name.
  - Cost: some constraints on identifier design now. Federation is still unspecified.

---

## 2. Identity format

**Status:** closed by [decision 0016](../decisions/0016-user-identity-and-linked-devices.md) with option A, applied to a user key: a user is identified by a fingerprint of a user key that lives on the primary device and signs the user's device list. The open detail below is partly resolved there; what remains is listed at its end.

**Question:** How is a user identified, and how is the link between a user and their key material established?

**Options:**

- **A. Identifier derived from the identity public key.** For example, a hash of the public key, displayed in encoded form.
  - Cost: no human-chosen names. Identity is not recoverable if the key is lost, unless a recovery mechanism exists. Display names must be separate and cannot be trusted by themselves.
- **B. Server-assigned username, with the public key bound on the server.** Not applicable after decision 0005: there is no server to assign names.
  - Cost: the server controls the username namespace and the binding. Users depend on the server for identity. Lower key-verification value unless clients check the binding over time.
- **C. Human-readable username, with a self-signed binding to the identity key.** The binding is signed by the user's key and shown to contacts. Clients check it.
  - Cost: more complex to specify. Without a server or registry, names are not unique: two users can choose the same name, so a name alone never identifies a user. Clients must store and check history to detect silent changes.

**Open detail:**

- Whether the identifier is stable across devices. Resolved by decision 0016: it is, because it comes from the user key, not from a device.
- How a user's identity is recovered after losing all devices. Resolved by decision 0016: it is not. Losing the primary device loses the identity.
- How the identifier relates to the transport address (see question 12). Resolved by decision 0016: it does not. Addresses belong to devices and are listed in the signed device list.
- Whether a user's remaining devices can warn contacts that the primary device was lost or stolen. Such a warning cannot be signed by the user key, which the thief may hold.

---

## 3. Multi-device key handling

**Status:** closed by [decision 0016](../decisions/0016-user-identity-and-linked-devices.md) with options A and C: each device keeps its own keys, messages are encrypted once per device, and a new device is linked through the primary device, which signs the device list. Contacts hold every new device until their user approves it. The open detail below is partly resolved there; what remains is listed at its end.

**Question:** How does a user with several devices hold keys, and how do messages reach all of them?

**Options:**

- **A. One identity per device, with fan-out.** Each device has its own identity key. A sender encrypts once per recipient device.
  - Cost: more pairwise sessions and more fan-out traffic as devices grow. Users must verify each device, or the verification model must treat the user as the set of devices. Adding a device requires the other side to learn about it.
- **B. Shared identity key copied to every device.** All devices hold the same identity private key.
  - Cost: compromise of any device exposes the identity. Revoking one device means rotating the identity for all. Simpler session model.
- **C. Device linking through an existing device.** A new device is added by an approval from an already-trusted device. Each device still has its own keys; the link creates a signed statement that the device belongs to the user.
  - Cost: needs a linking flow (for example, a QR code or a short code) and clear rules for revocation. Adds to the verification surface.

**Open detail:**

- How device lists are signed, distributed and checked without a server. Resolved by decision 0016: the user key signs them, any of the user's devices passes them on, and a list is accepted only with valid signatures and a higher version.
- Whether one device can hide another device of the same user from a contact. Resolved by decision 0016: a device cannot change a signed list, and only the primary device can leave a device out of a new one. A device can pass on an older list, which is replaced as soon as any device passes on a newer one.
- Under online-only delivery, each recipient device must be reachable separately, so a message can reach one of a user's devices and not another. Whether a user's devices pass messages to each other is [question 14](#14-retry-expiry-and-relaying-under-online-only-delivery), option B. Not chosen for direct messages by [decision 0017](../decisions/0017-retry-expiry-and-relaying.md); it stays an open detail of question 14.
- The highest number of devices per user, and the exact format of the device list and the link request.
- How a client shows a held device to its user, so that approving it is an informed choice ([question 4](#4-key-verification-method)).

---

## 4. Key verification method

**Question:** How do two users confirm that they are talking to each other and not to someone who substituted keys?

**Options:**

- **A. Safety numbers.** Both users compare a short fingerprint of their combined keys, in text form, out of band.
  - Cost: manual comparison. Users often skip it. Works without a camera. A changed key shows as a changed number.
- **B. QR codes.** One device scans a code shown by the other.
  - Cost: needs both devices in the same place, or a camera. Good for in-person use. Same weakness as A when skipped.
- **C. Both A and B.** Offer either method. Users who compare in person use QR codes; others use safety numbers.
  - Cost: two code paths to implement and test. The UI must make the verified/unverified state clear.
- **D. Key transparency log.** A server publishes an append-only log of key changes, and clients check inclusion and consistency. Not applicable after decision 0005: there is no server to run the log.
  - Cost: significant design and operations work. Requires an auditor or gossip mechanism to be meaningful. Does not replace user-level verification by itself.

**Open detail:** what the client shows after a key change, and whether a change in a contact's key blocks sending until the user acknowledges it. For a new device of a contact, [decision 0016](../decisions/0016-user-identity-and-linked-devices.md) answers the second part: nothing is sent to it until the user approves it. Whether a safety code covers the user key alone or the whole device list, as WhatsApp's does, is open. Without a directory, first contact often happens through a key the contact hands over directly (question 13), so verification at first contact matters more.

---

## 5. Message history sync

**Question:** When a user adds a new device, does it receive earlier messages?

**Options:**

- **A. No history.** A new device sees only messages sent after it joined.
  - Cost: simplest. Users lose context on a new device. Forward secrecy holds.
- **B. Device-to-device transfer.** An existing device sends history to a new device over an encrypted channel.
  - Cost: needs an online existing device. Requires a secure transfer protocol and a design for large histories.
- **C. Encrypted server-side backup.** The client uploads encrypted history. The decryption key is derived from a recovery key or passphrase the user keeps. Not applicable after decision 0005 as a protocol feature: there is no server. A user may still copy an encrypted backup to storage they choose, outside the protocol.
  - Cost: the storage holds large ciphertext blobs and their sizes. Losing the recovery key loses the history. A weak passphrase weakens the backup. Backup timing reveals activity patterns.

**Open detail:** whether history sync applies to channels as well as direct messages, and what happens to messages that were deleted on one device.

---

## 6. Abuse handling for an encrypted service

**Question:** How do users and communities respond to abusive content or behavior when there is no server and no operator who can read messages?

Content policy itself is out of scope for the protocol. This question covers only the mechanisms available when no server exists.

**Options:**

- **A. User-initiated reports with disclosed content.** A reporting user chooses to send the plaintext of a message, with a proof that it came from the reported sender, to someone who can act on it, such as a channel moderator.
  - Cost: relies on the reporter's honesty. Disclosure is limited to what the reporter sends. Proof of origin needs a signature scheme. Without a server there is no operator to receive reports, so who receives them must be defined.
- **B. Metadata-based controls.** Rate limits, account age limits, and limits on sending to unknown users. Not applicable after decision 0005 as server-enforced controls. Receiving clients can apply limits to what they accept.
  - Cost: no content signal. Can affect legitimate users. Client-applied limits protect only the client that applies them.
- **C. Client-side classification before encryption.** The client checks content on the device before sending.
  - Cost: changes the trust model, because the client reports on its user. Requires a classifier on the device. It conflicts with the goal of private messaging. Listed for completeness; not a recommended option in v0.1.
- **D. Blocking and muting.** Users block contacts. Blocks are enforced by clients. Server enforcement is not applicable after decision 0005.
  - Cost: limited protection against a determined sender who creates new identities. Needs identity cost to be non-trivial (see [question 2](#2-identity-format)). A blocked sender can still try to connect, so blocks must be enforced before any work is spent on the sender's traffic.

**Open detail:** how reports interact with channels, and whether anyone keeps a record of reports. Moderation inside communities is covered by [question 16](#16-community-moderation-without-an-operator).

---

## 7. Community and channel structure visibility

Before [decision 0007](../decisions/0007-communities.md), this question used "server" for a community.

**Question:** Who can learn community names, channel names, roles and membership?

**Options:**

- **A. Visible to a server.** A server stores structure in plaintext. Not applicable after decision 0005: there is no server.
  - Cost: the server learns the community structure and membership.
- **B. Encrypted to members.** Structure is an encrypted state object in each channel's group, held only by members.
  - Cost: permission checks are done by clients, with a signed-capability model. Search and invitation flows need a design that does not rely on a server.

**Open detail:** what a non-member learns from an invitation, and whether the transport reveals that a set of devices forms a group.

---

## 8. Attachments and file transfer

**Question:** How are files delivered?

**Options:**

- **A. Encrypted blobs on the relay server.** The client encrypts the file, uploads it, and sends a key and a reference in the message. Not applicable after decision 0005: there is no relay server.
  - Cost: the server stores file ciphertext and sees file sizes. Storage and retention rules are needed.
- **B. Peer-to-peer transfer.** Devices exchange the encrypted file directly over the transport, after a message reference is delivered.
  - Cost: both devices must be online at the same time, as for messages. Large files take longer to deliver over Tor and I2P ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)), which do not expose network addresses to the other party.

**Open detail:** a size limit, and whether a group member who already has a file may pass it to another member.

---

## 9. Group protocol primitives and group size limits

Until [decision 0006](../decisions/0006-dcgka-for-groups.md), this question asked which MLS ciphersuite to use. DCGKA replaces MLS, so the question now covers DCGKA's primitives. The ordering problem that decision 0005 raised for MLS is handled by DCGKA's causal broadcast.

**Question:** Which concrete primitives instantiate DCGKA, and what group sizes must be supported?

DCGKA needs a signature scheme for authenticated causal broadcast, a key derivation function (the paper uses HKDF), an authenticated encryption scheme for application messages, and the primitives of the two-party component ([question 15](#15-two-party-component-for-dcgka)).

**Options:**

- **A. One fixed set of primitives.** One choice, with a version field in the protocol.
  - Cost: no algorithm agility without a new version. Simpler to test.
- **B. Negotiated sets.** Clients advertise what they support.
  - Cost: downgrade risk must be addressed. A larger test matrix.

**Open detail:**

- The maximum channel size for v0.1. The paper reports 70 ms of CPU and 40 kB of traffic per key update at 128 members, with cost growing linearly. Measurements on target devices are not yet done.
- Whether every primitive is available in libsodium, or in libcrux, as [decision 0011](../decisions/0011-cryptographic-suite-and-security-level.md) requires.
- How test vectors are produced. No published vectors exist for DCGKA, and the test-vector rule forbids copying them from an implementation.
- How the team's choice of a post-quantum key exchange applies to groups.

---

## 10. Metadata minimization

**Question:** Which metadata visible to parties other than the intended participants can be reduced in v0.1, and how?

The overview lists what contacts, group members, network observers, and transport relays can observe (see [overview section 3.3](overview.md#33-what-other-parties-can-observe)). The project requires that this be minimized. The mechanisms below are not yet chosen and are not specified.

**Options (may be combined):**

- **A. Sealed sender.** The sender's identity is hidden from the server that delivers the message. Not applicable after decision 0005: there is no delivering server. The recipient always learns the sender in a direct exchange.
  - Cost: none now. Listed so the change is visible.
- **B. Padding and batching.** Messages are padded to fixed size classes, and sends are delayed or batched.
  - Cost: more bandwidth and latency. Timing padding has limited effect against an observer who sees all traffic. Batching delays delivery that is already limited to times when both devices are online.
- **C. Network address hiding.** Devices reach each other through a transport that hides network addresses from peers and from observers, such as onion routing, garlic routing, or a mixnet.
  - Cost: latency, battery use on phones, and dependence on relays run by others. Chosen in [decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md): Tor onion services and I2P. Neither resists an observer who sees the whole network; a mixnet would.
- **D. Accept current exposure, documented.** Leave the gaps in place and state them clearly to users.
  - Cost: does not meet the minimal-metadata goal. Listed so that the choice is explicit.

**Open detail:** which of these the v0.1 threat model requires, and how each interacts with abuse handling ([question 6](#6-abuse-handling-for-an-encrypted-service)).

---

## 11. Ambiguities in the initial brief

These points are not clear from the initial brief. They are recorded here instead of being assumed.

- **"Server-independent identity."** Resolved by [decision 0005](../decisions/0005-serverless-online-only-delivery.md): there are no servers, so identity cannot depend on one. The overview now calls this goal "self-held identity".
- **"Servers" in the product sense and groups.** Resolved by [decision 0006](../decisions/0006-dcgka-for-groups.md): each channel is its own group, so a community with several channels has several groups. [Decision 0007](../decisions/0007-communities.md) renames "servers" in this sense to "communities".
- **License.** The project uses Mulan PSL v2, as recorded in the repository's LICENSE.md file. Any future relicensing is not considered in v0.1.

---

## 12. Transport and addressing

**Status:** closed by [decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md):
- Over the internet, Tor onion services (option A) and I2P (option B), combined per option J.
- Local links (option I) as a fallback when the internet is unavailable.
- Every link is encrypted and authenticated.

The open detail below is still open.

**Question:** How does a device find and reach another device, without servers and without domain names?

Every option below carries ciphertext that is already end-to-end encrypted. The transport adds reachability, and in some cases protects network addresses and traffic patterns. It never replaces the end-to-end encryption. The descriptions summarize each project's own documentation and must be checked against it before a decision is written.

**Options (may be combined):**

- **A. Tor onion services.** Each device runs an onion service. Its address is derived from an Ed25519 public key. Briar and Cwtch use this approach.
  - Cost: hides network addresses from peers and from an observer of one link. Adds latency and battery use on phones. Depends on relays run by volunteers, and on Tor's directory authorities to join the network. Tor is blocked in some countries and then needs bridges.
- **B. I2P.** Each device has an I2P destination, an identifier made of public keys. Traffic uses garlic routing over one-way tunnels: a round trip uses four tunnels. Applications connect through the SAM v3 interface.
  - Cost: hides network addresses from peers. A smaller network than Tor. A device that runs a router also routes traffic for others, which costs bandwidth and battery. Joining needs reseed hosts, and destinations are looked up in a distributed database kept by "floodfill" routers.
- **C. Nym mixnet.** Messages are split into fixed-size Sphinx packets, sent through entry and exit gateways and three mix layers, with random delays and cover traffic, following the Loopix design.
  - Cost: designed to resist traffic analysis by an observer who sees the whole network, which onion routing does not attempt. Higher latency and constant cover traffic. Gateways and mix nodes are run by operators, and access needs bandwidth credentials. Gateways can hold packets for offline clients, which is store-and-forward and must stay disabled under decision 0005.
- **D. Veilid.** A peer-to-peer framework in which nodes are identified by 256-bit public keys and can route privately, so the two ends need not learn each other's network address. It also offers a distributed hash table.
  - Cost: a young project (first released in 2023) whose interfaces still change between releases. Its storage features would be store-and-forward and must not be used for messages under decision 0005.
- **E. Yggdrasil.** An encrypted IPv6 overlay mesh. Each node's IPv6 address is derived from a hash of its public key.
  - Cost: it gives addressing and routing, not anonymity: peers and the overlay see network addresses. Addresses are truncated hashes, and the project has an open issue about brute-forcing them. It runs as a network interface, which needs operating-system privileges. Described by the project as experimental.
- **F. Reticulum.** A networking stack in which destinations are truncated hashes of public keys. It runs over LoRa, packet radio, Wi-Fi, and IP, and can work without IP.
  - Cost: very low bandwidth over radio links. Some countries ban encryption on amateur radio bands. Its own cryptographic design has had less public review than Tor's or I2P's.
- **G. libp2p.** Peers are identified by IDs derived from public keys. A Kademlia distributed hash table and NAT traversal help peers find and reach each other.
  - Cost: does not hide network addresses. Lookups are visible to the peers that answer them. Joining the hash table needs bootstrap peers that someone runs.
- **H. WireGuard.** An encrypted tunnel between two peers that know each other's static public keys and network endpoints, built on the Noise protocol framework.
  - Cost: no discovery, no NAT traversal of its own, and no address hiding. It adds a tunnel under the end-to-end encryption without adding end-to-end properties. Useful only together with another way to find endpoints.
- **I. Local links.** Bluetooth, Wi-Fi Direct, and the local network. Briar uses them alongside Tor.
  - Cost: works without the internet. Short range. Reveals presence to nearby observers.
- **J. Several transports, chosen per contact.** For example, an anonymizing transport over the internet and local links nearby.
  - Cost: the most to specify and test. Which transport a device uses, and when it switches, can itself reveal information.

**Open detail:**

- Joining a network needs infrastructure that someone else runs, such as directory authorities, reseed hosts, or bootstrap peers. Resolved by decision 0009: for Tor and I2P, this infrastructure belongs to the transport and does not store Mosgird messages.
- How an address relates to the user identifier ([question 2](#2-identity-format)).
- How mobile background limits affect reachability. This is now [question 17](#17-mobile-reachability-without-push-services).
- Whether a device runs Tor and I2P at the same time, how it chooses one for each contact, and whether switching between them reveals anything.
- How a device reaches Tor or I2P where they are blocked, for example through Tor bridges and pluggable transports.
- Which authenticated key exchange local links use (for example a Noise Protocol Framework handshake), and how local discovery avoids stable identifiers.
- Whether local links are also used while the internet is available.

---

## 13. First contact without a directory

**Status:** closed by [decision 0014](../decisions/0014-first-contact-by-invite.md): a one-time invite link or QR code (options A and B), then a contact request that the recipient accepts (option E). The open detail below is still open.

**Question:** How does a device get another device's address and identity KEM key the first time, with no server to publish them?

Since [decision 0012](../decisions/0012-mosgird-session-protocol.md), there are no pre-key bundles. A device needs only the other device's address and identity KEM key, and starts an interactive handshake. Options below that mention a bundle now mean those two items.

**Options:**

- **A. In person.** Devices exchange addresses and bundles directly, by QR code or over a local link.
  - Cost: needs the users to meet. Gives key verification at the same time ([question 4](#4-key-verification-method)).
- **B. Address out of band, bundle over the transport.** A user shares their address as text or a link through any channel. The devices then exchange bundles directly the first time both are online.
  - Cost: works at a distance. The first key is trusted on first use unless the users verify it later. The channel used to share the address learns that the two users intend to talk.
- **C. Introduction by a mutual contact.** A contact who knows both users passes on one user's address and bundle to the other.
  - Cost: the introducer can substitute keys. Verification is needed to detect it.
- **D. Publication in a distributed hash table.** A device publishes its address and bundle under a key-derived name.
  - Cost: peers that store or answer the lookup learn who is looking for whom. Tor and I2P ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)) look up an address that is already known. Neither is a public table for finding users who have not shared an address.
- **E. Contact only with permission.** A device accepts nothing but a contact request from an unknown device. No messages are delivered until the recipient's user accepts the request. Alternatively, both users must each add the other, as Briar does for contacts added at a distance. The team suggested this. It combines with A to D.
  - Cost: stops unsolicited messages before any conversation starts. The request itself is still delivered, so requests can be used for spam or harassment. Rate limits or proof-of-work against this are open. A request reveals the requester's address and identity key to the recipient before the recipient accepts. Mutual adding avoids that, but both users must act.

**Open detail:**

- One-time pre-keys: resolved by decision 0012. Each connection runs an interactive handshake with fresh ephemeral keys, so no pre-keys exist.
- What a contact link or QR code carries. Resolved by decision 0014: addresses, a fingerprint of the identity keys, and a one-time invite secret.
- A public, reusable link for users who want to be reachable by people they have not invited. Decision 0014 does not support one. If one is added, requests from it need limits against spam, such as rate limits or proof of work, and each option costs reachability or battery.
- Whether the Post-Quantum Noise paper's results cover the `psk` modifier that decision 0014 uses.

---

## 14. Retry, expiry and relaying under online-only delivery

**Status:** closed by [decision 0017](../decisions/0017-retry-expiry-and-relaying.md): option A for direct messages and option C for groups, with hash-graph reconciliation between members, an expiry of 30 days by default, and delivery shown per device and per member. The open detail below is partly resolved there; what remains is listed at its end.

**Question:** Under [decision 0005](../decisions/0005-serverless-online-only-delivery.md), how long does a sending device keep and retry undelivered messages, and may anyone other than the sender carry it?

**Options:**

- **A. Sender-only retry.** Only the sending device delivers. It retries until delivery or until the message expires.
  - Cost: delivery fails if the two devices are never online together. The sender's device stores ciphertext and uses battery and bandwidth to retry.
- **B. Another device of the recipient.** A message may be delivered to any of the recipient's own devices, and that device passes it to the others. For example, a desktop that is online more often.
  - Cost: depends on multi-device handling ([question 3](#3-multi-device-key-handling)). It is the user's own device, not a server. It does not help users with one device.
- **C. Relaying by group members.** A member who received a group message passes it on to members who were offline when it was sent.
  - Cost: members store ciphertext for others and learn more about each other's online times. Whether this counts as store-and-forward under decision 0005 must be decided. DCGKA ([decision 0006](../decisions/0006-dcgka-for-groups.md)) requires every member to eventually process every causally prior message. Without this option, only the original sender can re-send, and a group stalls for a member whenever that sender is offline.

**Open detail:**

- The expiry time. Resolved by decision 0017: 30 days by default, from 1 to 90 days by the user's choice, counted from when a device first stored the message. Messages a device has not yet processed do not expire.
- What the sender is told about undelivered messages. Resolved by decision 0017: pending, delivered or expired, with delivery per device and per member on request.
- Limits on storage. Resolved by decision 0017: 256 MiB per device by default. Messages held for others are dropped first, starting with the sender that takes the most space.
- Whether this counts as store-and-forward under decision 0005 (option C). Resolved by decision 0017: a member relays only control messages of its own groups, which it can check itself, so it is an intended participant, not a third party.

Still open:

- How a member catches up when every copy of a control message it needs has expired. DCGKA processes control messages in causal order, so the member is stuck. Options:
  - remove the member and add it again, which costs a membership change and a key update for the whole group, loses the messages in between for that member, and needs a member with permission to do it ([question 16](#16-community-moderation-without-an-operator));
  - a longer expiry for control messages, which costs storage on every member device;
  - both.
- Whether group application messages are signed, so that members can check and relay them. Options:
  - sign them, which lets members relay them but removes their deniability within the group;
  - do not sign them, which keeps deniability, but only their sender can re-send them.
- How far one member can use other members' storage by sending many large control messages. Decision 0017 evicts the largest sender's messages first. Whether a per-sender limit is needed, and which, is open.
- Option B for direct messages: a recipient's device passing a direct message to the recipient's other devices. Decision 0016 holds a contact's new device until the user approves it, and the recipient's devices do not know which devices the sender approved. Options: keep sender-only delivery, which costs slower delivery to rarely-online devices; let the sender name the approved devices in each message, which costs telling the recipient the sender's trust states, which decision 0016 keeps local; or encrypt to each approved device's identity key for later delivery, which costs forward secrecy until that device's next handshake and needs a published design.
- How a phone retries without push services ([question 17](#17-mobile-reachability-without-push-services)).

---

## 15. Two-party component for DCGKA

**Question:** Which two-party secure messaging (2SM) protocol does DCGKA use to send secrets to one member?

DCGKA sends some secrets to a single member in a direct message, encrypted with a 2SM protocol (paper section 5.3). The paper states that the Signal protocol "does not suffice for our purposes because it heals from a compromise only after several rounds of communication, not with each message sent". It uses a protocol with optimal forward secrecy and post-compromise security from D. Jost, U. Maurer, M. Mularczyk, "Efficient Ratcheting: Almost-Optimal Guarantees for Secure Messaging", EUROCRYPT 2019 (full version: IACR ePrint 2018/954).

**Options:**

- **A. The protocol the paper uses (Jost, Maurer, Mularczyk).** Direct messages keep the Mosgird session protocol ([decision 0012](../decisions/0012-mosgird-session-protocol.md), which replaced the Double Ratchet of decision 0002).
  - Cost: two different two-party protocols to implement and test. The 2SM protocol is less widely implemented than the Double Ratchet. Its cost on phones must be measured. The paper's security analysis applies.
- **B. The Mosgird session protocol as the 2SM component.** One two-party protocol for everything. Its ratchet (decision 0012) heals on each change of direction, like the Double Ratchet.
  - Cost: the paper says a ratchet of this kind does not suffice for its guarantees. The paper's security proof would not apply as stated, and new analysis would be needed. The project does not do that analysis itself. Not a recommended option.
- **C. The paper's protocol for direct messages too.** Replace the ratchet of decision 0012 with the same 2SM protocol, or treat a direct message as a two-member group.
  - Cost: supersedes part of decision 0012. One two-party protocol to implement.

**Open detail:** the paper requires that 2SM map identities to public keys through a public key infrastructure that includes ephemeral prekeys. Under decision 0005 those prekeys come from first contact ([question 13](#13-first-contact-without-a-directory)). Decision 0012 has no prekeys, so option A would bring them back for groups only. Whether the 2SM protocol of Jost, Maurer, and Mularczyk can be instantiated with post-quantum primitives at the level of [decision 0011](../decisions/0011-cryptographic-suite-and-security-level.md) must be checked against the paper.

---

## 16. Community moderation without an operator

**Question:** How do communities give members with a moderating role the power to act against bad-faith members, when there is no server and no operator ([decision 0007](../decisions/0007-communities.md))?

Any mechanism must follow a published design for decentralized access control. None is chosen yet, and this project does not invent one.

**Options (may be combined):**

- **A. Signed roles chained to a community key.** Whoever creates a community holds its key. Roles are granted by signed statements that chain back to that key. Clients check the chain before they apply a moderation action.
  - Cost: losing or leaking the community key loses or gives away control. Revoking a role needs rules. Grants and revocations made at the same time must resolve to the same result for every member, using only causal order.
- **B. Several moderators must agree.** An action takes effect only when a set number of moderators have signed it.
  - Cost: under online-only delivery, enough moderators must be reachable, so action is slower. It resists a single compromised or rogue moderator.
- **C. Local moderation only.** Each member mutes or blocks others for themselves. There is no community-wide removal.
  - Cost: does not meet the team's requirement to act against bad-faith members. Listed for completeness.
- **D. Admission by invitation.** New members join only with an invitation signed by a member who holds a role that allows it.
  - Cost: slows growth. Invitations that are shared widely act like open admission. Combines with A or B.

**Open detail:**

- How two moderators who act against each other at the same time are resolved. DCGKA reaches the same membership from causal order (decision 0006). The permission rules must give the same answer too.
- What evidence a moderator can see. It is limited to what reporters disclose (question 6, option A).
- Whether moderation actions are logged, and who can read the log.
- Resistance to one person creating many identities, since new identities cost nothing to create.
- Appeals, and the transfer of a community when its owner leaves.

---

## 17. Mobile reachability without push services

**Question:** How does a phone receive messages while the app is not in use, when push services are excluded ([decision 0008](../decisions/0008-no-push-services.md)) and delivery is online-only ([decision 0005](../decisions/0005-serverless-online-only-delivery.md))?

Platform limits change between operating system versions. The costs below must be checked against current Android and Apple documentation before a decision is written.

**Options (may be combined):**

- **A. Reachable only while the app is open.** The client connects to the transport only in the foreground.
  - Cost: the least battery use and the simplest option. Delivery to phones depends on both users having the app open at the same time. The only option certain to be available on iOS.
- **B. A long-running background service.** On Android, a foreground service keeps the transport connected. Briar uses this approach.
  - Cost: steady battery and data use, more so on an anonymizing transport. Android requires a persistent notification, which shows anyone who sees the screen that the app is running. Android limits which foreground service types an app may use and for how long. Not available on iOS.
- **C. Periodic wake-ups scheduled by the operating system.** For example, Android WorkManager, whose shortest repeat interval is 15 minutes, or iOS background app refresh, which runs when the system chooses.
  - Cost: a message arrives only if the sender retries during one of the recipient's short online periods, so delivery is slow and unreliable. Regular online periods can form a pattern that network observers or contacts can recognize. On iOS, the system decides when and whether the app runs.
- **D. Delivery to the user's other device.** An always-on device of the user, such as a desktop, receives messages. The phone fetches them from that device when it connects ([question 14](#14-retry-expiry-and-relaying-under-online-only-delivery), option B).
  - Cost: depends on multi-device handling ([question 3](#3-multi-device-key-handling)). It does not help users with only a phone. The other device is the user's own, not a server, but it must be online and reachable.

**Open detail:**

- Whether an iOS client is possible with any option other than A.
- Battery and data cost of B on each candidate transport ([question 12](#12-transport-and-addressing)). This needs measurement, not estimates.
- Whether the client's notification text, in option B, can avoid naming the app.

---

## 18. Post-quantum deniable authentication

**Status:** closed by [decision 0012](../decisions/0012-mosgird-session-protocol.md) with option B: authentication by key encapsulation, using the Post-Quantum Noise framework. The open detail below is still open.

**Question:** How do two devices authenticate each other in a way that resists quantum attackers and stays deniable ([decision 0011](../decisions/0011-cryptographic-suite-and-security-level.md))?

X-Wing protects the confidentiality of a session against quantum attackers. Authentication is a separate property. It must hold at the time a session is set up, and it must not produce proof that a third party could check. Signatures produce such proof, so session setup is not signed.

Delivery is online-only ([decision 0005](../decisions/0005-serverless-online-only-delivery.md)), so session setup can be interactive. Both devices are online at the same time. This allows designs that need a round trip, which Signal's asynchronous handshake avoids.

**Options:**

- **A. Classical deniable authentication for now.** Devices authenticate each other with X25519 Diffie-Hellman between identity and session keys, as X3DH and Signal's PQXDH do. X-Wing adds post-quantum confidentiality.
  - Cost: deniable, and built on published, analyzed designs. Authentication is classical. Once a quantum computer exists, an attacker who can break X25519 at the time of setup can impersonate a device. Recorded sessions stay confidential.
- **B. Authentication by key encapsulation.** Each device holds a long-term X-Wing key. Each side encapsulates a secret to the other's long-term key, and only the holder of the matching private key can derive the session keys. Published designs of this kind include KEMTLS (Schwabe, Stebila, Wiggers, ACM CCS 2020) and Post-Quantum Noise (Angel, Dowling, Hülsing, Schwabe, Weber, ACM CCS 2022).
  - Cost: post-quantum and deniable, because nothing is signed. The designs are newer than X3DH and need more round trips, which online-only delivery permits. Adapting them to Mosgird must not change their structure, and needs a cryptographer's review.
- **C. Deniable post-quantum signatures.** Designated-verifier signatures (Brendel, Fiedler, Günther, Janson, Stebila, PKC 2022) or ring signatures (RingXKEM, Hashimoto, Katsumata, Niot, Tucker, Wiggers).
  - Cost: designed for an asynchronous handshake like Signal's. They are research designs with no production library.
- **D. Sign session setup with the hybrid signature.**
  - Cost: post-quantum authentication, but not deniable. A signed transcript proves to anyone who took part. This conflicts with the team's deniability requirement and is listed for completeness.

**Open detail:**

- How the Ed25519 and ML-DSA-87 parts of a signature are bound together (decision 0011). It must follow a published design so that neither part can be removed or replaced alone.
- How the chosen option interacts with first contact ([question 13](#13-first-contact-without-a-directory)) and with the group protocol's two-party component ([question 15](#15-two-party-component-for-dcgka)).
- How deniability is shown for the patterns of decision 0012. The symbolic provers that [decision 0013](../decisions/0013-formal-verification.md) requires do not check deniability in their usual form, so it needs a separate argument.
- Group control messages are signed, because DCGKA requires it. Group membership changes are therefore not deniable to other members, even if direct messages are.

---

## 19. Protection of data stored on the device

**Status:** closed by [decision 0015](../decisions/0015-protection-of-stored-data.md): encryption under a key held by the operating system's key store, always on (option A), and an optional passphrase (option B). There are no backups for now. Disappearing messages (option C) and the open detail below are still open.

**Question:** How does a device protect what it stores: identity keys, contacts, message history, and messages waiting for delivery?

Forward secrecy ([decision 0012](../decisions/0012-mosgird-session-protocol.md)) protects traffic, not stored data. Someone with access to an unlocked device, or to a copy of its storage, can read everything the device keeps unless the storage itself is protected. Messages waiting for delivery are kept in plaintext form until the next connection, so they depend on this protection too.

**Options (may be combined):**

- **A. Encrypt storage under a key held by the operating system's key store.** Examples are the Android Keystore and the Apple Keychain, backed by secure hardware where present.
  - Cost: protects against copying the storage off the device. Does not protect against someone who can unlock the device. The strength depends on the platform and the hardware.
- **B. Encrypt storage under a key derived from a passphrase** (Argon2id, in libsodium).
  - Cost: protects even if the device is unlocked, while the app is locked. Users must remember another secret, which conflicts with the goal of being easy for everyone. A forgotten passphrase loses all data.
- **C. Disappearing messages.** Messages are deleted after a time that the conversation sets.
  - Cost: limits what a seized device reveals. The other side's device must also delete, and a modified client can ignore the setting.
- **D. Keep no history.** Messages are shown and then deleted, unless the user saves them.
  - Cost: the strongest protection of history, and the least convenient.

**Open detail:**

- How long undelivered messages are kept ([question 14](#14-retry-expiry-and-relaying-under-online-only-delivery)).
- Whether backups exist, and how they are encrypted ([question 5](#5-message-history-sync)). Resolved for v0.1 by decision 0015: no backups.
- Whether all of this is the same on every platform, which the core library ([decision 0010](../decisions/0010-shared-core-library.md)) makes possible. Resolved by decision 0015: the core library encrypts records itself everywhere, and only the key store differs.
- Whether stored records are padded, so that a copy of the storage does not reveal how much a user talks.
- Disappearing messages: whether they are added, their default, and how the other device is asked to honour them.
