# Test vectors

This directory holds the test vectors for the specification: known inputs and expected outputs for key agreement, ratchet steps, MLS epoch derivation, and message encoding.

Every implementation runs these vectors in its own repository. A vector is added together with the specification section it tests, and a vector that changes the expected output of an existing section is a change to a released version, which needs a new version under [VERSIONING.md](../spec/VERSIONING.md).

The directory is empty until the specification sections it tests are written. No vector is copied from an implementation. Each is derived from the referenced documents (RFC 9420, and the Signal X3DH and Double Ratchet specifications) and checked against them.
