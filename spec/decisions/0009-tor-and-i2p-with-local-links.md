# 0009. Tor onion services and I2P, with local links as a fallback

**Status:** Proposed

## Context

[Decision 0005](0005-serverless-online-only-delivery.md) removed servers and domain names and left the transport open ([open question 12](../v0.1/open-questions.md#12-transport-and-addressing)). Privacy is the primary constraint of the project. A transport that shows each device's network address to every contact, such as a direct connection over the internet, libp2p, Yggdrasil, or WireGuard alone, adds to what other parties can observe.

The team chose Tor onion services and I2P for the internet. It also chose local links as a second transport for times when the internet is unavailable or cut off, and asked that encryption on them be strongly enforced.

## Decision

- **Internet transports.** A device is reachable as a Tor onion service and as an I2P destination. Its address on each network is derived from a public key, as each network defines it: a version 3 onion address for Tor, and a destination for I2P. A client supports both networks. Whether a device runs both at the same time, and how it chooses one for each contact, is open ([open question 12](../v0.1/open-questions.md#12-transport-and-addressing)).
- **No direct internet connections.** Clients do not connect to each other's network addresses directly over the internet, and they do not publish their network address for the protocol.
- **Local links.** Clients may also deliver over Bluetooth, Wi-Fi Direct, and the local network when two devices are nearby. This is meant for times when neither Tor nor I2P can be reached, for example during a network shutdown. Whether local links are also used while the internet is available is open.
- **Encryption on every link.** The end-to-end encryption of decisions 0002 and 0006 applies on every transport. In addition:
  - Over local links, devices first run an authenticated key exchange from a published design, such as a handshake from the Noise Protocol Framework. Only then do they send anything beyond what discovery needs. Which handshake is used is open.
  - The security that Bluetooth or Wi-Fi provides is not relied upon.
  - A client never falls back to an unencrypted or unauthenticated link on any transport. If it cannot establish one, it does not connect.
- **Discovery on local links** must not reveal the user's identity key, or any other stable identifier, to observers who are not contacts. How it does so is open.
- **The networks' own infrastructure.** Tor relays, Tor's directory authorities, I2P routers, and I2P reseed hosts belong to the transport. They are not servers of this protocol. They carry ciphertext and the transport's own routing data. They never store Mosgird messages, which matches decision 0005. What they can observe is listed in [overview section 3.3](../v0.1/overview.md#33-what-other-parties-can-observe).

## Consequences

- **Lookup.** Both networks already look up an address from a public key, through their own distributed directories: Tor's onion service descriptor directories, and I2P's network database. The protocol needs no directory or distributed hash table of its own to reach a known address. First contact, meaning how a user learns another user's address in the first place, is still open ([open question 13](../v0.1/open-questions.md#13-first-contact-without-a-directory)).
- **Linked addresses.** A device has two internet addresses. A contact learns both, and so learns that they belong to the same device. Other parties can link them only if a contact discloses them.
- **New observations.** Network observers can see that a device uses Tor or I2P. In many countries this is itself sensitive, and some block Tor; bridges and pluggable transports are open detail. An I2P router lists its network address in I2P's network database unless it runs in hidden or firewalled mode. Overview section 3.3 records both.
- **Cost on phones.** Running Tor and I2P together adds the background cost of a second network to the cost of staying reachable. This adds to [open question 17](../v0.1/open-questions.md#17-mobile-reachability-without-push-services) and needs measurement. An I2P router normally also routes traffic for other users. Whether a client may limit this, and what limiting it costs, must be checked against I2P's documentation.
- **Latency.** Both networks route through several relays, so delivery is slower than a direct connection. This is acceptable for messaging, and the protocol must not assume low latency.
- **Neither network resists an observer who sees the whole network.** Timing correlation across the network remains possible. This limit is recorded in overview section 3.3 and [open question 10](../v0.1/open-questions.md#10-metadata-minimization).
- **Local links reveal presence.** Nearby observers can see that a device is broadcasting or connecting. Discovery that hides stable identifiers limits what they learn, but does not hide the radio activity itself.
- **Implementation.** The specification does not name a Tor or I2P implementation or library. That choice belongs to `mosgird/client` and `mosgird/android`, which must follow this record.

## Alternatives considered

- **Tor only.** Simpler, with one network to specify, run, and test. Not chosen. The team wants two independent networks, so that a device stays reachable if one is blocked or fails.
- **I2P only.** Not chosen, for the same reason. I2P's network is also smaller than Tor's.
- **Nym mixnet.** It resists an observer who sees the whole network, which neither chosen network does. Not chosen, because of higher latency, constant cover traffic, and paid access through gateways. It remains a possible later addition.
- **Veilid.** Not chosen. The project is young, and its interfaces still change.
- **BitTorrent-style peer discovery (the Mainline DHT, with BitTorrent's "forced encryption").** Rejected for the internet:
  - Announcing in the Mainline DHT shows the device's network address to the DHT nodes that store and answer lookups, and so to anyone who runs such nodes.
  - BitTorrent's protocol encryption (Message Stream Encryption) is obfuscation against traffic shaping. It does not authenticate the peer, so it gives no protection against an active attacker.
  - Inside Tor and I2P, key-addressed lookup already exists, as described under Consequences.
  - The team's wish to meet peers only with permission is a first-contact question. It is recorded as option E of open question 13.
- **Direct internet connections, libp2p, Yggdrasil, or WireGuard.** Rejected as transports, because each shows network addresses to contacts.
- **Reticulum.** Not chosen for now. It may be reconsidered for radio links when local links are specified.
