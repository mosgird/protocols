# 0014. First contact by one-time invite and contact request

**Status:** Proposed

## Context

There is no server or directory ([decision 0005](0005-serverless-online-only-delivery.md)), so a device cannot look another device up. [Open question 13](../v0.1/open-questions.md#13-first-contact-without-a-directory) asked how two users who have never talked get each other's address and identity KEM key ([decision 0012](0012-mosgird-session-protocol.md)).

The team wants a user who has just created an identity to start talking to another user almost at once, at any distance, and wants no message delivered without the recipient's consent. The team chose:

- a link or QR code, followed by a contact request that the recipient accepts (options A, B and E of question 13);
- a link that carries the address, a fingerprint of the identity keys, and a one-time invite secret.

## Decision

The flow below has user B invite user A.

1. **B's device creates an invite.** It generates a random 256-bit invite secret and stores it with an expiry time. The invite is encoded as a link and as a QR code that carry:
   - B's device addresses: its onion address and its I2P destination hash ([decision 0009](0009-tor-and-i2p-with-local-links.md));
   - a 256-bit fingerprint of B's public identity keys: keyed BLAKE2b ([decision 0011](0011-cryptographic-suite-and-security-level.md)) over the identity KEM key and the two signature public keys;
   - the invite secret;
   - a format version.

   The link uses its own URI scheme and contains no domain name. B shares it through any channel, or A scans the QR code in person.
2. **A's device connects.** When A opens the link, A's device connects to one of B's addresses over Tor or I2P, or over a local link when scanned in person. It sends an invite identifier, derived from the invite secret with keyed BLAKE2b, so that B's device can find the matching secret.
3. **First-contact handshake.** The devices run the Post-Quantum Noise form of Noise pattern `XX` with the invite secret as a pre-shared key, mixed in before the first message (the Noise framework's `psk0` modifier).
   - B's device sends its identity KEM key encrypted in the handshake. A's device checks it against the fingerprint in the link and aborts if it does not match.
   - A's device sends its own identity KEM key encrypted in the handshake.
   - B's device drops the connection without an answer if the invite identifier is unknown or expired, or if the pre-shared key does not match. So only a holder of a valid invite learns B's identity KEM key or that B's device answers.
   - This replaces the `IK` pattern that decision 0012 named for first contact, because A knows only a fingerprint of B's key in advance, not the key itself.
4. **Contact request.** Over the new session, A's device sends a contact request. It may carry a display name and a short introduction, which B's user sees. No other message is accepted from A until B accepts.
5. **B's user decides.**
   - **Accept:** both devices store each other's identity keys and addresses as a contact. Messages that A's user wrote meanwhile are delivered. Later connections use the `KK` pattern of decision 0012.
   - **Decline or ignore:** B's device deletes A's keys and the request. A's device is told nothing beyond what its connection shows.
6. **The invite is used up.** An invite is accepted once and deleted when a request arrives with it, whatever B decides. It also expires: after 7 days by default, which the user can change. B can delete an invite at any time.

**Trust.** A's device trusts B's key because it matches the fingerprint in the link, so A trusts the channel the link came through. B's device trusts A's key because A held the invite. Comparing a safety code later protects against a link that was swapped on its way ([open question 4](../v0.1/open-questions.md#4-key-verification-method)). A QR code scanned in person needs no further check.

This closes [open question 13](../v0.1/open-questions.md#13-first-contact-without-a-directory).

## Consequences

- **Fast first contact.** After A opens the link, the steps that wait are the Tor or I2P connection and B's tap on Accept. There is no setup beyond creating an identity.
- **No unsolicited messages.** Only a link holder can reach B's device with a request, and each link works once. Strangers who learn B's address but not an invite get no answer.
- **A public, reusable link is not supported.** Users who want to be reachable by strangers, for example in a community, would need one. It is a new open detail of question 13.
- **Online at the same time.** A's device can use the invite only while B's device is reachable (decision 0005). If B is offline, A's device keeps retrying until the invite expires ([open question 14](../v0.1/open-questions.md#14-retry-expiry-and-relaying-under-online-only-delivery), [open question 17](../v0.1/open-questions.md#17-mobile-reachability-without-push-services)).
- **What leaks, and to whom:**
  - The channel used to share the link learns everything in it: B's addresses, the fingerprint, and the invite secret. Anyone who reads the link first can use it in A's place. B sees the request and can decline it, and a safety code comparison detects the swap.
  - B learns A's addresses and identity keys, even if B declines.
  - B's addresses in a link work for as long as B's device uses them, which can be longer than the invite lasts. Changing addresses is part of [open question 12](../v0.1/open-questions.md#12-transport-and-addressing).
- **Link size.** Two 32-byte addresses, a 32-byte fingerprint, a 32-byte secret, and a version: about 130 bytes, about 210 characters in base32. That fits a QR code that phone cameras read easily. The exact encoding is part of the specification text.
- **To be checked by a cryptographer:** the Post-Quantum Noise paper defines KEM forms of the Noise patterns, but must be checked for how it treats the `psk` modifier.
- **Formal model.** [Decision 0013](0013-formal-verification.md) requires that this flow is in the formal model. No model exists yet. The first model covers this flow together with decision 0012.

## Alternatives considered

- **Opening the link is enough, with no request.** Not chosen. Anyone with the link could message B without consent.
- **In person only.** Not chosen. It does not let people at a distance start talking.
- **A link with the full identity KEM key.** Not chosen. It is about 1.7 KB of text, and its QR code is too dense for many phone cameras. A fingerprint gives the same assurance in 32 bytes.
- **Introduction by a mutual contact** (question 13, option C). Not chosen for now. The introducer could substitute keys. It can be added later by a new decision.
- **A distributed hash table** (question 13, option D). Not chosen. The peers answering lookups would learn who looks for whom.
