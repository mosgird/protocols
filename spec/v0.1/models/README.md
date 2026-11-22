# Formal models

**Status: draft.** An AI tool drafted these models. Under [decision 0013](../../decisions/0013-formal-verification.md) and [AI_POLICY.md](../../../AI_POLICY.md), they are not a proof until a human with experience in ProVerif or Tamarin has reviewed every line, and decisions 0012 and 0014 stay Proposed until then.

| Model | Tool | What it covers |
|---|---|---|
| [proverif/handshake_kk.pv](proverif/handshake_kk.pv) | ProVerif 2.05 | The handshake between known contacts: the Post-Quantum Noise form of `KK` ([decision 0012](../../decisions/0012-mosgird-session-protocol.md)). |
| [proverif/handshake_xxpsk0.pv](proverif/handshake_xxpsk0.pv) | ProVerif 2.05 | First contact: the Post-Quantum Noise form of `XXpsk0` with the invite secret, followed by the contact request ([decision 0014](../../decisions/0014-first-contact-by-invite.md)). |
| [tamarin/ratchet.spthy](tamarin/ratchet.spthy) | Tamarin 1.12.0 | The ratchet inside a connection, with KEM-based key agreement (decision 0012). |

Shared ProVerif declarations are in [proverif/common.pvl](proverif/common.pvl).

## Properties checked

| Property | `KK` | `XXpsk0` | Ratchet |
|---|---|---|---|
| Secrecy of messages | yes | yes (contact request and reply) | yes |
| Forward secrecy | yes: all identity keys revealed after the session | yes: identity keys and invite secrets revealed after the session | yes: any state revealed after a message is received |
| Recovery after compromise | not applicable | not applicable | yes: after the peer generates a fresh KEM key |
| Mutual authentication (injective agreement) | yes, both directions | yes, both directions | not modelled (inherited from the handshake) |
| Sanity: an honest run completes | yes | yes | yes, and a compromise can leak a message |

The sanity checks show that the models are not vacuous. A model in which no session completes would prove every property trivially. They were also checked once by hand with a negative control: removing the ephemeral encapsulation from `KK` makes ProVerif find the forward-secrecy attack.

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
  - more than two honest devices.
- **First contact assumes the link arrives unchanged.** A link that the attacker reads first lets it make a request in the invited user's place. Decision 0014 states this, and the model doesn't contradict it, because the attacker's own invites are modelled separately.
