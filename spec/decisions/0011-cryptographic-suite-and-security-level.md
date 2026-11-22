# 0011. Cryptographic suite and security level

**Status:** Proposed

## Context

The team set a security level: at least 192 bits, ideally 256 bits or more. It also asked for post-quantum security, deniability, authenticity, and integrity, using one set of libraries on every platform ([decision 0010](0010-shared-core-library.md)).

The protocol so far uses only classical primitives: X25519 and Ed25519, about 128 bits each. Recorded traffic could be decrypted later by a quantum computer. The team had earlier considered the hybrid X25519 + sntrup761 (RFC 9941). sntrup761 is rated NIST category 2, below the new minimum, and no audited library offers it on every platform.

"Bits" here means the following:

- For a key exchange or a signature, it is the cost of the best known attack, matched to NIST's post-quantum categories. Category 3 is comparable to finding an AES-192 key, about 192 bits. Category 5 is comparable to AES-256, about 256 bits.
- For a symmetric key, a 256-bit key gives about 256 bits against classical attackers, and keeps NIST category 5 strength against quantum attackers.

## Decision

The protocol uses these primitives and no others, unless a later decision record adds them.

| Purpose | Primitive | Strength | Library |
|---|---|---|---|
| Key exchange | **X-Wing**: hybrid of X25519 and ML-KEM-768 | category 3 (about 192 bits) while ML-KEM-768 holds; about 128 bits from X25519 if it does not | libsodium (version 1.0.22 or later) |
| Authenticated encryption | **XChaCha20-Poly1305** | 256-bit key | libsodium |
| Hash, MAC, and key derivation | **BLAKE2b-512**, keyed BLAKE2b as MAC and key derivation function | 256 bits against collisions | libsodium |
| Signatures | **Ed25519 and ML-DSA-87 together.** A signature is valid only if both parts verify. | category 5 (about 256 bits) while ML-DSA-87 holds; about 128 bits from Ed25519 if it does not | libsodium (Ed25519) and libcrux (ML-DSA-87) |

The team accepts a classical half below 192 bits in each hybrid. The post-quantum half sets the strength, and the classical half protects against a future break of the post-quantum algorithm.

Further rules:

- **Signatures are used only where proof is wanted.** That covers community roles, moderation actions, and group control messages as DCGKA requires. Message content and session setup are never signed, so that they stay deniable. Deniable authentication comes from key exchange, not signatures. Making that authentication post-quantum is open ([open question 18](../v0.1/open-questions.md#18-post-quantum-deniable-authentication)).
- **sntrup761 is not used.** It is below the minimum.
- **No negotiation.** Every device uses this one suite. A change of suite is a new decision record and a new specification version, so an attacker cannot force a weaker choice.

## Consequences

- The minimum is met while ML-KEM and ML-DSA hold. If a lattice attack broke them, key exchange and signatures would fall back to about 128 bits, which is still today's common standard.
- Message keys and stored data use 256-bit symmetric keys, which meets the ideal.
- The key exchange reaches the minimum, not the ideal. ML-KEM-1024 would reach about 256 bits, but no standard pairing of X25519 with ML-KEM-1024 exists. RFC 10024 pairs ML-KEM-1024 with P-384, and X-Wing is defined only for ML-KEM-768. The team preferred X-Wing because it is one complete, specified construction available in libsodium on every platform.
- **X-Wing is an IETF draft (draft-connolly-cfrg-xwing-kem), not yet an RFC.** The specification must name the exact draft version it follows, and its test vectors must come from that version.
- **No standard format combines Ed25519 and ML-DSA-87.** As far as found, the IETF's draft composite signatures pair ML-DSA-87 with other classical algorithms. How the two signatures are bound together is an open detail of question 18. It must follow a published design, so that neither part can be removed or replaced alone. A cryptographer must review it.
- **libcrux's ML-DSA code had bugs that escaped its formal verification** (ePrint 2026/192). The version used must include their fixes.
- **Larger keys and signatures.** An X-Wing public key is 1,216 bytes and its ciphertext 1,120 bytes. An ML-DSA-87 signature is about 4.6 KB. Contact links and QR codes carry an address and a fingerprint, and the full keys are exchanged over the transport ([open question 13](../v0.1/open-questions.md#13-first-contact-without-a-directory)).
- **Decision 0002 is replaced.** It named X3DH and the Double Ratchet, which use only X25519. The team wants Mosgird's own structure, built from these primitives and from published concepts. [Decision 0012](0012-mosgird-session-protocol.md) defines it and supersedes 0002.
- **BLAKE2b is used less often as a key derivation function** than HKDF with SHA-2 in published designs. Every use must be specified exactly, including keys, personalization strings, and output lengths, and be covered by test vectors.

## Alternatives considered

- **X25519 + sntrup761.** Rejected. sntrup761 is below the minimum and has no audited cross-platform library. The larger NTRU Prime parameter sets have no RFC and no audited library.
- **P-384 + ML-KEM-1024 (RFC 10024).** It is about 192 bits or more in both halves. Not chosen: it needs libraries other than libsodium, and P-384 is a NIST curve.
- **X25519 + ML-KEM-1024 with a generic combiner.** Closest to the ideal. Not chosen, because the pairing is not standardized and would need its own review.
- **AES-256-GCM.** Not chosen. It is slow or open to timing attacks on processors without AES instructions, and its 96-bit nonce must never repeat.
- **SHA-512 with HKDF, or SHA-3.** Not chosen. The team preferred BLAKE2b, which is in libsodium. SHA-3 is not in libsodium.
- **ML-DSA-87 alone, or SLH-DSA.** Not chosen. ML-DSA alone has no fallback. SLH-DSA signatures are tens of kilobytes at this level.
