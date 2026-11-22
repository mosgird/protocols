# Test vectors

This directory holds the test vectors for the specification: known inputs and expected outputs for key agreement, ratchet steps, group key updates, and message encoding.

Every implementation runs these vectors in its own repository. A vector is added together with the specification section it tests. Changing a vector's expected output after release needs a new version under [VERSIONING.md](../spec/VERSIONING.md): a PATCH if the old vector disagreed with the referenced document, and a breaking version if the procedure itself changed.

The directory is empty until the specification sections it tests are written. No vector is copied from an implementation. Each is derived from the referenced documents (the Post-Quantum Noise and generic double ratchet papers, the X-Wing draft, and the DCGKA paper) and checked against them. The DCGKA paper publishes no vectors, so how its vectors are produced is open (see [open question 9](../spec/v0.1/open-questions.md#9-group-protocol-primitives-and-group-size-limits)).
