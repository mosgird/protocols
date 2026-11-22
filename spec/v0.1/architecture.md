# Architecture (v0.1)

**Status:** draft.

## 1. Components

- **Client.** Software running on a user's device. It generates and stores key material, encrypts outgoing messages, decrypts incoming messages, delivers ciphertext to other devices, keeps undelivered messages in protected local storage until it can deliver them, and manages local state. The protocol, cryptography, storage, and transports are implemented once in the shared library `mosgird/core`. The applications `mosgird/desktop` and `mosgird/android` add the user interface ([decision 0010](../decisions/0010-shared-core-library.md)).
- **Transport.** The means by which one device finds and reaches another, using an address derived from key material. It carries ciphertext and is not trusted with content. Over the internet, the transports are Tor onion services and I2P. Local links (Bluetooth, Wi-Fi Direct, the local network) are a fallback for when the internet is unavailable. Every link is encrypted and authenticated, and no client connects directly over the internet ([decision 0009](../decisions/0009-tor-and-i2p-with-local-links.md)).

The protocol has no server component. Implementations are not part of this specification. Their repositories name the version of the specification they follow (see [VERSIONING.md](../VERSIONING.md)).

## 2. Trust model

- Clients trust their own key material. Each device keeps its private keys locally.
- A contact's device is trusted with the messages addressed to it, and with nothing else.
- The transport and the network are not trusted. They may observe, delay, drop, replay, or reorder traffic. They cannot read or forge content without breaking the end-to-end encryption.
- A device can present false key material for someone else, for example when passing on a contact's identity KEM key or contact link. Detection depends on key verification ([open question 4](open-questions.md#4-key-verification-method)).
- A user's devices trust a device list signed by their own user key. A contact's device sends nothing to a device of that user until its own user approves it, and never to a device its user distrusted ([decision 0016](../decisions/0016-user-identity-and-linked-devices.md)). Whoever holds a user's primary device can sign device lists for that user.
