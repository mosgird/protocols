# Formal models

**Status: draft.** An AI tool drafted these models. Under [decision 0013](../../decisions/0013-formal-verification.md) and [AI_POLICY.md](../../../AI_POLICY.md), they are not a proof until a human with experience in ProVerif or Tamarin has reviewed every line, and decisions 0012 and 0014 stay Proposed until then.

| Model | Tool | What it covers |
|---|---|---|
| [proverif/handshake_kk.pv](proverif/handshake_kk.pv) | ProVerif 2.05 | The handshake between known contacts: the Post-Quantum Noise form of `KK` ([decision 0012](../../decisions/0012-mosgird-session-protocol.md)). |
| [proverif/handshake_xxpsk0.pv](proverif/handshake_xxpsk0.pv) | ProVerif 2.05 | First contact: the Post-Quantum Noise form of `XXpsk0` with the invite secret, followed by the contact request ([decision 0014](../../decisions/0014-first-contact-by-invite.md)). |
| [tamarin/ratchet.spthy](tamarin/ratchet.spthy) | Tamarin 1.12.0 | The ratchet inside a connection, with KEM-based key agreement (decision 0012). |
| [proverif/group_relay.pv](proverif/group_relay.pv) | ProVerif 2.05 | Group messages passed on by other members ([decision 0017](../../decisions/0017-retry-expiry-and-relaying.md)): a relayed message is accepted only as its sender signed it. Also application messages signed under short-lived keys ([decision 0018](../../decisions/0018-deniable-signatures-for-group-messages.md)). |
| [proverif/two_party.pv](proverif/two_party.pv) | ProVerif 2.05 | DCGKA's two-party component ([decision 0019](../../decisions/0019-two-party-component-for-dcgka.md)): one bounded exchange that starts under a one-time prekey. |

Shared ProVerif declarations are in [proverif/common.pvl](proverif/common.pvl).

## Properties checked

| Property | `KK` | `XXpsk0` | Ratchet |
|---|---|---|---|
| Secrecy of messages | yes | yes (contact request and reply) | yes |
| Forward secrecy | yes: all identity keys revealed after the session | yes: identity keys and invite secrets revealed after the session | yes: any state revealed after a message is received |
| Recovery after compromise | not applicable | not applicable | yes: after the peer generates a fresh KEM key |
| Mutual authentication (injective agreement) | yes, both directions | yes, both directions | not modelled (inherited from the handshake) |
| Sanity: an honest run completes | yes | yes | yes, and a compromise can leak a message |

For group relaying (`group_relay.pv`): a message accepted as from an honest member was sent by that member with the same group, predecessor hashes and content, whichever member relayed it. The identifier is part of the signed content. The sanity query shows that a relayed message is accepted. The same holds for application messages signed under a short-lived key, when a device accepts that key only through the sender's session, modelled as a private channel. Secrecy is not checked, because group keys come from DCGKA, which has no model yet.

For the two-party component (`two_party.pv`): device A sends two messages, device B replies, and A answers. Delivery is authentic and in order, as DCGKA's authenticated causal broadcast provides. All four payloads stay secret, also after every key both devices still hold is revealed (forward secrecy). The sanity query shows that B receives the last message.

The sanity checks show that the models are not vacuous. A model in which no session completes would prove every property trivially. They were also checked once by hand with a negative control: removing the ephemeral encapsulation from `KK` makes ProVerif find the forward-secrecy attack. In `group_relay.pv`, removing the signature check makes ProVerif find forgeries for both authenticity queries, and letting a device take a short-lived key from the public channel instead of the sender's session makes ProVerif find forgeries of application messages for both members. In `two_party.pv`, revealing B's prekey afterwards, as when a signed prekey leaks before it is deleted, makes ProVerif find both messages A sent before B's reply, and only those.

## Running the models

```sh
python3 scripts/check_models.py --proverif   # about 20 seconds
python3 scripts/check_models.py --tamarin    # about 3 minutes; uses up to 3 GB of memory
```

The tools must be on `PATH`. CI installs them as in `.github/workflows/formal-models.yml`. The ProVerif models run on every pull request that changes this directory. The Tamarin model runs when it changes, and once a week.

ProVerif reports a sanity query as `not event(...) is false`, which means the event is reachable. `scripts/check_models.py` expects that for sanity queries and `true` for every other query, and it expects every Tamarin lemma to be verified.

## What the models do not cover

These are open for the expert review.

- **Bounded ratchet.** The Tamarin model unrolls one connection into two changes of direction, one message each. With loops, Tamarin's automatic search did not terminate within 3 GB of memory. An unbounded model needs hand-written loop invariants (helper lemmas).
- **Symbolic primitives.** X-Wing, XChaCha20-Poly1305, and keyed BLAKE2b are ideal primitives in these models. The computational security of the combination needs a separate argument, for example in CryptoVerif or on paper.
- **Simplifications.**
  - Nonces are left out.
  - Handshake ciphertexts are hashed into the transcript, but not encrypted as Post-Quantum Noise does after the first key exists. That affects identity hiding, not secrecy.
  - The two outputs of each key derivation are separate functions.
- **Not checked:**
  - deniability ([open question 18](../open-questions.md#18-post-quantum-deniable-authentication));
  - identity hiding;
  - key-compromise impersonation;
  - that a device without an invite learns nothing;
  - messages that arrive out of order, and their skipped keys;
  - more than two honest devices;
  - for group relaying: DCGKA itself, the new signing key a member gets on every key update (one fixed key per member is modelled, so a leaked old key is not covered), reconciliation (that every member eventually gets every message), expiry, and detection of a sender that signs two messages that fork. The hybrid signature is one ideal signature. For short-lived keys (decision 0018): the decision 0012 session is an ideal private channel between honest members, so the authenticity result follows closely from that assumption; no dishonest member and no leaked key are modelled; a key is not tied to a group or epoch; the proof-of-possession and key-list steps of mpOTR are not modelled; and deniability, including that no long-term signature covers an application message, is not checked.
- **The two-party component** is one bounded run between two honest devices. Recovery after compromise, messages sent by both sides at once, the signed prekey's lifetime, and DCGKA around it are not modelled. Public-key encryption is an ideal X-Wing followed by an ideal AEAD.
- **First contact assumes the link arrives unchanged.** A link that the attacker reads first lets it make a request in the invited user's place. Decision 0014 states this, and the model doesn't contradict it, because the attacker's own invites are modelled separately.
