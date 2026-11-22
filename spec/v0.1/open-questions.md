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

**Question:** How is a user identified, and how is the link between a user and their key material established?

**Options:**

- **A. Identifier derived from the identity public key.** For example, a hash of the public key, displayed in encoded form.
  - Cost: no human-chosen names. Identity is not recoverable if the key is lost, unless a recovery mechanism exists. Display names must be separate and cannot be trusted by themselves.
- **B. Server-assigned username, with the public key bound on the server.** Not applicable after decision 0005: there is no server to assign names.
  - Cost: the server controls the username namespace and the binding. Users depend on the server for identity. Lower key-verification value unless clients check the binding over time.
- **C. Human-readable username, with a self-signed binding to the identity key.** The binding is signed by the user's key and shown to contacts. Clients check it.
  - Cost: more complex to specify. Without a server or registry, names are not unique: two users can choose the same name, so a name alone never identifies a user. Clients must store and check history to detect silent changes.

**Open detail:** whether the identifier is stable across devices, how a user's identity is recovered after losing all devices, and how the identifier relates to the transport address (see question 12).

---

## 3. Multi-device key handling

**Question:** How does a user with several devices hold keys, and how do messages reach all of them?

**Options:**

- **A. One identity per device, with fan-out.** Each device has its own identity key. A sender encrypts once per recipient device.
  - Cost: more pairwise sessions and more fan-out traffic as devices grow. Users must verify each device, or the verification model must treat the user as the set of devices. Adding a device requires the other side to learn about it.
- **B. Shared identity key copied to every device.** All devices hold the same identity private key.
  - Cost: compromise of any device exposes the identity. Revoking one device means rotating the identity for all. Simpler session model.
- **C. Device linking through an existing device.** A new device is added by an approval from an already-trusted device. Each device still has its own keys; the link creates a signed statement that the device belongs to the user.
  - Cost: needs a linking flow (for example, a QR code or a short code) and clear rules for revocation. Adds to the verification surface.

**Open detail:** how device lists are signed, distributed and checked without a server, and whether one device can hide another device of the same user from a contact. Under online-only delivery, each recipient device must be reachable separately, so a message can reach one of a user's devices and not another.

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

**Open detail:** what the client shows after a key change, and whether a change in a contact's key blocks sending until the user acknowledges it. Without a directory, first contact often happens through a key the contact hands over directly (question 13), so verification at first contact matters more.

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

**Open detail:** how reports interact with group channels, and whether anyone keeps a record of reports.

---

## 7. Server and channel structure visibility

**Question:** Who can learn server names, channel names, roles and membership?

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
  - Cost: both devices must be online at the same time, as for messages. Large files take longer to deliver over anonymizing transports. Exposes network addresses to the other party unless the transport hides them.

**Open detail:** a size limit, and whether a group member who already has a file may pass it to another member.

---

## 9. MLS ciphersuite and group size limits

**Question:** Which MLS ciphersuite is used, and what group sizes must be supported?

**Options:**

- **A. A single ciphersuite from RFC 9420's registry.** Fixed choice, with a version field in the protocol.
  - Cost: no algorithm agility without a new version. Simpler to test.
- **B. Negotiated ciphersuites.** Clients advertise support.
  - Cost: downgrade risk must be addressed. More test matrix.

**Open detail:** the maximum channel size for v0.1, and the performance target for commits in large groups. These need measurements, which are not yet done. After decision 0005 there is no Delivery Service. RFC 9420 relies on one to deliver commits so that members agree on their order. How commits are delivered and ordered without a server is not decided.

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
  - Cost: latency, battery use on phones, and dependence on relays run by others. The choice is made in [question 12](#12-transport-and-addressing).
- **D. Accept current exposure, documented.** Leave the gaps in place and state them clearly to users.
  - Cost: does not meet the minimal-metadata goal. Listed so that the choice is explicit.

**Open detail:** which of these the v0.1 threat model requires, and how each interacts with abuse handling ([question 6](#6-abuse-handling-for-an-encrypted-service)).

---

## 11. Ambiguities in the initial brief

These points are not clear from the initial brief. They are recorded here instead of being assumed.

- **"Server-independent identity."** Resolved by [decision 0005](../decisions/0005-serverless-online-only-delivery.md): there are no servers, so identity cannot depend on one. The overview now calls this goal "self-held identity".
- **"Servers" in the product sense and MLS groups.** It is not decided whether one server is one large group, or whether each channel is its own group. This draft assumes each channel is its own group. "Server" in this sense is a community of channels, not a machine.
- **License.** The project uses Mulan PSL v2, as recorded in the repository's LICENSE.md file. Any future relicensing is not considered in v0.1.

---

## 12. Transport and addressing

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

- Almost every option needs a way to join the network that someone else runs: directory authorities, reseed hosts, or bootstrap peers. Whether that fits [decision 0005](../decisions/0005-serverless-online-only-delivery.md) is undecided.
- How an address relates to the user identifier ([question 2](#2-identity-format)).
- How mobile background limits affect reachability.

---

## 13. First contact without a directory

**Question:** How does a device get another device's address and pre-key bundle the first time, with no server to publish them?

**Options:**

- **A. In person.** Devices exchange addresses and bundles directly, by QR code or over a local link.
  - Cost: needs the users to meet. Gives key verification at the same time ([question 4](#4-key-verification-method)).
- **B. Address out of band, bundle over the transport.** A user shares their address as text or a link through any channel. The devices then exchange bundles directly the first time both are online.
  - Cost: works at a distance. The first key is trusted on first use unless the users verify it later. The channel used to share the address learns that the two users intend to talk.
- **C. Introduction by a mutual contact.** A contact who knows both users passes on one user's address and bundle to the other.
  - Cost: the introducer can substitute keys. Verification is needed to detect it.
- **D. Publication in a distributed hash table.** A device publishes its address and bundle under a key-derived name.
  - Cost: peers that store or answer the lookup learn who is looking for whom. It depends on the transport offering such a table (question 12).

**Open detail:** whether one-time pre-keys are still needed when a bundle is exchanged directly, and how a device replaces a bundle that has been used.

---

## 14. Retry, expiry and relaying under online-only delivery

**Question:** Under [decision 0005](../decisions/0005-serverless-online-only-delivery.md), how long does a sending device keep and retry undelivered ciphertext, and may anyone other than the sender carry it?

**Options:**

- **A. Sender-only retry.** Only the sending device delivers. It retries until delivery or until the message expires.
  - Cost: delivery fails if the two devices are never online together. The sender's device stores ciphertext and uses battery and bandwidth to retry.
- **B. Another device of the recipient.** A message may be delivered to any of the recipient's own devices, and that device passes it to the others. For example, a desktop that is online more often.
  - Cost: depends on multi-device handling ([question 3](#3-multi-device-key-handling)). It is the user's own device, not a server. It does not help users with one device.
- **C. Relaying by group members.** A member who received a group message passes it on to members who were offline when it was sent.
  - Cost: members store ciphertext for others and learn more about each other's online times. It may be needed by group protocols that require every member to receive every message. Whether this counts as store-and-forward under decision 0005 must be decided.

**Open detail:** the expiry time, what the sender is told about undelivered messages, and limits on storage.
