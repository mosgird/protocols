# References (v0.1)

**Status:** draft.

No cryptographic constructions are invented in this specification. Each mechanism follows one of the published designs below. The decision records say which design each part follows.

## Research papers

- M. Weidner, M. Kleppmann, D. Hugenroth, A. R. Beresford. Key Agreement for Decentralized Secure Group Messaging with Strong Security Guarantees. ACM CCS 2021, doi:10.1145/3460120.3484542. Extended version: IACR ePrint 2020/1281. Group protocol ([decision 0006](../decisions/0006-dcgka-for-groups.md)).
- D. Jost, U. Maurer, M. Mularczyk. Efficient Ratcheting: Almost-Optimal Guarantees for Secure Messaging. EUROCRYPT 2019. Full version: IACR ePrint 2018/954. The two-party component of DCGKA ([decision 0019](../decisions/0019-two-party-component-for-dcgka.md)).
- Y. Angel, B. Dowling, A. Hülsing, P. Schwabe, F. Weber. Post Quantum Noise. ACM CCS 2022. Handshakes ([decisions 0012](../decisions/0012-mosgird-session-protocol.md) and [0014](../decisions/0014-first-contact-by-invite.md)).
- J. Alwen, S. Coretti, Y. Dodis. The Double Ratchet: Security Notions, Proofs, and Modularization for the Signal Protocol. EUROCRYPT 2019. IACR ePrint 2018/1037. The ratchet within a connection (decision 0012).
- I. Goldberg, B. Ustaoglu, M. D. Van Gundy, H. Chen. Multi-party Off-the-Record Messaging. ACM CCS 2009. Short-lived signing keys for group application messages ([decision 0018](../decisions/0018-deniable-signatures-for-group-messages.md)).
- M. Kleppmann, H. Howard. Byzantine Eventual Consistency and the Fundamental Limits of Peer-to-Peer Databases. arXiv:2012.00472, 2020. Relaying and reconciliation between group members ([decision 0017](../decisions/0017-retry-expiry-and-relaying.md)).
- R. Cramer, V. Shoup. Design and analysis of practical public-key encryption schemes secure against adaptive chosen ciphertext attack. SIAM Journal on Computing, 2003. KEM-DEM encryption (decision 0019).
- P. Schwabe, D. Stebila, T. Wiggers. Post-Quantum TLS Without Handshake Signatures (KEMTLS). ACM CCS 2020. Cited as an alternative in [open question 18](open-questions.md#18-post-quantum-deniable-authentication).
- J. Brendel, R. Fiedler, F. Günther, C. Janson, D. Stebila. Post-quantum Asynchronous Deniable Key Exchange and the Signal Handshake. PKC 2022. Cited as an alternative in open question 18.
- K. Hashimoto, S. Katsumata, G. Niot, I. Tucker, T. Wiggers. RingXKEM. Cited as an alternative in open question 18.

## Standards and drafts

- X-Wing: the hybrid KEM in the IETF draft draft-connolly-cfrg-xwing-kem ([decision 0011](../decisions/0011-cryptographic-suite-and-security-level.md)).
- RFC 9106: Argon2 memory-hard function, for the optional passphrase ([decision 0015](../decisions/0015-protection-of-stored-data.md)).
- RFC 9180: Hybrid Public Key Encryption, which has the same KEM-DEM structure (decision 0019).
- The Noise Protocol Framework, by T. Perrin, on which Post Quantum Noise builds.
- The Tor Project's specifications for version 3 onion services, and the I2P project's specifications, including the network database and SAM version 3 ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)).

## Libraries

- libsodium, for X-Wing (from version 1.0.22), XChaCha20-Poly1305, BLAKE2b, Ed25519 and Argon2id.
- libcrux, for ML-DSA-87. IACR ePrint 2026/192 reports bugs in it that escaped formal verification (decision 0011).

## Deployed systems cited as background

These systems are cited for comparison and for the problems they show. Mosgird does not adopt their protocols.

- WhatsApp's multi-device design, from its encryption whitepaper, and the XMPP extensions XEP-0384 (OMEMO) and XEP-0450, and Matrix cross-signing ([decision 0016](../decisions/0016-user-identity-and-linked-devices.md)).
- Briar and Cwtch, cited in open questions as examples of peer-to-peer messengers.
