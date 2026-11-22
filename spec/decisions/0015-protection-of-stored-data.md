# 0015. Protection of stored data: key store always, passphrase optional, no backups

**Status:** Proposed

## Context

Forward secrecy ([decision 0012](0012-mosgird-session-protocol.md)) protects traffic, not what a device stores. A device keeps identity keys, contacts, message history, open invites ([decision 0014](0014-first-contact-by-invite.md)), and messages waiting for delivery. Waiting messages are stored before they are encrypted for a session. [Open question 19](../v0.1/open-questions.md#19-protection-of-data-stored-on-the-device) asked how all of this is protected.

The team chose:

- encryption under a key held by the operating system's key store, always on (option A);
- an optional app passphrase (option B);
- no backups for now.

## Decision

1. **Everything the core library stores is encrypted.** This covers keys, contacts, history, invites, and waiting messages.
   - Each record is sealed with XChaCha20-Poly1305 under a random 256-bit *storage key*, with a fresh random nonce.
   - The record's type and identifier are bound in as associated data, so that a record cannot be moved to another place without detection.
   - The core library does this itself, on every platform ([decision 0010](0010-shared-core-library.md)), and does not depend on a database's own encryption.
2. **The storage key is wrapped by the operating system's key store.** Wrapped means encrypted under another key. The storage key is stored only in wrapped form. The key store's key is created on the device and marked non-exportable, and is backed by secure hardware where the platform has it. The key stores are:
   - Android Keystore, backed by StrongBox or the TEE where present;
   - the Apple Keychain, with the Secure Enclave where present, on iOS and macOS;
   - on Windows, the Data Protection API with the TPM where present;
   - on Linux, the Secret Service, or the kernel key retention service.

   Where a device has no usable key store, which is common on BSD and on some Linux setups, the passphrase of point 3 becomes required on that device.
3. **Optional passphrase.** A user may set an app passphrase, off by default.
   - When it is set, the storage key is wrapped twice: under the key store, and under a key derived from the passphrase with **Argon2id** (RFC 9106, from libsodium). Unlocking the app needs both.
   - Argon2id is added to the suite of [decision 0011](0011-cryptographic-suite-and-security-level.md) for this one purpose.
   - Its parameters are at least 256 MiB of memory and 3 passes (libsodium's "moderate" level). They are lowered only on devices that cannot run that, and never below 64 MiB. The values are measured on target devices and written in the specification text.
   - A forgotten passphrase cannot be recovered. The app says so when the passphrase is set.
4. **Keys in memory.** Secret keys and plaintext are cleared from memory when no longer needed. Where the platform allows it, they are kept out of swap.
5. **No backups in v0.1.**
   - The core library offers no export or backup feature.
   - The apps opt out of operating-system backups: Android `allowBackup` off and no device-transfer rules for app data, and iOS and macOS data excluded from iCloud and device backups.
   - If a device is lost, the identity and history are lost with it, and contacts must accept a new invite.
6. **Deletion.** Deleting a record also deletes the record's ciphertext. Flash storage may keep old copies, so deletion is not guaranteed to erase them. Deleting the storage key, for example when the user removes the identity, makes all of it unreadable.

This closes [open question 19](../v0.1/open-questions.md#19-protection-of-data-stored-on-the-device), except for disappearing messages, which stay open.

## Consequences

- **A copy of the storage is unreadable** without the device's key store, because the key never leaves the device.
- **An unlocked device with no passphrase set is not protected.** Anyone who can use it can open the app and read everything. A passphrase protects against this while the app is locked.
- **The strength depends on the platform.** Hardware-backed key stores resist extraction better than software ones. A device without secure hardware gives weaker protection, and the app cannot always tell which kind it has.
- **Argon2id is an added primitive.** It is used only for the passphrase. A 256-bit storage key is not weakened by it, but a weak passphrase is still weak. The app should guide users toward long passphrases.
- **Losing a device loses everything.** This is not friendly to users who lose phones often. Backups and moving to a new device are revisited with multi-device support ([open question 5](../v0.1/open-questions.md#5-message-history-sync)).
- **Waiting messages** are as safe as the rest of storage until the next connection encrypts them for a session.
- **Disappearing messages** (question 19, option C) remain open.
- **Metadata.** The number and size of stored records may reveal how much a user talks, to someone with a copy of the storage. Padding records is an open detail of question 19.

## Alternatives considered

- **Passphrase always required.** Not chosen as the default. It conflicts with the goal of being easy for everyone, and a forgotten passphrase loses all data. It stays required only where no key store exists.
- **Database-level encryption, such as SQLCipher.** Not chosen. It uses primitives outside decision 0011, and it would differ between platforms.
- **No history** (question 19, option D). Not chosen. It is the least convenient.
- **An encrypted export file protected by a recovery code.** Not chosen for now. The file could be copied and attacked offline, and the recovery code would need 192 bits or more to keep the security level.
