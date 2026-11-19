# Open questions (v0.1)

Each question lists options and what each option costs. A question is closed when a decision record is added under [../decisions/](../decisions/) and this file is updated to point to it.

---

## 1. Federation

**Question:** Do independent servers interoperate with each other, or does each deployment stand alone?

**Options:**

- **A. No federation.** One official instance. Users on one server cannot reach users on another.
  - Cost: simplest trust model and key directory. Users cannot choose their operator. Growth depends on a single deployment.
- **B. Federation with server-to-server protocol.** Servers relay events to one another and each server holds its own users.
  - Cost: a second protocol to specify and secure. Key directory consistency must cross operators. Metadata is shared with more parties. Abuse handling must work across operators.
- **C. Defer, but keep identifiers operator-neutral.** Do not specify federation in v0.1. Avoid designs that make a later federation protocol impossible, such as identifiers that embed the server name.
  - Cost: some constraints on identifier design now. Federation is still unspecified.

**Current working assumption:** Option C. It is a working assumption only. Federation is not assumed in v0.1.

---

## 2. Identity format

**Question:** How is a user identified, and how is the link between a user and their key material established?

**Options:**

- **A. Identifier derived from the identity public key.** For example, a hash of the public key, displayed in encoded form.
  - Cost: no human-chosen names. Identity is not recoverable if the key is lost, unless a recovery mechanism exists. Display names must be separate and cannot be trusted by themselves.
- **B. Server-assigned username, with the public key bound on the server.**
  - Cost: the server controls the username namespace and the binding. Users depend on the server for identity. Lower key-verification value unless clients check the binding over time.
- **C. Human-readable username, with a self-signed binding to the identity key.** The binding is signed by the user's key and published by the server. Clients check it.
  - Cost: more complex to specify. Username changes and reclaiming a name after account loss need rules. Clients must store and check history to detect silent changes.

**Open detail:** whether the identifier is stable across devices, and how a user's identity is recovered after losing all devices.

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

**Open detail:** how device lists are signed, published and checked, and whether the server can hide a device from a contact.

---

## 4. Key verification method

**Question:** How do two users confirm that they are talking to each other and not to a server that substitutes keys?

**Options:**

- **A. Safety numbers.** Both users compare a short fingerprint of their combined keys, in text form, out of band.
  - Cost: manual comparison. Users often skip it. Works without a camera. A changed key shows as a changed number.
- **B. QR codes.** One device scans a code shown by the other.
  - Cost: needs both devices in the same place, or a camera. Good for in-person use. Same weakness as A when skipped.
- **C. Both A and B.** Offer either method. Users who compare in person use QR codes; others use safety numbers.
  - Cost: two code paths to implement and test. The UI must make the verified/unverified state clear.
- **D. Key transparency log.** The server publishes an append-only log of key changes, and clients check inclusion and consistency.
  - Cost: significant design and operations work. Requires an auditor or gossip mechanism to be meaningful. Does not replace user-level verification by itself.

**Open detail:** what the client shows after a key change, and whether a change in a contact's key blocks sending until the user acknowledges it.

---

## 5. Message history sync

**Question:** When a user adds a new device, does it receive earlier messages?

**Options:**

- **A. No history.** A new device sees only messages sent after it joined.
  - Cost: simplest. Users lose context on a new device. Forward secrecy holds.
- **B. Device-to-device transfer.** An existing device sends history to a new device over an encrypted channel.
  - Cost: needs an online existing device. Requires a secure transfer protocol and a design for large histories.
- **C. Encrypted server-side backup.** The client uploads encrypted history. The decryption key is derived from a recovery key or passphrase the user keeps.
  - Cost: the server holds large ciphertext blobs and their sizes. Losing the recovery key loses the history. A weak passphrase weakens the backup. Backup timing reveals activity patterns.

**Open detail:** whether history sync applies to channels as well as direct messages, and what happens to messages that were deleted on one device.

---

## 6. Abuse handling for an encrypted service

**Question:** How does the platform respond to reports of abusive content or behavior when the server cannot read message content?

Content policy itself is out of scope for the protocol. This question covers only the mechanisms available to a service that cannot read messages.

**Options:**

- **A. User-initiated reports with disclosed content.** A reporting user chooses to send the plaintext of a message, with a proof that it came from the reported sender, to the operator.
  - Cost: relies on the reporter's honesty. Disclosure is limited to what the reporter sends. Proof of origin needs a signature scheme.
- **B. Metadata-based controls.** Rate limits, account age limits, and limits on sending to unknown users.
  - Cost: no content signal. Can affect legitimate users. Needs metadata the server already sees.
- **C. Client-side classification before encryption.** The client checks content on the device before sending.
  - Cost: changes the trust model, because the client reports on its user. Requires a classifier on the device. Known to be contested, and it conflicts with the goal of private messaging. Listed for completeness; not a recommended option in v0.1.
- **D. Blocking and muting.** Users block contacts. Blocks are enforced by the server and by clients.
  - Cost: limited protection against a determined sender who creates new identities. Needs identity cost to be non-trivial (see identity format).

**Open detail:** how reports interact with group channels, and whether the operator keeps any record of reports.

---

## 7. Server and channel structure visibility

**Question:** Are server names, channel names, roles and membership encrypted from the relay server?

**Options:**

- **A. Visible to the server.** The server stores structure in plaintext. It can route and index without extra key management.
  - Cost: the server learns the community structure and membership.
- **B. Encrypted to members.** Structure is an encrypted state object in each channel's MLS group, with the server storing only ciphertext.
  - Cost: the server cannot enforce permissions on its own. Permission checks move to clients or to a signed-capability model. Search and invitation flows need redesign.

---

## 8. Attachments and file transfer

**Question:** How are files delivered?

**Options:**

- **A. Encrypted blobs on the relay server.** The client encrypts the file, uploads it, and sends a key and a reference in the message.
  - Cost: the server stores file ciphertext and sees file sizes. Storage and retention rules are needed.
- **B. Peer-to-peer transfer.** Devices exchange files directly, for example over WebRTC, after a message reference is delivered.
  - Cost: both devices must be online at the same time, or the transfer must be queued. Exposes IP addresses to the other party. Decision 0001 allows this for later.

---

## 9. MLS ciphersuite and group size limits

**Question:** Which MLS ciphersuite is used, and what group sizes must be supported?

**Options:**

- **A. A single ciphersuite from RFC 9420's registry.** Fixed choice, with a version field in the protocol.
  - Cost: no algorithm agility without a new version. Simpler to test.
- **B. Negotiated ciphersuites.** Clients advertise support.
  - Cost: downgrade risk must be addressed. More test matrix.

**Open detail:** the maximum channel size for v0.1, and the performance target for commits in large groups. These need measurements, which are not yet done.

---

## 10. Ambiguities in the initial brief

These points are not clear from the initial brief. They are recorded here instead of being assumed.

- **"Server-independent identity."** It is not clear whether this means that identity survives a change of server (which requires federation or portability), or that identity does not depend on the server for its security properties. This draft uses the second reading. Confirm before the spec is finalized.
- **"Servers" in the product sense and MLS groups.** It is not decided whether one server is one large MLS group, or whether each channel is its own group. This draft assumes each channel is its own group.
- **License.** The project uses Mulan PSL v2, as recorded in the repository's LICENSE file. Any future relicensing is not considered in v0.1.
